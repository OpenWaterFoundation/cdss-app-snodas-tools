# Name: SNODAS_utilites.py
# Author: Emma Giles
# Organization: Open Water Foundation
#
# Purpose: This script contains the functions utilized within the SNODAS tools (SNODASDaily_Automated.py and
#   SNODASDaily_Interactive.py). Both scripts process zonal statistics of SNODAS raster datasets(minimum SWE, maximim
#   SWE, mean SWE, standard deviation SWE, count of pixels within each boundary, and percentage of ground covered by
#   snow) with respect to the input vector shapefile (basin boundaries). The SNODAS tools were originally developed to
#   calculate zonal statistics of Colorado Basin boundaries.
#
#   Both scripts call the same functions defined in this SNODAS_utilities.py script. SNODASDaily_Automated.py
#   downloads the current date of SNODAS data and outputs the results in multiple .csv files (one .csv file for the
#   current date and one .csv file for EACH basin in the input vector shapefile). SNODASDaily_Interactive.py allows
#   access to historical dates of SNODAS data and outputs the results in multiple .csv files (one .csv file for EACH
#   historical date and one .csv file for EACH basin in the input vector shapefile).


# Import necessary modules
import ftplib, os, tarfile, gzip, gdal, csv, logging, configparser, glob
from logging.config import fileConfig
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsZonalStatistics
from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsField, QgsExpression
from PyQt4.QtCore import QVariant
from datetime import datetime
from shutil import copy



# Reads the configuration file to assign variables. Reference the following for code details:
# https://wiki.python.org/moin/ConfigParserExamples

Config = configparser.ConfigParser()
Configfile = "..\SNODASconfig.ini"
Config.read(Configfile)

# Create and configures logging file
fileConfig(Configfile)
logger = logging.getLogger('log02')


# Helper function to obtain option values of config file sections.
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# Assigns the values from the configuration file to the python variables. See below for description of each
# variable obtained by the configuration file.
#
#   website: The SNODAS FTP site url to access the downloadable data.
#
#   username: The SNODAS FTP site username to access the downloadable data.
#
#   password: The SNODAS FTP site password to access the downloadable data.
#
#   SNODAS_FTP_folder: The folder pathname within the SNODAS FTP site that accesses the SNODAS masked datasets. The
#   masked datasets are SNODAS grids clipped to the contiguous U.S. boundary.
#
#   projectionInput: The EPSG projection code of the input basin extent shapefile. Defaulted to WGS84. The basin
#   extent shapefile is used to clip the national SNOADS grids to the clipped extent of the basin boundaries.
#
#   projectionOutput: The desired EPSG projection code of the final products (snow cover grid and clipped SNODAS grid).
#   Defaulted to NAD83 Zone 13N.
#
#   ID_Field_Name: The field name of the basin boundary attribute table describing the identification of each basin.
#   The naming convention of the CSVByBasin result files use the ID_Field_Name.
#
#   null_value: The null values that SNODAS applies to the data's null value. Defaulted to -9999 but should be changed
#   if the null values provided by SNODAS are changed.

website = ConfigSectionMap("SNODAS_FTPSite")['website']
username = ConfigSectionMap("SNODAS_FTPSite")['username']
password = ConfigSectionMap("SNODAS_FTPSite")['password']
SNODAS_FTP_folder = ConfigSectionMap("SNODAS_FTPSite")['folder_path']
projectionInput = "EPSG:" + ConfigSectionMap("VectorInputExtent")['projection_epsg']
projectionOutput = "EPSG:" + ConfigSectionMap("VectorInputShapefile")['projection_epsg']
ID_Field_Name = ConfigSectionMap("VectorInputShapefile")['basin_id']
null_value = ConfigSectionMap("SNODAS_FTPSite")['null_value']

# Get today's date. ---------------------------------------------------------------------------------------------------
now = datetime.now()


