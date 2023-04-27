"""
This module contains the functions utilized by the SNODAS tools (daily_automated.py and daily_interactive.py).
Both scripts process zonal statistics for SNODAS raster datasets for the input vector shapefile (basin boundaries).
The SNODAS Tools were originally developed to calculate zonal statistics for Colorado hydrologic basin boundaries.
Both automated and interactive scripts call the same functions defined in this module.

'daily_automated.py' downloads the current date of SNODAS data and outputs the results in multiple geometries
(geoJSON and shapefile) and multiple .csv files
(one .csv file for the processing date and one .csv file for EACH basin in the input vector shapefile).

'daily_interactive.py' processes historical dates of SNODAS data and outputs the results
in multiple geometries (geoJSON and shapefile) and multiple .csv files
(one .csv file for the processing date and one .csv file for EACH basin in the input vector shapefile).
"""

# Import necessary modules.
import configparser
import csv
import errno
import ftplib
import glob
import gzip
import logging
import os
import snodastools.util.config_util as config_util
import snodastools.util.os_util as os_util
import snodastools.util.qgis_version_util as qgis_version_util
import subprocess
import sys
import tarfile
import time
import zipfile

# TODO smalers 2023-03-01 could catch an ImportError exception but application probably needs to just exit.
if (qgis_version_util.get_qgis_version_int(1) >= 3) and (qgis_version_util.get_qgis_version_int(2) <= 10):
    # The following worked with QGIS 3.10.
    import gdal
    import osr
    import ogr
elif (qgis_version_util.get_qgis_version_int(1) >= 3) and (qgis_version_util.get_qgis_version_int(2) > 10):
    # The following works with QGIS 3.26.3:
    # - could adjust the PYTHONPATH that runs GeoProcessor.
    import osgeo.gdal as gdal
    import osgeo.ogr as ogr
    #import osgeo.osr as osre
    import osgeo.osr as osr

from datetime import date, datetime, timedelta
from logging.config import fileConfig
from pathlib import Path
from shutil import copy, copyfile

from PyQt5.QtCore import QVariant
from qgis.analysis import (
    QgsRasterCalculator,
    QgsRasterCalculatorEntry,
    QgsZonalStatistics
)
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

# If set to False, the module data have not been initialized by the init_snodas_util() function.
# If set to True, the moudle data have been initialized in the init_snodas_util() function.
init_snodas_util_called: bool = False

# Assigns the values from the configuration file to the python variables.
# See below for description of each variable obtained by the configuration file.
#
# HOST:
#   The SNODAS FTP site url to access the downloadable data.
# USERNAME:
#   The SNODAS FTP site username to access the downloadable data.
# PASSWORD:
#   The SNODAS FTP site password to access the downloadable data.
# SNODAS_FTP_FOLDER:
#   The folder pathname within the SNODAS FTP site that accesses the SNODAS masked datasets.
#   The masked datasets are SNODAS grids clipped to the contiguous U.S. boundary.
# CLIP_PROJECTION:
#   The EPSG projection code of the input basin extent shapefile. Defaulted to WGS84.
#   The basin extent shapefile is used to clip the national SNODAS grids to the clipped extent of the basin boundaries.
# CALCULATE_STATS_PROJECTION:
#   The desired EPSG projection code of the final products (snow cover grid and clipped SNODAS grid).
#   Defaulted to Albers Equal Area.
# ID_FIELD_NAME:
#   The field name of the basin boundary attribute table describing the identification of each basin.
#   The naming convention of the CSVByBasin result files use the ID_FIELD_NAME.
# NULL_VAL:
#   The null values that SNODAS applies to the data's null value.
#   Defaulted to -9999 but should be changed if the null values provided by SNODAS are changed.
# CALCULATE_SWE_MIN:
#   Daily zonal SWE minimum statistic will be calculated if this value is 'True'.
# CALCULATE_SWE_MAX:
#   Daily zonal SWE maximum statistic will be calculated if this value is 'True'.
# CALCULATE_SWE_STD_DEV:
#   Daily zonal SWE standard deviation statistic will be calculated if this value is 'True'.
# CELL_SIZE_X:
#   The spatial resolution of the SNODAS (CALCULATE_STATS_PROJECTION) cells' x-axis (in meters).
# CELL_SIZE_Y:
#   The spatial resolution of the SNODAS (CALCULATE_STATS_PROJECTION) cells' y-axis (in meters).
# GEOJSON_PRECISION:
#   The number of decimal places (precision) used in the output GeoJSON geometry.
# TSTOOL_INSTALL_PATH:
#   The full pathname to the TSTool program.
# TSToolBatchFile:
#   The full pathname to the TSTool Batch file responsible for creating the time-series graphs.
# AEA_CONIC_STRING:
#   USA_Albers_Equal_Area projection in WKT (Proj4) - for use in Linux systems

TSTOOL_INSTALL_PATH: str or None = None
TSTOOL_SNODAS_GRAPHS_PATH: str or None = None
AWS_BATCH_PATH: str or None = None

HOST: str or None = None
USERNAME: str or None = None
PASSWORD: str or None = None
SNODAS_FTP_FOLDER: str or None = None
NULL_VAL: str or None = None

ID_FIELD_NAME: str or None = None

CLIP_PROJECTION: str or None = None
CALCULATE_STATS_PROJECTION: str or None = None
CELL_SIZE_X: str or None = None
CELL_SIZE_Y: str or None = None

GEOJSON_PRECISION: str or None = None
GEOJSON_ZIP: str or None = None
TSGRAPH_WEEKLY_UPDATE: str or None = None
TSGRAPH_WEEKLY_UPDATE_DATE: str or None = None

CALCULATE_SWE_MIN: str or None = None
CALCULATE_SWE_MAX: str or None = None
CALCULATE_SWE_STD_DEV: str or None = None

AEA_CONIC_STRING: str or None =\
    "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

# Set the srs for the CALCULATE_STATS_PROJECTION for a Linux system.
calculate_statistics_projection_srs = osr.SpatialReference()
calculate_statistics_projection_srs.ImportFromProj4(AEA_CONIC_STRING)
CALCULATE_STATS_PROJ_WKT = calculate_statistics_projection_srs.ExportToWkt()

# Get today's date.
now = datetime.now()


def download_snodas(download_dir: Path, single_date: date) -> list:
    """
    Access the SNODAS FTP site and download the .tar file of single_date.
    The .tar file saves to the specified download_dir folder.
    download_dir: full path name to the location where the downloaded SNODAS rasters are stored
    single_date: the date of interest
    """

    start_time = datetime.now()
    logger = logging.getLogger(__name__)
    logger.info('Start downloading SNODAS tar for {}'.format(single_date))

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    # Connect to FTP server.
    # Code format for the following block of code in reference to:
    # http://www.informit.com/articles/article.aspx?p=686162&seqNum=7 and
    # http://stackoverflow.com/questions/5230966/python-ftp-download-all-files-in-directory
    ftp = ftplib.FTP(HOST, USERNAME, PASSWORD)

    logger.info('  Connected to FTP server {}. Saving in {}'.format(HOST, single_date))

    # Change to the top-level folder within FTP site storing the SNODAS masked data,
    # configuration should have something like:
    #   host = sidads.colorado.edu
    #   username = anonymous
    #   password = None
    #   folder_path = /DATASETS/NOAA/G02158/masked/
    #   null_value = -9999

    # TODO smalers 2023-04-25 need to implement retries to handle TimeoutError.
    retries = 10
    retry_wait_seconds = 5

    ftp.cwd(SNODAS_FTP_FOLDER)


    # For example: /DATASETS/NOAA/G02158/masked/
    os.chdir(download_dir)

    # Change into the folder containing the data from single_date's year (4-digits).
    ftp.cwd(str(single_date.year) + '/')

    # Change into the folder containing the data from single_date's month (e.g., 01_Jan).
    month_folder = single_date.strftime('%m') + "_" + single_date.strftime('%b') + '/'
    ftp.cwd(month_folder)

    # Get the day value as 2-digit zero-padded (e.g., 02).
    day = single_date.strftime('%d')

    # Iterate through files in FTP folder and save single_date's data as a file in download folder.
    # Create empty list to track whether a download is available.
    no_download_available = []
    filenames = ftp.nlst()
    for file in filenames:
        if file.endswith('{}.tar'.format(day)):
            # Open the local file to receive the output, same name as the remote, like:
            #   SNODAS_20230424.tar
            local_file = open(file, 'wb')
            # RETR file = retrieve file
            # local_file.write = function called for each block, so in this case write the binary data
            # Use a block size that seems to be recommended.
            block_size = 8192
            ftp.retrbinary('RETR ' + file, local_file.write, blocksize=block_size)

            logger.info('  Downloaded {}'.format(single_date))
            # If SNODAS data is available for download, append a '1'.
            no_download_available.append(1)
            local_file.close()
        else:
            # If SNODAS data is not available for download, append a '0'.
            no_download_available.append(0)

    if 1 not in no_download_available:
        # List only contains zeros so was not able to download.
        # Report error if download marker '1' is not in the list.
        logger.error('  Download unsuccessful for {}'.format(single_date), exc_info=True)
        failed_date = single_date

    else:
        # Report success if download marker '1' is in the list.
        end_time = datetime.now()
        download_time = end_time - start_time
        print('Download complete for {}.'.format(single_date), file=sys.stderr)
        logger.info('  Download complete for {}, took {} ms.'.format(
            single_date, int(download_time.microseconds/1000)))
        failed_date = 'None'

    # Set a timestamp to later export to the statistical results:
    # - this helps data users know when the data for a date was last updated
    timestamp = datetime.now().isoformat()

    # Add values of optional statistics to a list to be checked for validity in 'daily_automated.py' and
    # 'daily_interactive.py' scripts.
    opt_stats = [
        CALCULATE_SWE_MAX,
        CALCULATE_SWE_MIN,
        CALCULATE_SWE_STD_DEV
    ]

    return [timestamp, opt_stats, failed_date]


def format_date_yyyymmdd(date: date) -> str:
    """
    Convert date to string date in format: YYYYMMDD.
    date: the date of interest
    """
    #logger = logging.getLogger(__name__)
    #logger.debug('Start formatting {}.'.format(date))

    # Parse year, month and day of input date into separate entities.
    year = date.year
    month = date.strftime('%m')
    day = date.strftime('%d')

    # Concatenate strings of the year, double-digit month, and double-digit day.
    day_string = str(year) + month + day

    #logger.debug('  Finished {} formatting.'.format(date))

    # Return string.
    return day_string


