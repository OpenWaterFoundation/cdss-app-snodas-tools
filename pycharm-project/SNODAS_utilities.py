# Name: SNODAS_utilites.py
# Version: 1
# Author: Emma Giles
# Organization: Open Water Foundation
#
# Purpose: SNODAS_utilites.py contains the functions utilized within the SNODAS tools (SNODASDaily_Automated.py and
#   SNODASDaily_Interactive.py). Both scripts process zonal statistics of SNODAS raster datasets with respect to the
#   input vector shapefile (basin boundaries). The SNODAS tools were originally developed to calculate zonal statistics
#   of Colorado Basin boundaries.
#
#   Both scripts call the same functions defined in this SNODAS_utilities.py script. SNODASDaily_Automated.py
#   downloads the current date of SNODAS data and outputs the results in multiple geometries (geoJSON and shapefile)
#   and multiple .csv files (one .csv file for the processing date and one .csv file for EACH basin in the input
#   vector shapefile). SNODASDaily_Interactive.py processes historical dates of SNODAS data and outputs the results
#   in multiple geometries (geoJSON and shapefile) and multiple .csv files (one .csv file for the processing date and
#   one .csv file for EACH basin in the input vector shapefile).

# Import necessary modules
import ftplib, os, tarfile, gzip, gdal, csv, logging, configparser, glob, osr, zipfile, ogr
from subprocess import Popen
from logging.config import fileConfig
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsZonalStatistics
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsField
from qgis.core import QgsExpression, QgsVectorFileWriter, QgsCoordinateReferenceSystem
from PyQt4.QtCore import QVariant
from datetime import datetime, timedelta
from shutil import copy, copyfile

# Reads the configuration file to assign variables. Reference the following for code details:
# https://wiki.python.org/moin/ConfigParserExamples
Config = configparser.ConfigParser()
Configfile = "../SNODAS_Tools/config/SNODAS-Tools-Config.ini"
Config.read(Configfile)

# Create and configures logging file
fileConfig(Configfile)
logger = logging.getLogger('log02')

