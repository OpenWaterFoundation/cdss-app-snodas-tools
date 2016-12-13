# Name: SNODAS_utilities.py
# Author: Emma Giles
# Organization: Open Water Foundation
# Date Created: 11/21/2016
# Last Updated: 11/21/2016
#
#
# Purpose: This script holds the functions that will be utilized within the developed SNODAS tools. There are two other
#   .py scripts (the developed SNODAS tools) that are packaged with this .py script. The first script is called
#   userInputP1.1.py and the second is called automatedDailyP1.1.py. Both scripts process zonal statistics of SNODAS
#   raster datasets(minimum SWE, maximim SWE, mean SWE, standard deviation SWE, count of pixels within each boundary,
#   and percentage of ground covered by snow) with respect to the Colorado Basin boundaries. Both scripts call many of
#   the same functions defined in this .py script. automatedDailyP1.1.py will download today's date of SNODAS data and
#   will output the results in multiple .csv files (one .csv file for today's date and one .csv file for EACH basin in
#   the Colorado Basin boundaries dataset). userInputP1.1.py gives the user more freedom to determine which past dates
#   of SNODAS data they would like processed.


# Import necessary modules
import ftplib, os, tarfile, gzip, gdal, csv, logging
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsZonalStatistics
from qgis.core import QgsRasterLayer, QgsApplication, QgsVectorLayer, QgsField, QgsExpression
from PyQt4.QtCore import QVariant
from datetime import datetime, timedelta
from time import strptime
from shutil import copy

# Downloading functions
def download_today_SNODAS(downloadDir):
    """This function will access the SNODAS FTP site and download today's .tar file. The .tar file will be downloaded
    to the specified downloadDir. This function will only be utilized within the automatedDailyP1.1.py script.
    downloadDir: this should be the full path name to the location where the original SNODAS rasters will be stored"""

    logging.info('download_today_SNODAS: Starting')

    # Get today's date.
    now = datetime.now()

    logging.info("download_today_SNODAS: Today's date has been retrieved.")

    # Code format for the following block of code in reference to:
    # http://www.informit.com/articles/article.aspx?p=686162&seqNum=7 and
    # http://stackoverflow.com/questions/5230966/python-ftp-download-all-files-in-directory

    # Connect to FTP server
    ftp = ftplib.FTP('sidads.colorado.edu', 'anonymous', None)

    logging.info("download_today_SNODAS: Connected to server.")

    # Direct to folder within FTP site storing the SNODAS masked data.
    ftp.cwd('/DATASETS/NOAA/G02158/masked/')

    # Change local working directory to the directory where you want the files to download - this is variable
    # 'downloadDir'.
    os.chdir(downloadDir)

    # Move into the ftp folder that holds the data from today's year
    ftp.cwd(str(now.year) + '/')

    # Move into the ftp folder that holds the data from today's month
    if now.month == 1:
        ftp.cwd('01_Jan/')
    elif now.month == 2:
        ftp.cwd('02_Feb/')
    elif now.month == 3:
        ftp.cwd('03_Mar/')
    elif now.month == 4:
        ftp.cwd('04_Apr/')
    elif now.month == 5:
        ftp.cwd('05_May/')
    elif now.month == 6:
        ftp.cwd('06_Jun/')
    elif now.month == 7:
        ftp.cwd('07_Jul/')
    elif now.month == 8:
        ftp.cwd('08_Aug/')
    elif now.month == 9:
        ftp.cwd('09_Sep/')
    elif now.month == 10:
        ftp.cwd('10_Oct/')
    elif now.month == 11:
        ftp.cwd('11_Nov/')
    else:
        ftp.cwd('12_Dec/')

    # Sets day value as a double digit entity rather than a singular value ex. 7 will turn into 07
    if now.day == 1:
        day = '01'
    elif now.day == 2:
        day = '02'
    elif now.day == 3:
        day = '03'
    elif now.day == 4:
        day = '04'
    elif now.day == 5:
        day = '05'
    elif now.day == 6:
        day = '06'
    elif now.day == 7:
        day = '07'
    elif now.day == 8:
        day = '08'
    elif now.day == 9:
        day = '09'
    else:
        day = str(now.day)

    # Iterates through files in the ftp folder and saves today's data as a variable.
    filenames = ftp.nlst()
    for file in filenames:
        if file.endswith('%s.tar' % day):
            localfile = open(file, 'wb')
            ftp.retrbinary('RETR ' + file, localfile.write, 1024)

            # Logging note to inform level of processing
            logging.info("download_today_SNODAS: Download of %s from FTP site completed." % file)
            print "Download from FTP site completed. Please wait while the tool processes. This could take a few " \
                  "of minutes.\n"

    logging.info('download_today_SNODAS: Finished \n')