def init_snodas_util():
    """
    Initialize this confirmation module.
    :return:
    """
    global init_snodas_util_called

    global TSTOOL_INSTALL_PATH
    global TSTOOL_SNODAS_GRAPHS_PATH
    global AWS_BATCH_PATH

    global HOST
    global USERNAME
    global PASSWORD
    global SNODAS_FTP_FOLDER
    global NULL_VAL

    global ID_FIELD_NAME

    global CLIP_PROJECTION
    global CALCULATE_STATS_PROJECTION
    global CELL_SIZE_X
    global CELL_SIZE_Y

    global GEOJSON_PRECISION
    global GEOJSON_ZIP
    global TSGRAPH_WEEKLY_UPDATE
    global TSGRAPH_WEEKLY_UPDATE_DATE

    global CALCULATE_SWE_MIN
    global CALCULATE_SWE_MAX
    global CALCULATE_SWE_STD_DEV

    if init_snodas_util_called:
        # Already initialized.
        return
    else:
        # Initialize module data.
        TSTOOL_INSTALL_PATH = config_util.get_config_prop("ProgramInstall.tstool_path")
        if not TSTOOL_INSTALL_PATH:
            # Old syntax.
            TSTOOL_INSTALL_PATH = config_util.get_config_prop("ProgramInstall.tstool_pathname")
        TSTOOL_SNODAS_GRAPHS_PATH = config_util.get_config_prop(
            "ProgramInstall.tstool_create_snodas_graphs_command_file")
        if not TSTOOL_SNODAS_GRAPHS_PATH:
            # Old syntax.
            TSTOOL_SNODAS_GRAPHS_PATH = config_util.get_config_prop(
                "ProgramInstall.tstool_create-snodas-graphs_pathname")
        AWS_BATCH_PATH = config_util.get_config_prop("ProgramInstall.aws_batch_pathname")

        HOST = config_util.get_config_prop("SNODAS_FTPSite.host")
        USERNAME = config_util.get_config_prop("SNODAS_FTPSite.username")
        PASSWORD = config_util.get_config_prop("SNODAS_FTPSite.password")
        SNODAS_FTP_FOLDER = config_util.get_config_prop("SNODAS_FTPSite.folder_path")
        NULL_VAL = config_util.get_config_prop("SNODAS_FTPSite.null_value")

        ID_FIELD_NAME = config_util.get_config_prop("BasinBoundaryShapefile.basin_id_fieldname")

        # TODO smalers 2022-04-25 SNODAS Tools 2.0 code forced EPSGS.  Now allow in config file.
        #CLIP_PROJECTION = "EPSG:" + config_util.get_config_prop("Projections.datum_epsg")
        #CALCULATE_STATS_PROJECTION = "EPSG:" + config_util.get_config_prop("Projections.calcstats_proj_epsg")
        CLIP_PROJECTION = config_util.get_config_prop("Projections.datum_crs")
        CALCULATE_STATS_PROJECTION = config_util.get_config_prop("Projections.calcstats_crs")
        CELL_SIZE_X = float(config_util.get_config_prop("Projections.calculate_cellsize_x"))
        CELL_SIZE_Y = float(config_util.get_config_prop("Projections.calculate_cellsize_y"))

        GEOJSON_PRECISION = config_util.get_config_prop("OutputLayers.geojson_precision")
        GEOJSON_ZIP = config_util.get_config_prop("OutputLayers.geojson_zip")
        TSGRAPH_WEEKLY_UPDATE = config_util.get_config_prop("OutputLayers.tsgraph_weekly_update")
        TSGRAPH_WEEKLY_UPDATE_DATE = config_util.get_config_prop("OutputLayers.tsgraph_weekly_update_date")

        CALCULATE_SWE_MIN = config_util.get_config_prop("OptionalZonalStatistics.calculate_swe_minimum")
        CALCULATE_SWE_MAX = config_util.get_config_prop("OptionalZonalStatistics.calculate_swe_maximum")
        CALCULATE_SWE_STD_DEV = config_util.get_config_prop("OptionalZonalStatistics.calculate_swe_standard_deviation")

        # Indicate that initialization has occurred.
        init_snodas_util_called = True


def list_dir(path: Path, pattern: str or [str]) -> [Path]:
    """
    List all files that end with the provided extension(s).
    path: The directory to search through.
    patther: The single string or multiple pattherns to match, using glob-style regular expression.
    multiple_types: Whether multiple extensions need to be searched. Default is False.
    Returns: Either a generator (iterator) from path.glob(), or a list of the files.
    """

    if type(pattern) is str:
        # Pattern is a single string.
        return path.glob(pattern)
    else:
        # Pattern is an array.
        all_files = []
        for x in pattern:
            all_files.extend(path.glob(x))
        return all_files


def read_dat_txt_properties ( txt_file_path: Path ):
    """
    Read the properties from a 'txt' file associated with SNODAS 'dat' file.
    Properties have syntax:

    property name: value

    :param txt_file_path:  Path to the 'txt' file to read.
    :return: A dictionary of properties, all string values
    """

    properties = {}
    with open(txt_file_path, 'r') as in_file:
        while True:
            line = in_file.readline()
            if not line:
                # No more data lines.
                break
            if line.find(":") > 0:
                # Found a property.
                parts = line.split(":")
                properties[parts[0].strip()] = parts[1].strip()

    # Return the dictionary of properties.
    return properties


def untar_snodas_file(file: Path, folder_input: Path, folder_output: Path) -> None:
    """
    Untar downloaded SNODAS .tar file and extract the contained files to the folder_output.
    file: SNODAS .tar file to untar without the path, typically with a name like SNODAS_20230424.tar
    folder_input: the full pathname to the folder containing 'file'
    folder_output: the full pathname to the folder containing the extracted files.
    """

    logger = logging.getLogger(__name__)

    # Set full pathname of file.
    file_full = folder_input / file

    logger.info('Start untarring {}'.format(file_full))

    # Open .tar file.
    tar = tarfile.open(file_full)

    # Change working directory to output folder.
    os.chdir(folder_output)

    # Extract .tar file and save contents in output directory.
    tar.extractall()

    # Close .tar file.
    tar.close()

    logger.info('  Untarred: {}'.format(file_full))
    logger.info('  Output folder: {}'.format(folder_output))

# TODO smalers 2023-04-25 alphabeize methods once know that everthing is working.
# Everything above is alphabetized.  Everything below is not.


def delete_irrelevant_snodas_files(file: Path) -> None:
    """
    Delete file if not identified by the unique SWE ID.
    The SNODAS .tar files contain many SNODAS datasets.
    For this project, the parameter of interest is SWE, uniquely named with ID '1034'.
    If the configuration file is set to 'False' for the value of the 'SaveAllSNODASParameters' section,
    then the parameters other than SWE are deleted.
    file: file extracted from the downloaded SNODAS .tar file
    """

    logger = logging.getLogger(__name__)

    # Check for unique identifier '1034'.
    if '1034' in str(file):
        logger.info('  Keeping SWE (1034) file: {}'.format(file))
    else:
        # Delete file.
        file.unlink()
        logger.info('  Deleted: {}'.format(file))


def move_irrelevant_snodas_files(file: str, folder_output: Path) -> None:
    """
    Move file to the 'OtherParameters' folder if not identified by the unique SWE ID, '1034'.
    The SNODAS .tar files contain many SNODAS datasets.
    For current SNODAS Tools, the parameter of interest is SWE, uniquely named with ID '1034'.
    If the configuration file is set to 'True' for the value of the 'SaveAllSNODASParameters' section,
    then the parameters other than SWE are moved to the '2_SetFormat/OtherParameters' sub-folder, for example.
    These files are not currently processed.
    file: file extracted from the downloaded SNODAS .tar file
    folder_output: full pathname to folder where the other-than-SWE files are contained, OtherParameters
    """
    logger = logging.getLogger(__name__)

    logger.info('Start moving file {}'.format(file))

    # Check for unique identifier '1034'.
    if '1034' in file:
        logger.info('  Not moving SWE 1034 file: {}.'.format(file))
    else:
        # Move copy of file to folder_output. Delete original file from original location.
        copy(file, folder_output)
        logger.info('  Moved:'.format(file, folder_output))
        logger.info('    from: {}.'.format(file))
        logger.info('      to: {}.'.format(folder_output))
        Path(file).unlink()


def extract_snodas_gz_file(file: Path) -> None:
    """
    Extract .dat and .Hdr files from SNODAS .gz file.

    New
    ====
    Each daily SNODAS raster has 2 gz files, one that includes .dat and the other that incldues .txt.
    Not sure if the txt file has information that old Hdr file had?

    Old
    ====
    Each daily SNODAS raster has 2 files associated with it (.dat and .Hdr).
    Both are zipped within one .gz file.
    A custom Hdr file is created during processing and the original file is ignored.

    file: .gz file to be extracted
    """

    logger = logging.getLogger(__name__)
    logger.info('Start extracting gz file {}'.format(file))

    # This block of script was based off of the script from the following resource:
    # http://stackoverflow.com/questions/20635245/using-gzip-module-with-python
    in_file = gzip.open(str(file), 'r')
    with open(file.stem, 'wb') as out_file:
        out_file.write(in_file.read())
    in_file.close()

    # Delete the .gz file.
    file.unlink()

    logger.info('  Extracted files from: {}'.format(file))


def convert_snodas_dat_to_bil(dat_file_path: Path) -> None:
    """
    Convert SNODAS .dat file into supported file format (.bil).
    The .dat and .Hdr files are not supported file formats to use with QGS processing tools.
    This is a simple file rename from '.dat' to .'bil'.
    The .dat file is not retained if keeping files for troubleshooting since the .bil is the same contents.
    The QGS processing tools are used to calculate the daily zonal stats.
    file: .dat file to be converted to .bil format
    """

    logger = logging.getLogger(__name__)
    logger.info('Start converting dat {}'.format(dat_file_path))

    # Change file extension from .dat to .bil.
    # If the '.bil' file exists (for example because keeping files for troubleshooting ia previous step),
    # remove the '.bil' file before renaming.
    bil_file_path = dat_file_path.with_suffix('.bil')
    if bil_file_path.exists():
        # The .bil file exists so remove before rename or will get an error.
        bil_file_path.unlink()
    dat_file_path.rename(bil_file_path)

    logger.info('  Renamed .dat to .bil: {}'.format(bil_file_path))


