# Name: SNODAS_utilities.py
# Version: 1
# Author: Emma Giles
# Organization: Open Water Foundation
#
# Purpose: SNODAS_utilities.py contains the functions utilized within the SNODAS tools (SNODASDaily_Automated.py and
# SNODASDaily_Interactive.py). Both scripts process zonal statistics of SNODAS raster datasets with respect to the
# input vector shapefile (basin boundaries). The SNODAS tools were originally developed to calculate zonal statistics
# of Colorado Basin boundaries.
#
# Both scripts call the same functions defined in this SNODAS_utilities.py script. SNODASDaily_Automated.py
# downloads the current date of SNODAS data and outputs the results in multiple geometries (geoJSON and shapefile)
# and multiple .csv files (one .csv file for the processing date and one .csv file for EACH basin in the input
# vector shapefile). SNODASDaily_Interactive.py processes historical dates of SNODAS data and outputs the results
# in multiple geometries (geoJSON and shapefile) and multiple .csv files (one .csv file for the processing date and
# one .csv file for EACH basin in the input vector shapefile).

# Import necessary modules
import configparser
import csv
import ftplib
import gdal
import glob
import gzip
import logging
import ogr
import os
import osr
import subprocess
import sys
import tarfile
import time
import zipfile

from datetime import datetime, timedelta
from logging.config import fileConfig
from pathlib import Path
from shutil import copy, copyfile

from PyQt5.QtCore import QVariant
from qgis.analysis import (
    QgsRasterCalculator,
    QgsRasterCalculatorEntry,
    QgsZonalStatistics)
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextScope,
    QgsField,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsVectorFileWriter
)
sys.path.append('/usr/share/qgis/python/plugins')

# gdal.UseExceptions()
# Read the config file to assign variables. Reference the following for code details:
# https://wiki.python.org/moin/ConfigParserExamples
# Check to see which OS is running
if sys.platform == 'linux' or sys.platform == 'linux2' or sys.platform == 'cygwin' or sys.platform == 'darwin':
    LINUX_OS = True
else:
    LINUX_OS = False
# This used to import ConfigParser, but it has been renamed configparser for PEP 8 compliance.
CONFIG = configparser.ConfigParser()


CONFIG_FILE = "../test-CDSS/config/SNODAS-Tools-Config.ini"
CONFIG.read(CONFIG_FILE)

# Create and configures logging file
fileConfig(CONFIG_FILE)
logger = logging.getLogger('utilities')


# Helper function to obtain option values of config file sections.
def config_map(section: str) -> dict:
    dict1 = {}
    options = CONFIG.options(section)
    for option in options:
        dict1[option] = CONFIG.get(section, option)
    return dict1

# Assigns the values from the configuration file to the python variables. See below for description of each
# variable obtained by the configuration file.
#
# HOST: The SNODAS FTP site url to access the downloadable data.
# USERNAME: The SNODAS FTP site username to access the downloadable data.
# PASSWORD: The SNODAS FTP site password to access the downloadable data.
# SNODAS_FTP_FOLDER: The folder pathname within the SNODAS FTP site that accesses the SNODAS masked datasets. The
# masked datasets are SNODAS grids clipped to the contiguous U.S. boundary.
# CLIP_PROJECTION: The EPSG projection code of the input basin extent shapefile. Defaulted to WGS84. The basin
# extent shapefile is used to clip the national SNODAS grids to the clipped extent of the basin boundaries.
# CALCULATE_STATS_PROJECTION: The desired EPSG projection code of the final products (snow cover grid and
# clipped SNODAS grid). Defaulted to Albers Equal Area.
# ID_FIELD_NAME: The field name of the basin boundary attribute table describing the identification of each basin.
# The naming convention of the CSVByBasin result files use the ID_FIELD_NAME.
# NULL_VAL: The null values that SNODAS applies to the data's null value. Defaulted to -9999 but should be changed
# if the null values provided by SNODAS are changed.
# CALCULATE_SWE_MIN: Daily zonal SWE minimum statistic will be calculated if this value is 'True'.
# CALCULATE_SWE_MAX: Daily zonal SWE maximum statistic will be calculated if this value is 'True'.
# CALCULATE_SWE_STD_DEV: Daily zonal SWE standard deviation statistic will be calculated if this value is 'True'.
# CELL_SIZE_X: The spatial resolution of the SNODAS (CALCULATE_STATS_PROJECTION) cells' x-axis (in meters).
# CELL_SIZE_Y: The spatial resolution of the SNODAS (CALCULATE_STATS_PROJECTION) cells' y-axis (in meters).
# GEOJSON_PRECISION: The number of decimal places (precision) used in the output GeoJSON geometry.
# TSTOOL_INSTALL_PATH: The full pathname to the TsTool program.
# TsToolBatchFile: The full pathname to the TsTool Batch file responsible for creating the time-series graphs.
# AEA_CONIC_STRING: USA_Albers_Equal_Area projection in WKT (Proj4) - for use in Linux systems


TSTOOL_INSTALL_PATH = config_map("ProgramInstall")['tstool_pathname']
TSTOOL_SNODAS_GRAPHS_PATH = config_map("ProgramInstall")['tstool_create-snodas-graphs_pathname']
AWS_BATCH_PATH = config_map("ProgramInstall")['aws_batch_pathname']

HOST = config_map("SNODAS_FTPSite")['host']
USERNAME = config_map("SNODAS_FTPSite")['username']
PASSWORD = config_map("SNODAS_FTPSite")['password']
SNODAS_FTP_FOLDER = config_map("SNODAS_FTPSite")['folder_path']
NULL_VAL = config_map("SNODAS_FTPSite")['null_value']

ID_FIELD_NAME = config_map("BasinBoundaryShapefile")['basin_id_fieldname']

CLIP_PROJECTION = "EPSG:" + config_map("Projections")['datum_epsg']
CALCULATE_STATS_PROJECTION = "EPSG:" + config_map("Projections")['calcstats_proj_epsg']
CELL_SIZE_X = float(config_map("Projections")['calculate_cellsize_x'])
CELL_SIZE_Y = float(config_map("Projections")['calculate_cellsize_y'])

GEOJSON_PRECISION = config_map("OutputLayers")['geojson_precision']
GEOJSON_ZIP: str = config_map('OutputLayers')['geojson_zip']
TSGRAPH_WEEKLY_UPDATE = config_map("OutputLayers")['tsgraph_weekly_update']
TSGRAPH_WEEKLY_UPDATE_DATE = config_map("OutputLayers")['tsgraph_weekly_update_date']

CALCULATE_SWE_MIN = config_map("OptionalZonalStatistics")['calculate_swe_minimum']
CALCULATE_SWE_MAX = config_map("OptionalZonalStatistics")['calculate_swe_maximum']
CALCULATE_SWE_STD_DEV = config_map("OptionalZonalStatistics")['calculate_swe_standard_deviation']


AEA_CONIC_STRING =\
    "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

# Set the srs for the CALCULATE_STATS_PROJECTION for a Linux system.
calculate_statistics_projection_srs = osr.SpatialReference()
calculate_statistics_projection_srs.ImportFromProj4(AEA_CONIC_STRING)
CALCULATE_STATS_PROJ_WKT = calculate_statistics_projection_srs.ExportToWkt()

# Get today's date.
now = datetime.now()


def download_snodas(download_dir: Path, single_date: datetime) -> list:
    """Access the SNODAS FTP site and download the .tar file of single_date. The .tar file saves to the specified
    download_dir folder.
    download_dir: full path name to the location where the downloaded SNODAS rasters are stored
    single_date: the date of interest in datetime format"""

    logger.info('download_snodas: Starting {}'.format(single_date))

    # Code format for the following block of code in reference to:
    # http://www.informit.com/articles/article.aspx?p=686162&seqNum=7 and
    # http://stackoverflow.com/questions/5230966/python-ftp-download-all-files-in-directory
    # Connect to FTP server
    ftp = ftplib.FTP(HOST, USERNAME, PASSWORD)

    logger.info('download_snodas: Connected to FTP server. Routing to {}'.format(single_date))

    # Direct to folder within FTP site storing the SNODAS masked data.
    ftp.cwd(SNODAS_FTP_FOLDER)

    os.chdir(download_dir)

    # Move into FTP folder containing the data from single_date's year
    ftp.cwd(str(single_date.year) + '/')

    # Move into FTP folder containing the data from single_date's month
    month_folder = single_date.strftime('%m') + "_" + single_date.strftime('%b') + '/'
    ftp.cwd(month_folder)

    # Set day value to a padded digit. Ex: 2 would change to 02
    day = single_date.strftime('%d')

    # Iterate through files in FTP folder and save single_date's data as a file in download folder
    # Create empty list to track if a download is available
    no_download_available = []
    filenames = ftp.nlst()
    for file in filenames:
        if file.endswith('{}.tar'.format(day)):
            local_file = open(file, 'wb')
            ftp.retrbinary('RETR ' + file, local_file.write, 1024)

            logger.info('download_snodas: Downloaded {}'.format(single_date))
            # If SNODAS data is available for download, append a '1'
            no_download_available.append(1)
            local_file.close()
        else:
            # If SNODAS data is not available for download, append a '0'
            no_download_available.append(0)

    logger.info('download_snodas: Finished {} \n'.format(single_date))
    # Report error if download marker '1' is not in the list
    if 1 not in no_download_available:
        logger.error('download_snodas: Download unsuccessful for {}'.format(single_date), exc_info=True)
        failed_date = single_date

    # Report success if download marker '1' is in the list
    else:
        print('\nDownload complete for {}.'.format(single_date))
        logger.info('download_snodas: Download complete for {}.'.format(single_date))
        failed_date = 'None'

    # Retrieve a timestamp to later export to the statistical results
    timestamp = datetime.now().isoformat()

    # Add values of optional statistics to a list to be checked for validity in SNODASDaily_Automated.py and
    # SNODASDaily_Interactive.py scripts
    opt_stats = [CALCULATE_SWE_MAX, CALCULATE_SWE_MIN, CALCULATE_SWE_STD_DEV]

    return [timestamp, opt_stats, failed_date]