def download_user_single_date_SNODAS(downloadDir, singleDate):
    """This function will access the SNODAS FTP site and download the .tar file of the date that the user has defined as
    singleDate. The .tar file will be downloaded to the specified downloadDir. This function will also work for the
    range of dates. The range of dates will target one date at a time. That one date will be defined in the singleDate
    argument. The data from that date will be downloaded to the specificed downloadDir. This function will only be
    called within the userInputP1.1.py.
    downloadDir: this should be the full path name to the location where the original SNODAS rasters will be stored"""

    logging.info('download_user_single_date: Starting %s' % singleDate)

    # Code format for the following block of code in reference to:
    # http://www.informit.com/articles/article.aspx?p=686162&seqNum=7 and
    # http://stackoverflow.com/questions/5230966/python-ftp-download-all-files-in-directory
    # Connect to FTP server
    ftp = ftplib.FTP('sidads.colorado.edu', 'anonymous', None)

    logging.info('Connected to FTP server. Routing to %s' % singleDate)

    # Direct to folder within FTP site storing the SNODAS masked data.
    ftp.cwd('/DATASETS/NOAA/G02158/masked/')

    # Change local working directory to the directory where you want the files to download - this is variable
    # 'downloadDir'.
    os.chdir(downloadDir)

    # Move into the ftp folder that holds the data from today's year
    ftp.cwd(str(singleDate.year) + '/')

    # Move into the ftp folder that holds the data from today's month
    if singleDate.month == 1:
        ftp.cwd('01_Jan/')
    elif singleDate.month == 2:
        ftp.cwd('02_Feb/')
    elif singleDate.month == 3:
        ftp.cwd('03_Mar/')
    elif singleDate.month == 4:
        ftp.cwd('04_Apr/')
    elif singleDate.month == 5:
        ftp.cwd('05_May/')
    elif singleDate.month == 6:
        ftp.cwd('06_Jun/')
    elif singleDate.month == 7:
        ftp.cwd('07_Jul/')
    elif singleDate.month == 8:
        ftp.cwd('08_Aug/')
    elif singleDate.month == 9:
        ftp.cwd('09_Sep/')
    elif singleDate.month == 10:
        ftp.cwd('10_Oct/')
    elif singleDate.month == 11:
        ftp.cwd('11_Nov/')
    else:
        ftp.cwd('12_Dec/')

    # Sets day value as a double digit entity rather than a singular value ex. 7 will turn into 07
    if singleDate.day == 1:
        day = '01'
    elif singleDate.day == 2:
        day = '02'
    elif singleDate.day == 3:
        day = '03'
    elif singleDate.day == 4:
        day = '04'
    elif singleDate.day == 5:
        day = '05'
    elif singleDate.day == 6:
        day = '06'
    elif singleDate.day == 7:
        day = '07'
    elif singleDate.day == 8:
        day = '08'
    elif singleDate.day == 9:
        day = '09'
    else:
        day = str(singleDate.day)

    # Iterates through files in the ftp folder and saves today's data as a variable.
    filenames = ftp.nlst()
    for file in filenames:
        if file.endswith('%s.tar' % day):
            localfile = open(file, 'wb')
            ftp.retrbinary('RETR ' + file, localfile.write, 1024)

            # Logging note to inform level of processing
            logging.info('Downloaded %s' % singleDate)
            print "Download from FTP site completed. Please wait while the tool processes. This could take a couple " \
                  "of minutes.\n"

    logging.info('download_user_single_date: Finished %s \n' % singleDate)

# Formatting function
def get_date_string(date):
    """This function will take a datetime date and will convert it into a string date in the following format:
     YYYYMMDD.
     date: this should be a date developed from the imported datetime.datetime module"""

    logging.info('get_date_string: Starting %s' % date)

    # Parses the year, month and day of the input date into separate entities.
    year = date.year
    month = str(date.month)
    day = str(date.day)

    # Sets month value as a double-digit entity rather than a singular value ex. 1 will turn into 01
    if month == '1':
        month_name = '01'
    elif month == '2':
        month_name = '02'
    elif month == '3':
        month_name = '03'
    elif month == '4':
        month_name = '04'
    elif month == '5':
        month_name = '05'
    elif month == '6':
        month_name = '06'
    elif month == '7':
        month_name = '07'
    elif month == '8':
        month_name = '08'
    elif month == '9':
        month_name = '09'
    else:
        month_name = month

    # Sets day value as a double-digit entity rather than a singular value ex. 7 will turn into 07
    if day == '1':
        day_name = '01'
    elif day == '2':
        day_name = '02'
    elif day == '3':
        day_name = '03'
    elif day == '4':
        day_name = '04'
    elif day == '5':
        day_name = '05'
    elif day == '6':
        day_name = '06'
    elif day == '7':
        day_name = '07'
    elif day == '8':
        day_name = '08'
    elif day == '9':
        day_name = '09'
    else:
        day_name = day

    # Concatenates the strings of the year, double-digit month, and double-digit day.
    day_string = str(year) + month_name + day_name

    logging.info('get_date_string: Finished %s \n' % date)

    # Returns string value for use within the remaining script.
    return day_string

# Converting SNODAS data into usable format functions
def untar_SNODAS_file(file, folder_input, folder_output):
    """This function will untar the downloaded SNODAS .tar file and will extract the files within the folder_output
    file: this should be the name of the SNODAS .tar file that is to be untarred
    folder_input: this should be the full pathname to the folder holding the file
    folder_output: this should be the full pathname to the folder that will store the extracted files"""

    logging.info('untar_SNODAS_file: Starting %s' % file)

    # Checks to make sure that file is a .tar file
    file_upper = file.upper()
    if file_upper.endswith('.TAR'):

        # Sets full path name of the file
        file_full = os.path.join(folder_input, file)

        # Opens the tar file
        tar = tarfile.open(file_full)

        # Changes working directory to location of folder
        os.chdir(folder_output)

        # Extracts the .tar file and places the contents in the working directory
        tar.extractall()

        # Closes the tar file
        tar.close

        logging.info('untar_SNODAS_file: %s has been untarred.' % file)

    else:
        logging.info('untar_SNODAS_file: %s is not a .tar file and has not been untarred.' % file)

    logging.info('untar_SNODAS_file: Finished %s \n' % file)