def create_snodas_hdr_file(bil_file_path: Path) -> None:
    """
    Create custom .hdr file.
    A custom .hdr file needs to be created to indicate the raster settings of the .bil file.
    The custom .hdr file aids in converting the .bil file to a usable .tif file.
    See the SNODAS format documentation:  https://nsidc.org/sites/default/files/nsidc_special_report_11.pdf
    file: .bil file that needs a custom .hdr file
    """

    logger = logging.getLogger(__name__)
    logger.info('Start creating hdr for {}'.format(bil_file_path))

    # Create name for the new .hdr file.
    hdr_file_path = bil_file_path.with_suffix('.hdr')

    # Read properties from the original 'txt' file and map to 'hdr' file properties.
    # - first read the 'txt' file propeties
    # - then map them to new names
    txt_property_dict = {
        "Benchmark x-axis coordinate": "ulxmap",
        "Benchmark y-axis coordinate": "ulymap",
        "Number of columns" : "ncols",
        "Number of rows" : "nrows",
        "X-axis resolution" : "xdim",
        "Y-axis resolution" : "ydim"
    }
    txt_file_path = bil_file_path.with_suffix('.txt')
    dat_txt_properties = read_dat_txt_properties(txt_file_path)
    # Create a new dictionary.
    bil_dict = {}
    error_count = 0
    for key, value in txt_property_dict.items():
        try:
            bil_dict[value] = dat_txt_properties[key]
        except KeyError:
            logger.warning("  Did not find '{}' property in file: {}".format(key, txt_file_path))
            error_count = error_count + 1
    if error_count > 0:
        logger.warning("  Had {} errors processing header properties.".format(error_count))
        raise RuntimeError("SNODAS txt file does not contain expected properties: {}".format(txt_file_path))

    # These lines of code create a custom .hdr file to give details about the .bil/raster file.
    # The specifics inside each .hdr file are the same for each daily raster.
    # However, there must be a .hdr file that matches the name of each .bil/.tif file for QGS to import each dataset.
    # The text included in the .Hdr file originated from page 12 of the
    # 'National Operational Hydrologic Remote Sensing Center SNOw Data Assimilation System (SNODAS) Products of NSIDC'.
    # This document can be found at the following url:
    #    https://nsidc.org/sites/default/files/nsidc_special_report_11.pdf
    # Although the above documentation says that the header is constant,
    # the numbers have changed slightly since the orginal SNODAS Tools code was implemented so get the values
    # from the 'txt' file where appropriate.
    # An exception will be raised if the values are not found in the 'txt' file,
    # which is probably OK because the code and data would need to be reviewed.
    with open(hdr_file_path, 'w') as file2:
        # byteorder is not in the txt file but is known to be M (Motorola or big endian).
        file2.write('byteorder M\n')
        # File type is set to "bil" (band interleaved by line).
        file2.write('layout bil\n')
        # Number of bands is not in the txt file but is known to be 1.
        file2.write('nbands 1\n')
        # Number of bits is not in the txt file but "Data bytes per pixel: 2" indicates 2x8 = 16.
        file2.write('nbits 16\n')
        # "Number of columns: 6935" is found in the txt file:
        # - extract and transfer
        file2.write('ncols {}\n'.format(bil_dict['ncols']))
        # "Number of rows: 3351" is found in the txt file:
        # - extract and transfer
        file2.write('nrows {}\n'.format(bil_dict['nrows']))
        # Pixel type is "Data type: integer" in the txt file, which is a signed integer.
        file2.write('pixeltype SIGNEDINT\n')
        # Newer files: reference is "Benchmark x-axis coordinate: -124.729166666662" in the txt file so extract.
        # Older files: reference is "Benchmark x-axis coordinate: -124.729583333331703"
        file2.write('ulxmap {}\n'.format(bil_dict['ulxmap']))
        # Newer files: reference is "Benchmark y-axis coordinate: 52.8708333333312" in the txt file so extract.
        # Older files: reference is "Benchmark y-axis coordinate: 52.871249516804028"
        file2.write('ulymap {}\n'.format(bil_dict['ulymap']))
        # Not sure that this is a recognized property:
        # - the txt file data are decimal degrees
        # - the txt file does have "Horizontal datum: WGS84"
        file2.write('units dd\n')
        # X dimension is "X-axis resolution: 0.00833333333333300" in the txt file so extract.
        file2.write('xdim {}\n'.format(bil_dict['xdim']))
        # Y dimension is "Y-axis resolution: 0.00833333333333300" in the txt file so extract.
        file2.write('ydim {}\n'.format(bil_dict['ydim']))

    logger.info('  Created a custom .hdr file: {}'.format(hdr_file_path))


def convert_snodas_bil_to_tif(bil_file_path: Path, folder_output: Path) -> None:
    """
    Convert .bil file into .tif file for processing within the QGIS environment.
    bil_file_path: file to be converted into a .tif file
    folder_output: full pathname to folder where the created .tif files are contained
    """

    logger = logging.getLogger(__name__)
    logger.info('Start converting .bil: {}'.format(bil_file_path))

    # Create name with replaced .tif file extension:
    # - the output is to a different folder
    tif_file_path = folder_output / bil_file_path.with_suffix('.tif').name

    # Convert file to .tif format by modifying the original file and saving to the output folder.
    gdal.Translate(str(tif_file_path), str(bil_file_path), format='GTiff')

    logger.info('  Converted to .tif: {}'.format(tif_file_path))


def delete_snodas_files(file: Path) -> None:
    """
    Delete file with .bil or .hdr extensions.
    The .bil and .hdr formats are no longer important to keep because the newly created .tif file holds the same data.
    file: file to be checked for either .hdr or .bil extension (and, ultimately deleted)
    """

    logger = logging.getLogger(__name__)
    logger.info('Start deleting file {}'.format(file))

    # Delete file.
    if file.exists():
        file.unlink()
        logger.info('  {} has been deleted.'.format(file))
    else:
        logger.info('  {} does not exist so no need to delete.'.format(file))


def create_extent(basin_shp: str, folder_output: Path) -> None:
    """
    Create a single-feature bounding box shapefile representing the extent of the input shapefile the watershed
    boundary input shapefile).
    The created extent shapefile will be used to clip the SNODAS daily national grid to the size of the study area.
    Reference: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
    basin_shp: the input shapefile for which to create the extent shapefile
    folder_output: full pathname to the folder that will hold the extent shapefile
    """

    logger = logging.getLogger(__name__)

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    # Get basin boundary extent.
    in_driver = ogr.GetDriverByName("ESRI Shapefile")
    basin_shp_path = Path(basin_shp)
    if not basin_shp_path.exists():
        logger.error("Bounding box shapefile does not exist: {}".format(basin_shp))
        # Raise an exception:
        # - the following is apparently the correct way to do it
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), basin_shp)
    in_data_source = in_driver.Open(basin_shp, 0)
    in_layer = in_data_source.GetLayer()
    extent = in_layer.GetExtent()

    # Create a Polygon from the extent tuple.
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(extent[0], extent[2])
    ring.AddPoint(extent[1], extent[2])
    ring.AddPoint(extent[1], extent[3])
    ring.AddPoint(extent[0], extent[3])
    ring.AddPoint(extent[0], extent[2])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    # Save extent to a new Shapefile.
    basename = 'studyArea_extent'
    output_shape_file = basename + '.shp'
    output_projection = basename + '.prj'
    out_driver = ogr.GetDriverByName("ESRI Shapefile")
    output_shp_full_name = folder_output / output_shape_file
    output_prj_full_name = folder_output / output_projection

    # Create the output shapefile and add an ID Field (there will only be 1 ID because there will only be 1 feature).
    out_data_source = out_driver.CreateDataSource(str(output_shp_full_name))
    out_layer = out_data_source.CreateLayer("studyArea_extent", geom_type=ogr.wkbPolygon)
    id_field = ogr.FieldDefn("id", ogr.OFTInteger)
    out_layer.CreateField(id_field)

    # Create the feature and set values.
    feat_def = out_layer.GetLayerDefn()
    feature = ogr.Feature(feat_def)
    feature.SetGeometry(poly)
    feature.SetField("id", 1)
    out_layer.CreateFeature(feature)
    feature = None

    # Save and close DataSource. Important - do not remove.
    in_data_source = None
    out_data_source = None
    # in_just_code = float('NaN')
    # out_just_code = float('NaN')

    # Set projection to CALCULATE_STATS_PROJECTION
    # (the projection set in the config file to be the same as the basin boundary shapefile).
    with open(output_prj_full_name, 'w') as file:
        if os_util.is_linux_os():
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
    # Set file names.
    infile = str(output_shp_full_name)
    outfile = str(output_shp_full_name).replace('_extent', 'Extent_prj')

    # Get outfile path.
    outfile_path = Path(outfile).parent
    # Get file name without extension.
    outfile_short_name = Path(outfile).stem

    if os_util.is_linux_os():
        # Spatial Reference of the input file. Access the Spatial Reference and assign the input projection.
        in_spatial_ref = calculate_statistics_projection_srs

        # Spatial Reference of the output file. Access the Spatial Reference and assign the output projection.
        out_spatial_ref = osr.SpatialReference()
        out_spatial_ref.ImportFromEPSG(int(CLIP_PROJECTION.replace('EPSG:', '')))

    else:
        # Spatial Reference of the input file. Access the Spatial Reference and assign the input projection.
        in_spatial_ref = osr.SpatialReference()
        in_spatial_ref.ImportFromEPSG(in_just_code)

        # Spatial Reference of the output file. Access the Spatial Reference and assign the output projection.
        out_spatial_ref = osr.SpatialReference()
        out_spatial_ref.ImportFromEPSG(out_just_code)

    transform_old = True
    # Create the Coordinate Transformation:
    if transform_old:
        # This is the old way
        coord_transform = osr.CoordinateTransformation(in_spatial_ref, out_spatial_ref)
    else:
        # New way:
        transform_context=QgsCoordinateTransformContext()
        # Transform provides the source and destination CRS:
        # - allowFallback=False because want it to fail if cannot be done
        transform_context.addCoordinateOperation(
            sourceCrs=in_spatial_ref,
            destinationCrs=out_spatial_ref,
            coordinateOperationProjString="",
            allowFallback=False)
        # Not enabled!

    # Open the input shapefile and get the layer.
    driver = ogr.GetDriverByName('ESRI Shapefile')
    in_dataset = driver.Open(infile, 0)
    inlayer = in_dataset.GetLayer()

    # Create the output shapefile but check first if file exists.
    if Path(outfile).exists():
        driver.DeleteDataSource(outfile)

    out_dataset = driver.CreateDataSource(outfile)
    outlayer = out_dataset.CreateLayer(str(outfile_short_name), geom_type=ogr.wkbPolygon)

    # Get the field_def_1 for attribute ID and add to output shapefile.
    feature = inlayer.GetFeature(0)
    field_def_1 = feature.GetFieldDefnRef('id')
    outlayer.CreateField(field_def_1)

    # Get the feat_def for the output shapefile.
    feat_def = outlayer.GetLayerDefn()

    # Loop through input features and write to output file.
    in_feature = inlayer.GetNextFeature()
    while in_feature:

        # Get the input geometry.
        geometry = in_feature.GetGeometryRef()

        # Reproject the geometry, each one has to be projected separately.
        geometry.Transform(coord_transform)

        # Create a new output feature.
        out_feature = ogr.Feature(feat_def)

        # Set the geometry and attribute.
        out_feature.SetGeometry(geometry)
        out_feature.SetField('id', in_feature.GetField('id'))

        # Add the feature to the output shapefile.
        outlayer.CreateFeature(out_feature)

        # Destroy the features and get the next input features.
        out_feature.Destroy()
        in_feature.Destroy()
        in_feature = inlayer.GetNextFeature()

    # Close the shapefiles.
    in_dataset.Destroy()
    out_dataset.Destroy()

    # Create the prj projection file.
    out_spatial_ref.MorphToESRI()
    with open(outfile_path.joinpath(outfile_short_name + '.prj'), 'w') as proj_file:
        proj_file.write(out_spatial_ref.ExportToWkt())

    # Delete the unnecessary extent shapefile files projected in the CALCULATE_STATS_PROJECTION.
    extensions = ['.dbf', '.prj', '.shp', '.shx']
    for extension in extensions:
        delete_file = str(output_shp_full_name).replace('.shp', extension)
        Path(delete_file).unlink()