def format_date_yyyymmdd(date: datetime) -> str:
    """Convert datetime date to string date in format: YYYYMMDD.
     date: the date of interest in datetime format"""

    logger.info('format_date_yyyymmdd: Starting {}'.format(date))

    # Parse year, month and day of input date into separate entities.
    year = date.year
    month = date.strftime('%m')
    day = date.strftime('%d')

    # Concatenate strings of the year, double-digit month, and double-digit day.
    day_string = str(year) + month + day

    logger.info('format_date_yyyymmdd: Finished {} \n'.format(date))

    # Return string.
    return day_string


def untar_snodas_file(file: str, folder_input: Path, folder_output: Path) -> None:
    """Untar downloaded SNODAS .tar file and extract the contained files to the folder_output
    file: SNODAS .tar file to untar
    folder_input: the full pathname to the folder containing 'file'
    folder_output: the full pathname to the folder containing the extracted files"""

    logger.info('untar_snodas_file: Starting {}'.format(file))

    # Check for file extension .tar
    if file.upper().endswith('.TAR'):

        # Set full pathname of file
        file_full = folder_input / file

        # Open .tar file
        tar = tarfile.open(file_full)

        # Change working directory to output folder
        os.chdir(folder_output)

        # Extract .tar file and save contents in output directory
        tar.extractall()

        # Close .tar file
        tar.close()

        logger.info('untar_snodas_file: {} has been untarred.'.format(file))

    else:
        logger.info('untar_snodas_file: {} is not a .tar file and has not been untarred.'.format(file))

    logger.info('untar_snodas_file: Finished {} \n'.format(file))


def delete_irrelevant_snodas_files(file: str) -> None:
    """Delete file if not identified by the unique SWE ID. The SNODAS .tar files contain many different SNODAS datasets.
     For this project, the parameter of interest is SWE, uniquely named with ID '1034'. If the configuration file is
     set to 'False' for the value of the 'SaveAllSNODASParameters' section, then the parameters other than SWE are
     deleted.
     file: file extracted from the downloaded SNODAS .tar file"""

    # Check for unique identifier '1034'.
    if '1034' not in file:

        # Delete file
        Path(file).unlink()
        logger.info('delete_irrelevant_snodas_files: {} has been deleted.'.format(file))

    else:
        logger.info('delete_irrelevant_snodas_files: {} has the unique code 1034 and won\'t be deleted.'.format(file))

    logger.info('delete_irrelevant_snodas_files: Finished {} \n'.format(file))


def move_irrelevant_snodas_files(file: str, folder_output: Path) -> None:
    """Move file to the 'OtherParameters' folder if not identified by the unique SWE ID, '1034'. The SNODAS .tar files
    contain many different SNODAS datasets. For this project, the parameter of interest is SWE, uniquely named with ID
    '1034'. If the configuration file is set to 'True' for the value of the 'SaveAllSNODASParameters' section, then the
    parameters other than SWE are moved to 'OtherParameters' subfolder of the 2_SetEnvironment folder.
    file: file extracted from the downloaded SNODAS .tar file
    folder_output: full pathname to folder where the other-than-SWE files are contained, OtherParameters"""

    logger.info('move_irrelevant_snodas_files: Starting {}'.format(file))

    # Check for unique identifier '1034'.
    if '1034' not in file:

        # Move copy of file to folder_output. Delete original file from original location.
        copy(file, folder_output)
        logger.info('move_irrelevant_snodas_files: {} has been moved to {}.'.format(file, folder_output))
        Path(file).unlink()

    else:

        logger.info('move_irrelevant_snodas_files: {} has the unique code 1034 and has not been moved to {}.'
                    .format(file, folder_output))

    logger.info('move_irrelevant_snodas_files: Finished {} \n'.format(file))


def extract_snodas_gz_file(file: str) -> None:
    """Extract .dat and .Hdr files from SNODAS .gz file. Each daily SNODAS raster has 2 files associated with it
    (.dat and .Hdr) Both are zipped within a .gz file.
    file: .gz file to be extracted"""

    logger.info('extract_snodas_gz_file: Starting {}'.format(file))

    # Check for file extension .gz
    if file.upper().endswith('.GZ'):

        # This block of script was based off of the script from the following resource:
        # http://stackoverflow.com/questions/20635245/using-gzip-module-with-python
        in_file = gzip.open(file, 'r')
        with open(file[0:46], 'wb') as out_file:
            out_file.write(in_file.read())
        in_file.close()

        # Delete .gz file
        Path(file).unlink()

        logger.info('extract_snodas_gz_file: {} has been extracted'.format(file))

    else:
        logger.info('extract_snodas_gz_file: {} is not of .gz format and was not extracted.'.format(file))

    logger.info('extract_snodas_gz_file: Finished {} \n'.format(file))


def convert_snodas_dat_to_bil(file: str) -> None:
    """Convert SNODAS .dat file into supported file format (.tif). The .dat and .Hdr files are not supported file
    formats to use with QGS processing tools. The QGS processing tools are used to calculate the daily zonal stats.
    file: .dat file to be converted to .bil format"""

    logger.info('convert_snodas_dat_to_bil: Starting {}'.format(file))

    # Check for file extension .dat
    if file.upper().endswith('.DAT'):
        # Change file extension from .dat to .bil
        Path(file).rename(Path(file).with_suffix('.bil'))

        logger.info('convert_snodas_dat_to_bil: {} has been converted into .bil format'.format(file))

    else:
        logger.info('convert_snodas_dat_to_bil: {} is not a .dat file and has not been converted into .bil format.\n'
                    .format(file))
        return

    logger.info('convert_snodas_dat_to_bil: Finished {} \n'.format(file))


def create_snodas_hdr_file(file: str) -> None:
    """Create custom .hdr file. A custom .Hdr file needs to be created to indicate the raster settings of the .bil file.
    The custom .Hdr file aids in converting the .bil file to a usable .tif file.
    file: .bil file that needs a custom .Hdr file"""

    logger.info('create_snodas_hdr_file: Starting {}'.format(file))

    # Check for file extension .bil
    if file.upper().endswith('.BIL'):

        # Create name for the new .hdr file
        hdr_name = file.replace('.bil', '.hdr')

        # These lines of code create a custom .hdr file to give details about the .bil/raster file. The
        # specifics inside each .hdr file are the same for each daily raster. However, there must be a .hdr file
        # that matches the name of each .bil/.tif file in order for QGS to import each dataset. The text included in
        # the .Hdr file originated from page 12 of the 'National Operational Hydrologic Remote Sensing Center SNOw Data
        # Assimilation System (SNODAS) Products of NSIDC', This document can be found at the following url:
        # https://nsidc.org/pubs/documents/special/nsidc_special_report_11.pdf
        with open(hdr_name, 'w') as file2:
            file2.write('units dd\n')
            file2.write('nbands 1\n')
            file2.write('nrows 3351\n')
            file2.write('ncols 6935\n')
            file2.write('nbits 16\n')
            file2.write('pixeltype signedint')
            file2.write('byteorder M\n')
            file2.write('layout bil\n')
            file2.write('ulxmap -124.729583333333\n')
            file2.write('ulymap 52.8704166666666\n')
            file2.write('xdim 0.00833333333333333\n')
            file2.write('ydim 0.00833333333333333\n')

        logger.info('create_snodas_hdr_file: {} now has a created .Hdr file.'.format(file))

    else:
        logger.info('create_snodas_hdr_file: {} is not a .bil file and an .Hdr component file has not been created.\n'
                    .format(file))
        return

    logger.info('create_snodas_hdr_file: Finished {} \n'.format(file))


def convert_snodas_bil_to_tif(file: str, folder_output: Path) -> None:
    """Convert .bil file into .tif file for processing within the QGIS environment.
    file: file to be converted into a .tif file
    folder_output: full pathname to location where the created .tif files are contained"""

    logger.info('convert_snodas_bil_to_tif: Starting {}'.format(file))

    # Check for file extension .bil
    if file.upper().endswith('.BIL'):

        # If in a Linux system
        if LINUX_OS:

            # Remove the original .Hdr file so that the created .hdr file will be read instead.
            orig_hdr_file = folder_output / file.replace('.bil', '.Hdr')
            if orig_hdr_file.exists():
                orig_hdr_file.unlink()

        # Create name with replaced .tif file extension
        tif_file = file.replace('.bil', '.tif')

        abs_output_tif = folder_output / tif_file

        # Convert file to .tif format by modifying the original file. No new file is created.
        gdal.Translate(str(abs_output_tif), file, format='GTiff')

        logger.info('convert_snodas_bil_to_tif: {} has been converted into a .tif file.'.format(file))

    else:
        logger.info('convert_snodas_bil_to_tif: {} is not a .bil file and has not been converted into a .tif file.\n'
                    .format(file))
        return

    logger.info('convert_snodas_bil_to_tif: Finished {} \n'.format(file))


def delete_snodas_bil_file(file: str) -> None:
    """Delete file with .bil or .hdr extensions. The .bil and .hdr formats are no longer important to keep because the
    newly created .tif file holds the same data.
    file: file to be checked for either .hdr or .bil extension (and, ultimately deleted)"""

    logger.info('delete_snodas_bil_file: Starting {}'.format(file))

    # Check for extension .bil or .Hdr
    if file.upper().endswith('.BIL') or file.upper().endswith('.HDR'):

        # Delete file
        Path(file).unlink()

        logger.info('delete_snodas_bil_file: {} has been deleted.'.format(file))

    else:
        logger.info('delete_snodas_bil_file: {} is not a .bil file or a .hdr file. It won\'t be deleted.\n'
                    .format(file))
        return

    logger.info('delete_snodas_bil_file: Finished {} \n'.format(file))