def delete_irrelevant_SNODAS_files(file):
    """The SNODAS .tar files contain many different SNODAS datasets. For this project we are only interested in the SWE
     raster sets. The SWE rasters are named with a unique ID of '1034'. This function will delete a file if it is
     not identified by this unique ID.
     file: this should be the name of the raster extracted from the downloaded SNODAS .tar file"""

    logging.info('delete_irrelevant_SNODAS_files: Starting %s' % file)

    # Checks to determine if file name has unique identifier '1034'.
    if '1034' not in str(file):

        # Deletes file
        os.remove(file)
        logging.info('delete_irrelevant_SNODAS_files: %s has been deleted.' % file)

    else:

        logging.info('delete_irrelevant_SNODAS_files: %s has the unique code 1034 and has not been deleted.' % file)

    logging.info('delete_irrelevant_SNODAS_files: Finished %s \n' % file)
def extract_SNODAS_gz_file(file):
    """Each daily SNODAS raster has two files associated with it, a .dat file and .Hdr file. Both are zipped within a
    .gz file. This function will extract the .dat and .Hdr files from a SNODAS .gz file.
    file: this should be the name of the .gz file that is to be extracted"""

    logging.info('extract_SNODAS_gz_file: Starting %s' % file)

    # Checks to make sure that file is a .gz file
    file_upper = file.upper()
    if file_upper.endswith('.GZ'):

        # This block of script was based off of the script from the following resource:
        # http://stackoverflow.com/questions/20635245/using-gzip-module-with-python
        inF = gzip.open(file, 'rb')
        outF = open(file[0:46], 'wb')
        outF.write(inF.read())
        inF.close()
        outF.close()

        # Deletes the .gz file
        os.remove(file)

        logging.info('extract_SNODAS_gz_file: %s has been extracted' % file)

    else:
        logging.info('extract_SNODAS_gz_file: %s is not of .gz format and was not extracted.' % file)

    logging.info('extract_SNODAS_gz_file: Finished %s \n' % file)
def convert_SNODAS_dat_to_bil(file):
    """The .dat and .Hdr files are not appropriate file formats to use Qgs processing tools. The Qgs processing tools
    will be used to calculate the daily zonal statistics. This function converts a SNODAS .dat file into a SNODAS .tif
    file.
    file: this is the name of the .dat file to be converted to .bil format"""

    logging.info('convert_SNODAS_dat_to_bil: Starting %s' % file)

    # Checks to make sure that file is a .dat file
    file_upper = file.upper()
    if file_upper.endswith('.DAT'):

        # Changes the file name ending from .dat to .bil
        new_name = file.replace('.dat', '.bil')
        os.rename(file, new_name)

        logging.info('convert_SNODAS_dat_to_bil: %s has been converted into .bil format' % file)

    else:
        logging.info('convert_SNODAS_dat_to_bil: %s is not a .dat file and has not been converted into .bil format' % file)

    logging.info('convert_SNODAS_dat_to_bil: Finished %s \n' % file)
def create_SNODAS_hdr_file(file):
    """A custom .Hdr file needs to be created in order to tell the computer what raster settings the .bil file holds.
    This created .Hdr file will be used to convert the .bil file to a usable .tif file.
    file: this is the name of the .bil file that needs a .Hdr component"""

    logging.info('create_SNODAS_hdr_file: Starting %s' % file)

    # Checks to make sure that file is a .bil file
    file_upper = file.upper()
    if file_upper.endswith('.BIL'):

        # Creates a name for the new .hdr file
        hdr_name = file.replace('.bil', '.hdr')

        # These lines of code create a custom .hdr file to give the specific about the .bil/raster file. The
        # specifics inside each .hdr file are the same for each daily raster. However, there must be a .hdr file
        # that matches the name of each .bil/.tif file in order for QGIS to import each dataset.
        file2 = open(hdr_name, 'w')
        file2.write('units dd\n')
        file2.write('unites dd\n')
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

        logging.info('create_SNODAS_hdr_file: %s now has a created .Hdr component.' % file)

    else:
        logging.info('create_SNODAS_hdr_file: %s is not a .bil file and an .Hdr component file has not been created.' % file)

    logging.info('create_SNODAS_hdr_file: Finished %s \n' % file)
def delete_any_SNODAS_txt_files(file):
    """This function will delete any .txt files that were created within the folder and convert them to the correct
    .Hdr file format.
    file: this is the name of the file within the folder to be checked for .txt format"""

    logging.info('delete_any_SNODAS_txt_files: Starting %s' % file)

    # Ensures that the created .hdr file is actually of .hdr format rather than of .txt format. If the file ends
    # with .txt, it is replaced with a .hdr extension.
    file_upper = file.upper()
    if file_upper.endswith('.TXT'):

        # Replaces .txt with .Hdr
        new_name = file.replace('txt', 'Hdr')
        os.rename(file, new_name)

        logging.info('delete_any_SNODAS_txt_files: Deleted %s' % file)

    else:
        logging.info('delete_any_SNODAS_txt_files: %s is not a .txt file and has not been deleted.' % file)

    logging.info('delete_any_SNODAS_txt_files: Finished %s \n' % file)
def convert_SNODAS_bil_to_tif(file, folder_output):
    """This function converts the .bil file into a usable .tif file for future processing within the QGS environment.
    file: this is the name of tht file to be converted into a .tif file
    folder_output: this is the full pathname to the location where the created .tif files will be stored"""

    logging.info('convert_SNODAS_bil_to_tif: Starting %s' % file)

    # Checks to make sure that file is a .bil file
    file_upper = file.upper()
    if file_upper.endswith('.BIL'):

        # Assigns new name by replacing .bil with .tif
        new_name = file.replace('.bil', '.tif')

        # Sets full pathname
        file_full = os.path.join(folder_output, new_name)

        # Converts file to .tif format
        gdal.Translate(file_full, file, format='GTiff')

        logging.info('convert_SNODAS_bil_to_tif: %s has been converted into a .tif file.' % file)

    else:
        logging.info('convert_SNODAS_bil_to_tif: %s is not a .bil file and has not been converted into a .tif file.' % file)

    logging.info('convert_SNODAS_bil_to_tif: Finished %s \n' % file)