def copy_snodas_tif_to_clip_folder(tif_file_path: Path, clip_folder_path: Path) -> None:
    """
    Copy original unclipped tif location to folder_output.
    The copied file will be clipped.
    To keep the file as it is, the original is saved within the original folder.
    tif_file_path: .tif file to be copied to folder_output
    clip_folder_path: full path to the destination folder
    """

    logger = logging.getLogger(__name__)
    logger.info('Start copying .tif to clip folder.')
    # Set full pathname of file.
    file_copy_path = clip_folder_path / tif_file_path.name

    # Copy file to file_full_output.
    copy(tif_file_path, file_copy_path)

    logger.info('  Copied:')
    logger.info('    from: {}'.format(tif_file_path))
    logger.info('      to: {}'.format(file_copy_path))


def assign_snodas_datum(tif_file_path: Path, folder: Path) -> None:
    """
    Define WGS84 as datum. Defaulted in configuration file to assign SNODAS grid with WGS84 datum.
    The downloaded SNODAS raster is un-projected however the
    "SNODAS fields are grids of point estimates of snow cover in
    latitude/longitude coordinates with the horizontal datum WGS84." - SNODAS Data Products at NSIDC User Guide
    http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/index.html
    tif_file_path: the name of the .tif file that is to be assigned a projection
    folder: full pathname to the folder where both the un-projected and projected raster are stored
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)
    logger.info('Start assigning datum to: {}'.format(tif_file_path))

    # Check for un-projected .tif files.
    if str(tif_file_path).upper().endswith('HP001.TIF'):

        # Change name from 'us_ssmv11034tS__T0001TTNATS2003093005HP001.tif' to '20030930_WGS84.tif'.
        new_file = str(tif_file_path.name).replace('05HP001', '_WGS84').replace('us_ssmv11034tS__T0001TTNATS', '')

        # Set up for gdal.Translate tool. Set full path names for both input and output files.
        input_raster = tif_file_path
        output_raster = folder / new_file

        # Assign datum (Defaulted to 'EPSG:4326').
        gdal.Translate(str(output_raster), str(input_raster), outputSRS=CLIP_PROJECTION)

        # Delete un-projected file.
        input_raster.unlink()

        logger.info('  Assigned projection of {} to: {}'.format(CLIP_PROJECTION, tif_file_path))

        # Writes the projection information to the log file.
        ds = gdal.Open(str(output_raster))
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        datum = srs.GetAttrValue('GEOGCS')

        if srs.IsProjected:
            proj_name = srs.GetAttrValue('AUTHORITY')
            proj_num = srs.GetAttrValue('AUTHORITY', 1)
            logger.info("  Have projection {}:{} and datum {} for: {}"
                        .format(proj_name, proj_num, datum, output_raster.name))
        else:
            logger.info("  Have projection {} and datum {} for: {}".format(prj, datum, output_raster.name))
    else:
        logger.warning("  Does not end in 'HP001.tif' and therefore has not been assigned projection of {}:".format(
            CLIP_PROJECTION))
        logger.warning("  {}".format(tif_file_path))
        return

    logger.info('  Successfully converted:')
    logger.info('    from: {}'.format(tif_file_path))
    logger.info('      to: {}'.format(output_raster.name))


def snodas_raster_clip(tif_file_path: Path, vector_extent: Path) -> None:
    """
    Clip file by vector_extent shapefile. The output filename starts with 'Clip'.
    tif_file_path: the projected (defaulted to WGS84) .tif file to be clipped
    vector_extent: full pathname to shapefile holding the extent of the basin boundaries.
    This shapefile must be projected in projection assigned in function assign_snodas_datum (defaulted to WGS84).
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)
    logger.info('Start clipping raster {}'.format(tif_file_path))

    # Check for file extension .tif.
    if str(tif_file_path).upper().endswith('_WGS84.TIF'):

        # Change name from 20030930_WGS84.tif to 'Clip_YYYYMMDD.tif'.
        date_name = str(tif_file_path.name).replace('_WGS84', '')
        new_name = tif_file_path.parent / ('Clip_' + date_name)

        # Set full pathname of both input and output files to be used in the gdal.Warp tool.
        file_full_input = tif_file_path
        file_full_output = new_name

        # Clip .tif file by the input extent shapefile.
        # For more info on gdal.WarpOptions parameters, reference:
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

        # Delete un-clipped raster files.
        file_full_input.unlink()
        # Writes the projection to the log file.
        ds = gdal.Open(str(file_full_output))
        if not ds:
            logger.warning('  Null reading file: {}'.format(file_full_output))
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        datum = srs.GetAttrValue('GEOGCS')

        if srs.IsProjected:
            proj_name = srs.GetAttrValue('AUTHORITY')
            proj_num = srs.GetAttrValue('AUTHORITY', 1)
            logger.info("  Have projection {}:{} and datum {} for: {}".format(
                proj_name, proj_num, datum, file_full_output.name))
        else:
            logger.info("  Have projection {} and datum {} for: {}".format(prj, datum, file_full_output.name))
        logger.info('  Successfully clipped:')
        logger.info('    from: {}.'.format(tif_file_path))
        logger.info('      to: {}.'.format(file_full_output))
    else:
        logger.info('  File does not end with _WGS84.tif so the clip was not processed:')
        logger.info('    {}'.format(tif_file_path))

    return