# Helper function to obtain option values of config file sections.
def config_section_map(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        dict1[option] = Config.get(section, option)
    return dict1

# Assigns the values from the configuration file to the python variables. See below for description of each
# variable obtained by the configuration file.
#
#   host: The SNODAS FTP site url to access the downloadable data.
#   username: The SNODAS FTP site username to access the downloadable data.
#   password: The SNODAS FTP site password to access the downloadable data.
#   SNODAS_FTP_folder: The folder pathname within the SNODAS FTP site that accesses the SNODAS masked datasets. The
#   masked datasets are SNODAS grids clipped to the contiguous U.S. boundary.
#   clip_projection: The EPSG projection code of the input basin extent shapefile. Defaulted to WGS84. The basin
#   extent shapefile is used to clip the national SNOADS grids to the clipped extent of the basin boundaries.
#   calculate_statistics_projection: The desired EPSG projection code of the final products (snow cover grid and 
#   clipped SNODAS grid). Defaulted to Albers Equal Area. 
#   ID_Field_Name: The field name of the basin boundary attribute table describing the identification of each basin.
#   The naming convention of the CSVByBasin result files use the ID_Field_Name.
#   null_value: The null values that SNODAS applies to the data's null value. Defaulted to -9999 but should be changed
#   if the null values provided by SNODAS are changed.
#   calculate_SWE_minimum: Daily zonal SWE minimum statistic will be calculated if this value is 'True'.
#   calculate_SWE_maximum: Daily zonal SWE maximum statistic will be calculated if this value is 'True'.
#   calculate_SWE_stdDev: Daily zonal SWE standard deviation statistic will be calculated if this value is 'True'.
#   cellsizeX: The spatial resolution of the SNODAS (calculate_statistics_projection) cells' x-axis (in meters).
#   cellsizeY: The spatial resolution of the SNODAS (calculate_statistics_projection) cells' y-axis (in meters).
#   root: The full pathname to the processedData folder.
#   geoJSON_precision: The number of decimal places (precision) used in the output GeoJSON geometry.
#   TsToolInstall: The full pathname to the TsTool program.
#   TsToolBatchFile: The full pathname to the TsTool Batch file responsible for creating the time-series graphs.


host = config_section_map("SNODAS_FTPSite")['host']
username = config_section_map("SNODAS_FTPSite")['username']
password = config_section_map("SNODAS_FTPSite")['password']
SNODAS_FTP_folder = config_section_map("SNODAS_FTPSite")['folder_path']
clip_projection = "EPSG:" + config_section_map("Projections")['datum_epsg']
calculate_statistics_projection = "EPSG:" + config_section_map("Projections")['calcstats_proj_epsg']
ID_Field_Name = config_section_map("BasinBoundaryShapefile")['basin_id_fieldname']
null_value = config_section_map("SNODAS_FTPSite")['null_value']
calculate_SWE_minimum = config_section_map("OptionalZonalStatistics")['calculate_swe_minimum']
calculate_SWE_maximum =  config_section_map("OptionalZonalStatistics")['calculate_swe_maximum']
calculate_SWE_stdDev =  config_section_map("OptionalZonalStatistics")['calculate_swe_standard_deviation']
cellsizeX = float(config_section_map("Projections")['calculate_cellsize_x'])
cellsizeY = float(config_section_map("Projections")['calculate_cellsize_y'])
root = config_section_map("Folders")['root_pathname']
geoJSON_precision = config_section_map("OutputLayers")['geojson_precision']
TsToolInstall = config_section_map("ProgramInstall")['tstool_pathname']
TsToolCreateTimeSeries = config_section_map("ProgramInstall")['tstool_create-snodas-graphs_pathname']
weekly_update = config_section_map("OutputLayers")['tsgraph_weekly_update']
weekly_update_date = config_section_map("OutputLayers")['tsgraph_weekly_update_date']
AWS_batch_file = config_section_map("ProgramInstall")['aws_batch_pathname']

# Get today's date ----------------------------------------------------------------------------------------------------
now = datetime.now()

# Downloading function ------------------------------------------------------------------------------------------------
def download_SNODAS(downloadDir, singleDate):
    """Access the SNODAS FTP site and download the .tar file of singleDate. The .tar file saves to the specified
    downloadDir folder.
    downloadDir: full path name to the location where the downloaded SNODAS rasters are stored
    singleDate: the date of interest in datetime format"""

    logger.info('download_SNODAS: Starting %s' % singleDate)

    # Code format for the following block of code in reference to:
    # http://www.informit.com/articles/article.aspx?p=686162&seqNum=7 and
    # http://stackoverflow.com/questions/5230966/python-ftp-download-all-files-in-directory
    # Connect to FTP server
    ftp = ftplib.FTP(host, username, password)

    logger.info('download_SNODAS: Connected to FTP server. Routing to %s' % singleDate)

    # Direct to folder within FTP site storing the SNODAS masked data.
    ftp.cwd(SNODAS_FTP_folder)

    os.chdir(downloadDir)

    # Move into FTP folder containing the data from singleDate's year
    ftp.cwd(str(singleDate.year) + '/')

    # Move into FTP folder containing the data from singleDate's month
    month_folder = singleDate.strftime('%m') + "_" + singleDate.strftime('%b') + '/'
    ftp.cwd(month_folder)

    # Set day value to a padded digit. Ex: 2 would change to 02
    day = singleDate.strftime('%d')

    # Iterate through files in FTP folder and save singleDate's data as a file in download folder
    # Create empty list to track if a download is available
    no_download_available = []
    filenames = ftp.nlst()
    for file in filenames:
        if file.endswith('%s.tar' % day):
            localfile = open(file, 'wb')
            ftp.retrbinary('RETR ' + file, localfile.write, 1024)

            logger.info('download_SNODAS: Downloaded %s' % singleDate)
            # If SNODAS data is available for download, append a '1'
            no_download_available.append(1)
        else:
            # If SNODAS data is not available for download, append a '0'
            no_download_available.append(0)


    logger.info('download_SNODAS: Finished %s \n' % singleDate)
    # Report error if download marker '1' is not in the list
    if 1 not in no_download_available:
        logger.error('ERROR: download_SNODAS: Download unsuccessful for %s' % singleDate)
        logging.error('ERROR: download_SNODAS: Download unsuccessful for %s' % singleDate)
        failed_date = singleDate

    # Report success if download marker '1' is in the list
    else:
        print 'Download complete for %s.' % singleDate
        logger.info('download_SNODAS: Download complete for %s.' % singleDate)
        failed_date = 'None'

    # Retrieve a timestamp to later export to the statistical results
    timestamp = datetime.now().isoformat()

    # Add values of optional statistics to a list to be checked for validity in SNODASDaily_Automated.py and
    # SNODASDaily_Interactive.py scripts
    optStats = [calculate_SWE_maximum, calculate_SWE_minimum, calculate_SWE_stdDev]

    returnedList = [timestamp, optStats, failed_date]
    return returnedList

# Formatting function -------------------------------------------------------------------------------------------------
def format_date_YYYYMMDD(date):
    """Convert datetime date to string date in format: YYYYMMDD.
     date: the date of interest in datetime format"""

    logger.info('format_date_YYYYMMDD: Starting %s' % date)

    # Parse year, month and day of input date into separate entities.
    year = date.year
    month = date.strftime('%m')
    day = date.strftime('%d')

    # Concatenate strings of the year, double-digit month, and double-digit day.
    day_string = str(year) + month + day

    logger.info('format_date_YYYYMMDD: Finished %s \n' % date)

    # Return string.
    return day_string

# Functions to convert SNODAS data into usable format -----------------------------------------------------------------
def untar_SNODAS_file(file, folder_input, folder_output):
    """Untar downloaded SNODAS .tar file and extract the contained files to the folder_output
    file: SNODAS .tar file to untar
    folder_input: the full pathname to the folder containing 'file'
    folder_output: the full pathname to the folder containing the extracted files"""

    logger.info('untar_SNODAS_file: Starting %s' % file)

    # Check for file extension .tar
    file_upper = file.upper()
    if file_upper.endswith('.TAR'):

        # Set full pathname of file
        file_full = os.path.join(folder_input, file)

        # Open .tar file
        tar = tarfile.open(file_full)

        # Change working directory to output folder
        os.chdir(folder_output)

        # Extract .tar file and save contents in output directory
        tar.extractall()

        # Close .tar file
        tar.close

        logger.info('untar_SNODAS_file: %s has been untarred.' % file)

    else:
        logger.info('untar_SNODAS_file: %s is not a .tar file and has not been untarred.' % file)

    logger.info('untar_SNODAS_file: Finished %s \n' % file)

def delete_irrelevant_SNODAS_files(file):
    """Delete file if not identified by the unique SWE ID. The SNODAS .tar files contain many different SNODAS datasets.
     For this project, the parameter of interest is SWE, uniquely named with ID '1034'. If the configuration file is
     set to 'False' for the value of the 'SaveAllSNODASparameters' section, then the parameters other than SWE are
     deleted.
     file: file extracted from the downloaded SNODAS .tar file"""

    # Check for unique identifier '1034'.
    if '1034' not in str(file):

        # Delete file
        os.remove(file)
        logger.info('delete_irrelevant_SNODAS_files: %s has been deleted.' % file)

    else:

        logger.info('delete_irrelevant_SNODAS_files: %s has the unique code 1034 and has not been deleted.' % file)

    logger.info('delete_irrelevant_SNODAS_files: Finished %s \n' % file)

def move_irrelevant_SNODAS_files(file, folder_output):
    """Move file to the 'OtherParameters' folder if not identified by the unique SWE ID, '1034'. The SNODAS .tar files
    contain many different SNODAS datasets. For this project, the parameter of interest is SWE, uniquely named with ID
    '1034'. If the configuration file is set to 'True' for the value of the 'SaveAllSNODASparameters' section, then the
    parameters other than SWE are moved to 'OtherParameters' subfolder of the 2_SetEnvironment folder.
    file: file extracted from the downloaded SNODAS .tar file
    folder_output: full pathname to folder where the other-than-SWE files are contained, OtherParameters"""

    logger.info('move_irrelevant_SNODAS_files: Starting %s' % file)

    # Check for unique identifier '1034'.
    if '1034' not in str(file):

        # Move copy of file to folder_output. Delete original file from original location.
        copy(file, folder_output)
        logger.info('move_irrelevant_SNODAS_files: %s has been moved to %s.' %(file, folder_output))
        os.remove(file)

    else:

        logger.info('move_irrelevant_SNODAS_files: %s has the unique code 1034 and has not been moved to %s.'
                     %(file, folder_output))

    logger.info('move_irrelevant_SNODAS_files: Finished %s \n' % file)

def extract_SNODAS_gz_file(file):
    """Extract .dat and .Hdr files from SNODAS .gz file. Each daily SNODAS raster has 2 files associated with it
    (.dat and .Hdr) Both are zipped within a .gz file.
    file: .gz file to be extracted"""

    logger.info('extract_SNODAS_gz_file: Starting %s' % file)

    # Check for file extension .gz
    file_upper = file.upper()
    if file_upper.endswith('.GZ'):

        # This block of script was based off of the script from the following resource:
        # http://stackoverflow.com/questions/20635245/using-gzip-module-with-python
        inF = gzip.open(file, 'rb')
        outF = open(file[0:46], 'wb')
        outF.write(inF.read())
        inF.close()
        outF.close()

        # Delete .gz file
        os.remove(file)

        logger.info('extract_SNODAS_gz_file: %s has been extracted' % file)

    else:
        logger.info('extract_SNODAS_gz_file: %s is not of .gz format and was not extracted.' % file)

    logger.info('extract_SNODAS_gz_file: Finished %s \n' % file)

def convert_SNODAS_dat_to_bil(file):
    """Convert SNODAS .dat file into supported file format (.tif). The .dat and .Hdr files are not supported file
    formats to use with QGS processing tools. The QGS processing tools are used to calculate the daily zonal stats.
    file: .dat file to be converted to .bil format"""

    logger.info('convert_SNODAS_dat_to_bil: Starting %s' % file)

    # Check for file extension .dat
    file_upper = file.upper()
    if file_upper.endswith('.DAT'):

        # Change file extension from .dat to .bil
        new_name = file.replace('.dat', '.bil')
        os.rename(file, new_name)

        logger.info('convert_SNODAS_dat_to_bil: %s has been converted into .bil format' % file)

    else:
        logger.info('convert_SNODAS_dat_to_bil: %s is not a .dat file and has not been converted into .bil format' % file)

    logger.info('convert_SNODAS_dat_to_bil: Finished %s \n' % file)

def create_SNODAS_hdr_file(file):
    """Create custom .hdr file. A custom .Hdr file needs to be created to indicate the raster settings of the .bil file.
    The custom .Hdr file aids in converting the .bil file to a usable .tif file.
    file: .bil file that needs a custom .Hdr file"""

    logger.info('create_SNODAS_hdr_file: Starting %s' % file)

    # Check for file extension .bil
    file_upper = file.upper()
    if file_upper.endswith('.BIL'):

        # Create name for the new .hdr file
        hdr_name = file.replace('.bil', '.hdr')

        # These lines of code create a custom .hdr file to give the specific about the .bil/raster file. The
        # specifics inside each .hdr file are the same for each daily raster. However, there must be a .hdr file
        # that matches the name of each .bil/.tif file in order for QGS to import each dataset. The text included in
        # the .Hdr file originated from page 12 of the 'National Operational Hydrologic Remote Sensing Center SNOw Data
        # Assimilation System (SNODAS) Products of NSIDC', This document can be found at the following url:
        # https://nsidc.org/pubs/documents/special/nsidc_special_report_11.pdf
        file2 = open(hdr_name, 'w')
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
        file2.close()

        logger.info('create_SNODAS_hdr_file: %s now has a created .Hdr file.' % file)

    else:
        logger.info('create_SNODAS_hdr_file: %s is not a .bil file and an .Hdr component file has not been created.' % file)

    logger.info('create_SNODAS_hdr_file: Finished %s \n' % file)

def convert_SNODAS_bil_to_tif(file, folder_output):
    """Convert .bil file into .tif file for processing within the QGIS environment.
    file: file to be converted into a .tif file
    folder_output: full pathname to location where the created .tif files are contained"""

    logger.info('convert_SNODAS_bil_to_tif: Starting %s' % file)

    # Check for file extension .bil
    file_upper = file.upper()
    if file_upper.endswith('.BIL'):

        # Create name with replaced .tif file extension
        new_name = file.replace('.bil', '.tif')

        # Set full pathname
        file_full = os.path.join(folder_output, new_name)

        # Convert file to .tif format by modifying the original file. No new file is created.
        gdal.Translate(file_full, file, format='GTiff')

        logger.info('convert_SNODAS_bil_to_tif: %s has been converted into a .tif file.' % file)

    else:
        logger.info('convert_SNODAS_bil_to_tif: %s is not a .bil file and has not been converted into a .tif file.' % file)

    logger.info('convert_SNODAS_bil_to_tif: Finished %s \n' % file)

def delete_SNODAS_bil_file(file):
    """Delete file with .bil or .hdr extensions. The .bil and .hdr formats are no longer important to keep because the
    newly created .tif file holds the same data.
    file: file to be checked for either .hdr or .bil extension (and, ultimately deleted)"""

    logger.info('delete_SNODAS_bil_file: Starting %s' % file)

    # Check for extension .bil or .Hdr
    file_upper = file.upper()
    if file_upper.endswith('.BIL') or file_upper.endswith('.HDR'):

        # Delete file
        os.remove(file)

        logger.info('delete_SNODAS_bil_file: %s has been deleted.' % file)

    else:
        logger.info('delete_SNODAS_bil_file: %s is not a .bil file or a .hdr file. It has not been deleted.' % file)

    logger.info('delete_SNODAS_bil_file: Finished %s \n' % file)

# Assigning projections and clipping functions ------------------------------------------------------------------------
def create_extent(basin_shp, folder_output):
    """Create a single-feature bounding box shapefile representing the extent of the input shapefile the watershed
    boundary input shapefile). The created extent shapefile will be used to clip the SNODAS daily national grid to the
    size of the study area. Reference: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
    basin_shp: the input shapefile for which to create the extent shapefile
    folder_output: full pathname to the folder that will hold the extent shapefile"""

    # Get basin boundary extent
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(basin_shp, 0)
    inLayer = inDataSource.GetLayer()
    extent = inLayer.GetExtent()

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
    outputShapefile = basename + '.shp'
    outputProjection = basename + '.prj'
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    outputShp_full_name = os.path.join(folder_output, outputShapefile)
    outputPrj_full_name = os.path.join(folder_output, outputProjection)

    # Create the output shapefile and add an ID Field (there will only be 1 ID because there will only be 1 feature)
    outDataSource = outDriver.CreateDataSource(outputShp_full_name)
    outLayer = outDataSource.CreateLayer("studyArea_extent", geom_type=ogr.wkbPolygon)
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    outLayer.CreateField(idField)

    # Create the feature and set values
    featureDefn = outLayer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(poly)
    feature.SetField("id", 1)
    outLayer.CreateFeature(feature)
    feature = None

    # Save and close DataSource. Important - Do not remove.
    inDataSource = None
    outDataSource = None

    # Set projection to calculate_statistics_projection (the projection set in the configutation file to be the same
    # as the basin boundary shapefile)
    InJustCode = int(calculate_statistics_projection.replace('EPSG:', ''))
    OutJustCode= int(clip_projection.replace('EPSG:', ''))
    InSpatialRef = osr.SpatialReference()
    InSpatialRef.ImportFromEPSG(InJustCode)

    InSpatialRef.MorphToESRI()
    file = open(outputPrj_full_name, 'w')
    file.write(InSpatialRef.ExportToWkt())
    file.close()

    # Reproject to the clip_projection
    # REF: http://geoinformaticstutorial.blogspot.com/2012/10/reprojecting-shapefile-with-gdalogr-and.html
    # Set file names
    infile = outputShp_full_name
    outfile = outputShp_full_name.replace('_extent', 'Extent_prj')

    # get path and filename seperately
    (outfilepath, outfilename) = os.path.split(outfile)
    # get file name without extension
    (outfileshortname, extension) = os.path.splitext(outfilename)

    # Spatial Reference of the input file
    # Access the Spatial Reference and assign the input projection
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(InJustCode)

    # Spatial Reference of the output file
    # Access the Spatial Reference and assign the output projection
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(OutJustCode)

    # create Coordinate Transformation
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # Open the input shapefile and get the layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    indataset = driver.Open(infile, 0)
    inlayer = indataset.GetLayer()

    # Create the output shapefile but check first if file exists
    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)

    outdataset = driver.CreateDataSource(outfile)
    outlayer = outdataset.CreateLayer(outfileshortname, geom_type=ogr.wkbPolygon)

    # Get the FieldDefn for attribute ID and add to output shapefile
    feature = inlayer.GetFeature(0)
    fieldDefn1 = feature.GetFieldDefnRef('id')
    outlayer.CreateField(fieldDefn1)

    # get the FeatureDefn for the output shapefile
    featureDefn = outlayer.GetLayerDefn()

    # Loop through input features and write to output file
    infeature = inlayer.GetNextFeature()
    while infeature:
        # get the input geometry
        geometry = infeature.GetGeometryRef()

        # reproject the geometry, each one has to be projected seperately
        geometry.Transform(coordTransform)

        # create a new output feature
        outfeature = ogr.Feature(featureDefn)

        # set the geometry and attribute
        outfeature.SetGeometry(geometry)
        outfeature.SetField('id', infeature.GetField('id'))

        # add the feature to the output shapefile
        outlayer.CreateFeature(outfeature)

        # destroy the features and get the next input features
        outfeature.Destroy
        infeature.Destroy
        infeature = inlayer.GetNextFeature()

    # close the shapefiles
    indataset.Destroy()
    outdataset.Destroy()

    # create the prj projection file
    outSpatialRef.MorphToESRI()
    file = open(outfilepath + '\\' + outfileshortname + '.prj', 'w')
    file.write(outSpatialRef.ExportToWkt())
    file.close()

    # Delete the unnecessary extent shapefile files  projected in the calculate_statistics_projection
    extensions = ['.dbf', '.prj', '.shp', '.shx']
    for extension in extensions:
        fileToDelete = outputShp_full_name.replace('.shp', extension)
        os.remove(fileToDelete)