def delete_SNODAS_bil_file(file):
    """The .bil and .hdr formats are no longer important to keep in storage becasue the newly created .tif file holds
    the same data. This function will delete the file if the file is of .bil or .hdr format.
    file: this is the name of the file to be checked for either .hdr or .bil format (and, ultimately deleted)"""

    logging.info('delete_SNODAS_bil_file: Starting %s' % file)

    # Checks to make sure that file is a .bil or .Hdr file
    file_upper = file.upper()
    if file_upper.endswith('.BIL') or file_upper.endswith('.HDR'):

        # Deletes file
        os.remove(file)

        logging.info('delete_SNODAS_bil_file: %s has been deleted.' % file)

    else:
        logging.info('delete_SNODAS_bil_file: %s is not a .bil file or a .hdr file. It has not been deleted.' % file)

    logging.info('delete_SNODAS_bil_file: Finished %s \n' % file)

# Assigning projections and clipping functions
def copy_and_move_SNODAS_tif_file(file, folder_output):
    """This function will copy and move the created .tif file from its original location to the folder_output.
    file: the name of the .tif file to be copied and moved to another location
    folder_output: the full pathname to the folder that will hold the newly copied .tif file"""

    logging.info('copy_and_move_SNODAS_tif_file: Starting %s' % file)

    # Sets full path name of file
    file_full_output = os.path.join(file, folder_output)

    # Ensures that the file is of .tif format
    file_upper = file.upper()
    if file_upper.endswith(".TIF"):

        # Copies file and moves the copy to file_full_output
        copy(file, file_full_output)

        logging.info('copy_and_move_SNODAS_tif_file: %s has been copied and moved to %s' % (file, folder_output))

    else:
        logging.info('copy_and_move_SNODAS_tif_file: %s is not a .tif file and has not been copied and moved to %s' % (file, folder_output))

    logging.info('copy_and_move_SNODAS_tif_file: Finished %s \n' % file)
def assign_SNODAS_projection_WGS84(file, folder):
    """The downloaded SNODAS raster does not have a projection. This function will assign projection WGS84 to the file
    file: the name of the .tif file that is to be assigned a projection
    folder: the full pathname to the folder where both the unprojected and projected raster is/will be stored"""

    logging.info('assign_SNODAS_projection_WGS84: Starting %s' % file)

    # Checks for unprojected .tif rasters to apply the gdal.Translate 'Define Projection'.
    file_upper = file.upper()
    if file_upper.endswith('HP001.TIF'):

        # Changes raster name from 'us_ssmv11034tS__T0001TTNATS2003093005HP001.tif' to '20030930WGS84.tif'
        file_new = file.replace('05HP001', 'WGS84')
        file_new2 = file_new.replace('us_ssmv11034tS__T0001TTNATS', '')

        # Set up for gdal.Translate tool. Sets full path names for both the input and output raster.
        input_raster = os.path.join(folder, file)
        output_raster = os.path.join(folder, file_new2)

        # Assigns WGS84 projection ('EPSG:4326') to the raster.
        gdal.Translate(output_raster, input_raster, outputSRS='EPSG:4326')

        # Deletes unprojected file
        os.remove(input_raster)

        logging.info('assign_SNODAS_projection_WGS84: %s has been assigned a WGS84 projection.' % file)

    else:
        logging.info("assign_SNODAS_projection_WGS84: %s does not end in 'HP001.tif' and has not been assigned a WGS84 projection." % file)

    logging.info('assign_SNODAS_projection_WGS84: Finished %s \n' % file)
def SNODAS_raster_clip_WGS84(file, folder, vector_extent):
    """This function will clip the file (raster) by the extent of vector_extent. The output file will  start with
    'Clip'
    file: the name of the projected (WGS84) .tif file that will be clipped
    folder: the full pathname to the folder where both the unclipped and clipped raster is/will be stored
    vector_extent: the full pathname to the shapefile holding the extent of the Colorado Basin boundaries. This
    shapefile should be projected in WGS84 rather than NAD83"""

    logging.info('SNODAS_raster_clip_WGS84: Starting %s' % file)

    # Ensures that the clipping is only taking place on projected WGS84.tif file
    file_upper = file.upper()
    if file_upper.endswith('WGS84.TIF'):

        # Changes name to add Clip at the beginning of the file name
        date_name = 'Clip' + str(file)

        # Sets full path name of both the input and output file that will be used in the gdal.Warp tool
        file_full_input = os.path.join(folder, file)
        file_full_output = os.path.join(folder, date_name)

        # Clips each daily .tif file by the input shapefile (CO Basins)
        # Reference http://gdal.org/python/ to get more information on the gdal.WarpOptions parameters
        gdal.Warp(file_full_output, file_full_input, format='GTiff', xRes=0.00833333333333, yRes=0.00833333333333,
                  dstNodata='-9999', cutlineDSName=vector_extent, cropToCutline=True)

        # Deletes unclipped rasters
        os.remove(file_full_input)

        logging.info('SNODAS_raster_clip_WGS84: %s has been clipped.' % file)

    else:
        logging.info('SNODAS_raster_clip_WGS84: %s does not end with WGS84.tif and the clip was not processed on this raster.' % file)

    logging.info('SNODAS_raster_clip_WGS84: Finished %s \n' % file)