def assign_snodas_projection(tif_file_path: Path) -> None:
    """
    Project clipped raster from its original datum (defaulted to WGS84) to desired projection
    (defaulted to Albers Equal Area).
    file: clipped file with original projection to be projected into desired projection
    clip_folder: full pathname of folder for both the originally clipped rasters and the projected clipped rasters
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)
    logger.info('Start assigning projection to: {}'.format(tif_file_path))

    # Check for projected SNODAS rasters.
    if str(tif_file_path.name).startswith('Clip_') and str(tif_file_path).endswith('.tif'):

        # Change name from 'Clip_YYYYMMDD.tif' to 'SNODAS_SWE_ClipAndProj_YYYYMMDD.tif'.
        new_name = str(tif_file_path.name).replace('Clip_', 'SNODAS_SWE_ClipAndProj_')

        # Set full pathname of both input and output file to be used in the gdal.
        file_full_input = tif_file_path
        file_full_output = tif_file_path.parent / new_name

        # Re-project the clipped SNODAS .tif files from original projection to desired projection.
        if os_util.is_linux_os():
            # This is potentially another way to perform the algorithm using the processing module.
            # The original method is still working, so that will be used.
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

            logger.info('  Has been projected from {} to USA_Albers_Equal_Area_Conic:'.format(CLIP_PROJECTION))
            logger.info('    {}'.format(tif_file_path))

        else:
            gdal.Warp(str(file_full_output),
                      str(file_full_input),
                      format='GTiff',
                      xRes=CELL_SIZE_X,
                      yRes=CELL_SIZE_Y,
                      srcSRS=CLIP_PROJECTION,
                      dstSRS=CALCULATE_STATS_PROJECTION,
                      resampleAlg='bilinear',
                      dstNodata=NULL_VAL)

            logger.info('  Projected to {}:'.format(CLIP_PROJECTION))

        # Delete the original projected clipped file.
        file_full_input.unlink()

        # Writes the projection information to the log file.
        ds = gdal.Open(str(file_full_output))
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        datum = srs.GetAttrValue('GEOGCS')

        if srs.IsProjected:
            proj_name = srs.GetAttrValue('AUTHORITY')
            proj_num = srs.GetAttrValue('AUTHORITY', 1)
            logger.info("  Has projection {}:{} and datum {}:".format(proj_name, proj_num, datum))
            logger.info("    {}".format(file_full_output))
        else:
            logger.info("  Has projection {} and datum {}:".format(prj, datum))
            logger.info("    {}:".format(file_full_output))

        logger.info('  Successfully assigned projection:')
        logger.info('    from: {}'.format(tif_file_path))
        logger.info('      to: {}'.format(file_full_output))
    else:
        logger.warning("  Does not start with 'Clip_' and will not be projected:")
        logger.warning("    {}".format(tif_file_path))

    return


def snow_coverage(tif_file_path: Path, folder_output: Path) -> None:
    """
    Create binary .tif raster indicating snow coverage.
    If a pixel in the input file is > 0 (there is snow on the ground) then the new raster's pixel value is assigned '1'.
    If a pixel in the input raster is 0 or a null value (there is no snow on the ground),
    then the new raster's pixel value is assigned '0'.
    The output raster is used to calculate the percent of daily snow coverage for each basin.
    tif_file_path: daily SNODAS SWE .tif raster, with name similar to 'SNODAS_SWE_ClipAndProj_YYYYMMDD.tif'
    folder_output: full pathname to the folder where the newly created binary snow cover raster is stored
    """

    logger = logging.getLogger(__name__)
    logger.info('Start creating snow coverage for {}'.format(tif_file_path))

    # Check for projected SNODAS rasters.
    if str(tif_file_path.name).startswith('SNODAS_SWE_ClipAndProj_'):

        # Set name of snow cover .tif file, something like:
        #   SNODAS_SnowCover_ClipAndProj_YYYYMMDD.tif
        snow_file = 'SNODAS_SnowCover_ClipAndProj_' + tif_file_path.name[23:]

        # Set full pathname variables for input into later raster calculator options.
        file_full_input = tif_file_path
        file_full_output_snow = folder_output / snow_file

        # Check for previous processing of file.
        if Path(file_full_input).exists():
            logger.info('  {} has been previously created. Overwriting.'.format(snow_file))

        # Create QGS object raster layer for input.
        logger.info('  Creating a QGS raster object layer for: {}'.format(tif_file_path))
        raster_layer = QgsRasterLayer(str(file_full_input), '{}'.format(tif_file_path))

        # Check for valid file within QGS environment.
        if raster_layer.isValid():

            # Set name (without extension) for input into the raster calculator expression.
            # '@1' means the calculation occurs on band 1 of the raster.
            raster_input = tif_file_path.name[0:31]
            raster_calc_name = raster_input + '@1'

            # Set variables for raster calculator options/settings.
            # See`: http://gis.stackexchange.com/questions/141659/qgis-from-console-raster-algebra
            resulting_layer = QgsRasterCalculatorEntry()
            resulting_layer.ref = raster_calc_name
            resulting_layer.raster = raster_layer
            resulting_layer.bandNumber = 1
            entries = [resulting_layer]

            # Set raster calculator options/settings (expression, output path, output type, output extent,
            # output width, output height, entries, context).
            # The TranformContext is needed to use the most up-to-date.
            context = QgsCoordinateTransformContext()
            calc = QgsRasterCalculator('({})>0'.format(raster_calc_name), '{}'.format(file_full_output_snow), 'GTiff',
                                       raster_layer.extent(), raster_layer.width(), raster_layer.height(), entries,
                                       context)

            # Begin calculation.
            calc.processCalculation()

            logger.info('  Snow calculations complete for: {}'.format(file_full_output_snow))

        else:
            logger.warning('  Not a valid object raster layer: {}'.format(tif_file_path))
    else:
        logger.warning("  File does not start with 'SNODAS_SWE_ClipAndProj_'. No raster calculation took place.".format(
            tif_file_path))


def create_empty_csv_files(tif_file_path: Path, boundaries_file_path: Path,
                           csv_by_date_folder: Path, csv_by_basin_folder: Path) -> None:
    """
    Create empty csv files for output - both by date and by basin.
    The empty csv files have a header row with each column represented by a different field name
    (refer to 'fieldnames' section of the function for actual fieldnames).
    Csv files by date contain one .csv file for each date and is titled 'SnowpackStatisticsByDate_YYYYMMDD.csv'.
    Each byDate file contains the zonal stats for each basin on that date.
    Csv files by basin contain one .csv file for each watershed basin & is titled 'SnowpackStatisticsByBasin_BasinId'.
    Each byBasin file contains the zonal stats for that basin for each date that has been processed.
    tif_file_path: daily .tif file to be processed with zonal statistics (has previously been clipped and projected)
    boundaries_file_file: shapefile of basin boundaries (these boundaries are used as the polygons in the
        zonal stats calculations)
    csv_by_date: full pathname of folder containing the results by date (.csv file)
    csv_by_basin: full pathname of folder containing the results by basin (.csv file)
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)
    logger.info('Start creating empty csv files for: {}'.format(tif_file_path))

    # Create QGS object vector layer for the basins.
    basins_layer = QgsVectorLayer(str(boundaries_file_path), 'Reprojected Basins', 'ogr')

    # Check to determine if the shapefile is valid as an object.
    # If this test shows that the shapefile is not a valid vector file,
    # the script does not run the zonal statistic processing (located in the 'else' block of code).
    # If the user gets the following error message, it is important to address the initialization of the QGIS resources.
    if not basins_layer.isValid():
        logger.warning('  Basin boundary shapefile is not a valid QGS object layer.')
    else:
        # Get the current directory.
        curr_dir = Path.cwd()

        # Retrieve date of current file.
        # Filename: 'SNODAS_SWE_ClipAndProj_YYYYMMDD'.
        # File[22:30] pulls the 'YYYYMMDD' section.
        date_name = tif_file_path.name[23:31]

        # Define fieldnames for output .csv files. These MUST match the keys of the dictionaries.
        # Fieldnames make up the header row of the .csv output files.
        # The column headers of the .csv files are in sequential order as laid out in the fieldnames list.
        fieldnames = [
            'Date_YYYYMMDD',
            ID_FIELD_NAME,
            'LOCAL_NAME',
            'SNODAS_SWE_Mean_in',
            'SNODAS_SWE_Mean_mm',
            'SNODAS_EffectiveArea_sqmi',
            'SNODAS_SWE_Volume_acft',
            'SNODAS_SWE_Volume_1WeekChange_acft',
            'SNODAS_SnowCover_percent',
            'Updated_Timestamp'
        ]

        if CALCULATE_SWE_MAX.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_Max_in', 'SNODAS_SWE_Max_mm'])

        if CALCULATE_SWE_MIN.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_Min_in', 'SNODAS_SWE_Min_mm'])

        if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_StdDev_in', 'SNODAS_SWE_StdDev_mm'])

        # Create string variable for name of .csv output file by date. Name: SnowpackStatisticsByDate_YYYYMMDD.csv.
        results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'
        results_date_path = csv_by_date_folder / results_date

        if not results_date_path.exists():
            # Set directory where the output .csv daily files are stored (by date).
            os.chdir(csv_by_date_folder)

            logger.info('  Creating result CSV: {}'.format(results_date_path))

            # Create .csv file with the appropriate fieldnames as the info in the header row (by date).
            with open(results_date, 'w') as csv_file:
                if os_util.is_linux_os():
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",")
                else:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",", lineterminator='\n')
                writer.writeheader()

        # Iterate through each basin of the basin boundary shapefile.
        for feature in basins_layer.getFeatures():

            # Create str variable for the name of output .csv file byBasin.
            # Name: SnowpackStatisticsByBasin_LOCALID.csv.
            results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv'
            results_basin_path = csv_by_basin_folder / results_basin

            # Check to see if the output file has already been created.
            # If so, the script moves onto the raster processing.
            # If not, a .csv file is created with the appropriate fieldnames as the info in the header row (by basin).
            if not results_basin_path.exists():

                # Set directory where the output .csv daily files are stored (by basin).
                os.chdir(csv_by_basin_folder)

                logger.info('  Creating CSV file: {}'.format(results_basin_path))

                # Create .csv file with appropriate fieldnames as the header row (by date).
                with open(results_basin, 'w') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",")
                    writer.writeheader()

                # Return directory back to original.
                os.chdir(curr_dir)

    logger.info('  Finished creating empty csv files for: {}'.format(tif_file_path))


def delete_by_basin_csv_rows_for_date(tif_file_path: Path, boundaries_file_path: Path,
                                      csv_by_basin_folder: Path) -> None:
    """
    Check to see if date has already been processed.
    If so, iterate through by basin csv file and only write rows to new csv file that do not start with the date.
    This results in removing the current day's data from all basin files so that no duplicate occurs when the
    statistics are calculated.
    tif_file_path: daily .tif file  to be processed with zonal statistics (clipped, projected)
    boundaries_file_path: shapefile of basin boundaries (these boundaries are used as the polygons
        in the zonal stats calculations)
    csv_by_basin_folder: full pathname of folder containing the results by basin (.csv file)
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)
    logger.info('Start deleting repeated rows in ByBasin file for: {}'.format(tif_file_path))

    # Create a QGS object vector layer for the boundaries.
    basins_layer = QgsVectorLayer(str(boundaries_file_path), 'Reprojected Basins', 'ogr')

    # Check to determine if the shapefile is valid as an object.
    # If this test shows that the shapefile is not a valid vector file,
    # the script does not run the zonal statistic processing (located in the 'else' block of code).
    # If the user gets the  following error message,
    # it is important to address the initialization of the QGIS resources.
    if not basins_layer.isValid():
        logger.warning('  Basin boundary shapefile is not a valid QGS object layer.')
    else:
        # Retrieve date of current file.
        # File name is 'SNODAS_SWE_ClipAndProj_YYYYMMDD'.
        # File[22:30] is pulling the 'YYYYMMDD' section.
        date_name = tif_file_path.name[23:31]

        # Iterate through each basin of the basin boundary shapefile.
        for feature in basins_layer.getFeatures():
            # Create string variable to be used as the name for the .csv output file (by basin):
            # - this is just a template string populated from the first feature
            results_basin_file = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv'
            break

        # Set directory where the output .csv daily files are stored (by basin).
        os.chdir(csv_by_basin_folder)
        # Check to see if the daily raster has already been processed:
        # - the first CSV file is read and put into file_contents
        # - then it is immediately closed so there are no issues trying to close it later
        # - this assumes that the first basin is successfully processed and can be relied on for the check
        results_basin_path = csv_by_basin_folder / results_basin_file
        file_handler = open(results_basin_path)
        # Read the entire file into 'file_contents'.
        file_contents = file_handler.read()
        file_handler.close()

        need_to_edit = False

        # TODO smalers 2023-04-25 not sure that the check on extension is needed with the current code:
        # - maybe was put in to guard against some unexpected behavior?
        if date_name in file_contents and str(tif_file_path).endswith('.tif'):
            # Found the tif_file_path date in the file so need to edit
            need_to_edit = True
            logger.info('  Date {} appears to have been previously been processed based on check of:')
            logger.info('    {}'.format(results_basin_path))
            logger.info("  Removing data for this date from all 'ByBasin' csv files so new results can be added.")
        if '\n\n' in file_contents:
            # Not sure why blank lines are in the csv.
            logger.info('  Found blank lines so need to edit to remove:')
            logger.info('    {}'.format(results_basin_path))
            need_to_edit = True
        if '\r\n\r\n' in file_contents:
            # Not sure why blank lines are in the csv.
            logger.info('  Found blank lines so need to edit to remove:')
            logger.info('    {}'.format(results_basin_path))
            need_to_edit = True

        if need_to_edit:

            # Iterate through each basin of the basin boundary shapefile.
            for feature in basins_layer.getFeatures():

                # Create string variable to be used as the name for the input and output .csv file (by basin).
                results_basin_orig_path = csv_by_basin_folder / \
                                          ('SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv')
                results_basin_edit_path = csv_by_basin_folder / \
                                          ('SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + 'edit.csv')

                logger.info('  Removing {} rows:'.format(date_name))
                logger.info('    read from: {}'.format(results_basin_orig_path))
                logger.info('      save to: {}'.format(results_basin_edit_path))

                # Open input_file and output_file files. Input will be read and output_file will be written.
                input_file = open(results_basin_orig_path, 'r')
                output_file = open(results_basin_edit_path, 'w')

                # If the first column in the input_file row is 'tif_file_path' date,
                # the row is not written to the new file.
                writer = csv.writer(output_file)
                for row in csv.reader(input_file):
                    if len(row) == 0:
                        # Empty row, don't write.
                        continue
                    else:
                        if row[0] != date_name:
                            writer.writerow(row)
                input_file.close()
                output_file.close()

                # Delete original, now inaccurate, csv ByBasin file.
                try:
                    results_basin_orig_path.unlink()
                except OSError as e:
                    logger.error('  Error deleting file: {}'.format(results_basin_orig_path))
                    logger.error('  Exception: {}'.format(e))

                # Rename the new edited csv ByBasin file to its original name of SnowpackStatisticsByBasin_ +
                # feature[ID_FIELD_NAME] + '.csv'
                Path(results_basin_edit_path).rename(results_basin_orig_path)

    logger.info('  Finished {}'.format(tif_file_path))


def zip_shapefile(shp_file_path: Path, csv_by_date_folder: Path, delete_original: str) -> None:
    """
    Code block from http://emilsarcpython.blogspot.com/2015/10/zipping-shapefiles-with-python.html
    List of file extensions included in the shapefile.
    shp_file_path: the output shapefile (any extension). All other extensions will be included by means of the function.
    csv_by_date_folder: full pathname of folder containing the results by date (.csv files, GeoJSON, and shapefiles)
    delete_original: Boolean string to determine if the original unzipped shapefile files should be deleted.
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    extensions = [
        '.shx',
        '.shp',
        '.qpj',
        '.prj',
        '.dbf',
        '.cpg'
    ]

    # Define naming conventions.
    # Get the file name without the extension.
    in_name = shp_file_path.stem
    file_to_zip = csv_by_date_folder / (in_name + '.zip')
    # The third argument for zipfile - ZIP_DEFLATED - is what actually compresses the file.
    # Otherwise, the file is essentially copied.
    zip_file = zipfile.ZipFile(str(file_to_zip), 'w', zipfile.ZIP_DEFLATED)

    # Empty list to store files to delete.
    files_to_delete = []

    for fl in os.listdir(csv_by_date_folder):
        for extension in extensions:
            if fl == (in_name + extension):
                # Get full pathname of file.
                in_file = csv_by_date_folder / fl
                files_to_delete += [str(in_file)]
                zip_file.write(str(in_file), fl)
                break
    zip_file.close()

    # Delete unzipped shapefile files, if configured.
    if delete_original.upper() == 'TRUE':
        for fl in files_to_delete:
            Path(fl).unlink()