def create_extent(basin_shp: str, folder_output: Path) -> None:
    """Create a single-feature bounding box shapefile representing the extent of the input shapefile the watershed
    boundary input shapefile). The created extent shapefile will be used to clip the SNODAS daily national grid to the
    size of the study area. Reference: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
    basin_shp: the input shapefile for which to create the extent shapefile
    folder_output: full pathname to the folder that will hold the extent shapefile"""

    # Get basin boundary extent
    in_driver = ogr.GetDriverByName("ESRI Shapefile")
    in_data_source = in_driver.Open(basin_shp, 0)
    in_layer = in_data_source.GetLayer()
    extent = in_layer.GetExtent()

    # Create a Polygon from the extent tuple
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(extent[0], extent[2])
    ring.AddPoint(extent[1], extent[2])
    ring.AddPoint(extent[1], extent[3])
    ring.AddPoint(extent[0], extent[3])
    ring.AddPoint(extent[0], extent[2])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    # Save extent to a new Shapefile
    basename = 'studyArea_extent'
    output_shape_file = basename + '.shp'
    output_projection = basename + '.prj'
    out_driver = ogr.GetDriverByName("ESRI Shapefile")
    output_shp_full_name = folder_output / output_shape_file
    output_prj_full_name = folder_output / output_projection

    # Create the output shapefile and add an ID Field (there will only be 1 ID because there will only be 1 feature)
    out_data_source = out_driver.CreateDataSource(str(output_shp_full_name))
    out_layer = out_data_source.CreateLayer("studyArea_extent", geom_type=ogr.wkbPolygon)
    id_field = ogr.FieldDefn("id", ogr.OFTInteger)
    out_layer.CreateField(id_field)

    # Create the feature and set values
    feat_def = out_layer.GetLayerDefn()
    feature = ogr.Feature(feat_def)
    feature.SetGeometry(poly)
    feature.SetField("id", 1)
    out_layer.CreateFeature(feature)
    feature = None

    # Save and close DataSource. Important - Do not remove.
    in_data_source = None
    out_data_source = None
    # in_just_code = float('NaN')
    # out_just_code = float('NaN')

    # Set projection to CALCULATE_STATS_PROJECTION (the projection set in the config file to be the same
    # as the basin boundary shapefile)
    with open(output_prj_full_name, 'w') as file:
        if LINUX_OS:
            in_spatial_ref = calculate_statistics_projection_srs
            in_spatial_ref.MorphToESRI()
            file.write(in_spatial_ref.ExportToWkt())

        else:
            in_just_code = int(CALCULATE_STATS_PROJECTION.replace('EPSG:', ''))
            out_just_code = int(CLIP_PROJECTION.replace('EPSG:', ''))
            in_spatial_ref = osr.SpatialReference()
            in_spatial_ref.ImportFromEPSG(in_just_code)

            in_spatial_ref.MorphToESRI()
            file.write(in_spatial_ref.ExportToWkt())

    # Re-project to the CLIP_PROJECTION
    # REF: http://geoinformaticstutorial.blogspot.com/2012/10/reprojecting-shapefile-with-gdalogr-and.html
    # Set file names
    infile = str(output_shp_full_name)
    outfile = str(output_shp_full_name).replace('_extent', 'Extent_prj')

    # Get outfile path.
    outfile_path = Path(outfile).parent
    # Get file name without extension.
    outfile_short_name = Path(outfile).stem

    if LINUX_OS:
        # Spatial Reference of the input file. Access the Spatial Reference and assign the input projection
        in_spatial_ref = calculate_statistics_projection_srs

        # Spatial Reference of the output file. Access the Spatial Reference and assign the output projection
        out_spatial_ref = osr.SpatialReference()
        out_spatial_ref.ImportFromEPSG(int(CLIP_PROJECTION.replace('EPSG:', '')))

    else:
        # Spatial Reference of the input file. Access the Spatial Reference and assign the input projection
        in_spatial_ref = osr.SpatialReference()
        in_spatial_ref.ImportFromEPSG(in_just_code)

        # Spatial Reference of the output file. Access the Spatial Reference and assign the output projection
        out_spatial_ref = osr.SpatialReference()
        out_spatial_ref.ImportFromEPSG(out_just_code)

    # create Coordinate Transformation
    coord_transform = osr.CoordinateTransformation(in_spatial_ref, out_spatial_ref)

    # Open the input shapefile and get the layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    in_dataset = driver.Open(infile, 0)
    inlayer = in_dataset.GetLayer()

    # Create the output shapefile but check first if file exists.
    if Path(outfile).exists():
        driver.DeleteDataSource(outfile)

    out_dataset = driver.CreateDataSource(outfile)
    outlayer = out_dataset.CreateLayer(str(outfile_short_name), geom_type=ogr.wkbPolygon)

    # Get the field_def_1 for attribute ID and add to output shapefile
    feature = inlayer.GetFeature(0)
    field_def_1 = feature.GetFieldDefnRef('id')
    outlayer.CreateField(field_def_1)

    # get the feat_def for the output shapefile.
    feat_def = outlayer.GetLayerDefn()

    # Loop through input features and write to output file.
    in_feature = inlayer.GetNextFeature()
    while in_feature:

        # Get the input geometry.
        geometry = in_feature.GetGeometryRef()

        # Re-project the geometry, each one has to be projected separately.
        geometry.Transform(coord_transform)

        # create a new output feature.
        out_feature = ogr.Feature(feat_def)

        # set the geometry and attribute.
        out_feature.SetGeometry(geometry)
        out_feature.SetField('id', in_feature.GetField('id'))

        # add the feature to the output shapefile
        outlayer.CreateFeature(out_feature)

        # destroy the features and get the next input features
        out_feature.Destroy()
        in_feature.Destroy()
        in_feature = inlayer.GetNextFeature()

    # close the shapefiles
    in_dataset.Destroy()
    out_dataset.Destroy()

    # create the prj projection file
    out_spatial_ref.MorphToESRI()
    with open(outfile_path.joinpath(outfile_short_name + '.prj'), 'w') as proj_file:
        proj_file.write(out_spatial_ref.ExportToWkt())

    # Delete the unnecessary extent shapefile files projected in the CALCULATE_STATS_PROJECTION
    extensions = ['.dbf', '.prj', '.shp', '.shx']
    for extension in extensions:
        delete_file = str(output_shp_full_name).replace('.shp', extension)
        Path(delete_file).unlink()


def copy_and_move_snodas_tif_file(file: str, folder_output: Path) -> None:
    """Copy and move created .tif file from original location to folder_output. The copied and moved file will be
    edited. To keep the file as it is, the original is saved within the original folder.
    file: .tif file to be copied and moved to folder_output
    folder_output: full pathname to the folder holding the newly copied .tif file"""

    logger.info('copy_and_move_snodas_tif_file: Starting {}'.format(file))

    # Set full pathname of file
    file_full_output = Path(file) / folder_output

    # Check for file extension .tif
    if file.upper().endswith(".TIF"):

        # Copy and move file to file_full_output
        copy(file, file_full_output)

        logger.info('copy_and_move_snodas_tif_file: {} has been copied and moved to {}'.format(file, folder_output))

    else:
        logger.info('copy_and_move_snodas_tif_file: {} is not a .tif file and has not been copied and moved to {}'
                    .format(file, folder_output))

    logger.info('copy_and_move_snodas_tif_file: Finished {} \n'.format(file))


def assign_snodas_datum(file: str, folder: Path) -> None:
    """Define WGS84 as datum. Defaulted in configuration file to assign SNODAS grid with WGS84 datum. The
    downloaded SNODAS raster is un-projected however the "SNODAS fields are grids of point estimates of snow cover in
    latitude/longitude coordinates with the horizontal datum WGS84." - SNODAS Data Products at NSIDC User Guide
    http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/index.html
    file: the name of the .tif file that is to be assigned a projection
    folder: full pathname to the folder where both the un-projected and projected raster are stored"""

    logger.info('assign_snodas_datum: Starting {}'.format(file))

    # Check for un-projected .tif files
    if file.upper().endswith('HP001.TIF'):

        # Change name from 'us_ssmv11034tS__T0001TTNATS2003093005HP001.tif' to '20030930WGS84.tif'
        new_file = file.replace('05HP001', 'WGS84').replace('us_ssmv11034tS__T0001TTNATS', '')

        # Set up for gdal.Translate tool. Set full path names for both input and output files.
        input_raster = folder / file
        output_raster = folder / new_file

        # Assign datum (Defaulted to 'EPSG:4326').
        gdal.Translate(str(output_raster), str(input_raster), outputSRS=CLIP_PROJECTION)

        # Delete un-projected file.
        input_raster.unlink()

        logger.info('assign_snodas_datum: {} has been assigned projection of {}.'.format(file, CLIP_PROJECTION))

        # Writes the projection information to the log file.
        ds = gdal.Open(str(output_raster))
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        datum = srs.GetAttrValue('GEOGCS')

        if srs.IsProjected:
            proj_name = srs.GetAttrValue('AUTHORITY')
            proj_num = srs.GetAttrValue('AUTHORITY', 1)
            logger.info("assign_snodas_datum: {} has projection {}:{} and datum {}"
                        .format(output_raster.name, proj_name, proj_num, datum))
        else:
            logger.info("assign_snodas_datum: {} has projection {} and datum {}".format(output_raster.name, prj, datum))
    else:
        logger.warning("assign_snodas_datum: {} does not end in 'HP001.tif' and has not been assigned projection "
                       "of {}.\n".format(file, CLIP_PROJECTION))
        return

    logger.info('assign_snodas_datum: Successfully converted {} to {}.\n'.format(file, output_raster.name))