def SNODAS_raster_reproject_NAD83(file, folder):
    """Reprojects the clipped raster input from it's original projection of WGS84 to our desired projection of NAD83
    UTM Zone 13N.
    file: the name of the clipped file with a WGS84 projection to be reprojected into NAD83
    folder: the full pathname to the folder where both the WGS84 clipped raster and the NAD83 clipped raster is/will be
    stored"""

    logging.info('SNODAS_raster_reproject_NAD83: Starting %s' % file)

    # Ensures that the reprojection is only taking place with the proper file
    if file.startswith('Clip'):

        # Changes naming convention from 'Clip' prefix to 'Repj'
        new_name1 = file.replace("Clip", "Repj")
        new_name = new_name1.replace("WGS84", "")

        # Sets full path name of both the input and output file that will be used in the gdal.Warp tool
        file_full_input = os.path.join(folder, file)
        file_full_output = os.path.join(folder, new_name)

        # Reprojects the clipped SNODAS .tif files from WGS 84 to NAD 83 UTM Zone 13
        gdal.Warp(file_full_output, file_full_input, format='GTiff', srcSRS='EPSG:4326', dstSRS='EPSG:26913')

        # Deletes WGS84 clipped file
        os.remove(file_full_input)
        logging.info('SNODAS_raster_reproject_NAD83: %s has been reprojected from WGS84 to NAD83' % file)

    else:
        logging.info("SNODAS_raster_reproject_NAD83: %s does not start with 'Clip' and will not be reprojected." % file)

    logging.info('SNODAS_raster_reproject_NAD83: Finished %s \n' % file)

# Creating binary snow cover raster function
def snowCoverage(file, folder_input, folder_output):
    """This function will create a binary .tif raster that displays snow coverage. If a pixel in the input file is
    greater than 0 (there is snow on the ground) then the new raster's pixel will have the value of 1. If a pixel in
    the input raster is 0 or a null value (there is no snow on the ground) then the new raster's pixel will have the
    value of 0. The output raster will be used to calculate the percent of daily snow coverage for each basin.
    Checks to ensure that the code only runs on today's raster. The output .tif file will be saved in folder_output.
    file: the name of the daily SNODAS SWE .tif raster that is to be the input of the created binary raster
    folder_input: the full pathname to the folder where the file is stored
    folder_output: the full pathname to the folder where the newly created binary snow cover raster will be stored"""

    logging.info('snowCoverage: Starting %s' % file)

    # Ensures that the raster calculation is only operated on .tif files starting with 'Repj'
    if file.startswith('Repj'):

        # Sets full pathname variables for input into later raster calculator options
        file_full_input = os.path.join(folder_input, file)
        file_full_output = os.path.join(folder_output, file)

        # Checks to see if the file has already been processed.
        if not os.path.exists(file_full_output):

            logging.info('snowCoverage: Enveloping %s as a QGS raster object layer' % file)

            # Envelops the current file as a QGS object raster layer
            rLyr = QgsRasterLayer(file_full_input, '%s' % file)

            # Checks to make sure that the QGS environment successfully accepts the file
            if rLyr.isValid():

                # Sets name (without the .tif extension) for input into the raster calculator expression. The @1 means
                # that the calculation will be occuring on band 1 of the raster.
                rasterinput = file[0:12]
                rastercalcname = rasterinput + '@1'

                # Sets the variables for the raster calculator options/settings. Refer to: http://gis.stackexchange.com/
                # questions/141659/qgis-from-console-raster-algebra
                resultingLayer = QgsRasterCalculatorEntry()
                resultingLayer.ref = rastercalcname
                resultingLayer.raster = rLyr
                resultingLayer.bandNumber = 1
                entries = [resultingLayer]

                # Sets the raster calculator options/settings. (expression, output path, output type, output extent, output
                # width, output height, entries)
                calc = QgsRasterCalculator('(%s)>0' % rastercalcname, '%s' % file_full_output, 'GTiff',
                                           rLyr.extent(),
                                           rLyr.width(),
                                           rLyr.height(), entries)

                # Calls calculation to begin
                calc.processCalculation()

                logging.info('snowCoverage: Snow calculations for %s complete.' % file)

            else:
                logging.warning('snowCoverage: %s is not a valid object raster layer.' % file)

        # Skips to the next raster in the directory if the raster has already been processed by this script.
        else:
            logging.info("snowCoverage: %s has previously been processed so no raster calculation took place." % file)
    else:
        logging.info("snowCoverage: %s does not start with 'Repj' and no raster calculation took place." % file)

    logging.info('snowCoverage: Finished %s \n' % file)