# Downloading function ------------------------------------------------------------------------------------------------
def download_SNODAS(downloadDir, singleDate):
    """Access the SNODAS FTP site and download the .tar file of singleDate. The .tar file saves to the specified
    downloadDir folder.
    downloadDir: full path name to the location where the downloaded SNODAS rasters are stored
    singleDate: the date of interest from import datetime module"""

    logger.info('download_SNODAS: Starting %s' % singleDate)


    # Code format for the following block of code in reference to:
    # http://www.informit.com/articles/article.aspx?p=686162&seqNum=7 and
    # http://stackoverflow.com/questions/5230966/python-ftp-download-all-files-in-directory
    # Connect to FTP server
    ftp = ftplib.FTP(website, username, password)

    logger.info('download_SNODAS: Connected to FTP server. Routing to %s' % singleDate)

    # Direct to folder within FTP site storing the SNODAS masked data.
    ftp.cwd(SNODAS_FTP_folder)

    # Change local working directory to the download folder
    os.chdir(downloadDir)

    # Move into FTP folder containing the data from singleDate's year
    ftp.cwd(str(singleDate.year) + '/')

    # Move into FTP folder containing the data from singleDate's month
    month_folder = singleDate.strftime('%m') + "_" + singleDate.strftime('%b') + '/'
    ftp.cwd(month_folder)

    # Set day value to a padded digit. Ex: 2 would change to 02
    day = singleDate.strftime('%d')

    # Iterate through files in FTP folder and save singleDate's data as a file in download folder
    filenames = ftp.nlst()
    for file in filenames:
        if file.endswith('%s.tar' % day):
            localfile = open(file, 'wb')
            ftp.retrbinary('RETR ' + file, localfile.write, 1024)

            logger.info('download_SNODAS: Downloaded %s' % singleDate)
            print ("Download of %s from FTP site completed.") % singleDate

    logger.info('download_SNODAS: Finished %s \n' % singleDate)


# Formatting function -------------------------------------------------------------------------------------------------
def format_date_YYYYMMDD(date):
    """Convert datetime date to string date in format: YYYYMMDD.
     date: the date of interest from import datetime module"""

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

def assign_SNODAS_projection(file, folder):
    """Assign projection to file. Defaulted in configuration file to project to WGS84. The downloaded SNODAS raster
    is unprojected however the "SNODAS fields are grids of point estimates of snow cover in latitude/longitude
    coordinates with the horizontal datum WGS84." - SNODAS Data Products at NSIDC User Guide
    http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/index.html
    file: the name of the .tif file that is to be assigned a projection
    folder: full pathname to the folder where both the unprojected and projected raster are stored"""

    logger.info('assign_SNODAS_projection: Starting %s' % file)

    # Check for unprojected .tif files
    file_upper = file.upper()
    if file_upper.endswith('HP001.TIF'):

        # Change name from 'us_ssmv11034tS__T0001TTNATS2003093005HP001.tif' to '20030930PRJCT.tif'
        file_new = file.replace('05HP001', 'PRJCT')
        file_new2 = file_new.replace('us_ssmv11034tS__T0001TTNATS', '')

        # Set up for gdal.Translate tool. Set full pathnames for both input and output files.
        input_raster = os.path.join(folder, file)
        output_raster = os.path.join(folder, file_new2)

        # Assign projection (Defaulted to 'EPSG:4326').
        gdal.Translate(output_raster, input_raster, outputSRS=projectionInput)

        # Delete unprojected file.
        os.remove(input_raster)

        logger.info('assign_SNODAS_projection: %s has been assigned projection of %s.' % (file, projectionInput))

    else:
        logger.info("assign_SNODAS_projection: %s does not end in 'HP001.tif' and has not been assigned projection "
                     "of %s." % (file, projectionInput))

    logger.info('assign_SNODAS_projection: Finished %s \n' % file)