def z_stat_and_export(tif_file_path: Path, boundaries_file_path: Path,
                      csv_by_basin_folder: Path, csv_by_date_folder: Path,
                      clip_folder: Path, snow_cover_folder: Path,
                      today_date: date, timestamp: str, output_crs: str) -> None:
    """
    Calculate zonal statistics for basin boundary shapefile and the current SNODAS file.
    The zonal stats export to both the byDate and the byBasin csv files.
    A daily shapefile and geoJSON is also exported.
    tif_file_path: daily raster .tif SNODAS file that is to be processed in the zonal statistics tool
        (should have previously been clipped and projected)
    boundaries_file_path: the basin boundary shapefile (used as the zone dataset for the zonal statistics calculations)
    csv_by_date_folder: full pathname to the folder containing results by date (.csv file).
        Shapefile and GeoJSON saved here.
    csv_by_basin_folder: full pathname to the folder containing results by basin (.csv file)
    clip_folder: full pathname to the folder containing all daily clipped, projected .tif SNODAS rasters
    snow_cover_folder: full pathname to the folder containing all binary snow coverage rasters
    today_date: date of processed SNODAS data
    timestamp: the download timestamp in datetime format (returned in download_snodas function)
    output_crs: the desired projection of the output shapefile and GeoJSON (configured in configuration file),
        for example "EPSG:4326"
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)

    logger.info('Start processing zonal statistics by basin for:')
    logger.info('  {}'.format(tif_file_path))

    # Create empty dictionary to hold the zonal statistic outputs before they are written to the .csv files.
    # Shapefiles have a limited number of fields available in the attribute table so the statistics must be calculated,
    # exported and then deleted from the shapefile.
    d = {}

    # Hold current directory in a variable, curr_dir, to be called at the end of the script.
    curr_dir = Path.cwd()

    # Determine the date for current file:
    # - file example: SNODAS_SWE_ClipAndProj_YYYYMMDD.tif
    # - file name using range [23:31]: YYYYMMDD
    date_name = tif_file_path.name[23:31]

    # Define fieldnames for output .csv files (the header row):
    # - these MUST match the keys of the dictionaries
    # - the column headers of the .csv files are in sequential order as displayed in the fieldnames list
    # - the LOCAL_NAME will be defaulted to ID_FIELD_NAME if not found in data
    fieldnames = [
        'Date_YYYYMMDD',
        ID_FIELD_NAME,
        'LOCAL_NAME',
        'SNODAS_SWE_Mean_in',
        'SNODAS_SWE_Mean_mm',
        'SNODAS_EffectiveArea_sqmi',
        'SNODAS_SWE_Volume_acft',
        'SNODAS_SWE_Volume_1WeekChange_acft',
        'SNODAS_SnowCover_percent',
        'Updated_Timestamp'
    ]

    if CALCULATE_SWE_MAX.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_Max_in', 'SNODAS_SWE_Max_mm'])

    if CALCULATE_SWE_MIN.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_Min_in', 'SNODAS_SWE_Min_mm'])

    if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_StdDev_in', 'SNODAS_SWE_StdDev_mm'])

    # Create a layer for the input shapefile (for example, the Colorado River Basin projected shapefile).
    vector_layer = QgsVectorLayer(str(boundaries_file_path), 'Reprojected Basins', 'ogr')

    # Check validity of shapefile as a QGS object. If this test shows that the vector is not a valid vector file,
    # the script does not run the zonal statistic processing (located in the 'else' block of code).
    # Address the initialization of the QGIS resources if received following error message.
    if not vector_layer.isValid():
        logger.warning('  Vector shapefile is not a valid QGS object layer: {}'.format(boundaries_file_path))

    else:
        # Check for extension .tif.
        if str(tif_file_path).upper().endswith('.TIF'):
            # Set conditional variables so they are defined.
            e_min = None
            e_swe_min_in = None
            e_max = None
            e_swe_max_in = None
            e_std = None
            e_swe_s_dev_in = None

            # Set directory to the directory where the output .csv daily files are contained (by basin).
            os.chdir(csv_by_basin_folder)

            # Create date value of the working dictionary.
            d['Date_YYYYMMDD'] = date_name

            logger.info('  Start processing zonal statistics.')

            # Retrieve the date for 7 days before today and convert to string format (YYYYMMDD).
            week_ago_date = today_date - timedelta(days=7)
            week_ago_str = format_date_yyyymmdd(week_ago_date)

            # Create string variable with week_ago_str to be used as the title for the .csv output file (by bate).
            results_date_csv = 'SnowpackStatisticsByDate_' + week_ago_str + '.csv'
            results_date_csv_full_path = csv_by_date_folder / results_date_csv

            # Set full pathname of rasters for later input into the zonal stat tool.
            snow_file = 'SNODAS_SnowCover_ClipAndProj_' + date_name + '.tif'
            raster_path_h = clip_folder / tif_file_path.name
            raster_path_s = snow_cover_folder / snow_file

            # Open vector_layer for editing.
            vector_layer.startEditing()

            # Create the raster layer, needed by QgsZonalStatistics.
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

            # Set raster calculator expression to populate the 'Mean' field. This field calculates mm.
            # Change the QGSExpression if different units are desired.
            e_mean = QgsExpression('SWE_mean')

            # Set the raster calculator expression to populate the 'SWEMean_in' field.
            # 25.4 is the number of millimeters in an inch.
            e_swe_mean_in = QgsExpression('SWE_mean / 25.4')

            if CALCULATE_SWE_MIN.upper() == 'TRUE':
                # Set input object options for the zonal stat tool (Minimum).
                zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "SWE_", 1, QgsZonalStatistics.Min)
                # Call zonal stat tool to start processing.
                zonal_stats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Min' field.
                e_min = QgsExpression('SWE_min')

                # Set the raster calculator expression to populate the 'SWEMin_in' field.
                e_swe_min_in = QgsExpression('SWE_min  / 25.4')

            if CALCULATE_SWE_MAX.upper() == 'TRUE':
                # Set input object options for zonal stat tool (Maximum).
                zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "SWE_", 1, QgsZonalStatistics.Max)
                # Call zonal stat tool to start processing.
                zonal_stats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Max' field.
                e_max = QgsExpression('SWE_max')

                # Set the raster calculator expression to populate the 'SWEMax_in' field.
                e_swe_max_in = QgsExpression('SWE_max / 25.4')

            if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
                # Set input object options for the zonal stat tool (Standard Deviation).
                zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "SWE_", 1, QgsZonalStatistics.StDev)
                # Call zonal stat tool to start processing.
                zonal_stats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Std Dev' field.
                e_std = QgsExpression('SWE_stdev')

                # Set the raster calculator expression to populate the 'SWESDev_in' field.
                e_swe_s_dev_in = QgsExpression('SWE_stdev / 25.4')

            # Set input object options for the zonal stat tool (Count of Total Basin Cells).
            zonal_stats = QgsZonalStatistics(vector_layer, raster_layer, "Cell", 1, QgsZonalStatistics.Count)
            # Call zonal stat tool to start processing.
            zonal_stats.calculateStatistics(None)

            # Set input object options for the zonal stat tool (Sum of snow cover raster).
            zonal_stats = QgsZonalStatistics(vector_layer, snow_raster_layer, "SCover", 1, QgsZonalStatistics.Sum)
            # Call zonal stat tool to start processing.
            zonal_stats.calculateStatistics(None)

            # Update changes to fields of shapefile.
            vector_layer.updateFields()

            # Set raster calculator expression to populate the 'Area_sqmi' field.
            # The area of the cell (square meters) multiplied by the count of basin cells.
            # There are 2589988.10 sq meters in 1 sq mile.
            a = QgsExpression('({}) * ({}) * Cellcount / 2589988.10'.format(CELL_SIZE_X, CELL_SIZE_Y))

            # Set raster calculator expression  to populate the 'SCover_pct' field.
            # Sum of basin cells covered by snow divided by total count of basin cells.
            e = QgsExpression('SCoversum / Cellcount * 100')

            # Set raster calculator expression to populate 'SWEVol_af' field.
            # Mean SWE (mm) multiplied by effective area 'Area_sqmi' divided by 304.8.
            # There are 640 acres in 1 square mile. There are 304.8 mm in 1 foot.
            v = QgsExpression('Area_sqmi * SWE_mean * 640 / 304.8')

            # Create an empty array to hold the components of the zonal stats calculations dictionary.
            # This array is copied to the .csv output file and then erased only to be filled again
            # with the next daily raster's dictionary calculations (by date).
            # There are two arrays in this function, array_date and array_basin.
            # The main difference is that the array_basin only holds one dictionary at a time before it writes
            # to a .csv file (one dictionary per basin and then the information is deleted).
            # The array_date holds multiple dictionaries at one time (one dictionary per basin).
            # The information in the array is only deleted after the date changes).
            array_date = []

            # Set directory to the directory where the output .csv daily files are stored (by basin).
            os.chdir(csv_by_basin_folder)

            # Define output coordinate reference system.
            if output_crs.find(":") >= 0:
                # Use as is.
                output_crs = output_crs
            else:
                # Assume EPSG.
                output_crs = "EPSG:" + output_crs

            # Iterate through each basin of the basin boundary shapefile.
            for feature in vector_layer.getFeatures():

                # Check to see if the SNODAS data has already been processed for the week_ago date.
                os.chdir(csv_by_date_folder)

                # If so, get the volume value from last week for each basin.
                # The for loop iterates over the basins and calculates the one-week-change in volume statistic.
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
                            logger.warning('The DictReader is empty.')

                    # Set raster calculator expression to populate 'SWEVolC_af' field.
                    # 'SWEVol_af' from today ('SWEVol_af' from 7 days ago).
                    c = QgsExpression('SWEVol_af - {}'.format(week_ago_value))

                else:
                    c = QgsExpression('noData')

                os.chdir(csv_by_basin_folder)

                # Create string variable to be used as the title for the output .csv file (by basin).
                results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_FIELD_NAME] + '.csv'

                # Create dictionary that sets rounding properties (to what decimal place) for each field.
                # Key is the field name.
                # Value[0] is the preset raster calculator expression.
                # Value[1] is the number of decimals that the field is rounded to.
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
                    # Both the context and the scope need to be created for each evaluation.
                    # If done in the feature for loop, a segmentation fault occurs.
                    # If done outside the feature for-loop, a double free takes place.
                    context = QgsExpressionContext()
                    scope = QgsExpressionContextScope()
                    scope.setFeature(feature)
                    context.appendScope(scope)

                    expression = value[0]
                    feature[key] = expression.evaluate(context)

                # Round the raster calculations to appropriate decimal places (defined in rounding dictionary).
                # All rounding is completed AFTER all calculations have been completed.
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
                    try:
                        d[key] = feature[value[0]]
                    except KeyError:
                        # LOCAL_NAME may not be found if the input basin boundary layer is minimal and only has the
                        # [BasinBoundaryShapefile].basin_id.
                        if key == 'LOCAL_NAME':
                            # Just use the same as the ID.
                            d[key] = feature[ID_FIELD_NAME]

                # Append current dictionary to the empty basin array.
                # This array is exported to the output .csv file at the end of this 'for' loop.
                array_basin.append(d.copy())

                # Append current dictionary to the empty basin array.
                # This array is exported to the output .csv file outside of this 'for' loop.
                array_date.append(d.copy())

                # Export the daily date array to a .csv file. Overwrite the .csv file if it already exists.
                # See: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
                with open(results_basin, 'a') as csv_file:
                    csv_writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=fieldnames)
                    for row in array_basin:
                        csv_writer.writerow(row)
                # Read and sort every line but the header.
                with open(results_basin, 'r') as full_csv_file:
                    csv_file_contents = list(full_csv_file)
                    csv_file_contents[1:] = sorted(csv_file_contents[1:])
                # Write the sorted list to the file.
                with open(results_basin, 'w') as sorted_csv_file:
                    for item in csv_file_contents:
                        sorted_csv_file.write('{}'.format(item))

            # Close edits and save changes to the shapefile.
            vector_layer.commitChanges()

            # Delete attribute fields of the shapefile used in the calculations
            # but not important for export to final product shapefile.
            cell_count_index = vector_layer.dataProvider().fieldNameIndex('CellCount')
            s_cover_sum_index = vector_layer.dataProvider().fieldNameIndex('SCoversum')
            vector_layer.dataProvider().deleteAttributes([cell_count_index, s_cover_sum_index])

            # Update shapefile with its newly-named attribute fields.
            vector_layer.updateFields()

            # Create daily shapefile and daily geoJSON.
            shapefile_name = 'SnowpackStatisticsByDate_' + date_name + '.shp'
            geojson_name = 'SnowpackStatisticsByDate_' + date_name + '.geojson'
            shapefile_name_full = csv_by_date_folder / shapefile_name
            geojson_name_full = csv_by_date_folder / geojson_name

            # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name.
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

            # Write the GeoJSON file.
            # - IGNORE `Unexpected Argument` error for layerOptions. This value is appropriate and functions properly.
            # - irritatingly, must request the GeoJSON 2 format using RFC7946=YES
            layer_options = [
                'COORDINATE_PRECISION={}'.format(GEOJSON_PRECISION),
                'RFC7946=YES',
                'WRITE_NAME=NO'
            ]
            QgsVectorFileWriter.writeAsVectorFormat(layer=vector_layer,
                                                    fileName=str(geojson_name_full),
                                                    fileEncoding="utf-8",
                                                    destCRS=QgsCoordinateReferenceSystem(output_crs),
                                                    driverName="GeoJSON",
                                                    layerOptions=layer_options)

            # Write the shapefile.
            QgsVectorFileWriter.writeAsVectorFormat(layer=vector_layer,
                                                    fileName=str(shapefile_name_full),
                                                    fileEncoding="utf-8",
                                                    destCRS=QgsCoordinateReferenceSystem(output_crs),
                                                    driverName="ESRI Shapefile")

            # Change fieldnames of output GeoJSON file. Envelop GeoJSON file as a QGS object vector layer.
            # new_name = geojson_name.replace(".geojson", "_intermediate.geojson")
            # int_geojson_name_full = csv_by_date / new_name
            # geojson_name_full.rename(int_geojson_name_full)

            vector_file_geojson = QgsVectorLayer(str(geojson_name_full), 'GeoJsonStatistics', 'ogr')

            # Rename attribute fields of GeoJSON.
            if not os_util.is_linux_os():

                # Open vector_file for editing.
                vector_file_geojson.startEditing()

                # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name.
                fields = {
                    'SWEMean_mm': 'SNODAS_SWE_Mean_mm',
                    'SWEVolC_af': 'SNODAS_SWE_Volume_1WeekChange_acft',
                    'SWEMean_in': 'SNODAS_SWE_Mean_in',
                    'Area_sqmi': 'SNODAS_EffectiveArea_sqmi',
                    'SWEVol_af': 'SNODAS_SWE_Volume_acft',
                    'SCover_pct': 'SNODAS_SnowCover_percent'
                }

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
                # (with shapefile fieldnames).
                vector_file_geojson.updateFields()
                commit_status = vector_file_geojson.commitChanges()
                if commit_status:
                    logger.info('Layer changes committed.')
                else:
                    logger.warning('Layer commit failed.')

            # Write the GeoJSON file.
            # - IGNORE `Unexpected Argument` error for layerOptions. This value is appropriate and functions properly.
            # - irritatingly, must request the GeoJSON 2 format
            layer_options = [
                'COORDINATE_PRECISION={}'.format(GEOJSON_PRECISION),
                'RFC7946=YES',
                'WRITE_NAME=NO'
            ]
            QgsVectorFileWriter.writeAsVectorFormat(layer=vector_file_geojson,
                                                    fileName=str(geojson_name_full),
                                                    fileEncoding="utf-8",
                                                    destCRS=QgsCoordinateReferenceSystem(output_crs),
                                                    driverName="GeoJSON",
                                                    layerOptions=layer_options)

            # Rename attribute fields of GeoJSON.
            if os_util.is_linux_os():
                change_field_names(str(geojson_name_full))

            if GEOJSON_ZIP.upper() == 'TRUE':
                with zipfile.ZipFile(str(geojson_name_full) + '.zip', 'w', zipfile.ZIP_DEFLATED) as my_zip:
                    my_zip.write(geojson_name_full)
                # Delete the uncompressed geojson file.
                geojson_name_full.unlink()

            # Close the vector_file_geojson so that the vector_layer can open.
            # print('int_geojson_name_full: {}'.format(int_geojson_name_full))
            # int_geojson_name_full.unlink()
            vector_layer.startEditing()

            # Delete attribute fields of the shapefile related to the daily calculated zonal statistics.
            field_names = [
                'SWEMean_mm',
                'SCover_pct',
                'SWEMean_in',
                'Area_sqmi',
                'SWEVolC_af',
                'SWEVol_af'
            ]
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

            # Create a string variable to be used as the title for the .csv output file (by date).
            results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'

            # Set directory to the directory where the output .csv daily files are contained (by date).
            os.chdir(csv_by_date_folder)

            # Update text file, ListOfDates.txt, with list of dates represented by csv files in the ByDate folder.
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
            # See: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
            with open(results_date, 'a') as csv_file:
                csv_writer = csv.DictWriter(csv_file, delimiter=",", fieldnames=fieldnames)
                for row in array_date:
                    csv_writer.writerow(row)

            # Get most recent processed SNODAS date & make a copy called 'SnowpackStatisticsByDate_LatestDate.csv'
            # and 'SnowpackStatisticsByDate_LatestDate.geojson' and 'SnowpackStatisticsByDate_LatestDate.zip/.shp'.
            most_recent_date = str(max(array_recent_date))
            src = 'SnowpackStatisticsByDate_' + most_recent_date + '.csv'
            dst = 'SnowpackStatisticsByDate_LatestDate.csv'
            copyfile(str(csv_by_date_folder / src), str(csv_by_date_folder / dst))
            src = 'SnowpackStatisticsByDate_' + most_recent_date + '.geojson'
            dst = 'SnowpackStatisticsByDate_LatestDate.geojson'
            copyfile(str(csv_by_date_folder / src), str(csv_by_date_folder / dst))
            # List of extensions referring to the output shapefile.
            ext_list = ['.cpg', '.dbf', '.prj', '.qpj', '.shp', '.shx']
            for item in ext_list:
                src = 'SnowpackStatisticsByDate_' + most_recent_date + item
                dst = 'SnowpackStatisticsByDate_LatestDate' + item
                if Path(src).exists():
                    copyfile(str(csv_by_date_folder / src), str(csv_by_date_folder / dst))

            # Return working directory back to its original setting before the script began.
            os.chdir(curr_dir)

            logger.info('  Saved zonal statistics to {} for: {}'.format(csv_by_basin_folder, tif_file_path))
            print("Zonal statistics for {} are complete. \n".format(date_name), file=sys.stderr)

        else:
            logger.info('  Zonal statistics were not processed because file is not a .tif:')
            logger.info('    {}:'.format(tif_file_path))


def create_snodas_swe_graphs() -> None:
    """
    Create, or update, the snowpack time series graphs from the by basin data.
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)

    # Refer to configuration file.
    # If true, update the time series graphs weekly.
    # If false, update the TS graphs daily.
    if TSGRAPH_WEEKLY_UPDATE.upper() == 'TRUE':
    
        # Check that today is the set weekday to update the time series graphs.
        if str(datetime.today().weekday()) == str(TSGRAPH_WEEKLY_UPDATE_DATE):
    
            print('Running TSTool file to create the weekly SNODAS SWE graphs. This could take a couple of minutes.',
                  file=sys.stderr)
            logger.info('Running TSTool file to create the weekly SNODAS Time Series graphs. TSTool file pathname:')
            logger.info('  {}'.format(TSTOOL_SNODAS_GRAPHS_PATH))
    
            # Run the TSTool command file, 'TSTOOL_SNODAS_GRAPHS_PATH', in the background.
            # Wait for the subprocess to complete before continuing.
            try:
                with subprocess.Popen([TSTOOL_INSTALL_PATH, '-commands', TSTOOL_SNODAS_GRAPHS_PATH]) as _:
                    pass
            except OSError:
                print('Skipping TSTool graph creation.', file=sys.stderr)
                return
                # error_message = 'Error reading the TSTool executable file: {}'.format(bad_file)
                # print(error_message)
                # logger.error(error_message)
                # exit(1)
    
            print('Weekly SNODAS Time Series Graphs have been created.', file=sys.stderr)
    else:
        print('Running TSTool file to create the daily SNODAS SWE graphs. This could take up to 5 minutes.',
              file=sys.stderr)
        logger.info('Running TSTool file to create the daily SNODAS Time Series graphs. TSTool file pathname:')
        logger.info('  {}'.format(TSTOOL_SNODAS_GRAPHS_PATH))
    
        # Run the TSTool command file, 'TSTOOL_SNODAS_GRAPHS_PATH', in the background.
        # Wait for the subprocess to complete before continuing.
        try:
            with subprocess.Popen([TSTOOL_INSTALL_PATH, '-commands', TSTOOL_SNODAS_GRAPHS_PATH]) as _:
                pass
        except OSError:
            print('Skipping TSTool graph creation.', file=sys.stderr)
            return
            # error_message = 'Error reading the TSTool executable file: {}'.format(bad_file)
            # print(error_message)
            # logger.error(error_message)
            # exit(1)
        print('Daily SNODAS Time Series Graphs have been created.', file=sys.stderr)