# Calculating zonal statistics and exporting functions
def create_csv_files(file, vFile, csv_byDate, csv_byBasin):
    """This function creates the needed csv files for output - both by date and by basin. The csv files by date will be
    one .csv file for each date and will be titled 'ResultsByDateYYYYMMDD.csv'. Each byDate file will contain the zonal
    statistics for each basin on that date. The csv files by basin will be one .csv file for each Colorado basin and
    will be titled 'ResultsByBasin(BasinId)'. Each byBasin file will contain the zonal statistics for that basin for
    each date that has been processed.
    file: the daily .tif SNODAS raster file that is to be processed with zonal statistics (clipped, NAD83)
    vFile: the shapefile of the Colorado basin boundaries (these boundaries will be used as the polygons in the zonal
    statistics calculations)
    csv_byDate: the full pathname to the folder holding the results by date (.csv file)
    csv_byBasin: the full pathname to the folder holding the results by basin (.csv file)"""

    # Envelops the input shapefile (in our case, the Colorado River Basin NAD83 shapefile) as a QGS object vector layer
    vectorFile = QgsVectorLayer(vFile, 'Colorado Basins NAD83', 'ogr')

    # Checks to determine if the shapefile is valid as an object. If this test shows that the vector is not a valid
    # vector file, the script will not run the zonal statistic processing (located in the 'else' block of code). If the
    # user gets the  following error message, it is important to address the initialization of the QGIS resources.
    if vectorFile.isValid() == False:
        logging.warning('ZStat_SNODAS_byBasin: Vector shapefile is not a valid QGS object layer.')
    else:
        # Holds the current directory in a variable, currdir, that will be called at the end of the script. This is
        # important so that the script will not change the original settings of the computer that is running this tool.
        currdir = os.getcwd()

        # Gets date of current file
        date_name = file[4:12]

        # Defines the field names for out the output .csv files. These MUST match the keys of the dictionaries. These
        # fieldnames will be the header row for the outputed .csv files. The column headers of the .csv files will be in
        # sequential order as layed out in the fieldnames list.
        fieldnames = ['Date_YYYYMMDD', 'Local_ID', 'Mean_meters', 'Minimum_meters', 'Maximum_meters',
                      'StdDev_meters', 'Count_pixels', 'SnowCover_percent', 'Mean_inches', 'Min_inches',
                        'Max_inches', 'StDev_inches']

        # Creates a string variable that will be used as the title for the outputed .csv file - By Date
        results_date = 'ResultsByDate' + date_name + '.csv'

        # Checks to see if the output file has already been created. If so, the script moves onto the raster
        # processing. - By Date
        if not os.path.exists(os.path.join(csv_byDate, results_date)):

            # Sets directory to the directory where the outputed .csv daily files will be stored. - By Date
            os.chdir(csv_byDate)

            logging.info('ZStat_SNODAS_byDate: Creating %s' % results_date)

            # Creates a.csv file with the appropriate fieldnames as the info in the header row. - By Date
            with open(results_date, 'wb') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
                writer.writeheader()
            csvfile.close()
        else:
            pass

        # Accesses the features of the CO Basin shapefile.
        iter = vectorFile.getFeatures()

        # Iterates through each basin of the Colorado River Basin shapefile.
        for feature in iter:

            # Creates a string variable that will be used as the title for the outputed .csv file - By Basin
            results_basin = 'ResultsByBasin' + feature[2] + '.csv'

            # Checks to see if the output file has already been created. If so, the script moves onto the raster
            # processing. If not, a .csv file is created with the appropriate fieldnames as the info in the
            # header row. - By Basin
            if not os.path.exists(os.path.join(csv_byBasin, results_basin)):

                # Sets directory to the directory where the outputed .csv daily files will be stored - By Basin
                os.chdir(csv_byBasin)

                logging.info('ZStat_SNODAS_byBasin: Creating %s' % results_basin)

                # Creates a.csv file with the appropriate fieldnames as the info in the header row. - By Date
                with open(results_basin, 'wb') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
                    writer.writeheader()
                csvfile.close()

                # Retrun directory back to original
                os.chdir(currdir)
            else:
                pass