def SNODAS_raster_clip(file, folder, vector_extent):
    """Clip file by vector_extent shapefile. The output filename starts with 'Clip'.
    file: the projected (defaulted to WGS84) .tif file to be clipped
    folder: full pathname to folder where both the unclipped and clipped rasters are stored
    vector_extent: full pathname to shapefile holding the extent of the basin boundaries. This shapefile must be
    projected in projection assigned in function assign_SNODAS_projection (defaulted to WGS84)."""

    logger.info('SNODAS_raster_clip: Starting %s' % file)

    # Check for file extension .tif
    file_upper = file.upper()
    if file_upper.endswith('PRJCT.TIF'):

        # Change name by adding prefix Clip
        date_name = 'Clip' + str(file)

        # Set full pathname of both input and output files to be used in the gdal.Warp tool
        file_full_input = os.path.join(folder, file)
        file_full_output = os.path.join(folder, date_name)

        # Clip .tif file by the input extent shapefile. For more info on gdal.WarpOptions paramerters, reference
        # osgeo.gdal.Warp & osgeo.gdal.WarpOptions in the Table of Contents of URL: http://gdal.org/python/.
        #
        # Parameters Explained:
        # (1) destNameOrDestDS --- Output dataset name or object
        # (2) srcDSOrSrcDSTab --- an array of Dataset objects or filenames, or a Dataset object or a filename
        # (3) format --- output format ("GTiff", etc...)
        # (4 and 5) xRes, yRes --- output resolution in target SRS
        # (6) dstNodata --- output nodata value(s)
        # (7) cutlineDSName --- cutline dataset name
        # (8) cropToCutline --- whether to use cutline extent for output bounds
        gdal.Warp(file_full_output, file_full_input, format='GTiff', xRes=0.00833333333333, yRes=0.00833333333333,
                  dstNodata=null_value, cutlineDSName=vector_extent, cropToCutline=True)

        # Delete unclipped raster files
        os.remove(file_full_input)

        logger.info('SNODAS_raster_clip: %s has been clipped.' % file)

    else:
        logger.info('SNODAS_raster_clip: %s does not end with PRJCT.tif and the clip was not processed on this raster.' % file)

    logger.info('SNODAS_raster_clip: Finished %s \n' % file)

def SNODAS_raster_reproject_NAD83(file, folder):
    """Reproject clipped raster from it's original projection (defaulted to WGS84) to desired projection (defaulted
    to NAD83 UTM Zone 13N).
    file: clipped file with original projection to be reprojected into desired projection
    folder: full pathname of folder where both the originally clipped rasters and the reprojected clipped rasters are
    contained"""

    logger.info('SNODAS_raster_reproject_NAD83: Starting %s' % file)

    # Check for projected SNODAS rasters
    if file.startswith('Clip'):

        # Change name prefix from 'Clip' prefix to 'SNODAS_SWE_ClipAndReproj'
        new_name1 = file.replace("Clip", "SNODAS_SWE_ClipAndReproj")
        new_name = new_name1.replace("PRJCT.tif", ".tif")

        # Set full pathname of both input and output file to be used in the gdal.Warp tool
        file_full_input = os.path.join(folder, file)
        file_full_output = os.path.join(folder, new_name)

        # Reproject the clipped SNODAS .tif files from original projection to desired projection
        gdal.Warp(file_full_output, file_full_input, format='GTiff', srcSRS=projectionInput, dstSRS=projectionOutput,
                  dstNodata=null_value,)

        # Delete originally-projected clipped file
        os.remove(file_full_input)
        logger.info('SNODAS_raster_reproject_NAD83: %s has been reprojected from %s to %s' % (file, projectionInput,
                                                                                               projectionOutput))


    else:
        logger.info("SNODAS_raster_reproject_NAD83: %s does not start with 'Clip' and will not be reprojected." % file)




    logger.info('SNODAS_raster_reproject_NAD83: Finished %s \n' % file)


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

    # Check for reprojected SNODAS rasters
    if file.startswith('SNODAS_SWE_ClipAndReproj'):

        # Set name of snow cover .tif file
        snow_file = 'SNODAS_SnowCover_ClipAndReproj' + file[24:32] + '.tif'

        # Set full pathname variables for input into later raster calculator options
        file_full_input = os.path.join(folder_input, file)
        file_full_output_snow = os.path.join(folder_output, snow_file)

        # Check for previous processing of file.
        if os.path.exists(file_full_output_snow):

            logger.warning('snowCoverage: WARNING: %s has been previously created. Overwriting the file now.' % snow_file)
            logging.warning('snowCoverage: WARNING: %s has been previously created. Overwriting the file now.' % snow_file)

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
                                           rLyr.extent(),
                                           rLyr.width(),
                                           rLyr.height(), entries)

            # Begin calculation
            calc.processCalculation()

            logger.info('snowCoverage: Snow calculations for %s complete.' % file)

        else:
            logger.warning('snowCoverage: WARNING: %s is not a valid object raster layer.' % file)
            logging.warning('snowCoverage: WARNING: %s is not a valid object raster layer.' % file)

        logger.info('snowCoverage: Finished %s \n' % file)
    else:
        logger.warning("snowCoverage: WARNING: %s does not start with 'Repj' and no raster calculation took place." % file)
        logging.warning("snowCoverage: WARNING: %s does not start with 'Repj' and no raster calculation took place." % file)