def snodas_raster_clip(file: str, folder: Path, vector_extent: Path) -> None:
    """Clip file by vector_extent shapefile. The output filename starts with 'Clip'.
    file: the projected (defaulted to WGS84) .tif file to be clipped
    folder: full pathname to folder where both the un-clipped and clipped rasters are stored
    vector_extent: full pathname to shapefile holding the extent of the basin boundaries. This shapefile must be
    projected in projection assigned in function assign_snodas_datum (defaulted to WGS84)."""

    logger.info('snodas_raster_clip: Starting {}'.format(file))

    # Check for file extension .tif
    if file.upper().endswith('WGS84.TIF'):

        # Change name from 20030930WGS84.tif.tif to 'ClipYYYYMMDD.tif'
        date_name = file.replace('WGS84', '')
        new_name = 'Clip' + date_name

        # Set full pathname of both input and output files to be used in the gdal.Warp tool
        file_full_input = folder / file
        file_full_output = folder / new_name

        # Clip .tif file by the input extent shapefile. For more info on gdal.WarpOptions parameters, reference
        # osgeo.gdal.Warp & osgeo.gdal.WarpOptions in the Table of Contents of URL: http://gdal.org/python/.
        #
        # Parameters Explained:
        # (1) destNameOrDestDS --- Output dataset name or object
        # (2) srcDSOrSrcDSTab  --- an array of Dataset objects or filenames, or a Dataset object or a filename
        # (3) format           --- output format ("GTiff", etc...)
        # (4) dstNodata        --- output nodata value(s)
        # (5) cutlineDSName    --- cutline dataset name
        # (6) cropToCutline    --- whether to use cutline extent for output bounds
        # raster_layer = QgsRasterLayer(str(file_full_input), '{}'.format(file))
        gdal.Warp(str(file_full_output), str(file_full_input), format='GTiff',
                  dstNodata=NULL_VAL, cutlineDSName=str(vector_extent), cropToCutline=True)

        # Delete un-clipped raster files
        file_full_input.unlink()
        # Writes the projection to the log file.
        ds = gdal.Open(str(file_full_output))
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        datum = srs.GetAttrValue('GEOGCS')

        if srs.IsProjected:
            proj_name = srs.GetAttrValue('AUTHORITY')
            proj_num = srs.GetAttrValue('AUTHORITY', 1)
            logger.info("snodas_raster_clip: {} has projection {}:{} and datum {}"
                        .format(file_full_output.name, proj_name, proj_num, datum))
        else:
            logger.info("snodas_raster_clip: {} has projection {} and datum {}"
                        .format(file_full_output.name, prj, datum))
    else:
        logger.info('snodas_raster_clip: {} does not end with PRJCT.tif. The clip was not processed.\n'.format(file))
        return
    logger.info('snodas_raster_clip: Successfully clipped {} to {}.\n'.format(file, file_full_output.name))


def assign_snodas_projection(file: str, folder: Path) -> None:
    """Project clipped raster from it's original datum (defaulted to WGS84) to desired projection (defaulted
    to Albers Equal Area).
    file: clipped file with original projection to be projected into desired projection
    folder: full pathname of folder where both the originally clipped rasters and the projected clipped rasters are
    contained"""
    logger.info('assign_snodas_projection: Starting {}'.format(file))
    # Check for projected SNODAS rasters.
    if file.startswith('Clip') and file.endswith('.tif'):

        # Change name from 'ClipYYYYMMDD.tif' to 'SNODAS_SWE_ClipAndProjYYYYMMDD.tif'
        new_name = file.replace('Clip', 'SNODAS_SWE_ClipAndProj')

        # Set full pathname of both input and output file to be used in the gdal.
        file_full_input = folder / file
        file_full_output = folder / new_name

        # Re-project the clipped SNODAS .tif files from original projection to desired projection
        if LINUX_OS:
            # This is potentially another way to perform the algorithm using the processing module. The original method
            # is still working, so that will be used.
            # alg_parameters = {
            #     'INPUT': str(file_full_input),
            #     'OUTPUT': str(file_full_output),
            #     'SOURCE_CRS': CLIP_PROJECTION,
            #     'TARGET_CRS': CALCULATE_STATS_PROJ_WKT,
            #     'RESAMPLING': 1,
            #     'TARGET_EXTENT': '-110.06,-101.11,38.28,41.26',
            #     'NODATA': NULL_VAL
            # }

            # Processing.initialize()
            #
            # feedback = QgsProcessingFeedback()
            # processing.run('gdal:warpreproject', alg_parameters, context=None, feedback=feedback)
            # processing.algorithmHelp('gdal:warpreproject')
            gdal.Warp(str(file_full_output),
                      str(file_full_input),
                      format='GTiff',
                      xRes=CELL_SIZE_X,
                      yRes=CELL_SIZE_Y,
                      srcSRS=CLIP_PROJECTION,
                      dstSRS=CALCULATE_STATS_PROJ_WKT,
                      resampleAlg='bilinear',
                      dstNodata=NULL_VAL)

            logger.info('assign_snodas_projection: '
                        '{} has been projected from {} to USA_Albers_Equal_Area_Conic'.format(file, CLIP_PROJECTION))

        else:
            gdal.Warp(str(file_full_output), str(file_full_input), format='GTiff',
                      xRes=CELL_SIZE_X, yRes=CELL_SIZE_Y, srcSRS=CLIP_PROJECTION,
                      dstSRS=CALCULATE_STATS_PROJECTION, resampleAlg='bilinear', dstNodata=NULL_VAL)

            logger.info('assign_snodas_projection: {} has been projected from {} to {}'
                        .format(file, CLIP_PROJECTION, CALCULATE_STATS_PROJECTION))

        # Delete the original projected clipped file
        file_full_input.unlink()

        # Writes the projection information to the log file.
        ds = gdal.Open(str(file_full_output))
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        datum = srs.GetAttrValue('GEOGCS')

        if srs.IsProjected:
            proj_name = srs.GetAttrValue('AUTHORITY')
            proj_num = srs.GetAttrValue('AUTHORITY', 1)
            logger.info("assign_snodas_projection: {} has projection {}:{} and datum {}"
                        .format(file_full_output.name, proj_name, proj_num, datum))
        else:
            logger.info("assign_snodas_projection: {} has projection {} and datum {}"
                        .format(file_full_output.name, prj, datum))
    else:
        logger.info("assign_snodas_projection: {} does not start with 'Clip' and will not be projected.\n".format(file))
        return

    logger.info('assign_snodas_projection: Successfully clipped {} into {}\n'.format(file, str(file_full_output)))


def snow_coverage(file: str, folder_input: Path, folder_output: Path) -> None:
    """Create binary .tif raster indicating snow coverage. If a pixel in the input file is > 0 (there is snow on the
    ground) then the new raster's pixel value is assigned '1'. If a pixel in the input raster is 0 or a null value
    (there is no snow on the ground) then the new raster's pixel value is assigned '0'. The output raster is used to
    calculate the percent of daily snow coverage for each basin.
    file: daily SNODAS SWE .tif raster
    folder_input: full pathname to the folder where the file is stored
    folder_output: full pathname to the folder where the newly created binary snow cover raster is stored"""

    logger.info('snow_coverage: Starting {}'.format(file))

    # Check for projected SNODAS rasters
    if file.startswith('SNODAS_SWE_ClipAndProj'):

        # Set name of snow cover .tif file
        snow_file = 'SNODAS_SnowCover_ClipAndProj' + file[22:30] + '.tif'

        # Set full pathname variables for input into later raster calculator options
        file_full_input = folder_input / file
        file_full_output_snow = folder_output / snow_file

        # Check for previous processing of file.
        if Path(file_full_input).exists():

            logger.warning('snow_coverage: {} has been previously created. Overwriting.'.format(snow_file))

        logger.info('snow_coverage: Enveloping {} as a QGS raster object layer'.format(file))

        # Envelop current file as QGS object raster layer
        raster_layer = QgsRasterLayer(str(file_full_input), '{}'.format(file))

        # Check for valid file within QGS environment.
        if raster_layer.isValid():

            # Set name (without extension) for input into the raster calculator expression. '@1' means the calculation
            # occurs on band 1 of the raster.
            raster_input = file[0:32]
            raster_calc_name = raster_input + '@1'

            # Set variables for raster calculator options/settings.
            # Refer to: http://gis.stackexchange.com/questions/141659/qgis-from-console-raster-algebra
            resulting_layer = QgsRasterCalculatorEntry()
            resulting_layer.ref = raster_calc_name
            resulting_layer.raster = raster_layer
            resulting_layer.bandNumber = 1
            entries = [resulting_layer]

            # Set raster calculator options/settings. (expression, output path, output type, output extent,
            # output width, output height, entries, context)
            context = QgsCoordinateTransformContext()
            calc = QgsRasterCalculator('({})>0'.format(raster_calc_name), '{}'.format(file_full_output_snow), 'GTiff',
                                       raster_layer.extent(), raster_layer.width(), raster_layer.height(), entries,
                                       context)

            # Begin calculation.
            calc.processCalculation()

            logger.info('snow_coverage: Snow calculations for {} complete.'.format(file))

        else:
            logger.warning('snow_coverage: {} is not a valid object raster layer.'.format(file))

        logger.info('snow_coverage: Finished {}.\n'.format(file))
    else:
        logger.warning("snow_coverage: {} does not start with 'Repj'. No raster calculation took place.\n".format(file))