def push_to_aws() -> None:
    """
    Runs batch file to push the newly-updated files to Amazon Web Services such as OWF cloud storage.
    The specifics are configured within the batch file, AWS_BATCH_PATH.
    """

    # Initialize this module (if it has not already been done) so that configuration data are available.
    init_snodas_util()

    logger = logging.getLogger(__name__)
    print('Pushing files to Amazon Web Services S3.', file=sys.stderr)
    logger.info('Pushing files to Amazon Web Services S3 with configuration from {}.'.format(AWS_BATCH_PATH))

    # Call batch file, AWS_BATCH_PATH, to push files up to Amazon Web Service.
    args = [AWS_BATCH_PATH]
    try:
        with subprocess.Popen(args, cwd="C:\\Program Files\\Amazon\\AWSCLI") as _:
            pass
    except OSError as bad_file:
        error_message = 'Error pushing to AWS: {}\nConfirm the path to the AWS bash script and the' \
                        'current working directory keyword argument path are correct.'.format(bad_file)
        print(error_message, file=sys.stderr)
        logger.error(error_message)
        exit(1)
    logger.info('Files have been pushed to Amazon Web Services S3 by:')
    logger.info('  {}'.format(AWS_BATCH_PATH))


def push_to_gcp() -> None:
    """
    Runs shell script to push the newly updated files to a GCP bucket, such as State of Colorado server.
    The specifics are configured within the batch file, gcp_shell_script.
    """

    logger = logging.getLogger(__name__)

    script_location = "/var/opt/snodas-tools"
    gcp_shell_script = "/var/opt/snodas-tools/cloud/copyAllToGCPBucket.bash"

    print('Pushing files to Google Cloud Platform bucket given shell script ({}) specifics'.format(gcp_shell_script),
          file=sys.stderr)
    logger.info('Pushing files to Google Cloud Platform bucket given details from {}.'.format(gcp_shell_script))

    # Call shell script, gcp_shell_script, to push files up to GCP.
    os.chdir(script_location)
    try:
        with subprocess.Popen(['bash', gcp_shell_script]) as _:
            pass
    except OSError as bad_file:
        error_message = 'push_to_gcp: Error pushing to GCP: {}\nConfirm the path to the GCP bash script is correct.'\
            .format(bad_file)
        print(error_message, file=sys.stderr)
        logger.error(error_message)
        exit(1)

    logger.info('Files have been pushed toGoogle Cloud Platform bucket as designed by {}.'
                .format(gcp_shell_script))