# Calculating zonal statistics and exporting functions ----------------------------------------------------------------
def create_csv_files(file, vFile, csv_byDate, csv_byBasin):
    """Create empty csv files for output - both by date and by basin. The empty csv files have a header row with
     each column represented by a different field name (refer to 'fieldnames' section of the function for actual
     fieldnames). Csv files by date contain one .csv file for each date and is titled 'SnowpackStatisticsByDate_YYYYMMDD.csv'.
     Each byDate file contains the zonal statistics for each basin on that date. Csv files by basin contain one .csv
     file for each watershed basin and is titled 'SnowpackStatisticsByBasin_BasinId)'. Each byBasin file contains the zonal
     statistics for that basin for each date that has been processed.
     file: daily .tif file  to be processed with zonal statistics (clipped, reprojected)
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

        # Retrieve date of current file. Filename: 'SNODAS_SWE_ClipAndReprojYYYYMMDD'. File[24:32] pulls the
        # 'YYYYMMDD' section.
        date_name = file[24:32]

        # Define fieldnames for output .csv files. These MUST match the keys of the dictionaries. Fieldnames make up
        # the header row of the outputed .csv files. The column headers of the .csv files are in
        # sequential order as layed out in the fieldnames list.
        fieldnames = ['Date_YYYYMMDD', ID_Field_Name, 'SNODAS_SWE_Mean_m', 'SNODAS_SWE_Min_m', 'SNODAS_SWE_Max_m',
                      'SNODAS_SWE_StdDev_m', 'SNODAS_Pixels_Count', 'SNODAS_SnowCover_percent', 'SNODAS_SWE_Mean_in',
                      'SNODAS_SWE_Min_in', 'SNODAS_SWE_Max_in', 'SNODAS_SWE_StdDev_in']

        # Create string variable for name of outputed .csv file by date. Name: SnowpackStatisticsByDate_YYYYMMDD.csv.
        results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'

        # Check to see if the output file has already been created.
        if os.path.exists(os.path.join(csv_byDate, results_date)):

            if file.endswith('.aux.xml') == False:

                logger.warning(('create_csv_files: WARNING: %s has been previously created. Overwriting the file now.' % file))
                logging.warning(('create_csv_files: WARNING: %s has been previously created. Overwriting the file now.' % file))

        # Set directory where the output .csv daily files are stored. - By Date
        os.chdir(csv_byDate)

        logger.info('create_csv_files: Creating %s' % results_date)

        # Create .csv file with the appropriate fieldnames as the info in the header row. - By Date
        with open(results_date, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
            writer.writeheader()
        csvfile.close()


        # Access features of the basin boundary shapefile.
        iter = vectorFile.getFeatures()

        # Iterate through each basin of the basin boundary shapefile.
        for feature in iter:

            # Create string variable for the name of output .csv file by basin. Name: SnowpackStatisticsByBasin_LOCALID.csv.
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
    """ Check to see if date has already been processed. If so, iterate through by basin csv file and only write rows to new csv file
	that do not start with the date. Ultimately, delete row of data for today's date so that new data can be overwritten without
	producing multiple rows of the same date.
	file: daily .tif file  to be processed with zonal statistics (clipped, reprojected)
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

        # Retrieve date of current file. File name is 'SNODAS_SWE_ClipAndReprojYYYYMMDD'. File[24:32] is pulling the
        # 'YYYYMMDD' section.
        date_name = file[24:32]

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