def copy_and_move_SNODAS_tif_file(file, folder_output):
    """Copy and move created .tif file from original location to folder_output. The copied and moved file will be
    edited. To keep the file as it is, the original is saved within the original folder.
    file: .tif file to be copied and moved to folder_output
    folder_output: full pathname to the folder holding the newly copied .tif file"""

    logger.info('copy_and_move_SNODAS_tif_file: Starting %s' % file)

    # Set full pathname of file
    file_full_output = os.path.join(file, folder_output)

    # Check for file extension .tif
    file_upper = file.upper()
    if file_upper.endswith(".TIF"):

        # Copy and move file to file_full_output
        copy(file, file_full_output)

        logger.info('copy_and_move_SNODAS_tif_file: %s has been copied and moved to %s' % (file, folder_output))

    else:
        logger.info('copy_and_move_SNODAS_tif_file: %s is not a .tif file and has not been copied and moved to %s' % (file, folder_output))

    logger.info('copy_and_move_SNODAS_tif_file: Finished %s \n' % file)

def assign_SNODAS_datum(file, folder):
    """Define WGS84 as datum. Defaulted in configuration file to assign SNODAS grid with WGS84 datum. The
    downloaded SNODAS raster is unprojected however the "SNODAS fields are grids of point estimates of snow cover in
    latitude/longitude coordinates with the horizontal datum WGS84." - SNODAS Data Products at NSIDC User Guide
    http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/index.html
    file: the name of the .tif file that is to be assigned a projection
    folder: full pathname to the folder where both the unprojected and projected raster are stored"""

    logger.info('assign_SNODAS_datum: Starting %s' % file)

    # Check for unprojected .tif files
    file_upper = file.upper()
    if file_upper.endswith('HP001.TIF'):

        # Change name from 'us_ssmv11034tS__T0001TTNATS2003093005HP001.tif' to '20030930WGS84.tif'
        file_new = file.replace('05HP001', 'WGS84')
        file_new2 = file_new.replace('us_ssmv11034tS__T0001TTNATS', '')

        # Set up for gdal.Translate tool. Set full pathnames for both input and output files.
        input_raster = os.path.join(folder, file)
        output_raster = os.path.join(folder, file_new2)

        # Assign datum (Defaulted to 'EPSG:4326').
        gdal.Translate(output_raster, input_raster, outputSRS=clip_projection)

        # Delete unprojected file.
        os.remove(input_raster)

        logger.info('assign_SNODAS_datum: %s has been assigned projection of %s.' % (file, clip_projection))

        # Writes the projection information to the log file.
        ds = gdal.Open(output_raster)
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        if srs.IsProjected:
            prj = srs.GetAttrValue('projcs')
        datum = srs.GetAttrValue('geogcs')
        logger.info("assign_SNODAS_datum: %s has projection %s and datum %s" % (output_raster, prj, datum))
    else:
        logger.warning("assign_SNODAS_datum: %s does not end in 'HP001.tif' and has not been assigned projection "
                     "of %s." % (file, clip_projection))

    logger.info('assign_SNODAS_datum: Finished %s \n' % file)