def create_csv_files(file: str, v_file: str, csv_by_date: Path, csv_by_basin: Path) -> None:
    """Create empty csv files for output - both by date and by basin. The empty csv files have a header row with
     each column represented by a different field name (refer to 'fieldnames' section of the function for actual
     fieldnames). Csv files by date contain one .csv file for each date and is titled
     'SnowpackStatisticsByDate_YYYYMMDD.csv'. Each byDate file contains the zonal stats for each basin on that date.
     Csv files by basin contain one .csv file for each watershed basin & is titled 'SnowpackStatisticsByBasin_BasinId'.
     Each byBasin file contains the zonal stats for that basin for each date that has been processed.
     file: daily .tif file  to be processed with zonal statistics (clipped, projected)
     v_file: shapefile of basin boundaries (these boundaries are used as the polygons in the zonal stats calculations)
     csv_by_date: full pathname of folder containing the results by date (.csv file)
     csv_by_basin: full pathname of folder containing the results by basin (.csv file)"""

    logger.info('create_csv_files: Starting {}'.format(file))

    # Envelop input shapefile as QGS object vector layer
    vector_file = QgsVectorLayer(v_file, 'Reprojected Basins', 'ogr')

    # Check to determine if the shapefile is valid as an object. If this test shows that the shapefile is not a valid
    # vector file, the script does not run the zonal statistic processing (located in the 'else' block of code). If the
    # user gets the following error message, it is important to address the initialization of the QGIS resources.
    if not vector_file.isValid():
        logger.warning('create_csv_files: Vector basin boundary shapefile is not a valid QGS object layer.')
    else:

        # Hold current directory in variable.
        curr_dir = Path.cwd()

        # Retrieve date of current file. Filename: 'SNODAS_SWE_ClipAndProjYYYYMMDD'. File[22:30] pulls the
        # 'YYYYMMDD' section.
        date_name = file[22:30]

        # Define fieldnames for output .csv files. These MUST match the keys of the dictionaries. Fieldnames make up
        # the header row of the .csv output files. The column headers of the .csv files are in
        # sequential order as laid out in the fieldnames list.
        fieldnames = ['Date_YYYYMMDD', ID_FIELD_NAME, 'LOCAL_NAME', 'SNODAS_SWE_Mean_in', 'SNODAS_SWE_Mean_mm',
                      'SNODAS_EffectiveArea_sqmi', 'SNODAS_SWE_Volume_acft', 'SNODAS_SWE_Volume_1WeekChange_acft',
                      'SNODAS_SnowCover_percent', 'Updated_Timestamp']

        if CALCULATE_SWE_MAX.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_Max_in', 'SNODAS_SWE_Max_mm'])

        if CALCULATE_SWE_MIN.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_Min_in', 'SNODAS_SWE_Min_mm'])

        if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_StdDev_in', 'SNODAS_SWE_StdDev_mm'])

        # Create string variable for name of .csv output file by date. Name: SnowpackStatisticsByDate_YYYYMMDD.csv.
        results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'

        # Check to see if the output file has already been created.
        if csv_by_date.joinpath(results_date).exists():
            if not file.endswith('.aux.xml'):
                logger.warning('create_csv_files: {} has been previously created. Overwriting.'.format(file))

        # Set directory where the output .csv daily files are stored. - By Date
        os.chdir(csv_by_date)

        logger.info('create_csv_files: Creating {}'.format(results_date))

        # Create .csv file with the appropriate fieldnames as the info in the header row. - By Date
        with open(results_date, 'w') as csv_file:
            if LINUX_OS:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",")
            else:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",", lineterminator='\n')
            writer.writeheader()

        # Iterate through each basin of the basin boundary shapefile.
        for feature in vector_file.getFeatures():

            # Create str variable for the name of output .csv file byBasin. Name: SnowpackStatisticsByBasin_LOCALID.csv.
            results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv'

            # Check to see if the output file has already been created. If so, the script moves onto the raster
            # processing. If not, a .csv file is created with the appropriate fieldnames as the info in the
            # header row. - By Basin
            if not csv_by_basin.joinpath(results_basin).exists():

                # Set directory where the output .csv daily files are stored - By Basin
                os.chdir(csv_by_basin)

                logger.info('create_csv_files: Creating {}'.format(results_basin))

                # Create .csv file with appropriate fieldnames as the header row. - By Date
                with open(results_basin, 'w') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",")
                    writer.writeheader()

                # Return directory back to original
                os.chdir(curr_dir)

    logger.info('create_csv_files: Finished {}.\n'.format(file))


def delete_by_basin_csv_repeated_rows(file: str, v_file: str, csv_by_basin: Path) -> None:
    """ Check to see if date has already been processed. If so, iterate through by basin csv file and only write rows
    to new csv file that do not start with the date. Ultimately, delete row of data for today's date so that new data
    can be overwritten without producing multiple rows of the same date.
    file: daily .tif file  to be processed with zonal statistics (clipped, projected)
    v_file: shapefile of basin boundaries (these boundaries are used as the polygons in the zonal stats calculations)
    csv_by_basin: full pathname of folder containing the results by basin (.csv file) """

    logger.info('delete_by_basin_csv_repeated_rows: Starting {}'.format(file))

    # Envelop input shapefile as QGS object vector layer
    vector_file = QgsVectorLayer(v_file, 'Reprojected Basins', 'ogr')

    # Check to determine if the shapefile is valid as an object. If this test shows that the shapefile is not a valid
    # vector file, the script does not run the zonal statistic processing (located in the 'else' block of code). If the
    # user gets the  following error message, it is important to address the initialization of the QGIS resources.
    if not vector_file.isValid():
        logger.warning('delete_by_basin_csv_repeated_rows: Vector basin boundary shapefile is not a valid QGS'
                       ' object layer.')
    else:
        # Hold current directory in a variable, curr_dir, to be used at the end of the script.
        curr_dir = Path.cwd()
        results_basin = None

        # Retrieve date of current file. File name is 'SNODAS_SWE_ClipAndProjYYYYMMDD'. File[22:30] is pulling the
        # 'YYYYMMDD' section.
        date_name = file[22:30]

        # Iterate through each basin of the basin boundary shapefile.
        for feature in vector_file.getFeatures():
            # Create string variable to be used as the title for the .csv output file - By Basin
            results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv'

        # Set directory where the output .csv daily files are stored. - By Basin
        os.chdir(csv_by_basin)

        # Check to see if the daily raster has already been processed.
        with open(results_basin) as f:
            if date_name in f.read() and file.endswith('.tif'):
                logger.warning(
                    'delete_by_basin_csv_repeated_rows: Raster {} has already been processed.'.format(file))

                # Iterate through each basin of the basin boundary shapefile.
                for feature in vector_file.getFeatures():

                    # Create string variable to be used as the title for the input and output .csv file - By Basin
                    results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv'
                    results_basin_edit = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + 'edit.csv'

                    logger.warning(
                        'delete_by_basin_csv_repeated_rows: Rewriting {}.'.format(results_basin))

                    # Open input_file and output_file files. Input will be read and output_file will be written.
                    input_file = open(results_basin, 'r')
                    output_file = open(results_basin_edit, 'w')

                    # If the first row in the input_file file is file's date, it is not written to the new file.
                    # Essentially, it is deleted.
                    writer = csv.writer(output_file)
                    for row in csv.reader(input_file):
                        if row[0] != date_name:
                            writer.writerow(row)
                    input_file.close()
                    output_file.close()

                    # Delete original, now inaccurate, csvByBasin file.
                    Path(results_basin).unlink()

                    # Rename the new edited csvByBasin file to its original name of SnowpackStatisticsByBasin_ +
                    # feature[ID_FIELD_NAME] + '.csv'
                    Path(results_basin_edit).rename(results_basin)

                # Return directory back to original
                os.chdir(curr_dir)

    logger.info('delete_by_basin_csv_repeated_rows: Finished {} \n'.format(file))


def zip_shapefile(file: str, csv_by_date: Path, delete_original: str) -> None:
    # Code block from http://emilsarcpython.blogspot.com/2015/10/zipping-shapefiles-with-python.html
    # List of file extensions included in the shapefile
    # file: the output shapefile (any extension). All other extensions will be included by means of the function.
    # csv_by_date: full pathname of folder containing the results by date (.csv files, GeoJSON, and shapefiles)
    # delete_original: Boolean string to determine if the original unzipped shapefile files should be deleted.
    extensions = ['.shx', '.shp', '.qpj', '.prj', '.dbf', '.cpg']

    # Define naming conventions
    in_name = Path(file).stem
    file_to_zip = csv_by_date / (in_name + '.zip')
    # The third argument for zipfile - ZIP_DEFLATED - is what actually compresses the file. Otherwise, the file
    # is essentially copied.
    zip_file = zipfile.ZipFile(str(file_to_zip), 'w', zipfile.ZIP_DEFLATED)

    # Empty list to store files to delete
    files_to_delete = []

    for fl in os.listdir(csv_by_date):
        for extension in extensions:
            if fl == (in_name + extension):
                # Get full pathname of file
                in_file = csv_by_date / fl
                files_to_delete += [str(in_file)]
                zip_file.write(str(in_file), fl)
                break
    zip_file.close()

    # Delete unzipped shapefile files, if configured.
    if delete_original.upper() == 'TRUE':
        for fl in files_to_delete:
            Path(fl).unlink()