def zStat_and_export(file, vFile, csv_byBasin, csv_byDate, DirClip, DirSnow):
    """Calculate zonal statistics of basin boundary shapefile and the current file. The zonal stats export to
    both the byDate and the byBasin csv files.
    file: daily raster .tif SNODAS file that is to be processed in the zonal statistics tool (clipped, reprojected)
    vfile: the shapefile of the basin boundaries (these boundaries are used as the polygons in the zonal
    statistics calculations)
    csv_byDate: full pathname to the folder containing results by date (.csv file)
    csv_byBasin: full pathname to the folder containing results by basin (.csv file)
    DirClip: full pathname to the folder containing all daily clipped, NAD83 .tif SNODAS rasters
    DirSnow: full pathname to the folder containing all binary snow coverage rasters"""

    # Create empty dictionary. This empty dictionary is used as a placeholder for the zonal statistic outputs
    # before they are written to the .csv file.  Shapefiles have a limited number of fields available in the attribute
    # table so the zonal statistics must be calculated, exported and then deleted from the shapefile.
    d = {}

    # Hold  current directory in a variable, currdir, to be called at the end of the script.
    currdir = os.getcwd()

    # Define fieldnames for output .csv files. These MUST match the keys of the dictionaries. The fieldnames make up
    # the header row for the output .csv files. The column headers of the .csv files are in sequential order as layed
    # out in the fieldnames list.
    fieldnames = ['Date_YYYYMMDD', ID_Field_Name, 'SNODAS_SWE_Mean_m', 'SNODAS_SWE_Min_m', 'SNODAS_SWE_Max_m',
                      'SNODAS_SWE_StdDev_m', 'SNODAS_Pixels_Count', 'SNODAS_SnowCover_percent', 'SNODAS_SWE_Mean_in',
                    'SNODAS_SWE_Min_in', 'SNODAS_SWE_Max_in', 'SNODAS_SWE_StdDev_in']

    # Envelop input shapefile (for example, the Colorado River Basin NAD83 shapefile) as a QGS object vector layer
    vectorFile = QgsVectorLayer(vFile, 'Reprojected Basins', 'ogr')

    # Check validity of shapefile as a QGS object. If this test shows that the vector is not a valid  vector file,
    # the script does not run the zonal statistic processing (located in the 'else' block of code). Address the
    # initialization of the QGIS resources if received following error message.
    if vectorFile.isValid() == False:
        logger.warning('zStat_and_export: WARNING: Vector shapefile is not a valid QGS object layer.')
        logging.warning('zStat_and_export: WARNING: Vector shapefile is not a valid QGS object layer.')

    else:
        # Retrieve date of current file. File : SNODAS_SWE_ClipAndReprojYYYYMMDD. File[24:32] : YYYYMMDD.
        date_name = file[24:32]

        # Check for extension .tif
        file_upper = file.upper()
        if file_upper.endswith('.TIF'):

            # Set directory to the directory where the output .csv daily files are contained - By Basin
            os.chdir(csv_byBasin)

            # Create date value of the working dictionary.
            d['Date_YYYYMMDD'] = date_name

            logger.info('zStat_and_export: Processing zonal statistics by basin of %s ...' % file)

            # Set full pathname of rasters for later input into the zonal stat tool
            snow_file = 'SNODAS_SnowCover_ClipAndReproj' + file[24:32] + '.tif'
            raster_pathH = os.path.join(DirClip, file)
            raster_pathS = os.path.join(DirSnow, snow_file)

            # Set input object options for the zonal stat tool - Mean.
            # [input shapefile (must be a valid QGS vector layer), input raster (must be the full pathname),
            # string (this is the title of the attribute table field header displaying the zonal stat.
            # Note that it is never seen by the user because the zonal statistic attribute field is
            # deleted later in this script), band of raster in which the calculations are processed,
            # statistic type]
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Mean)
            # Call zonal stat tool to start processing with the above set properties
            zonalStats.calculateStatistics(None)

            # Set raster calculator expression to populate the 'Mean' field. As described in
            # the 'Detailed Data Description' section of the 'SNODAS Data Products at NSIDC'
            # (http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/index.html#3.)the SWE data is set to
            # a scale factor of 1000. To convert integers in original SNODAS files to model output values, the
            # integers must be divided by the scale factor. This division occurs in the development of all SWE
            # statistics throughout this script.
            eMean = QgsExpression('Smean / 1000')
            eMean.prepare(vectorFile.pendingFields())

            # Set input object options for the zonal stat tool - Minimum
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Min)
            # Call zonal stat tool to start processing
            zonalStats.calculateStatistics(None)

            # Set raster calculator expression to populate the 'Min' field.
            eMin = QgsExpression('Smin / 1000')
            eMin.prepare(vectorFile.pendingFields())

            # Set input object options for zonal stat tool - Maximum
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Max)
            # Call zonal stat tool to start processing
            zonalStats.calculateStatistics(None)

            # Set raster calculator expression to populate the 'Max' field.
            eMax = QgsExpression('Smax / 1000')
            eMax.prepare(vectorFile.pendingFields())

            # Set input object options for the zonal stat tool - Standard Deviation
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.StDev)
            # Call zonal stat tool to start processing
            zonalStats.calculateStatistics(None)

            # Set raster calculator expression to populate the 'Std Dev' field.
            eStd = QgsExpression('Sstdev / 1000')
            eStd.prepare(vectorFile.pendingFields())

            # Set input object options for the zonal stat tool - Count of Total Basin Cells
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Count)
            # Call zonal stat tool to start processing
            zonalStats.calculateStatistics(None)

            # Set input object options for the zonal stat tool - Sum of snow cover raster
            zonalStats = QgsZonalStatistics(vectorFile, raster_pathS, "S", 1, QgsZonalStatistics.Sum)
            # Call zonal stat tool to start processing
            zonalStats.calculateStatistics(None)

            # Open vectorFile for editing - http://gis.stackexchange.com/questions/34974/is-it-possible-to-
            # programmatically-add-calculated-fields/59724#59724
            vectorFile.startEditing()

            # Add a new field to the shapefile titled 'SnowCover'. This holds integer type data. This field
            # holds the raster calculator outputs that determine the percentage of basin area covered by
            # snow.
            newField = QgsField('SnowCover', QVariant.Int)
            vectorFile.dataProvider().addAttributes([newField])

            # Add new fields to the shapefile to calculate SWE statistics in inches
            newFieldmean = QgsField('MeanIn', QVariant.Int)
            vectorFile.dataProvider().addAttributes([newFieldmean])
            newFieldmin = QgsField('MinIn', QVariant.Int)
            vectorFile.dataProvider().addAttributes([newFieldmin])
            newFieldmax = QgsField('MaxIn', QVariant.Int)
            vectorFile.dataProvider().addAttributes([newFieldmax])
            newFieldstdev = QgsField('StDevIn', QVariant.Int)
            vectorFile.dataProvider().addAttributes([newFieldstdev])
            vectorFile.updateFields()

            # Set raster calculator expression  to populate the 'SnowCover' field. Sum of basin pixels covered by snow
            # divided by total count of basin pixels.
            e = QgsExpression('Ssum / Scount * 100')
            e.prepare(vectorFile.pendingFields())

            # Set the raster calculator expression to populate the 'Inch' fields. 39.37008 is 3.28084 (feet in a meter)
            # multiplied by 12 (inches in a foot).
            eMeanIn = QgsExpression('Smean * 39.37008')
            eMeanIn.prepare(vectorFile.pendingFields())
            eMinIn = QgsExpression('Smin * 39.37008')
            eMinIn.prepare(vectorFile.pendingFields())
            eMaxIn = QgsExpression('Smax * 39.37008')
            eMaxIn.prepare(vectorFile.pendingFields())
            eStDevIn = QgsExpression('Sstdev * 39.37008')
            eStDevIn.prepare(vectorFile.pendingFields())

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

            # Iterate through each basin of the basin boundary shapefile.
            for feature in iter:

                # Create string variable to be used as the title for the output .csv file - By Basin
                results_basin = 'SnowpackStatisticsByBasin_' + feature[ID_Field_Name] + '.csv'

                # Calculate snow coverage percent. Add the calculation to created field 'SnowCover'
                feature['SnowCover'] = e.evaluate(feature)
                # Round snow coverage percent to one decimal place.
                s = QgsExpression('round("SnowCover", 1)')
                feature['SnowCover'] = s.evaluate(feature)
                vectorFile.updateFeature(feature)

                # Calculate mean SWE. Add the calculation to created field 'Smean'
                feature['Smean'] = eMean.evaluate(feature)
                # Round mean SWE to three decimal places.
                s = QgsExpression('round("Smean", 3)')
                feature['Smean'] = s.evaluate(feature)
                vectorFile.updateFeature(feature)

                # Calculate minimum SWE. Add the calculation to created field 'Smin'
                feature['Smin'] = eMin.evaluate(feature)
                vectorFile.updateFeature(feature)

                # Calculate maximum SWE. Add the calculation to created field 'Smax'
                feature['Smax'] = eMax.evaluate(feature)
                vectorFile.updateFeature(feature)

                # Calculate standard deviation SWE. Add the calculation to created field 'Sstdev'
                feature['Sstdev'] = eStd.evaluate(feature)

                # Round standard deviation SWE to four decimal places.
                s = QgsExpression('round("Sstdev", 4)')
                feature['Sstdev'] = s.evaluate(feature)
                vectorFile.updateFeature(feature)

                # Calculate inches SWE statistics and round to 2 decimal places. Add calculations to appropriate fields.
                feature['MeanIn'] = eMeanIn.evaluate(feature)
                s = QgsExpression('round("MeanIn", 3)')
                feature['MeanIn'] = s.evaluate(feature)
                feature['MinIn'] = eMinIn.evaluate(feature)
                s = QgsExpression('round("MinIn", 3)')
                feature['MinIn'] = s.evaluate(feature)
                feature['MaxIn'] = eMaxIn.evaluate(feature)
                s = QgsExpression('round("MaxIn", 3)')
                feature['MaxIn'] = s.evaluate(feature)
                feature['StdevIn'] = eStDevIn.evaluate(feature)
                s = QgsExpression('round("StdevIn", 4)')
                feature['StdevIn'] = s.evaluate(feature)
                vectorFile.updateFeature(feature)

                # Close edits and save changes to the shapefile.
                vectorFile.commitChanges()

                # Create empty array (basin) to hold the components of the zonal stats calculations.
                array_basin = []

                # Define basin ID (configured in the config file).
                d[ID_Field_Name] = feature[ID_Field_Name]

                # Assign values of dictionary keys to the zonal statistic outputs. > http://docs.qgis.org
                # /testing/en/docs/pyqgis_developer_cookbook/vector.html#retrieving-information-about-
                # attributes]. Other resources at http://stackoverflow.com/questions/1024847
                # /add-key-to-a-dictionary-in-python
                d['SNODAS_SWE_Mean_m'] = feature['Smean']
                d['SNODAS_SWE_Min_m'] = feature['Smin']
                d['SNODAS_SWE_Max_m'] = feature['Smax']
                d['SNODAS_SWE_StdDev_m'] = feature['Sstdev']
                d['SNODAS_Pixels_Count'] = feature['Scount']
                d['SNODAS_SnowCover_percent'] = feature['SnowCover']
                d['SNODAS_SWE_Mean_in'] = feature['MeanIn']
                d['SNODAS_SWE_Min_in'] = feature['MinIn']
                d['SNODAS_SWE_Max_in'] = feature['MaxIn']
                d['SNODAS_SWE_StdDev_in'] = feature['StDevIn']

                # Append current dictionary to the empty basin array. This array is exported to the
                # output .csv file at the end of this 'for' loop.
                array_basin.append(d.copy())

                # Append tcurrent dictionary to the empty basin array. This array is exported to the
                # output .csv file outside of this 'for' loop.
                array_date.append(d.copy())

                # Export the daily date array to a .csv file. Overwrite the .csv file if it already exists.
                # Reference: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
                with open(results_basin, 'ab') as csvfile:
                    csvwriter = csv.DictWriter(csvfile, delimiter=",", fieldnames=fieldnames)
                    for row in array_basin:
                        csvwriter.writerow(row)
                csvfile.close()

            # Delete attribute fields of the shapefile related to the daily calculated zonal statistics.
            indexForSMean = vectorFile.dataProvider().fieldNameIndex('Smean')
            indexForSMin = vectorFile.dataProvider().fieldNameIndex('Smin')
            indexForSMax = vectorFile.dataProvider().fieldNameIndex('Smax')
            indexForSStdDev = vectorFile.dataProvider().fieldNameIndex('Sstdev')
            indexForSCount = vectorFile.dataProvider().fieldNameIndex('Scount')
            indexForSSum = vectorFile.dataProvider().fieldNameIndex('Ssum')
            indexForSnowCover = vectorFile.dataProvider().fieldNameIndex('SnowCover')
            indexForMeanIn = vectorFile.dataProvider().fieldNameIndex('MeanIn')
            indexForMinIn = vectorFile.dataProvider().fieldNameIndex('MinIn')
            indexForMaxIn = vectorFile.dataProvider().fieldNameIndex('MaxIn')
            indexForStDevIn = vectorFile.dataProvider().fieldNameIndex('StDevIn')
            vectorFile.dataProvider().deleteAttributes([indexForSMean, indexForSMin, indexForSMax,
                                                           indexForSStdDev, indexForSCount, indexForSSum,
                                                           indexForSnowCover, indexForMeanIn, indexForMinIn,
                                                           indexForMaxIn, indexForStDevIn])

            # Update shapefile with its newly-deleted attribute fields.
            vectorFile.updateFields()

            # Create a string variable to be used as the title for the outputed .csv file - By Date
            results_date = 'SnowpackStatisticsByDate_' + date_name + '.csv'

            # Set directory to the directory where the output .csv daily files are contained. - By Date
            os.chdir(csv_byDate)

            # Update text file, ListOfDates.txt, with list of dates represented by csv files in ByDate folder
            array = glob.glob("*.csv")
            array.sort(reverse=True)

            with open("ListOfDates.txt", 'w') as output_file:
                for filename in array:
                    filename = filename.replace("SnowpackStatisticsByDate_", "")
                    filename = filename.replace(".csv", "")
                    output_file.write(filename + "\n")

            output_file.close()

            # Export the daily date array to a .csv file. Overwrite the .csv file if it already exists.
            # Reference: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
            with open(results_date, 'ab') as csvfile:
                csvwriter = csv.DictWriter(csvfile, delimiter=",", fieldnames=fieldnames)
                for row in array_date:
                    csvwriter.writerow(row)
            csvfile.close()

            # Return working directory back to its original setting before the script began.
            os.chdir(currdir)

            logger.info('zStat_and_export: Zonal statistics of %s are exported to %s' % (file, csv_byBasin))

            print ("Zonal statistics of %s are complete.") % date_name


        else:
            logger.info('zStat_and_export: %s is not a .tif file and the zonal statistics were not processed.' % file)