def SNODAS_raster_clip(file, folder, vector_extent):
    """Clip file by vector_extent shapefile. The output filename starts with 'Clip'.
    file: the projected (defaulted to WGS84) .tif file to be clipped
    folder: full pathname to folder where both the unclipped and clipped rasters are stored
    vector_extent: full pathname to shapefile holding the extent of the basin boundaries. This shapefile must be
    projected in projection assigned in function assign_SNODAS_datum (defaulted to WGS84)."""

    logger.info('SNODAS_raster_clip: Starting %s' % file)

    # Check for file extension .tif
    file_upper = file.upper()
    if file_upper.endswith('WGS84.TIF'):

        # Change name from 20030930WGS84.tif.tif to 'ClipYYYYMMDD.tif'
        date_name = file.replace('WGS84', '')
        new_name = 'Clip' + date_name

        # Set full pathname of both input and output files to be used in the gdal.Warp tool
        file_full_input = os.path.join(folder, file)
        file_full_output = os.path.join(folder, new_name)

        # Clip .tif file by the input extent shapefile. For more info on gdal.WarpOptions parameters, reference
        # osgeo.gdal.Warp & osgeo.gdal.WarpOptions in the Table of Contents of URL: http://gdal.org/python/.
        #
        # Parameters Explained:
        # (1) destNameOrDestDS --- Output dataset name or object
        # (2) srcDSOrSrcDSTab --- an array of Dataset objects or filenames, or a Dataset object or a filename
        # (3) format --- output format ("GTiff", etc...)
        # (4) dstNodata --- output nodata value(s)
        # (5) cutlineDSName --- cutline dataset name
        # (6) cropToCutline --- whether to use cutline extent for output bounds
        gdal.Warp(file_full_output, file_full_input, format='GTiff',
                  dstNodata=null_value, cutlineDSName=vector_extent, cropToCutline=True)

        # Delete unclipped raster files
        os.remove(file_full_input)

        # Writes the projection to the log file
        ds = gdal.Open(file_full_output)
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        if srs.IsProjected:
            prj = srs.GetAttrValue('projcs')
        datum = srs.GetAttrValue('geogcs')
        logger.info("SNODAS_raster_clip: %s has projection %s and datum %s" % (file_full_output, prj, datum))

        logger.info('SNODAS_raster_clip: %s has been clipped.' % file)

    else:
        logger.info('SNODAS_raster_clip: %s does not end with PRJCT.tif. The clip was not processed.' % file)

    logger.info('SNODAS_raster_clip: Finished %s \n' % file)

def assign_SNODAS_projection(file, folder):
    """Project clipped raster from it's original datum (defaulted to WGS84) to desired projection (defaulted
    to Albers Equal Area).
    file: clipped file with original projection to be projected into desired projection
    folder: full pathname of folder where both the originally clipped rasters and the projected clipped rasters are
    contained"""

    logger.info('assign_SNODAS_projection: Starting %s' % file)

    # Check for projected SNODAS rasters
    if file.startswith('Clip'):

        # Change name  from 'ClipYYYYMMDD.tif' to 'SNODAS_SWE_ClipAndProjYYYYMMDD.tif'
        new_name = file.replace('Clip', 'SNODAS_SWE_ClipAndProj')

        # Set full pathname of both input and output file to be used in the gdal.Warp tool
        file_full_input = os.path.join(folder, file)
        file_full_output = os.path.join(folder, new_name)

        # Reproject the clipped SNODAS .tif files from original projection to desired projection
        gdal.Warp(file_full_output, file_full_input, format='GTiff',
                  xRes=cellsizeX, yRes=cellsizeY, srcSRS = clip_projection,
                  dstSRS=calculate_statistics_projection, resampleAlg = 'bilinear', dstNodata=null_value,)

        # Delete originally-projected clipped file
        os.remove(file_full_input)
        logger.info('assign_SNODAS_projection: %s has been projected from %s to %s' % (file, clip_projection,
                                                                                    calculate_statistics_projection))

        # Writes the projection information to the log file.
        ds = gdal.Open(file_full_output)
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        if srs.IsProjected:
            prj = srs.GetAttrValue('projcs')
        datum = srs.GetAttrValue('geogcs')
        logger.info("assign_SNODAS_projection: %s has projection %s and datum %s" % (file_full_output, prj, datum))

    else:
        logger.info("assign_SNODAS_projection: %s does not start with 'Clip' and will not be projected." % file)

    logger.info('assign_SNODAS_projection: Finished %s \n' % file)


# Creating binary raster functions --------------------------------------------------------------------------
def snowCoverage(file, folder_input, folder_output):
    """Create binary .tif raster indicating snow coverage. If a pixel in the input file is > 0 (there is snow on the
    ground) then the new raster's pixel value is assigned '1'. If a pixel in the input raster is 0 or a null value
    (there is no snow on the ground) then the new raster's pixel value is assigned '0'. The output raster is used to
    calculate the percent of daily snow coverage for each basin.
    file: daily SNODAS SWE .tif raster
    folder_input: full pathname to the folder where the file is stored
    folder_output: full pathname to the folder where the newly created binary snow cover raster is stored"""

    logger.info('snowCoverage: Starting %s' % file)

    # Check for projected SNODAS rasters
    if file.startswith('SNODAS_SWE_ClipAndProj'):

        # Set name of snow cover .tif file
        snow_file = 'SNODAS_SnowCover_ClipAndProj' + file[22:30] + '.tif'

        # Set full pathname variables for input into later raster calculator options
        file_full_input = os.path.join(folder_input, file)
        file_full_output_snow = os.path.join(folder_output, snow_file)

        # Check for previous processing of file.
        if os.path.exists(file_full_output_snow):

            logger.warning('snowCoverage: WARNING: %s has been previously created. Overwriting.' % snow_file)
            logging.warning('snowCoverage: WARNING: %s has been previously created. Overwriting.' % snow_file)

        logger.info('snowCoverage: Enveloping %s as a QGS raster object layer' % file)

        # Envelop current file as QGS object raster layer
        rLyr = QgsRasterLayer(file_full_input, '%s' % file)

        # Check for valid file within QGS environment
        if rLyr.isValid():

            # Set name (without extension) for input into the raster calculator expression. '@1' means the calculation
            # occurs on band 1 of the raster.
            rasterinput = file[0:32]
            rastercalcname = rasterinput + '@1'

            # Set variables for raster calculator options/settings. Refer to: http://gis.stackexchange.com/
            # questions/141659/qgis-from-console-raster-algebra
            resultingLayer = QgsRasterCalculatorEntry()
            resultingLayer.ref = rastercalcname
            resultingLayer.raster = rLyr
            resultingLayer.bandNumber = 1
            entries = [resultingLayer]

            # Set raster calculator options/settings. (expression, output path, output type, output extent,
            # output width, output height, entries)
            calc = QgsRasterCalculator(('(%s)>0' % rastercalcname), '%s' % file_full_output_snow, 'GTiff',
                                           rLyr.extent(), rLyr.width(), rLyr.height(), entries)

            # Begin calculation
            calc.processCalculation()

            logger.info('snowCoverage: Snow calculations for %s complete.' % file)

        else:
            logger.warning('snowCoverage: WARNING: %s is not a valid object raster layer.' % file)
            logging.warning('snowCoverage: WARNING: %s is not a valid object raster layer.' % file)

        logger.info('snowCoverage: Finished %s \n' % file)
    else:
        logger.warning("snowCoverage:WARNING: %s does not start with 'Repj'. No raster calculation took place." % file)
        logging.warning("snowCoverage:WARNING: %s does not start with 'Repj'. No raster calculation took place." % file)