def z_stat_and_export(file: str, v_file: str, csv_by_basin: Path, csv_by_date: Path, dir_clip: Path,
                      dir_snow: Path, today_date: datetime, timestamp: str, output_crs_epsg: str) -> None:
    """Calculate zonal statistics of basin boundary shapefile and the current SNODAS file. The zonal stats export to
    both the byDate and the byBasin csv files. A daily shapefile and geoJSON is also exported.
    file: daily raster .tif SNODAS file that is to be processed in the zonal statistics tool (clipped, projected)
    vfile: the basin boundary shapefile (used as the zone dataset for the zonal statistics calculations)
    csv_by_date: full pathname to the folder containing results by date (.csv file). Shapefile and GeoJSON saved here.
    csv_by_basin: full pathname to the folder containing results by basin (.csv file)
    dir_clip: full pathname to the folder containing all daily clipped, projected .tif SNODAS rasters
    dir_snow: full pathname to the folder containing all binary snow coverage rasters
    today_date: date of processed SNODAS data in datetime format
    timestamp: the download timestamp in datetime format (returned in download_snodas function)
    output_crs_epsg: the desired projection of the output shapefile and geoJSON (configured in configuration file)"""

    # Create empty dictionary to hold the zonal statistic outputs before they are written to the .csv files.
    # Shapefiles have a limited number of fields available in the attribute table so the statistics must be calculated,
    # exported and then deleted from the shapefile.
    d = {}

    # Hold current directory in a variable, curr_dir, to be called at the end of the script.
    curr_dir = Path.cwd()

    # Retrieve date of current file. File : SNODAS_SWE_ClipAndProjYYYYMMDD. File[22:30] : YYYYMMDD.
    date_name = file[22:30]

    # Define fieldnames for output .csv files (the header row). These MUST match the keys of the dictionaries. The
    # column headers of the .csv files are in sequential order as displayed in the fieldnames list.
    fieldnames = ['Date_YYYYMMDD', ID_FIELD_NAME, 'LOCAL_NAME', 'SNODAS_SWE_Mean_in', 'SNODAS_SWE_Mean_mm',
                  'SNODAS_EffectiveArea_sqmi', 'SNODAS_SWE_Volume_acft', 'SNODAS_SWE_Volume_1WeekChange_acft',
                  'SNODAS_SnowCover_percent', 'Updated_Timestamp']

    if CALCULATE_SWE_MAX.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_Max_in', 'SNODAS_SWE_Max_mm'])

    if CALCULATE_SWE_MIN.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_Min_in', 'SNODAS_SWE_Min_mm'])

    if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_StdDev_in', 'SNODAS_SWE_StdDev_mm'])

    # Envelop input shapefile (for example, the Colorado River Basin projected shapefile) as a QGS object vector layer.
    vector_layer = QgsVectorLayer(v_file, 'Reprojected Basins', 'ogr')

    # Check validity of shapefile as a QGS object. If this test shows that the vector is not a valid  vector file,
    # the script does not run the zonal statistic processing (located in the 'else' block of code). Address the
    # initialization of the QGIS resources if received following error message.
    if not vector_layer.isValid():
        logger.warning('z_stat_and_export: Vector shapefile is not a valid QGS object layer.')

    else:
        # Check for extension .tif
        if file.upper().endswith('.TIF'):
            # Set conditional variables so they are defined
            e_min = None
            e_swe_min_in = None
            e_max = None
            e_swe_max_in = None
            e_std = None
            e_swe_s_dev_in = None

            # Set directory to the directory where the output .csv daily files are contained - By Basin
            os.chdir(csv_by_basin)

            # Create date value of the working dictionary.
            d['Date_YYYYMMDD'] = date_name

            logger.info('z_stat_and_export: Processing zonal statistics by basin of {} ...'.format(file))

            # Retrieve the datetime date for 7 days before today and convert to string format (YYYYMMDD).
            week_ago_date = today_date - timedelta(days=7)
            week_ago_str = format_date_yyyymmdd(week_ago_date)

            # Create string variable with week_ago_str to be used as the title for the .csv output file - By Date
            results_date_csv = 'SnowpackStatisticsByDate_' + week_ago_str + '.csv'
            results_date_csv_full_path = csv_by_date / results_date_csv

            # Set full pathname of rasters for later input into the zonal stat tool
            snow_file = 'SNODAS_SnowCover_ClipAndProj' + date_name + '.tif'
            raster_path_h = dir_clip / file
            raster_path_s = dir_snow / snow_file

            # Open vector_layer for editing
            vector_layer.startEditing()

            # Create the raster layer, needed by QgsZonalStatistics
            raster_layer = QgsRasterLayer(str(raster_path_h))
            snow_raster_layer = QgsRasterLayer(str(raster_path_s))

            # Set input object options for the zonal stat tool - Mean.
            # input shapefile: must be a valid QGS vector layer.
            # input raster: Must be a valid QGS raster layer.
            # field prefix (string): Prefix of the attribute field header containing the zonal statistics.
            # band (integer): Band of raster in which the calculations are processed.
            # statistics type: Zonal statistic to be calculated.

            zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "SWE_", 1, QgsZonalStatistics.Mean)
            zonal_stats.calculateStatistics(None)

            # output_dict - key: csv field name value: [shapefile attribute field name, attribute field type
            # ('None' for outputs of zonal statistics because a new field does not need to be created)]
            output_dict = {
                ID_FIELD_NAME: [ID_FIELD_NAME, 'None'],
                'LOCAL_NAME': ['LOCAL_NAME', 'None'],
                'SNODAS_SWE_Mean_in': ['SWEMean_in', QVariant.Double],
                'SNODAS_SWE_Mean_mm': ['SWE_mean', 'None'],
                'SNODAS_EffectiveArea_sqmi': ['Area_sqmi', QVariant.Double],
                'SNODAS_SWE_Volume_acft': ['SWEVol_af', QVariant.Int],
                'SNODAS_SWE_Volume_1WeekChange_acft': ['SWEVolC_af', QVariant.Int],
                'SNODAS_SnowCover_percent': ['SCover_pct', QVariant.Double]
            }

            if CALCULATE_SWE_MIN.upper() == 'TRUE':
                output_dict.update({'SNODAS_SWE_Min_mm': ['SWE_min', 'None'],
                                   'SNODAS_SWE_Min_in': ['SWEMin_in', QVariant.Double]})

            if CALCULATE_SWE_MAX.upper() == 'TRUE':
                output_dict.update({'SNODAS_SWE_Max_mm': ['SWE_max', 'None'],
                                   'SNODAS_SWE_Max_in': ['SWEMax_in', QVariant.Double]})

            if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
                output_dict.update({'SNODAS_SWE_StdDev_mm': ['SWE_stdev', 'None'],
                                   'SNODAS_SWE_StdDev_in': ['SWESDev_in', QVariant.Double]})

            # Create new fields in shapefile attribute table. Ignore fields that are already populated by zstats plugin.
            for key, value in output_dict.items():
                if value[1] != 'None':
                    new_field = QgsField(value[0], value[1])
                    vector_layer.dataProvider().addAttributes([new_field])

            # Set raster calculator expression to populate the 'Mean' field. This field calculates mm. Change the
            # QGSExpression if different units are desired.
            e_mean = QgsExpression('SWE_mean')

            # Set the raster calculator expression to populate the 'SWEMean_in' field.
            # 25.4 is the number of millimeters in an inch.
            e_swe_mean_in = QgsExpression('SWE_mean / 25.4')

            if CALCULATE_SWE_MIN.upper() == 'TRUE':
                # Set input object options for the zonal stat tool - Minimum
                zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "SWE_", 1, QgsZonalStatistics.Min)
                # Call zonal stat tool to start processing
                zonal_stats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Min' field.
                e_min = QgsExpression('SWE_min')

                # Set the raster calculator expression to populate the 'SWEMin_in' field.
                e_swe_min_in = QgsExpression('SWE_min  / 25.4')

            if CALCULATE_SWE_MAX.upper() == 'TRUE':
                # Set input object options for zonal stat tool - Maximum
                zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "SWE_", 1, QgsZonalStatistics.Max)
                # Call zonal stat tool to start processing
                zonal_stats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Max' field.
                e_max = QgsExpression('SWE_max')

                # Set the raster calculator expression to populate the 'SWEMax_in' field.
                e_swe_max_in = QgsExpression('SWE_max / 25.4')

            if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
                # Set input object options for the zonal stat tool - Standard Deviation
                zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "SWE_", 1, QgsZonalStatistics.StDev)
                # Call zonal stat tool to start processing
                zonal_stats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Std Dev' field.
                e_std = QgsExpression('SWE_stdev')

                # Set the raster calculator expression to populate the 'SWESDev_in' field.
                e_swe_s_dev_in = QgsExpression('SWE_stdev / 25.4')

            # Set input object options for the zonal stat tool - Count of Total Basin Cells
            zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "Cell", 1, QgsZonalStatistics.Count)
            # Call zonal stat tool to start processing
            zonal_stats.calculateStatistics(None)

            # Set input object options for the zonal stat tool - Sum of snow cover raster
            zonal_stats = QgsZonalStatistics(vector_layer, snow_raster_layer, "SCover", 1, QgsZonalStatistics.Sum)
            # Call zonal stat tool to start processing
            zonal_stats.calculateStatistics(None)

            # Update changes to fields of shapefile.
            vector_layer.updateFields()

            # Set raster calculator expression to populate the 'Area_sqmi' field. The area of the cell (square meters)
            # multiplied by the count of basin cells . There are 2589988.10 sq meters in 1 sq mile.
            a = QgsExpression('({}) * ({}) * Cellcount / 2589988.10'.format(CELL_SIZE_X, CELL_SIZE_Y))

            # Set raster calculator expression  to populate the 'SCover_pct' field. Sum of basin cells covered by snow
            # divided by total count of basin cells.
            e = QgsExpression('SCoversum / Cellcount * 100')

            # Set raster calculator expression to populate 'SWEVol_af' field. Mean SWE (mm) multiplied by effective area
            # 'Area_sqmi' divided by 304.8. There are 640 acres in 1 square mile. There are 304.8 mm in 1 foot.
            v = QgsExpression('Area_sqmi * SWE_mean * 640 / 304.8')

            # Create an empty array to hold the components of the zonal stats calculations dictionary. This
            # array is copied to the .csv output file and then erased only to be filled again
            # with the next daily raster's dictionary calculations. - By Date. There are two arrays in this
            # function, array_date and array_basin. The main difference is that the array_basin only holds one
            # dictionary at a time before it writes to a .csv file (one dictionary per basin and then the
            # information is deleted). The array_date holds multiple dictionaries at one time (one dictionary
            # per basin. The information in the array is only deleted after the date changes).
            array_date = []

            # Set directory to the directory where the output .csv daily files are stored - By Basin
            os.chdir(csv_by_basin)

            # Define output coordinate reference system
            output_crs = "EPSG:" + output_crs_epsg

            # Iterate through each basin of the basin boundary shapefile.
            for feature in vector_layer.getFeatures():

                # Check to see if the SNODAS data has already been processed for the week_ago date.
                os.chdir(csv_by_date)

                # If so, get the volume value from last week for each basin. The for loop iterates over the basins
                # and calculates the one-week-change in volume statistic.
                if results_date_csv_full_path.exists():
                    with open(results_date_csv) as csv_file:
                        reader = csv.DictReader(csv_file)
                        has_rows = False
                        for row in reader:
                            has_rows = True
                            if row['{}'.format(ID_FIELD_NAME)] == feature[ID_FIELD_NAME]:
                                week_ago_value = row['SNODAS_SWE_Volume_acft']
                                break

                        if not has_rows:
                            print('The DictReader is empty.')

                    # Set raster calculator expression to populate 'SWEVolC_af' field.
                    # 'SWEVol_af' from today - 'SWEVol_af' from 7 days ago
                    c = QgsExpression('SWEVol_af - {}'.format(week_ago_value))

                else:
                    c = QgsExpression('noData')

                os.chdir(csv_by_basin)

                # Create string variable to be used as the title for the output .csv file - By Basin
                results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv'

                # Create dictionary that sets rounding properties (to what decimal place) for each field. Key is the
                # field name. Value[0] is the preset raster calculator expression. Value[1] is the number of decimals
                # that the field is rounded to.
                rounding_props = {
                    'SCover_pct': [e, 2],
                    'Area_sqmi': [a, 1],
                    'SWE_mean': [e_mean, 0],
                    'SWEMean_in': [e_swe_mean_in, 1],
                    'SWEVol_af': [v, 0],
                    'SWEVolC_af': [c, 0]
                }

                if CALCULATE_SWE_MIN.upper() == 'TRUE':
                    rounding_props['SWE_min'] = [e_min, 0]
                    rounding_props['SWEMin_in'] = [e_swe_min_in, 1]
                if CALCULATE_SWE_MAX.upper() == 'TRUE':
                    rounding_props['SWE_max'] = [e_max, 0]
                    rounding_props['SWEMax_in'] = [e_swe_max_in, 1]
                if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
                    rounding_props['SWE_stdev'] = [e_std, 0]
                    rounding_props['SWESDev_in'] = [e_swe_s_dev_in, 1]

                # Perform raster calculations for each field.
                for key, value in rounding_props.items():
                    # Both the context and the scope need to be created for each evaluation. If done in the feature for
                    # loop, a segmentation fault occurs. If done outside the feature for-loop, a double free takes place
                    context = QgsExpressionContext()
                    scope = QgsExpressionContextScope()
                    scope.setFeature(feature)
                    context.appendScope(scope)

                    expression = value[0]
                    feature[key] = expression.evaluate(context)

                # Round the raster calculations to appropriate decimal places (defined in rounding dictionary). All
                # rounding is completed AFTER all calculations have been completed.
                for key, value in rounding_props.items():
                    context = QgsExpressionContext()
                    scope = QgsExpressionContextScope()
                    scope.setFeature(feature)
                    context.appendScope(scope)

                    rounding = value[1]
                    s = QgsExpression('round({},{})'.format(key, rounding))
                    feature[key] = s.evaluate(context)

                # Update features of basin shapefile.
                vector_layer.updateFeature(feature)

                # Create empty array (basin) to hold the components of the zonal stats calculations.
                array_basin = []

                # Append stats to dictionary 'd'.
                d['Updated_Timestamp'] = timestamp

                for key, value in output_dict.items():
                    d[key] = feature[value[0]]

                # Append current dictionary to the empty basin array. This array is exported to the
                # output .csv file at the end of this 'for' loop.
                array_basin.append(d.copy())

                # Append current dictionary to the empty basin array. This array is exported to the
                # output .csv file outside of this 'for' loop.
                array_date.append(d.copy())

                # Export the daily date array to a .csv file. Overwrite the .csv file if it already exists.
                # Ref: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
                with open(results_basin, 'a') as csv_file:
                    csv_writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=fieldnames)
                    for row in array_basin:
                        csv_writer.writerow(row)

            # Close edits and save changes to the shapefile.
            vector_layer.commitChanges()

            # Delete attribute fields of the shapefile used in the calculations but not important for export to final
            # product shapefile.
            cell_count_index = vector_layer.dataProvider().fieldNameIndex('CellCount')
            s_cover_sum_index = vector_layer.dataProvider().fieldNameIndex('SCoversum')
            vector_layer.dataProvider().deleteAttributes([cell_count_index, s_cover_sum_index])

            # Update shapefile with its newly-named attribute fields.
            vector_layer.updateFields()

            # Create daily shapefile and daily geoJSON.
            shapefile_name = 'SnowpackStatisticsByDate_' + date_name + '.shp'
            geojson_name = 'SnowpackStatisticsByDate_' + date_name + '.geojson'
            shapefile_name_full = csv_by_date / shapefile_name
            geojson_name_full = csv_by_date / geojson_name

            # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name
            swe_mean_index = vector_layer.dataProvider().fieldNameIndex('SWE_mean')
            vector_layer.dataProvider().renameAttributes({swe_mean_index: 'SWEMean_mm'})

            if CALCULATE_SWE_MIN.upper() == 'TRUE':
                swe_min_index = vector_layer.dataProvider().fieldNameIndex('SWE_min')
                vector_layer.dataProvider().renameAttributes({swe_min_index: 'SWEMin_mm'})

            if CALCULATE_SWE_MAX.upper() == 'TRUE':
                swe_max_index = vector_layer.dataProvider().fieldNameIndex('SWE_max')
                vector_layer.dataProvider().renameAttributes({swe_max_index: 'SWEMax_mm'})

            if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
                s_std_dev_index = vector_layer.dataProvider().fieldNameIndex('SWE_stdev')
                vector_layer.dataProvider().renameAttributes({s_std_dev_index: 'SWESDev_mm'})

            vector_layer.updateFields()
            vector_layer.commitChanges()

            # Export geojson and shapefile. (layer, full output pathname, file encoding, destination reference system,
            # output file type, layer options (GeoJSON): number of decimal places used in GeoJSON geometry)
            # crs_transform = QgsCoordinateTransformContext()
            # options = QgsVectorFileWriter.SaveVectorOptions()
            # QgsVectorFileWriter.writeAsVectorFormatV2(layer=vector_layer, fileName=geojson_name_full,
            #                                           transformContext=crs_transform, options=options)

            QgsVectorFileWriter.writeAsVectorFormat(vector_layer, str(geojson_name_full), "utf-8",
                                                    QgsCoordinateReferenceSystem(output_crs), "GeoJSON",
                                                    layerOptions=['COORDINATE_PRECISION=%s' % GEOJSON_PRECISION])
            QgsVectorFileWriter.writeAsVectorFormat(vector_layer, str(shapefile_name_full), "utf-8",
                                                    QgsCoordinateReferenceSystem(output_crs), "ESRI Shapefile")

            # Change fieldnames of output GeoJSON file
            # Envelop GeoJSON file as a QGS object vector layer.
            new_name = geojson_name.replace(".geojson", "_intermediate.geojson")
            int_geojson_name_full = os.path.join(str(csv_by_date), new_name)
            os.rename(geojson_name_full, int_geojson_name_full)

            vector_file_geojson = QgsVectorLayer(int_geojson_name_full, 'GeoJsonStatistics', 'ogr')

            # Rename attribute fields of GeoJSON.
            if not LINUX_OS:

                # Open vector_file for editing
                vector_file_geojson.startEditing()

                # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name
                fields = {'SWEMean_mm': 'SNODAS_SWE_Mean_mm', 'SWEVolC_af': 'SNODAS_SWE_Volume_1WeekChange_acft',
                          'SWEMean_in': 'SNODAS_SWE_Mean_in', 'Area_sqmi': 'SNODAS_EffectiveArea_sqmi',
                          'SWEVol_af': 'SNODAS_SWE_Volume_acft', 'SCover_pct': 'SNODAS_SnowCover_percent'}

                if CALCULATE_SWE_MIN.upper() == 'TRUE':
                    fields.update({'SWEMin_mm': 'SNODAS_SWE_Min_mm', 'SWEMin_in': 'SNODAS_SWE_Min_in'})

                if CALCULATE_SWE_MAX.upper() == 'TRUE':
                    fields.update({'SWEMax_mm': 'SNODAS_SWE_Max_mm', 'SWEMax_in': 'SNODAS_SWE_Max_in'})

                if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
                    fields.update({'SWESDev_mm': 'SNODAS_SWE_StdDev_mm', 'SWESDev_in': 'SNODAS_SWE_StdDev_in'})

                for key, value in fields.items():
                    index = vector_file_geojson.dataProvider().fieldNameIndex(key)
                    vector_file_geojson.dataProvider().renameAttributes({index: value})

                # Update the changes to the field names and remove the intermediate GeoJSON file
                # (with shapefile fieldnames)
                vector_file_geojson.updateFields()
                vector_file_geojson.commitChanges()

            # Export geojson. (layer, full output pathname, file encoding, destination reference system,
            # output file type, layer options (GeoJSON): number of decimal places used in GeoJSON geometry)
            QgsVectorFileWriter.writeAsVectorFormat(vector_file_geojson, str(geojson_name_full), "utf-8",
                                                    QgsCoordinateReferenceSystem(output_crs), "GeoJSON",
                                                    layerOptions=['COORDINATE_PRECISION={}'.format(GEOJSON_PRECISION)])

            # Rename attribute fields of GeoJSON.
            if LINUX_OS:
                change_field_names(str(geojson_name_full))

            if GEOJSON_ZIP.upper() == 'TRUE':
                with zipfile.ZipFile(str(geojson_name_full) + '.zip', 'w', zipfile.ZIP_DEFLATED) as my_zip:
                    my_zip.write(geojson_name_full)
                # Delete the uncompressed geojson file.
                geojson_name_full.unlink()

            # Close the vector_file_geojson so that the vector_layer can open
            Path(int_geojson_name_full).unlink()
            vector_layer.startEditing()

            # Delete attribute fields of the shapefile related to the daily calculated zonal statistics.
            field_names = ['SWEMean_mm', 'SCover_pct', 'SWEMean_in', 'Area_sqmi', 'SWEVolC_af', 'SWEVol_af']
            if CALCULATE_SWE_MIN.upper() == 'TRUE':
                field_names.extend(['SWEMin_mm', 'SWEMin_in'])
            if CALCULATE_SWE_MAX.upper() == 'TRUE':
                field_names.extend(['SWEMax_mm', 'SWEMax_in'])
            if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
                field_names.extend(['SWESDev_mm', 'SWESDev_in'])

            for item in field_names:
                index = vector_layer.dataProvider().fieldNameIndex(item)
                vector_layer.dataProvider().deleteAttributes([index])

            # Update shapefile with its newly-deleted attribute fields.
            vector_layer.updateFields()
            vector_layer.commitChanges()

            # Create a string variable to be used as the title for the .csv output file - By Date.
            results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'

            # Set directory to the directory where the output .csv daily files are contained. - By Date.
            os.chdir(csv_by_date)

            # Update text file, ListOfDates.txt, with list of dates represented by csv files in ByDate folder.
            array = glob.glob("*.csv")
            array.sort(reverse=True)
            array_recent_date = []

            with open("ListOfDates.txt", 'w') as output_file:
                for filename in array:
                    if filename.endswith("LatestDate.csv") is False and "Upstream" not in str(filename):
                        date = filename[25:33]
                        try:
                            int(date)
                            array_recent_date.append(date)
                            output_file.write(date + "\n")
                        except ValueError:
                            continue

            # Export the daily date array to a .csv file. Overwrite the .csv file if it already exists.
            # Ref: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
            with open(results_date, 'a') as csv_file:
                csv_writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=fieldnames)
                for row in array_date:
                    csv_writer.writerow(row)

            # Get most recent processed SNODAS date & make a copy called 'SnowpackStatisticsByDate_LatestDate.csv'
            # and 'SnowpackStatisticsByDate_LatestDate.geojson' and 'SnowpackStatisticsByDate_LatestDate.zip/.shp'
            most_recent_date = str(max(array_recent_date))
            src = 'SnowpackStatisticsByDate_' + most_recent_date + '.csv'
            dst = 'SnowpackStatisticsByDate_LatestDate.csv'
            copyfile(str(csv_by_date / src), str(csv_by_date / dst))
            src = 'SnowpackStatisticsByDate_' + most_recent_date + '.geojson'
            dst = 'SnowpackStatisticsByDate_LatestDate.geojson'
            copyfile(str(csv_by_date / src), str(csv_by_date / dst))
            # List of extensions referring to the output shapefile
            ext_list = ['.cpg', '.dbf', '.prj', '.qpj', '.shp', '.shx']
            for item in ext_list:
                src = 'SnowpackStatisticsByDate_' + most_recent_date + item
                dst = 'SnowpackStatisticsByDate_LatestDate' + item
                if Path(src).exists():
                    copyfile(str(csv_by_date / src), str(csv_by_date / dst))

            # Return working directory back to its original setting before the script began.
            os.chdir(curr_dir)

            logger.info('z_stat_and_export: Zonal statistics of {} are exported to {}'.format(file, csv_by_basin))
            print("Zonal statistics of {} are complete. \n".format(date_name))

        else:
            logger.info('z_stat_and_export: {} is not a .tif file and the zonal statistics were not processed.\n'
                        .format(file))