def change_field_names(geojson_file: str) -> None:
    """
    Renames the attribute field names of the output GeoJSON file for each date.
    This function is only to be used in the Linux environment because the Windows environment already
    has a built-in attribute field editor within the QGIS software.
    When the built-in QGIS mechanism is run on the Linux machine the following error is printed.
    Error 6: AlterFieldDefn() not supported by this layer.

    This function will create a separate geojson file with the updated attribute fields.
    The original geojson will be deleted and the new geojson will be renamed to the original geojson name.

    Args:
        geojson_file: the full pathname to the GeoJSON file to be edited.

    Returns: None
    """

    # Get the text content of the original GeoJSON file.
    file_handler = open(geojson_file, 'r')
    geojson_content = file_handler.read()
    file_handler.close()
    # with open(geojson_file, 'r') as geojson:
    #     geojson_content = geojson.read()

    # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name.
    fields = {
        'SWEMean_mm': 'SNODAS_SWE_Mean_mm',
        'SWEVolC_af': 'SNODAS_SWE_Volume_1WeekChange_acft',
        'SWEMean_in': 'SNODAS_SWE_Mean_in',
        'Area_sqmi': 'SNODAS_EffectiveArea_sqmi',
        'SWEVol_af': 'SNODAS_SWE_Volume_acft',
        'SCover_pct': 'SNODAS_SnowCover_percent'
    }

    if CALCULATE_SWE_MIN.upper() == 'TRUE':
        fields.update({'SWEMin_mm': 'SNODAS_SWE_Min_mm', 'SWEMin_in': 'SNODAS_SWE_Min_in'})

    if CALCULATE_SWE_MAX.upper() == 'TRUE':
        fields.update({'SWEMax_mm': 'SNODAS_SWE_Max_mm', 'SWEMax_in': 'SNODAS_SWE_Max_in'})

    if CALCULATE_SWE_STD_DEV.upper() == 'TRUE':
        fields.update({'SWESDev_mm': 'SNODAS_SWE_StdDev_mm', 'SWESDev_in': 'SNODAS_SWE_StdDev_in'})

    # Replace the appropriate files.
    for key, value in fields.items():
        geojson_content = geojson_content.replace(key, value)

    # Create an intermediate GeoJSON file that has the same contents of the original GeoJSON
    # but with the new attribute names.
    geojson_int_path = geojson_file.replace('.geojson', '_temp.geojson')
    file_handler = open(geojson_file, 'w')
    file_handler.write(geojson_content)
    file_handler.close()
    # with open(geojson_int_path, 'w') as geojson_int:
    #     geojson_int.write(geojson_content)

    # Remove the original GeoJSON file and rename the intermediate GeoJSON file to the name of the original GeoJSON.
    # This file is removed when it is zipped.
    # Path(geojson_file).unlink()
    # os.rename(geojson_int_path, geojson_file)


def clean_duplicates_from_by_basin_csv(csv_basin_dir: Path) -> None:
    """
    Sometimes duplicate dates end up in the byBasin csv files.
    This function will make sure that the duplicates are removed.
    """

    logger = logging.getLogger(__name__)

    # Get a list of the csv files within the byBasin folder (full path names). **/* is for recursive globbing.
    csv_files_to_check =\
        [csv_basin_dir.joinpath(file) for file in csv_basin_dir.glob('**/*') if file.suffix == '.csv']

    # Iterate over the csv files to check for duplicates.
    for csv_full_path in csv_files_to_check:

        # Boolean to determine if there is a duplicate. False until proven true.
        duplicate_exists = False

        # Date seen keeps track of all the dates seen within the csv file.
        date_seen = []

        # Clean rows keeps track of all the csv rows that are not duplicates.
        clean_rows = []

        # Open the csv file.
        with open(csv_full_path, 'r') as csv_file:

            # Iterate over each row in the csv file.
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:

                # Get the date from the row.
                try:
                    date = row[0]
                except IndexError:
                    # Might be an empty row:
                    # - should fix so empty rows don't exist
                    logger.warning("  Need to fix empty row in: {}".format(csv_full_path))
                    continue

                # If the date has already been seen, the row is a duplicate
                # and should not be written to the new file.
                if date in date_seen:
                    duplicate_exists = True

                # If the date is unique, the row is not a duplicate and should be written to the new file.
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