# Calculating zonal statistics and exporting functions ----------------------------------------------------------------
def create_csv_files(file, vFile, csv_byDate, csv_byBasin):
    """Create empty csv files for output - both by date and by basin. The empty csv files have a header row with
     each column represented by a different field name (refer to 'fieldnames' section of the function for actual
     fieldnames). Csv files by date contain one .csv file for each date and is titled
     'SnowpackStatisticsByDate_YYYYMMDD.csv'. Each byDate file contains the zonal stats for each basin on that date.
     Csv files by basin contain one .csv file for each watershed basin & is titled 'SnowpackStatisticsByBasin_BasinId'.
     Each byBasin file contains the zonal stats for that basin for each date that has been processed.
     file: daily .tif file  to be processed with zonal statistics (clipped, projected)
     vFile: shapefile of basin boundaries (these boundaries are used as the polygons in the zonal stats calculations)
     csv_byDate: full pathname of folder containing the results by date (.csv file)
     csv_byBasin: full pathname of folder containing the results by basin (.csv file)"""

    logger.info('create_csv_files: Starting %s' % file)

    # Envelop input shapefile as QGS object vector layer
    vectorFile = QgsVectorLayer(vFile, 'Reprojected Basins', 'ogr')

    # Check to determine if the shapefile is valid as an object. If this test shows that the shapefile is not a valid
    # vector file, the script does not run the zonal statistic processing (located in the 'else' block of code). If the
    # user gets the following error message, it is important to address the initialization of the QGIS resources.
    if vectorFile.isValid() == False:
        logger.warning('create_csv_files: WARNING: Vector basin boundary shapefile is not a valid QGS object layer.')
        logging.warning('create_csv_files: WARNING: Vector basin boundary shapefile is not a valid QGS object layer.')
    else:

        # Hold current directory in variable.
        currdir = os.getcwd()

        # Retrieve date of current file. Filename: 'SNODAS_SWE_ClipAndProjYYYYMMDD'. File[22:30] pulls the
        # 'YYYYMMDD' section.
        date_name = file[22:30]

        # Define fieldnames for output .csv files. These MUST match the keys of the dictionaries. Fieldnames make up
        # the header row of the outputed .csv files. The column headers of the .csv files are in
        # sequential order as layed out in the fieldnames list.
        fieldnames = ['Date_YYYYMMDD', ID_Field_Name, 'LOCAL_NAME', 'SNODAS_SWE_Mean_in','SNODAS_SWE_Mean_mm',
                      'SNODAS_EffectiveArea_sqmi', 'SNODAS_SWE_Volume_acft', 'SNODAS_SWE_Volume_1WeekChange_acft',
                      'SNODAS_SnowCover_percent', 'Updated_Timestamp']

        if calculate_SWE_maximum.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_Max_in', 'SNODAS_SWE_Max_mm'])

        if calculate_SWE_minimum.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_Min_in', 'SNODAS_SWE_Min_mm'])

        if calculate_SWE_stdDev.upper() == 'TRUE':
            fieldnames.extend(['SNODAS_SWE_StdDev_in', 'SNODAS_SWE_StdDev_mm'])

        # Create string variable for name of outputed .csv file by date. Name: SnowpackStatisticsByDate_YYYYMMDD.csv.
        results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'

        # Check to see if the output file has already been created.
        if os.path.exists(os.path.join(csv_byDate, results_date)):

            if file.endswith('.aux.xml') == False:

                logger.warning(('create_csv_files: WARNING: %s has been previously created. Overwriting.' % file))
                logging.warning(('create_csv_files: WARNING: %s has been previously created. Overwriting.' % file))

        # Set directory where the output .csv daily files are stored. - By Date
        os.chdir(csv_byDate)

        logger.info('create_csv_files: Creating %s' % results_date)

        # Create .csv file with the appropriate fieldnames as the info in the header row. - By Date
        with open(results_date, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",", lineterminator='\n')
            writer.writeheader()
        csvfile.close()

        # Access features of the basin boundary shapefile.
        iter = vectorFile.getFeatures()

        # Iterate through each basin of the basin boundary shapefile.
        for feature in iter:

            # Create str variable for the name of output .csv file byBasin. Name: SnowpackStatisticsByBasin_LOCALID.csv.
            results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_Field_Name] + '.csv'

            # Check to see if the output file has already been created. If so, the script moves onto the raster
            # processing. If not, a .csv file is created with the appropriate fieldnames as the info in the
            # header row. - By Basin
            if not os.path.exists(os.path.join(csv_byBasin, results_basin)):

                # Set directory where the output .csv daily files are stored - By Basin
                os.chdir(csv_byBasin)

                logger.info('create_csv_files: Creating %s' % results_basin)

                # Create .csv file with appropriate fieldnames as the header row. - By Date
                with open(results_basin, 'wb') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
                    writer.writeheader()
                csvfile.close()

                # Return directory back to original
                os.chdir(currdir)

    logger.info('create_csv_files: Finished %s' % file)

def delete_ByBasinCSV_repeated_rows(file, vFile, csv_byBasin):
    """ Check to see if date has already been processed. If so, iterate through by basin csv file and only write rows
    to new csv file that do not start with the date. Ultimately, delete row of data for today's date so that new data
    can be overwritten without producing multiple rows of the same date.
	file: daily .tif file  to be processed with zonal statistics (clipped, projected)
    vFile: shapefile of basin boundaries (these boundaries are used as the polygons in the zonal stats calculations)
    csv_byBasin: full pathname of folder containing the results by basin (.csv file)"""

    logger.info('delete_ByBasinCSV_repeated_rows: Starting %s' % file)

    # Envelop input shapefile as QGS object vector layer
    vectorFile = QgsVectorLayer(vFile, 'Reprojected Basins', 'ogr')

    # Access features of the basin boundary shapefile.
    iter = vectorFile.getFeatures()

    # Check to determine if the shapefile is valid as an object. If this test shows that the shapefile is not a valid
    # vector file, the script does not run the zonal statistic processing (located in the 'else' block of code). If the
    # user gets the  following error message, it is important to address the initialization of the QGIS resources.
    if vectorFile.isValid() == False:
        logger.warning('delete_ByBasinCSV_repeated_rows: WARNING: Vector basin boundary shapefile is not a valid QGS object layer.')
        logging.warning(
            'delete_ByBasinCSV_repeated_rows: WARNING:Vector basin boundary shapefile is not a valid QGS object layer.')
    else:
        # Hold current directory in a variable, currdir, to be used at the end of the script.
        currdir = os.getcwd()

        # Retrieve date of current file. File name is 'SNODAS_SWE_ClipAndProjYYYYMMDD'. File[22:30] is pulling the
        # 'YYYYMMDD' section.
        date_name = file[22:30]

        # Iterate through each basin of the basin boundary shapefile.
        for feature in iter:

            # Create string variable to be used as the title for the outputed .csv file - By Basin
            results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_Field_Name] + '.csv'

        # Set directory where the output .csv daily files are stored. - By Basin
        os.chdir(csv_byBasin)

        # Check to see if the daily raster has already been processed.
        if date_name in open(results_basin).read() and file.endswith('.tif'):
            logger.warning(
                'delete_ByBasinCSV_repeated_rows: WARNING: Raster %s has already been processed.' % file)
            logging.warning(
                'delete_ByBasinCSV_repeated_rows: WARNING: Raster %s has already been processed.' % file)

            # Access features of the basin boundary shapefile.
            iter = vectorFile.getFeatures()

            # Iterate through each basin of the basin boundary shapefile.
            for feature in iter:

                # Create string variable to be used as the title for the input and output .csv file - By Basin
                results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_Field_Name] + '.csv'
                results_basin_edit = 'SnowpackStatisticsByBasin_' + feature[ID_Field_Name] + 'edit.csv'

                logger.warning(
                    'delete_ByBasinCSV_repeated_rows: WARNING: Rewriting %s.' % results_basin)
                logging.warning(
                    'delete_ByBasinCSV_repeated_rows: WARNING: Rewriting %s.' % results_basin)

                # Open input and output files. Input will be read and output will be written.
                input = open(results_basin, 'rb')
                output = open(results_basin_edit, 'wb')

                # If the first row in the input file is file's date, it is not written to the new file.
                # Essentially, it is deleted.
                writer = csv.writer(output)
                for row in csv.reader(input):
                    if row[0] != date_name:
                        writer.writerow(row)
                input.close()
                output.close()

                # Delete original, now inaccurate, csvByBasin file.
                os.remove(results_basin)

                # Rename the new edited csvByBasin file to its original name of SnowpackStatisticsByBasin_ +
                # feature[ID_Field_Name] + '.csv'
                os.rename(results_basin_edit, results_basin)

            # Return directory back to original
            os.chdir(currdir)

    logger.info('delete_ByBasinCSV_repeated_rows: Finished %s \n' % file)

def zipShapefile (file, csv_byDate, delete_original):
    # Code block from http://emilsarcpython.blogspot.com/2015/10/zipping-shapefiles-with-python.html
    # List of file extensions included in the shapefile
    # file: the output shapefile (any extension). All other extensions will be included by means of the function.
    # csv_byDate: full pathname of folder containing the results by date (.csv files, GeoJSON, and shapefiles)
    # delete_original: Boolean string to determine if the original unzipped shapefile files should be deleted.
    extensions = ['.shx', '.shp', '.qpj', '.prj', '.dbf', '.cpg']

    # Define naming conventions
    inName = os.path.basename(os.path.splitext(file)[0])
    zipfl = os.path.join(csv_byDate, inName + '.zip')
    ZIP = zipfile.ZipFile(zipfl, 'w')

    # Empty list to store files to delete
    delFiles = []

    for fl in os.listdir(csv_byDate):
        for extension in extensions:
            if fl == inName + extension:
                # Get full pathname of file
                inFile = os.path.join(csv_byDate, fl)
                delFiles += [inFile]
                ZIP.write(inFile, fl)
                break
    ZIP.close()

    # Delete unzipped shapefile files, if configured.
    if delete_original.upper() == 'TRUE':
        for fl in delFiles:
            os.remove(fl)

