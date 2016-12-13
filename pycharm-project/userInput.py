# Name: userInputP1.1.py
# Author: Emma Giles
# Organization: Open Water Foundation
# Date Created: 11/21/2016
# Last Updated: 11/22/2016
#
#
# Purpose: This script will output zonal statistics for each daily SNODAS raster given the basin boundaries of the
#   Colorado Watershed Basins. The zonal statistics that are calculated are as follows: SWE mean, SWE minimum, SWE
#   maximum, SWE standard deviation, pixel count and percentage of snow coverage. The functions in this script are
#   housed within SNODAS_utilities.py. A more detailed description of each function is documented in the
#   SNODAS_utilities.py file. This script allows the user to decide which dates of data they would like processed. The
#   user can decide between a single date and a range of dates. This script does not allow for the user to pick a list
#   of non-sequential dates. If this become of need, it can be added to the script (contact Open Water Foundation).

# Import necessary modules
import SNODAS_utilities
import ftplib, os, tarfile, gzip, gdal, csv, logging
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsZonalStatistics
from qgis.core import QgsRasterLayer, QgsApplication, QgsVectorLayer, QgsField, QgsExpression
from PyQt4.QtCore import QVariant
from datetime import datetime, timedelta
from time import strptime
from shutil import copy

# Define the full pathnames of the following variables.
# root: The root folder will be the folder that will house all outputs from this script. Within the root folder, the
# script creates project folders. The user can specify which project folder (or decide to create a new project folder)
# in which they would prefer the outputs and results to be saved to. This feature allows for the user to organize
# their zonal statistic calculations in more depth without having all results stored in one location. ]
# basin_extent_WGS84: This is the full pathname to the shapefile of the EXTENT of the Colorado Watershed Basins. This
# shapefile should be one rectangular feature representing the bounding box of the Colorado Watershed Basins shapefile.
# Ensure that this shapefile is projected into WGS84
# basin_shp_NAD83 = This is the full pathname to the shapefile holding the boundaries of the Colorado Watershed Basins.
# The zonal statistics will be calculated for each feature. Ensure that the shapefile is projected into NAD83 Zone 13N.
root = r'D:\SNODAS\Raster\user_input'
basin_extent_WGS84 = r"D:\SNODAS\Vector\basin_extent_WGS84.shp"
basin_shp_NAD83 = r"D:\SNODAS\Vector\orig_watersheds_nad83.shp"