def zStat_and_export(file, vFile, csv_byBasin, csv_byDate, DirClip, DirSnow):
    """This function will calculate the zonal statistics of the Colorado basin shapefile and the current raster. The
    zonal statistics will be exported to both the byDate and the byBasin csv files.
    file: the daily raster .tif SNODAS file that is to be processed in the zonal statistics tool (clipped, NAD83)
    vfile: he shapefile of the Colorado basin boundaries (these boundaries will be used as the polygons in the zonal
    statistics calculations)
    csv_byDate: the full pathname to the folder holding the results by date (.csv file)
    csv_byBasin: the full pathname to the folder holding the results by basin (.csv file)
    DirClip: the full pathname to the folder holding all of the daily clipped, NAD83 .tif SNODAS rasters
    DirSnow: the full pathname to the folder holding all of the binary snow coverage rasters"""

    # Creates an empty dictionary. This empty dictionary will be used as a placeholder for the zonal statistic outputs
    # before they are written to the .csv file.  The shapefile 'CO_basins_NAD83' has a limited number of fields
    # available in the attribute table so the zonal statistics must be calculated, exported and then deleted from the
    # shapefile.
    d = {}

    # Holds the current directory in a variable, currdir, that will be called at the end of the script. This is
    # important so that the script will not change the original settings of the computer that is running this tool.
    currdir = os.getcwd()

    # Defines the field names for out the output .csv files. These MUST match the keys of the dictionaries. These
    # fieldnames will be the header row for the outputed .csv files. The column headers of the .csv files will be in
    # sequential order as layed out in the fieldnames list.
    fieldnames = ['Date_YYYYMMDD', 'Local_ID', 'Mean_meters', 'Minimum_meters', 'Maximum_meters',
                      'StdDev_meters', 'Count_pixels', 'SnowCover_percent', 'Mean_inches', 'Min_inches',
                        'Max_inches', 'StDev_inches']

    # Envelops the input shapefile (in our case, the Colorado River Basin NAD83 shapefile) as a QGS object vector layer
    vectorFile = QgsVectorLayer(vFile, 'Colorado Basins NAD83', 'ogr')

    # Checks to determine if the shapefile is valid as an object. If this test shows that the vector is not a valid
    # vector file, the script will not run the zonal statistic processing (located in the 'else' block of code). If the
    # user gets the  following error message, it is important to address the initialization of the QGIS resources.
    if vectorFile.isValid() == False:
        logging.warning('ZStat_SNODAS_byDate: Vector shapefile is not a valid QGS object layer.')

    else:
        # Gets date of current file
        date_name = file[4:12]

        # Ensures that only .tif files are processed.
        file_upper = file.upper()
        if file_upper.endswith('.TIF'):

            # Accesses the features of the CO Basin shapefile.
            iter = vectorFile.getFeatures()

            # Iterates through each basin of the Colorado River Basin shapefile.
            for feature in iter:

                # Creates a string variable that will be used as the title for the outputed .csv file - By Basin
                results_basin = 'ResultsByBasin' + feature[2] + '.csv'

            # Sets directory to the directory where the outputed .csv daily files will be stored - By Basin
            os.chdir(csv_byBasin)

            # Checks to see if the daily raster has already been processed.
            if date_name in open(results_basin).read():
                logging.info(
                'ZStat_SNODAS_byBasin: Raster %s has already been processed and the results are in the .csv files.' % file)
            else:
                # Creates the date value of the working dictionary.
                d['Date_YYYYMMDD'] = date_name

                logging.info('ZStat_SNODAS_byBasin: Processing zonal statistics by basin of %s ...' % file)

                # Sets full pathname of raster for later input into the zonal stat tool
                raster_pathH = os.path.join(DirClip, file)
                raster_pathS = os.path.join(DirSnow, file)

                # Sets the input object options for the zonal stat tool - Mean.
                # [input shapefile (must be a valid QGS vector layer), input raster (must be the full pathname),
                # string (this is the title of the attribute table field header that will display the zonal stat.
                # Note that it will never be seen by the user because the zonal statistic attribute field will be
                # deleted later in this script), band of raster in which the calculations will be processed,
                # statistic type]
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Mean)
                # Calls the zonal stat tool to start processing with the above set properties
                zonalStats.calculateStatistics(None)

                # Sets the expression that will be used in the raster calculator to populate the 'Mean' field.
                eMean = QgsExpression('Smean / 1000')
                eMean.prepare(vectorFile.pendingFields())

                # Sets the input object options for the zonal stat tool - Minimum
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Min)
                # Calls the zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Sets the expression that will be used in the raster calculator to populate the 'Min' field.
                eMin = QgsExpression('Smin / 1000')
                eMin.prepare(vectorFile.pendingFields())

                # Sets the input object options for the zonal stat tool - Maximum
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Max)
                # Calls the zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Sets the expression that will be used in the raster calculator to populate the 'Max' field.
                eMax = QgsExpression('Smax / 1000')
                eMax.prepare(vectorFile.pendingFields())

                # Sets the input object options for the zonal stat tool - Standard Deviation
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.StDev)
                # Calls the zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Sets the expression that will be used in the raster calculator to populate the 'Std Dev' field.
                eStd = QgsExpression('Sstdev / 1000')
                eStd.prepare(vectorFile.pendingFields())

                # Sets the input object options for the zonal stat tool - Count
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathH, "S", 1, QgsZonalStatistics.Count)
                # Calls the zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Sets the input object options for the zonal stat tool - Sum of snow cover raster
                zonalStats = QgsZonalStatistics(vectorFile, raster_pathS, "S", 1, QgsZonalStatistics.Sum)
                # Calls the zonal stat tool to start processing
                zonalStats.calculateStatistics(None)

                # Open vectorFile for editing - http://gis.stackexchange.com/questions/34974/is-it-possible-to-
                # programmatically-add-calculated-fields/59724#59724
                vectorFile.startEditing()

                # Adds a new field to the shapefile titled 'SnowCover'. This holds integer type data. This field
                # will hold the raster calculator outputs that determine the percentage of basin area covered by
                # snow.
                newField = QgsField('SnowCover', QVariant.Int)
                vectorFile.dataProvider().addAttributes([newField])

                # Adds new fields to the shapefile to calculate SWE statistics in inches
                newFieldmean = QgsField('MeanIn', QVariant.Int)
                vectorFile.dataProvider().addAttributes([newFieldmean])
                newFieldmin = QgsField('MinIn', QVariant.Int)
                vectorFile.dataProvider().addAttributes([newFieldmin])
                newFieldmax = QgsField('MaxIn', QVariant.Int)
                vectorFile.dataProvider().addAttributes([newFieldmax])
                newFieldstdev = QgsField('StDevIn', QVariant.Int)
                vectorFile.dataProvider().addAttributes([newFieldstdev])
                vectorFile.updateFields()

                # Sets the expression that will be used in the raster calculator to populate the 'SnowCover' field.
                e = QgsExpression('Ssum / Scount * 100')
                e.prepare(vectorFile.pendingFields())

                # Sets the expresson that will be used in the raster calculator to populate the '...In' fields.
                # 39.37008 is 3.28084 (feet in a meter) multiplied by 12 (inches in a foot).
                eMeanIn = QgsExpression('Smean * 39.37008')
                eMeanIn.prepare(vectorFile.pendingFields())
                eMinIn = QgsExpression('Smin * 39.37008')
                eMinIn.prepare(vectorFile.pendingFields())
                eMaxIn = QgsExpression('Smax * 39.37008')
                eMaxIn.prepare(vectorFile.pendingFields())
                eStDevIn = QgsExpression('Sstdev * 39.37008')
                eStDevIn.prepare(vectorFile.pendingFields())

                # Creates an empty array to hold the components of the zonal stats calculations dictionary. This
                # array will be copied to the outputed .csv file and then will be erased only to be filled again
                # with the next daily raster's dictionary calculations. - By Date. There are two arrays in this
                # function, array_date and array_basin. The main difference is that the array_basin only holds one
                # dictionary at a time before it writes to a .csv file (one dictionary per basin and then the
                # information is deleted). The array_date holds multiple dictionaries at one time (one dictionary
                # per basin. The information in the array is only deleted after the date changes).
                array_date = []

                # Accesses the features of the CO Basin shapefile.
                iter = vectorFile.getFeatures()

                # Sets directory to the directory where the outputed .csv daily files will be stored - By Basin
                os.chdir(csv_byBasin)

                # Iterates through each basin of the Colorado River Basin shapefile.
                for feature in iter:

                    # Creates a string variable that will be used as the title for the outputed .csv file - By Basin
                    results_basin = 'ResultsByBasin' + feature[2] + '.csv'

                    # Calculates snow coverage percent. Adds the calculation to created field index 16 - 'SnowCover'
                    feature[16] = e.evaluate(feature)
                    # Rounds snow coverage percent to one decimal place.
                    s = QgsExpression('round("SnowCover", 1)')
                    feature[16] = s.evaluate(feature)
                    vectorFile.updateFeature(feature)

                    # Calculates mean SWE. Adds the calculation to created field index 10
                    feature[10] = eMean.evaluate(feature)
                    # Rounds mean SWE to three decimal places.
                    s = QgsExpression('round("Smean", 3)')
                    feature[10] = s.evaluate(feature)
                    vectorFile.updateFeature(feature)

                    # Calculates minimum SWE. Adds the calculation to created field index 11
                    feature[11] = eMin.evaluate(feature)
                    vectorFile.updateFeature(feature)

                    # Calculates maximum SWE. Adds the calculation to created field index 12
                    feature[12] = eMax.evaluate(feature)
                    vectorFile.updateFeature(feature)

                    # Calculates standard deviation SWE. Adds the calculation to created field index 13
                    feature[13] = eStd.evaluate(feature)
                    # Rounds standard deviation SWE to four decimal places.
                    s = QgsExpression('round("Sstdev", 4)')
                    feature[13] = s.evaluate(feature)
                    vectorFile.updateFeature(feature)

                    # Calculates inches SWE statistics and rounds to 2 decimal places.
                    feature[17] = eMeanIn.evaluate(feature)
                    s = QgsExpression('round("MeanIn", 3)')
                    feature[17] = s.evaluate(feature)
                    feature[18] = eMinIn.evaluate(feature)
                    s = QgsExpression('round("MinIn", 3)')
                    feature[18] = s.evaluate(feature)
                    feature[19] = eMaxIn.evaluate(feature)
                    s = QgsExpression('round("MaxIn", 3)')
                    feature[19] = s.evaluate(feature)
                    feature[20] = eStDevIn.evaluate(feature)
                    s = QgsExpression('round("StdevIn", 4)')
                    feature[20] = s.evaluate(feature)
                    vectorFile.updateFeature(feature)

                    # Close edits and save changes to the shapefile.
                    vectorFile.commitChanges()

                    # Creates an empty array (basin) to hold the components of the zonal stats calculations.
                    array_basin = []

                    # Defines feature ID by accessing the third column of the shapefile's attribute table
                    d['Local_ID'] = feature[2]

                    # Assigns values of dictionary keys to the zonal statistic outputs. > http://docs.qgis.org
                    # /testing/en/docs/pyqgis_developer_cookbook/vector.html#retrieving-information-about-
                    # attributes]. Other resources at http://stackoverflow.com/questions/1024847
                    # /add-key-to-a-dictionary-in-python
                    d['Mean_meters'] = feature[10]
                    d['Minimum_meters'] = feature[11]
                    d['Maximum_meters'] = feature[12]
                    d['StdDev_meters'] = feature[13]
                    d['Count_pixels'] = feature[14]
                    d['SnowCover_percent'] = feature[16]
                    d['Mean_inches'] = feature[17]
                    d['Min_inches'] = feature[18]
                    d['Max_inches'] = feature[19]
                    d['StDev_inches'] = feature[20]

                    # Appends the current dictionary to the empty basin array. This array will be exported to the
                    # output .csv file at the end of this for loop.
                    array_basin.append(d.copy())

                    # Appends the current dictionary to the empty basin array. This array will be exported to the
                    # output .csv file in a separate function.
                    array_date.append(d.copy())

                    # Exports the daily date array to a .csv file. Overwrites the .csv file if it already exists.
                    # Reference: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
                    with open(results_basin, 'ab') as csvfile:
                        csvwriter = csv.DictWriter(csvfile, delimiter=",", fieldnames=fieldnames)
                        for row in array_basin:
                            csvwriter.writerow(row)
                    csvfile.close()

                # Deletes attribute fields of the shapefile related to the daily calculated zonal statistics.
                vectorFile.dataProvider().deleteAttributes([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

                # Updates the shapefile with its newly-deleted attribute fields.
                vectorFile.updateFields()

                # Creates a string variable that will be used as the title for the outputed .csv file - By Date
                results_date = 'ResultsByDate' + date_name + '.csv'

                # Sets directory to the directory where the outputed .csv daily files will be stored. - By Date
                os.chdir(csv_byDate)

                # Exports the daily date array to a .csv file. Overwrites the .csv file if it already exists.
                # Reference: http://stackoverflow.com/questions/28555112/export-a-simple-dictionary-into-excel-file-in-python
                with open(results_date, 'ab') as csvfile:
                    csvwriter = csv.DictWriter(csvfile, delimiter=",", fieldnames=fieldnames)
                    for row in array_date:
                        csvwriter.writerow(row)
                csvfile.close()

                # Returns working directory back to its original setting before the script began.
                os.chdir(currdir)

                logging.info('ZStat_SNODAS_byBasin: Zonal statistics of %s are exported to %s' % (file, csv_byBasin))

                print "Zonal stastics of %s are complete." % date_name


        else:
            logging.info('ZStat_SNODAS_byBasin: %s is not a .tif file and the zonal statistics were not processed.' % file)






