def zStat_and_export(file, vFile, csv_byBasin, csv_byDate, DirClip, DirSnow, today_date, timestamp, output_CRS_EPSG):
    """Calculate zonal statistics of basin boundary shapefile and the current SNODAS file. The zonal stats export to
    both the byDate and the byBasin csv files. A daily shapefile and geoJSON is also exported.
    file: daily raster .tif SNODAS file that is to be processed in the zonal statistics tool (clipped, projected)
    vfile: the basin boundary shapefile (used as the zone dataset for the zonal statistics calculations)
    csv_byDate: full pathname to the folder containing results by date (.csv file). Shapefile and GeoJSON saved here.
    csv_byBasin: full pathname to the folder containing results by basin (.csv file)
    DirClip: full pathname to the folder containing all daily clipped, projected .tif SNODAS rasters
    DirSnow: full pathname to the folder containing all binary snow coverage rasters
    today_date: date of processed SNODAS data in datetime format
    timestamp: the download timestamp in datetime format (returned in download_SNODAS function)
    output_CRS_EPSG: the desired projection of the output shapefile and geoJSON (configured in configuration file)"""

    # Create empty dictionary to hold the zonal statistic outputs before they are written to the .csv files.
    # Shapefiles have a limited number of fields available in the attribute table so the statistics must be calculated,
    # exported and then deleted from the shapefile.
    d = {}

    # Hold current directory in a variable, currdir, to be called at the end of the script.
    currdir = os.getcwd()

    # Retrieve date of current file. File : SNODAS_SWE_ClipAndProjYYYYMMDD. File[22:30] : YYYYMMDD.
    date_name = file[22:30]

    # Define fieldnames for output .csv files (the header row). These MUST match the keys of the dictionaries. The
    # column headers of the .csv files are in sequential order as displayed in the fieldnames list.
    fieldnames = ['Date_YYYYMMDD', ID_Field_Name, 'LOCAL_NAME', 'SNODAS_SWE_Mean_in', 'SNODAS_SWE_Mean_mm',
                  'SNODAS_EffectiveArea_sqmi', 'SNODAS_SWE_Volume_acft', 'SNODAS_SWE_Volume_1WeekChange_acft',
                  'SNODAS_SnowCover_percent', 'Updated_Timestamp']

    if calculate_SWE_maximum.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_Max_in', 'SNODAS_SWE_Max_mm'])

    if calculate_SWE_minimum.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_Min_in', 'SNODAS_SWE_Min_mm'])

    if calculate_SWE_stdDev.upper() == 'TRUE':
        fieldnames.extend(['SNODAS_SWE_StdDev_in', 'SNODAS_SWE_StdDev_mm'])

    # Envelop input shapefile (for example, the Colorado River Basin projected shapefile) as a QGS object vector layer.
    vectorFile = QgsVectorLayer(vFile, 'Reprojected Basins', 'ogr')

    # Check validity of shapefile as a QGS object. If this test shows that the vector is not a valid  vector file,
    # the script does not run the zonal statistic processing (located in the 'else' block of code). Address the
    # initialization of the QGIS resources if received following error message.
    if vectorFile.isValid() == False:
        logger.warning('zStat_and_export: WARNING: Vector shapefile is not a valid QGS object layer.')
        logging.warning('zStat_and_export: WARNING: Vector shapefile is not a valid QGS object layer.')

    else:
        # Check for extension .tif
        file_upper = file.upper()
        if file_upper.endswith('.TIF'):

            # Set directory to the directory where the output .csv daily files are contained - By Basin
            os.chdir(csv_byBasin)

            # Create date value of the working dictionary.
            d['Date_YYYYMMDD'] = date_name

            logger.info('zStat_and_export: Processing zonal statistics by basin of %s ...' % file)

            # Retrieve the datetime date for 7 days before today and convert to string format (YYYYMMDD).
            week_ago_date = today_date - timedelta(days=7)
            week_ago_str = format_date_YYYYMMDD(week_ago_date)

            # Create string variable with week_ago_str to be used as the title for the outputed .csv file - By Date
            results_date_csv = 'SnowpackStatisticsByDate_' + week_ago_str + '.csv'
            results_date_csv_fullpath = os.path.join(csv_byDate, results_date_csv)

            # Set full pathname of rasters for later input into the zonal stat tool
            snow_file = 'SNODAS_SnowCover_ClipAndProj' + date_name + '.tif'
            raster_pathH = os.path.join(DirClip, file)
            raster_pathS = os.path.join(DirSnow, snow_file)

            # Open vectorFile for editing
            vectorFile.startEditing()

            # Set input object options for the zonal stat tool - Mean.
                # input shapefile: must be a valid QGS vector layer
                # input raster: must be the full pathname
                # field prefix (string): prefix of the attribute field header containing the zonal statistics
                # band (integer): band of raster in which the calculations are processed
                # statistics type: zonal statistic to be calculated
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "SWE_", 1, QgsZonalStatistics.Mean)
            zonalStats.calculateStatistics(None)

            # OutputDict - key: csv fieldname value: [shapefile attribute field name, attribute field type
            # ('None' for outputs of zonal statistics because a new field does not need to be created)]
            OutputDict = {ID_Field_Name: [ID_Field_Name, 'None'],
                          'LOCAL_NAME': ['LOCAL_NAME', 'None'],
                          'SNODAS_SWE_Mean_in': ['SWEMean_in', QVariant.Double],
                          'SNODAS_SWE_Mean_mm': ['SWE_mean', 'None'],
                          'SNODAS_EffectiveArea_sqmi': ['Area_sqmi', QVariant.Double],
                          'SNODAS_SWE_Volume_acft': ['SWEVol_af', QVariant.Int],
                          'SNODAS_SWE_Volume_1WeekChange_acft': ['SWEVolC_af', QVariant.Int],
                          'SNODAS_SnowCover_percent': ['SCover_pct',QVariant.Double]}

            if calculate_SWE_minimum.upper() == 'TRUE':
                OutputDict.update({'SNODAS_SWE_Min_mm': ['SWE_min', 'None'],
                                   'SNODAS_SWE_Min_in': ['SWEMin_in', QVariant.Double]})

            if calculate_SWE_maximum.upper() == 'TRUE':
                OutputDict.update({'SNODAS_SWE_Max_mm': ['SWE_max', 'None'],
                                   'SNODAS_SWE_Max_in': ['SWEMax_in', QVariant.Double]})

            if calculate_SWE_stdDev.upper() == 'TRUE':
                OutputDict.update({'SNODAS_SWE_StdDev_mm': ['SWE_stdev', 'None'],
                                   'SNODAS_SWE_StdDev_in': ['SWESDev_in', QVariant.Double]})

            # Create new fields in shapefile attribute table. Ignore fields that are already populated by zstats plugin.
            for key, value in OutputDict.items():
                if value[1] != 'None':
                    newField = QgsField(value[0], value[1])
                    vectorFile.dataProvider().addAttributes([newField])

            # Set raster calculator expression to populate the 'Mean' field. This field calculates mm. Change the
            # QGSExpression if different units are desired.
            eMean = QgsExpression('SWE_mean')
            eMean.prepare(vectorFile.pendingFields())

            # Set the raster calculator expression to populate the 'SWEMean_in' field.
            # 25.4 is the number of millimeters in an inch.
            eSWEMean_in = QgsExpression('SWE_mean / 25.4')
            eSWEMean_in.prepare(vectorFile.pendingFields())

            if calculate_SWE_minimum.upper() == 'TRUE':
                # Set input object options for the zonal stat tool - Minimum
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "SWE_", 1, QgsZonalStatistics.Min)
                # Call zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Min' field.
                eMin = QgsExpression('SWE_min')
                eMin.prepare(vectorFile.pendingFields())

                # Set the raster calculator expression to populate the 'SWEMin_in' field.
                eSWEMin_in = QgsExpression('SWE_min  / 25.4')
                eSWEMin_in.prepare(vectorFile.pendingFields())

            if calculate_SWE_maximum.upper() == 'TRUE':
                # Set input object options for zonal stat tool - Maximum
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "SWE_", 1, QgsZonalStatistics.Max)
                # Call zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Max' field.
                eMax = QgsExpression('SWE_max')
                eMax.prepare(vectorFile.pendingFields())

                # Set the raster calculator expression to populate the 'SWEMax_in' field.
                eSWEMax_in = QgsExpression('SWE_max / 25.4')
                eSWEMax_in.prepare(vectorFile.pendingFields())

            if calculate_SWE_stdDev.upper() == 'TRUE':
                # Set input object options for the zonal stat tool - Standard Deviation
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "SWE_", 1, QgsZonalStatistics.StDev)
                # Call zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Set raster calculator expression to populate the 'Std Dev' field.
                eStd = QgsExpression('SWE_stdev')
                eStd.prepare(vectorFile.pendingFields())

                # Set the raster calculator expression to populate the 'SWESDev_in' field.
                eSWESDev_in = QgsExpression('SWE_stdev / 25.4')
                eSWESDev_in.prepare(vectorFile.pendingFields())

            # Set input object options for the zonal stat tool - Count of Total Basin Cells
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "Cell", 1, QgsZonalStatistics.Count)
            # Call zonal stat tool to start processing
            zonalStats.calculateStatistics(None)

            # Set input object options for the zonal stat tool - Sum of snow cover raster
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathS, "SCover", 1, QgsZonalStatistics.Sum)
            # Call zonal stat tool to start processing
            zonalStats.calculateStatistics(None)

            # Update changes to fields of shapefile.
            vectorFile.updateFields()

            # Set raster calculator expression to populate the 'Area_sqmi' field. The area of the cell (square meters)
            # multiplied by the count of basin cells . There are 2589988.10 sq meters in 1 sq mile.
            a = QgsExpression('(%s) * (%s) * Cellcount / 2589988.10' % (cellsizeX, cellsizeY))
            a.prepare(vectorFile.pendingFields())

            # Set raster calculator expression  to populate the 'SCover_pct' field. Sum of basin cells covered by snow
            # divided by total count of basin cells.
            e = QgsExpression('SCoversum / Cellcount * 100')
            e.prepare(vectorFile.pendingFields())

            # Set raster calculator expression to populate 'SWEVol_af' field. Mean SWE (mm) multiplied by effective area
            # 'Area_sqmi' divided by 304.8. There are 640 acres in 1 square mile. There are 304.8 mm in 1 foot.
            v = QgsExpression('Area_sqmi * SWE_mean * 640 / 304.8')
            v.prepare(vectorFile.pendingFields())

            # Create an empty array to hold the components of the zonal stats calculations dictionary. This
            # array is copied to the outputed .csv file and then erased only to be filled again
            # with the next daily raster's dictionary calculations. - By Date. There are two arrays in this
            # function, array_date and array_basin. The main difference is that the array_basin only holds one
            # dictionary at a time before it writes to a .csv file (one dictionary per basin and then the
            # information is deleted). The array_date holds multiple dictionaries at one time (one dictionary
            # per basin. The information in the array is only deleted after the date changes).
            array_date = []

            # Access the features of the basin boundary shapefile.
            iter = vectorFile.getFeatures()

            # Set directory to the directory where the output .csv daily files are stored - By Basin
            os.chdir(csv_byBasin)

            # Define output coordinate reference system
            output_CRS = "EPSG:" + output_CRS_EPSG

            # Iterate through each basin of the basin boundary shapefile.
            for feature in iter:

               # Check to see if the SNODAS data has already been processed for the week_ago date.
                os.chdir(csv_byDate)

                # If so, get the volume value from last week for each basin. The for loop iterates over the basins
                # and calculates the one-week-change in volume statistic.
                if os.path.exists(results_date_csv_fullpath):

                    with open(results_date_csv) as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row['%s' % ID_Field_Name] == feature[ID_Field_Name]:
                                week_ago_value = row['SNODAS_SWE_Volume_acft']
                                break
                    csvfile.close()

                    # Set raster calculator expression to populate 'SWEVolC_af' field.
                    # 'SWEVol_af' from today - 'SWEVol_af' from 7 days ago
                    c = QgsExpression('SWEVol_af - %s' % week_ago_value)
                    c.prepare(vectorFile.pendingFields())

                else:
                    c = QgsExpression('noData')
                    c.prepare(vectorFile.pendingFields())

                os.chdir(csv_byBasin)

                # Create string variable to be used as the title for the output .csv file - By Basin
                results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_Field_Name] + '.csv'

                # Create dictionary that sets rounding properties (to what decimal place) for each field. Key is the
                # field name. Value[0] is the preset raster calculator expression. Value[1] is the number of decimals
                # that the field is rounded to.
                roundingDict = {'SCover_pct': [e,2], 'Area_sqmi': [a,1], 'SWE_mean': [eMean,0],
                                'SWEMean_in': [eSWEMean_in,1],'SWEVol_af': [v,0], 'SWEVolC_af': [c,0]}

                if calculate_SWE_minimum.upper() == 'TRUE':
                    roundingDict['SWE_min'] = [eMin,0]
                    roundingDict['SWEMin_in'] = [eSWEMin_in,1]
                if calculate_SWE_maximum.upper() == 'TRUE':
                    roundingDict['SWE_max'] = [eMax,0]
                    roundingDict['SWEMax_in'] = [eSWEMax_in,1]
                if calculate_SWE_stdDev.upper() == 'TRUE':
                    roundingDict['SWE_stdev'] = [eStd,0]
                    roundingDict['SWESDev_in'] = [eSWESDev_in,1]

                # Perform raster calculations for each field.
                for key, value in roundingDict.items():
                   expression = value[0]
                   feature[key] = expression.evaluate(feature)

                # Round the raster calculations to appropriate decimal places (defined in rounding dictionary). All
                # rounding is completed AFTER all calculations have been completed.
                for key, value in roundingDict.items():
                    rounding = value[1]
                    s = QgsExpression('round(%s,%d)'% (key, rounding))
                    feature[key]= s.evaluate(feature)

               # Update features of basin shapefile
                vectorFile.updateFeature(feature)

                # Create empty array (basin) to hold the components of the zonal stats calculations.
                array_basin = []

                # Append stats to dictionary 'd'.
                d['Updated_Timestamp'] = timestamp

                for key, value in OutputDict.items():
                    d[key] = feature[value[0]]

                # Append current dictionary to the empty basin array. This array is exported to the
                # output .csv file at the end of this 'for' loop.
                array_basin.append(d.copy())

                # Append current dictionary to the empty basin array. This array is exported to the
                # output .csv file outside of this 'for' loop.
                array_date.append(d.copy())

                # Export the daily date array to a .csv file. Overwrite the .csv file if it already exists.
                # Reference: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
                with open(results_basin, 'ab') as csvfile:
                    csvwriter = csv.DictWriter(csvfile, delimiter=",", fieldnames=fieldnames)
                    for row in array_basin:
                        csvwriter.writerow(row)
                csvfile.close()

            # Close edits and save changes to the shapefile.
            vectorFile.commitChanges()

            # Delete attribute fields of the shapefile used in the calculations but not important for export to final
            # product shapefile.
            indexForCellCount = vectorFile.dataProvider().fieldNameIndex('CellCount')
            indexForSCoversum = vectorFile.dataProvider().fieldNameIndex('SCoversum')
            vectorFile.dataProvider().deleteAttributes([indexForCellCount, indexForSCoversum])

            # Update shapefile with its newly-named attribute fields.
            vectorFile.updateFields()


            # Create daily shapefile and daily geoJSON
            shapefile_name = 'SnowpackStatisticsByDate_' + date_name + '.shp'
            geojson_name = 'SnowpackStatisticsByDate_' + date_name + '.geojson'
            shapefile_name_full = os.path.join(csv_byDate, shapefile_name)
            geojson_name_full = os.path.join(csv_byDate, geojson_name)


            # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name
            indexForSWE_mean = vectorFile.dataProvider().fieldNameIndex('SWE_mean')
            vectorFile.dataProvider().renameAttributes({indexForSWE_mean: 'SWEMean_mm'})

            if calculate_SWE_minimum.upper() == 'TRUE':
                indexForSWE_min = vectorFile.dataProvider().fieldNameIndex('SWE_min')
                vectorFile.dataProvider().renameAttributes({indexForSWE_min: 'SWEMin_mm'})

            if calculate_SWE_maximum.upper() == 'TRUE':
                indexForSWE_max = vectorFile.dataProvider().fieldNameIndex('SWE_max')
                vectorFile.dataProvider().renameAttributes({indexForSWE_max: 'SWEMax_mm'})

            if calculate_SWE_stdDev.upper() == 'TRUE':
                indexForSStdDev = vectorFile.dataProvider().fieldNameIndex('SWE_stdev')
                vectorFile.dataProvider().renameAttributes({indexForSStdDev: 'SWESDev_mm'})

            vectorFile.updateFields()
            vectorFile.commitChanges()


            # Export geojson and shapefile. (layer, full output pathname, file encoding, destination reference system,
            # output file type, layer options (GeoJSON): number of decimal places used in GeoJSON geometry)
            QgsVectorFileWriter.writeAsVectorFormat(vectorFile, geojson_name_full, "utf-8",
                                                    QgsCoordinateReferenceSystem(output_CRS), "GeoJSON",
                                                    layerOptions=['COORDINATE_PRECISION=%s' % geoJSON_precision])
            QgsVectorFileWriter.writeAsVectorFormat(vectorFile, shapefile_name_full, "utf-8",
                                                    QgsCoordinateReferenceSystem(output_CRS), "ESRI Shapefile")

            # Change fieldnames of output GeoJSON file
            # Envelop GeoJSON file as a QGS object vector layer.
            newName = geojson_name.replace(".geojson", "_intermediate.geojson")
            int_geojson_name_full = os.path.join(csv_byDate, newName)
            os.rename(geojson_name_full, int_geojson_name_full)

            vectorFile_GeoJson = QgsVectorLayer(int_geojson_name_full, 'GeoJsonStatistics', 'ogr')

            # Open vectorFile for editing
            vectorFile_GeoJson.startEditing()

            # Rename attribute field names defaulted by QGS Zonal Stat tool to the desired field name
            fieldDict = {'SWEMean_mm': 'SNODAS_SWE_Mean_mm', 'SWEVolC_af': 'SNODAS_SWE_Volume_1WeekChange_acft',
                         'SWEMean_in': 'SNODAS_SWE_Mean_in', 'Area_sqmi': 'SNODAS_EffectiveArea_sqmi',
                         'SWEVol_af': 'SNODAS_SWE_Volume_acft', 'SCover_pct': 'SNODAS_SnowCover_percent'}

            if calculate_SWE_minimum.upper() == 'TRUE':
                fieldDict.update({'SWEMin_mm': 'SNODAS_SWE_Min_mm', 'SWEMin_in': 'SNODAS_SWE_Min_in'})

            if calculate_SWE_maximum.upper() == 'TRUE':
                fieldDict.update({'SWEMax_mm': 'SNODAS_SWE_Max_mm', 'SWEMax_in': 'SNODAS_SWE_Max_in'})

            if calculate_SWE_stdDev.upper() == 'TRUE':
                fieldDict.update({'SWESDev_mm': 'SNODAS_SWE_StdDev_mm', 'SWESDev_in': 'SNODAS_SWE_StdDev_in'})

            for key, value in fieldDict.items():
                index = vectorFile_GeoJson.dataProvider().fieldNameIndex(key)
                vectorFile_GeoJson.dataProvider().renameAttributes({index: value})

            # Update the changes to the field names and remove the intermediate GeoJSON file (with shapefile fieldnames)
            vectorFile_GeoJson.updateFields()
            vectorFile_GeoJson.commitChanges()

            # Export geojson. (layer, full output pathname, file encoding, destination reference system,
            # output file type, layer options (GeoJSON): number of decimal places used in GeoJSON geometry)
            QgsVectorFileWriter.writeAsVectorFormat(vectorFile_GeoJson, geojson_name_full, "utf-8",
                                                    QgsCoordinateReferenceSystem(output_CRS), "GeoJSON",
                                                    layerOptions=['COORDINATE_PRECISION=%s' % geoJSON_precision])

            # Close the vectorFile_GeoJSON so that the vectorFile can open
            os.remove(int_geojson_name_full)
            vectorFile.startEditing()


            # Delete attribute fields of the shapefile related to the daily calculated zonal statistics.
            listOfFieldNames = ['SWEMean_mm', 'SCover_pct', 'SWEMean_in', 'Area_sqmi', 'SWEVolC_af', 'SWEVol_af']
            if calculate_SWE_minimum.upper() == 'TRUE':
                listOfFieldNames.extend(['SWEMin_mm', 'SWEMin_in'])
            if calculate_SWE_maximum.upper() == 'TRUE':
                listOfFieldNames.extend(['SWEMax_mm', 'SWEMax_in'])
            if calculate_SWE_stdDev.upper() == 'TRUE':
                listOfFieldNames.extend(['SWESDev_mm', 'SWESDev_in'])

            for item in listOfFieldNames:
                index = vectorFile.dataProvider().fieldNameIndex(item)
                vectorFile.dataProvider().deleteAttributes([index])

            # Update shapefile with its newly-deleted attribute fields.
            vectorFile.updateFields()
            vectorFile.commitChanges()

            # Create a string variable to be used as the title for the outputed .csv file - By Date
            results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'

            # Set directory to the directory where the output .csv daily files are contained. - By Date
            os.chdir(csv_byDate)

            # Update text file, ListOfDates.txt, with list of dates represented by csv files in ByDate folder
            array = glob.glob("*.csv")
            array.sort(reverse=True)
            array_recent_date = []

            with open("ListOfDates.txt", 'w') as output_file:
                for filename in array:
                    if filename.endswith("LatestDate.csv") == False:
                        date = filename[25:33]
                        array_recent_date.append(date)
                        output_file.write(date + "\n")
            output_file.close()

            # Export the daily date array to a .csv file. Overwrite the .csv file if it already exists.
            # Reference: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
            with open(results_date, 'ab') as csvfile:
                csvwriter = csv.DictWriter(csvfile, delimiter=",", fieldnames=fieldnames)
                for row in array_date:
                    csvwriter.writerow(row)
            csvfile.close()

            # Get most recent processed SNODAS date & make a copy called 'SnowpackStatisticsByDate_LatestDate.csv'
            most_recent_date = str(max(array_recent_date))
            src = 'SnowpackStatisticsByDate_' + most_recent_date + '.csv'
            dst = 'SnowpackStatisticsByDate_LatestDate.csv'
            copyfile(os.path.join(csv_byDate, src), os.path.join(csv_byDate, dst))

            # Return working directory back to its original setting before the script began.
            os.chdir(currdir)

            logger.info('zStat_and_export: Zonal statistics of %s are exported to %s' % (file, csv_byBasin))
            print "Zonal statistics of %s are complete. \n" % date_name



        else:
            logger.info('zStat_and_export: %s is not a .tif file and the zonal statistics were not processed.' % file)