def create_snodas_swe_graphs() -> None:
    return
    """Create, or update, the snowpack time series graphs from the by basin data."""

    # Refer to configuration file. If true, update the time series graphs weekly. If false, update the TS graphs daily.
    if TSGRAPH_WEEKLY_UPDATE.upper() == 'TRUE':

        # Check that today is the set weekday to update the time series graphs.
        if str(datetime.today().weekday()) == str(TSGRAPH_WEEKLY_UPDATE_DATE):

            print('Running TsTool file to create the weekly SNODAS SWE graphs. This could take a couple of minutes.')
            logger.info('create_snodas_swe_graphs: Running TsTool file to create the weekly SNODAS Time Series graphs. '
                        'TsTool file pathname: {}'.format(TSTOOL_SNODAS_GRAPHS_PATH))

            # Run the TsTool command file, 'TSTOOL_SNODAS_GRAPHS_PATH', in the background. Wait for the subprocess
            # to complete before continuing.
            try:
                with subprocess.Popen([TSTOOL_INSTALL_PATH, '-commands', TSTOOL_SNODAS_GRAPHS_PATH]) as _:
                    pass
            except OSError:
                print('Currently skipping TSTool Graph creation')
                return
                # error_message = 'Error reading the TSTool executable file: {}'.format(bad_file)
                # print(error_message)
                # logger.error(error_message)
                # exit(1)

            print('Weekly SNODAS Time Series Graphs have been created.')
    else:
        print('Running TsTool file to create the daily SNODAS SWE graphs. This could take up to 5 minutes.')
        logger.info(
            'create_snodas_swe_graphs: Running TsTool file to create the daily SNODAS Time Series graphs. TsTool '
            'file pathname: {}'.format(TSTOOL_SNODAS_GRAPHS_PATH))

        # Run the TsTool command file, 'TSTOOL_SNODAS_GRAPHS_PATH', in the background. Wait for the subprocess
        # to complete before continuing.
        try:
            with subprocess.Popen([TSTOOL_INSTALL_PATH, '-commands', TSTOOL_SNODAS_GRAPHS_PATH]) as _:
                pass
        except OSError:
            print('Currently skipping TSTool Graph creation')
            return
            # error_message = 'Error reading the TSTool executable file: {}'.format(bad_file)
            # print(error_message)
            # logger.error(error_message)
            # exit(1)
        print('Daily SNODAS Time Series Graphs have been created.')