if __name__ == "__main__":

    # Initializes QGIS resources: more info at
    # http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html. This block of code allows for the
    # script to utilize QGIS functionality.
    QgsApplication.setPrefixPath("C:/OSGeo4W/apps/qgis", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()


    # Obtain today's date
    now = datetime.now()

    # Get user inputs as raw data

    # Asks the user to decide between downloading only one date of data or a range of multiple dates of data.
    singleOrRange = raw_input("Are you interested in one date or a range of dates?: Type 'One' or 'Range'. \n")

    # While loop that will continue to prompt the user for a new input if they fail to enter 'one' or 'range'.
    while singleOrRange.upper() != "ONE" and singleOrRange.upper() != "RANGE":

        # User prompt
        print "Your input is not recognized. Please enter 'One' or 'Range'.\n"

        # Asks the user to re-enter their downloading data type - one date or range of dates.
        singleOrRange = raw_input("Are you interested in one date or a range of dates?: Type 'One' or 'Range'. \n")

    # Asks the user if they would like the output to be stored in a new project folder?
    questionNewFolder = raw_input(
        "\n Do you want the results to output into a new project folder?: Type 'Yes' or 'No'\n ")

    # While loop that will continue to prompt the user if they fail to enter valid inputs (either 'yes' or 'no')
    while questionNewFolder.upper() != 'YES' and questionNewFolder.upper() != 'NO':

        # User prompt
        print "\n Your response is invalid. Please type either 'Yes' or 'No'"

        # Asks the user to re-enter their decision on a new project folder.
        questionNewFolder = raw_input(" \n Do you want the results to output into a new project folder?\n")

    # If the user would like to create a new folder
    if questionNewFolder.upper() == 'YES':

        # Asks user for a folder name.
        folder_name_new = raw_input("\n What would you like this new project folder to be named? Please do not use "
                                    "spaces or special characters.\n")

        # Creates the full path name of the new project folder using the user's input.
        full_path = os.path.join(root, folder_name_new)

        # If the folder does not exist then a folder will be created. If it does exist, the user will be prompted to
        # come up with another folder name.
        while os.path.exists(full_path):

            #User prompt
            print " \n That folder name has already been taken. Please input another folder name."

            # Asks the user to re-enter a valid name for the project folder.
            folder_name_new = raw_input(
                " \n What would you like this new project folder to be named? Please do not use spaces or special "
                "characters.\n")

            # Creates the full path name of the new project folder using the user's input.
            full_path = os.path.join(root, folder_name_new)

        # Creates the appropriate files for the outputs and results for the new project folder. Each project folder
        # holds 5 folders (download, setEnvironment, clip, snowCover, results and logging) that will store the outputs
        # of the script. The download folder will hold the originally-downloaded national SNODAS .tar files. The
        # setEnvironment folder will hold the national SNOADAS .tif files. The clip folder will hold the reprojected
        # (NAD83), clipped SNODAS .tif files. The results folder will hold two folders, byBasin and byDate. The byBasin
        # folder will hold the basin-specific zonal statistics results in .csv format. The byDate folder will hold the
        # date-specific zonal statistics results in .csv format. The logging folder will hold a .txt file containing
        # all logging notes created throughout the script.
        os.makedirs(full_path)
        download_path = os.path.join(full_path, 'download')
        os.makedirs(download_path)
        setEnvironment_path = os.path.join(full_path, 'setEnvironment')
        os.makedirs(setEnvironment_path)
        clip_path = os.path.join(full_path, 'clip')
        os.makedirs(clip_path)
        snowCover_path = os.path.join(full_path, 'snowCover')
        os.makedirs(snowCover_path)
        results_path = os.path.join(full_path, 'results')
        os.makedirs(results_path)
        resultsByBasin_path = os.path.join(full_path, 'results/ByBasin')
        os.makedirs(os.path.join(resultsByBasin_path))
        resultsByDate_path = os.path.join(full_path, 'results/ByDate')
        os.makedirs(resultsByDate_path)
        logging_path = os.path.join(full_path, 'logging')
        os.makedirs(logging_path)

    # If the user would like to output the results in a current project folder. Note: the results will be appended to
    # the .csv files currently housed within the selected project folder.
    else:

        # Displays existing project folders for the user to reference as they select a desired project folder.
        print "\n The following are the existing project folders:"
        print os.walk(root).next()[1]

        # Asks user which existing project folder they would like to add the By_basin results to.
        folder_name_existing = raw_input(
            " \n Which existing project folder would you like to add the By_Basin results?\n")

        # Creates the full path name of the new project folder using the user's input.
        full_path = os.path.join(root, folder_name_existing)

        # The full path name of the logging folder is needed within the logging module to produce the logging results.
        logging_path = os.path.join(full_path, 'logging')

        # If the user chooses a folder that is not already existing.
        while os.path.exists(full_path) == False:

            # User prompt.
            print "\n You did not choose a valid project folder. Please try again."

            # Asks the user to re-enter a valid name for an existing project folder.
            folder_name_existing = raw_input(
                "\n Which existing project folder would you like to add the By_Basin results?\n")
            full_path = os.path.join(root, folder_name_existing)

    # After the user chooses the project folder where the data will be stored, they must then choose the dates of
    # interest. If the user is interested in only one date of data.
    if singleOrRange.upper() == "ONE":

        # Nulls the startDate and endDate variables (will not be used with processing a single date of data.
        startDate = datetime.now()
        endDate = datetime.now()

        # Asks the user which date of data they would like. Must be in mm/dd/yy format and be within the specified
        # range of available dates. Continues to ask the user for a date if the entered string is not a valid date with
        # correct formatting or if the date chosen is outside the range of available data.
        count = True
        while count:
            try:
                userIn = raw_input(
                    "\n Which date are you interested in? The date must be of or between 01 October 2003 and today's "
                    "date. \n mm/dd/yy: \n")
                singleDate = datetime.strptime(userIn, "%m/%d/%y")
                if (datetime(year=2003, month=9, day=30) < singleDate <= now) == False:
                    print "\n You have chosen an invalid date."
                    count = True
                else:
                    count = False
            except ValueError:
                print "Invalid Format!"

    # If the user is interested in a range of multiple dates.
    else:

        # Nulls the singleDate variable (will not be used with processing a range of multiple dates).
        singleDate = datetime.now()

        # Asks the user which START date they would like. Must be in mm/dd/yy format and be within the specified
        # range of available dates. Continues to ask the user for a date if the entered string is not a valid date with
        # correct formatting or if the date chosen is outside the range of available data.
        count = True
        while count:
            try:
                userIn = raw_input(
                    "\n What is the STARTING date of data that you are interested in? The date must be of or between "
                    "01 October 2003 and today's date. \n mm/dd/yy: \n")
                startDate = datetime.strptime(userIn, "%m/%d/%y")
                if (datetime(year=2003, month=9, day=30) < startDate <= now) == False:
                    print "\n You have chosen an invalid date."
                    count = True
                else:
                    count = False
            except ValueError:
                print "Invalid Format!"

        # Asks the user which END date they would like. Must be in mm/dd/yy format and be within the specified
        # range of available dates. Continues to ask the user for a date if the entered string is not a valid date with
        # correct formatting or if the date chosen is outside the range of available data.
        count = True
        while count:
            try:
                userIn = raw_input(
                    "\n What is the ENDING date of data that you are interested in? The date must be between "
                    "the starting date and today's date. \n mm/dd/yy: \n")
                endDate = datetime.strptime(userIn, "%m/%d/%y")
                if (startDate < endDate <= now) == False:
                    print "\n You have chosen an invalid date."
                    count = True
                else:
                    count = False
            except ValueError:
                print "Invalid Format!"

    # It takes about 5 seconds for the FTP connection to take place. This prompt informs the user of the delay.
    print "\n Please wait while we connect to the FTP site ..."

    # Set up logging configurations
    logging_file = os.path.join(logging_path, 'logging.txt')
    logging.basicConfig(filename=logging_file, level=logging.WARNING, format='%(asctime)s %(message)s')
    logging.info('Started')

    # Determines if the user wanted a single date or a range of dates
    if singleOrRange.upper() == "ONE":

        # Formats date into a string with format YYYYMMDD
        current_date = SNODAS_utilities.get_date_string(singleDate)
        current_date_tar = 'SNODAS_' + current_date + '.tar'

        # Checks to see if this date of data has already been processed in the folder.
        download_path = os.path.join(full_path, 'download')
        possible_file = os.path.join(download_path, current_date_tar)

        # If it has already been processed within the folder, the download and zonal statistics are not processed.
        if os.path.exists(possible_file):
            print "\n This date (%s) has already been processed within this project folder. \n " \
                  "The zonal statistics will not be processed a multiple time." % singleDate
            pass

        # If it has not already been processed within the folder, the download and zonal statistics are processed.
        else:

            # Downloads one date
            SNODAS_utilities.download_user_single_date_SNODAS(full_path + '\download', singleDate)

            # Untar's the data
            for file in os.listdir(full_path + '\download'):
                if current_date in str(file):
                    SNODAS_utilities.untar_SNODAS_file(file, full_path + '\download', full_path + '\setEnvironment')
                else:
                    pass

            # Delete irrelevant files
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.delete_irrelevant_SNODAS_files(file)
                else:
                    pass

            # Extract .gz files
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.extract_SNODAS_gz_file(file)
                else:
                    pass

            # Convert .dat files into .bil format
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.convert_SNODAS_dat_to_bil(file)
                else:
                    pass

            # Create custom .Hdr file
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.create_SNODAS_hdr_file(file)
                else:
                    pass

            # Delete any created .txt files
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.delete_any_SNODAS_txt_files(file)
                else:
                    pass

            # Convert .bil files to .tif files
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.convert_SNODAS_bil_to_tif(file, full_path + '\setEnvironment')
                else:
                    pass

            # Delete .bil file
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.delete_SNODAS_bil_file(file)
                else:
                    pass

            # Copy and move .tif file into clip folder
            for file in os.listdir(full_path + '\setEnvironment'):
                if current_date in str(file):
                    SNODAS_utilities.copy_and_move_SNODAS_tif_file(file, full_path + '\clip')
                else:
                    pass

            # Assign WGS84 projection to  .tif file
            for file in os.listdir(full_path + '\clip'):
                if current_date in str(file):
                    SNODAS_utilities.assign_SNODAS_projection_WGS84(file, full_path + '\clip')
                else:
                    pass


                    # Clip .tif file to the extent of the Colorado Basin shapefile (WGS84)
            for file in os.listdir(full_path + '\clip'):
                if current_date in str(file):
                    SNODAS_utilities.SNODAS_raster_clip_WGS84(file, full_path + '\clip', basin_extent_WGS84)
                else:
                    pass

            # Reproject .tif file into NAD83
            for file in os.listdir(full_path + '\clip'):
                if current_date in str(file):
                    SNODAS_utilities.SNODAS_raster_reproject_NAD83(file, full_path + '\clip')
                else:
                    pass

            # Create snow cover binary raster
            for file in os.listdir(full_path + '\clip'):
                if current_date in str(file):
                    SNODAS_utilities.snowCoverage(file, full_path + '\clip', full_path + '\snowCover')
                else:
                    pass

            # Create .csv files of byBasin and byDate outputs
            for file in os.listdir(full_path + '\clip'):
                if current_date in str(file):
                    SNODAS_utilities.create_csv_files(file, basin_shp_NAD83, full_path + r'\results\byDate',
                                                      full_path + r'\results\byBasin')
                else:
                    pass

            # Calculate zonal statistics and export results
            for file in os.listdir(full_path + '\clip'):
                if current_date in str(file):
                    SNODAS_utilities.zStat_and_export(file, basin_shp_NAD83, full_path + r'\results\byBasin',
                                                      full_path + r'\results\byDate', full_path + r'\clip', full_path + r'\snowCover')
                else:
                    pass



    # Determines if the user wanted a single date or a range of dates. If the user wanted a range, the following script
    # is run.
    elif singleOrRange.upper() == "RANGE":

        # Iterates through each day of the user-specified range. Refer to: http://stackoverflow.com/questions/6901436/
        # python-expected-an-indented-block
        total_days = (endDate - startDate).days + 1
        for day_number in range(total_days):
            current = (startDate + timedelta(days=day_number)).date()

            # Formats date into a string with format YYYYMMDD
            current_date = SNODAS_utilities.get_date_string(current)
            current_date_tar = 'SNODAS_' + current_date + '.tar'

            # Checks to see if this date of data has already been processed in the folder.
            download_path = os.path.join(full_path, 'download')
            possible_file = os.path.join(download_path, current_date_tar)

            # If it has already been processed within the folder, the download and zonal statistics are not processed.
            if os.path.exists(possible_file):
                print "\n This date (%s) has already been processed within this project folder. \n " \
                      "The zonal statistics will not be processed a multiple time." % singleDate
                pass

            # If it has not already been processed within the folder, the download and zonal statistics are processed.
            else:
                # Downlaod the dates of data
                SNODAS_utilities.download_user_single_date_SNODAS(full_path + '\download', current)

                # Untar the data
                for file in os.listdir(full_path + '\download'):
                    if current_date in str(file):
                        SNODAS_utilities.untar_SNODAS_file(file, full_path + '\download', full_path + '\setEnvironment')
                    else:
                        pass

                # Delete irrelevant files
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.delete_irrelevant_SNODAS_files(file)
                    else:
                        pass

                # Extract .gz files
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.extract_SNODAS_gz_file(file)
                    else:
                        pass

                # Convert .dat files into .bil format
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.convert_SNODAS_dat_to_bil(file)
                    else:
                        pass

                # Create custom .Hdr file
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.create_SNODAS_hdr_file(file)
                    else:
                        pass

                # Delete any created .txt files
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.delete_any_SNODAS_txt_files(file)
                    else:
                        pass

                # Convert .bil files to .tif files
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.convert_SNODAS_bil_to_tif(file, full_path + '\setEnvironment')
                    else:
                        pass

                # Delete .bil file
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.delete_SNODAS_bil_file(file)
                    else:
                        pass

                # Copy and move .tif file into clip folder
                for file in os.listdir(full_path + '\setEnvironment'):
                    if current_date in str(file):
                        SNODAS_utilities.copy_and_move_SNODAS_tif_file(file, full_path + '\clip')
                    else:
                        pass

                # Assign WGS84 projection to  .tif file
                for file in os.listdir(full_path + '\clip'):
                    if current_date in str(file):
                        SNODAS_utilities.assign_SNODAS_projection_WGS84(file, full_path + '\clip')
                    else:
                        pass


                # Clip .tif file to the extent of the Colorado Basin shapefile (WGS84)
                for file in os.listdir(full_path + '\clip'):
                    if current_date in str(file):
                        SNODAS_utilities.SNODAS_raster_clip_WGS84(file, full_path + '\clip', basin_extent_WGS84)
                    else:
                        pass

                # Reproject .tif file into NAD83
                for file in os.listdir(full_path + '\clip'):
                    if current_date in str(file):
                        SNODAS_utilities.SNODAS_raster_reproject_NAD83(file, full_path + '\clip')
                    else:
                        pass

                # Create snow cover binary raster
                for file in os.listdir(full_path + '\clip'):
                    if current_date in str(file):
                        SNODAS_utilities.snowCoverage(file, full_path + '\clip', full_path + '\snowCover')
                    else:
                        pass
                # Create .csv files of byBasin and byDate outputs
                for file in os.listdir(full_path + '\clip'):
                    if current_date in str(file):
                        SNODAS_utilities.create_csv_files(file, basin_shp_NAD83, full_path + r'\results\byDate',
                                                              full_path + r'\results\byBasin')
                    else:
                        pass

                # Calculate zonal statistics and export results
                for file in os.listdir(full_path + '\clip'):
                    if current_date in str(file):
                        SNODAS_utilities.zStat_and_export(file, basin_shp_NAD83, full_path + r'\results\byBasin',
                                                              full_path + r'\results\byDate', full_path + r'\clip',
                                                              full_path + r'\snowCover')
                    else:
                        pass

    else:
        pass