def create_SNODAS_SWE_graphs():
    """Create, or update, the snowpack time series graphs from the by basin data."""

    # Refer to configuration file. If true, update the time series graphs weekly. If false, update the TS graphs daily.
    if weekly_update.upper() == 'TRUE':

        # Check that today is the set weekday to update the time series graphs.
        if str(datetime.today().weekday()) == str(weekly_update_date):

            print 'Running TsTool file to create SNODAS SWE graphs. This could take a couple of minutes.'
            logger.info('create_SNODAS_SWE_graphs: Running TsTool file to create SNODAS Time Series graphs. TsTool '
                        'file pathname: %s' % TsToolCreateTimeSeries)

            # Run the TsTool command file, 'TsToolCreateTimeSeries', in the background. Wait for the subprocess
            # to complete before continuing.
            Popen([TsToolInstall, '-commands', TsToolCreateTimeSeries]).wait()

            print 'SNODAS Time Series Graphs have been created.'
    else:
        print 'Running TsTool file to create SNODAS SWE graphs. This could take up to 5 minutes.'
        logger.info(
            'create_SNODAS_SWE_graphs: Running TsTool file to create SNODAS Time Series graphs. TsTool '
            'file pathname: %s' % TsToolCreateTimeSeries)

        # Run the TsTool command file, 'TsToolCreateTimeSeries', in the background. Wait for the subprocess
        # to complete before continuing.
        Popen([TsToolInstall, '-commands', TsToolCreateTimeSeries]).wait()
        print 'SNODAS Time Series Graphs have been created.'

def push_to_AWS():
    """Runs batch file to push the newly-updated files to Amazon Web Services. The specifics are configured within the
    batch file, AWS_batch_file. """
    logger.info('push_to_AWS: Pushing files to Amazon Web Services S3 given specifics of %s.'% AWS_batch_file)
    print 'Pushing files to Amazon Web Services S3'

    # Call batch file, AWS_batch_file, to push files up to Amazon Web Service
    args = [AWS_batch_file]
    Popen(args, cwd="C:\Program Files\Amazon\AWSCLI").wait()
    logger.info('push_to_AWS: Files have been pushed to Amazon Web Services S3 as designed by %s.'% AWS_batch_file)