def push_to_aws() -> None:
    """Runs batch file to push the newly-updated files to Amazon Web Services. The specifics are configured within the
    batch file, AWS_BATCH_PATH. """

    print('push_to_aws: Pushing files to Amazon Web Services S3.')
    logger.info('push_to_aws: Pushing files to Amazon Web Services S3 with configuration from {}.'
                .format(AWS_BATCH_PATH))

    # Call batch file, AWS_BATCH_PATH, to push files up to Amazon Web Service.
    args = [AWS_BATCH_PATH]
    try:
        with subprocess.Popen(args, cwd="C:\\Program Files\\Amazon\\AWSCLI") as _:
            pass
    except OSError as bad_file:
        error_message = 'push_to_aws: Error pushing to AWS: {}\nConfirm the path to the AWS bash script and the' \
                        'current working directory keyword argument path is correct.'.format(bad_file)
        print(error_message)
        logger.error(error_message)
        exit(1)
    logger.info('push_to_aws: Files have been pushed to Amazon Web Services S3 as designed by {}.'
                .format(AWS_BATCH_PATH))


def push_to_gcp() -> None:
    """Runs shell script to push the newly-updated files to a GCP bucket. The specifics are configured within the
    batch file, gcp_shell_script. """

    script_location = "/var/opt/snodas-tools/aws"
    gcp_shell_script = "/var/opt/snodas-tools/aws/copyAllToGCPBucket.sh"

    print('push_to_gcp: Pushing files to Google Cloud Platform bucket given shell script ({}) specifics'
          .format(gcp_shell_script))
    logger.info('push_to_gcp: Pushing files to Google Cloud Platform bucket given details from {}.'
                .format(gcp_shell_script))

    # Call shell script, gcp_shell_script, to push files up to GCP.
    os.chdir(script_location)
    try:
        with subprocess.Popen(['sudo', 'bash', gcp_shell_script]) as _:
            pass
    except OSError as bad_file:
        error_message = 'push_to_gcp: Error pushing to GCP: {}\nConfirm the path to the GCP bash script is correct.'\
            .format(bad_file)
        print(error_message)
        logger.error(error_message)
        exit(1)

    logger.info('push_to_gcp: Files have been pushed toGoogle Cloud Platform bucket as designed by {}.'
                .format(gcp_shell_script))


def change_field_names(geojson_file) -> None:
    """Renames the attribute field names of the output GeoJSON file for each date. This function is only to be used in
    the Linux environment because the Windows environment already has a built in attribute field editor within the
    QGIS software. When the built-in QGIS mechanism is run on the Linux machine the following error is printed.
    Error 6: AlterFieldDefn() not supported by this layer.

    This function will create a separate geojson file with the updated attribute fields. The original geojson will be
    deleted and the new geojson will be renamed to the original geojson name.

    Args:
        geojson_file: the full pathname to the GeoJSON file to be edited.

    Returns: None
    """

    # Get the text content of the original GeoJSON file.
    with open(geojson_file, 'r') as geojson:
        geojson_content = geojson.read()

    # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name
    fields = {'SWEMean_mm': 'SNODAS_SWE_Mean_mm', 'SWEVolC_af': 'SNODAS_SWE_Volume_1WeekChange_acft',
              'SWEMean_in': 'SNODAS_SWE_Mean_in', 'Area_sqmi': 'SNODAS_EffectiveArea_sqmi',
              'SWEVol_af': 'SNODAS_SWE_Volume_acft', 'SCover_pct': 'SNODAS_SnowCover_percent'}

    if CALCULATE_SWE_MIN.upper() == 'TRUE':
        fields.update({'SWEMin_mm': 'SNODAS_SWE_Min_mm', 'SWEMin_in': 'SNODAS_SWE_Min_in'})

    if CALCULATE_SWE_MAX.upper() == 'TRUE':
        fields.update({'SWEMax_mm': 'SNODAS_SWE_Max_mm', 'SWEMax_in': 'SNODAS_SWE_Max_in'})

    if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
        fields.update({'SWESDev_mm': 'SNODAS_SWE_StdDev_mm', 'SWESDev_in': 'SNODAS_SWE_StdDev_in'})

    # Replace the appropriate files.
    for key, value in fields.items():
        geojson_content = geojson_content.replace(key, value)

    # Create an intermediate GeoJSON file that has the same contents of the original GeoJSON but with the new
    # attribute names.
    geojson_int_path = geojson_file.replace('.geojson', '_temp.geojson')
    with open(geojson_int_path, 'w') as geojson_int:
        geojson_int.write(geojson_content)

    # Remove the original GeoJSON file and rename the intermediate GeoJSON file to the name of the original GeoJSON.
    Path(geojson_file).unlink()
    os.rename(geojson_int_path, geojson_file)


def clean_duplicates_from_by_basin_csv(csv_basin_dir: Path) -> None:
    """Sometimes duplicate dates end up in the byBasin csv files. This function will make sure that the duplicates
    are removed. """

    # Get a list of the csv files within the byBasin folder (full path names). **/* is for recursive globbing.
    csv_files_to_check =\
        [csv_basin_dir.joinpath(file) for file in csv_basin_dir.glob('**/*') if file.suffix == '.csv']

    # Iterate over the csv files to check for duplicates.
    for csv_full_path in csv_files_to_check:

        # Boolean to determine if there is a duplicate. False until proven true.
        duplicate_exists = False

        # Date seen keeps track of all of the dates seen within the csv file.
        date_seen = []

        # Clean rows keeps track of all of the csv rows that are not duplicates.
        clean_rows = []

        # Open the csv file.
        with open(csv_full_path, 'r') as csv_file:

            # Iterate over each row in the csv file.
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:

                # Get the date from the row.
                date = row[0]

                # If the date has already been seen then the row is a duplicate and should not be written to the new
                # file.
                if date in date_seen:
                    duplicate_exists = True

                # If the date is unique, than the row is not a duplicate and should be written to the new file.
                else:
                    date_seen.append(date)
                    clean_rows.append(row)

        # If there is a duplicate in the csv file, then rewrite the csv file with only the unique rows.
        if duplicate_exists:

            # Remove the original csv file (with the duplicates).
            csv_full_path.unlink()

            # Open the new csv file and write the unique rows to it.
            with open(csv_full_path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=",")
                for row in clean_rows:
                    csv_writer.writerow(row)
