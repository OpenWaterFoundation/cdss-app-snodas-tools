# Name: SNODASDaily_Interactive.py
# Version: 1
# Author: Emma Giles
# Organization: Open Water Foundation
#
# Purpose: This script outputs zonal statistics for historical daily SNODAS rasters given the basin boundaries of an
#   input basin boundary shapefile. The zonal statistics that are calculated are as follows: SWE mean, SWE minimum, SWE
#   maximum, SWE standard deviation, pixel count and percentage of snow coverage. The functions in this script are
#   housed within SNODAS_utilities.py. A more detailed description of each function is documented in the
#   SNODAS_utilities.py file. This script allows the user to interactively input historical dates of interest for
#   processing. The user can decide between a single date and a range of dates. This script does not allow for the user
#   to pick a list of non-sequential dates.


# Check to see which os is running
import sys
platform = sys.platform
if platform == 'linux' or platform == 'linux2' or platform == 'cygwin' or platform == 'darwin':
    linux_os = True
else:
    linux_os = False


# Import necessary modules
import SNODAS_utilities, os, logging, time, sys
from sys import version_info
from logging.config import fileConfig
from qgis.core import QgsApplication
from datetime import datetime, timedelta

# Read the config file to assign variables. Reference the following for code details:
# https://wiki.python.org/moin/ConfigParserExamples
if linux_os:
    import ConfigParser
    Config = ConfigParser.ConfigParser()
else:
    import configparser
    Config = configparser.ConfigParser()

Configfile = "../config/SNODAS-Tools-Config.ini"
Config.read(Configfile)

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

# Assign the values from the configuration file to the python variables. See below for description of each
# variable obtained by the configuration file.
#
#   root: The root folder is the folder housing all output files from this script.
#
#   basin_shp: This is the full pathname to the shapefile holding the vector input(watershed basin boundaries).
#   The zonal statistics will be calculated for each feature of this layer. The shapefile must be projected into
#   NAD83 Zone 13N. This script was originally developed to process Colorado Watershed Basins as the input shapefile.
#
#   QGIS_installation: The full path to QGIS installation on the local machine. This is used to initialize QGIS
#   resources & utilities. More info at: http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html.
#
#   Save_allSNODASparameters: Each daily downloaded .tar SNODAS file contains 8 parameters as follows: (1) Snow Water
#   Equivalent (2) Snow Depth (3) Snow Melt Runoff at the Base of the Snow Pack (4) Sublimation from the Snow Pack
#   (5) Sublimation of Blowing Snow (6) Solid Precipitation (7) Liquid Precipitation and (8) Snow Pack Average
#   Temperature. The default setting, False, will delete all parameters except 'Snow Water Equivalent'. The optional
#   setting, True, will move all other parameters to a sub-folder under 1_Download called 'OtherParameters'
#
#   name_of_download_folder: The name of the download folder. Defaulted to '1_DownloadSNODAS'. All downloaded SNODAS
#   .tar files are contained here.
#
#   name_of_setFormat_folder: The name of the setFormat folder. Defaulted to ' 2_SetFormat'. All SNODAS masked .tif
#   files are contained here.
#
#   name_of_clip_folder: The name of the clip folder. Defaulted to '3_ClipToExtnet'. All SNODAS clipped (to basin
#   extent)and reprojected .tif files are contained here.
#
#   name_of_createsnowcover_folder: The name of the snow cover folder. Defaulted to '4_CreateSnowCover'. All binary
#   snow cover .tif files (clipped to basin extent) are contained here.
#
#   name_of_calculateStatistics_folder: The name of the results folder. All zonal statistic results in csv format are
#   contained here.
#
#   name_of_byDate_folder: The name of the byDate folder. All zonal statistic results in csv format organized by date
#   are contained here.
#
#   name_of_byBasin_folder: The name of the byBasin folder. All zonal statistic results in csv format organized by
#   basin are contained here.

root = ConfigSectionMap("Folders")['root_pathname']
basin_shp = ConfigSectionMap("BasinBoundaryShapefile")['pathname']
QGIS_installation = ConfigSectionMap("ProgramInstall")['qgis_pathname']
Save_allSNODASparameters = ConfigSectionMap("SNODASparameters")['save_all_parameters']
name_of_download_folder = ConfigSectionMap("Folders")['download_snodas_tar_folder']
name_of_setFormat_folder = ConfigSectionMap("Folders")['untar_snodas_tif_folder']
name_of_clip_folder = ConfigSectionMap("Folders")['clip_proj_snodas_tif_folder']
name_of_createsnowcover_folder = ConfigSectionMap("Folders")['create_snowcover_tif_folder']
name_of_calculateStatistics_folder = ConfigSectionMap("Folders")['calculate_stats_folder']
name_of_byDate_folder = ConfigSectionMap("Folders")['output_stats_by_date_folder']
name_of_byBasin_folder = ConfigSectionMap("Folders")['output_stats_by_basin_folder']
name_of_processed_folder = ConfigSectionMap("Folders")['processed_data_folder']
output_CRS_EPSG = ConfigSectionMap("Projections")['output_proj_epsg']
delete_shp_orig = ConfigSectionMap("OutputLayers")['shp_delete_originals']
zip_shp = ConfigSectionMap("OutputLayers")['shp_zip']
name_of_static_folder = ConfigSectionMap("Folders")['static_data_folder']
UploadResultsToAmazonS3 = ConfigSectionMap("OutputLayers")['upload_results_to_amazon_s3']


if __name__ == "__main__":

    #Boolean vairable used to test python version throughout script.
    py3 = version_info[0] > 2

    # Initialize QGIS resources: more info at
    # http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html. This block of code allows for the
    # script to utilize QGIS functionality.
    QgsApplication.setPrefixPath(QGIS_installation, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # Define static folder and extent shapefile
    static_path = os.path.join(root, name_of_static_folder)
    extent_shapefile = static_path + 'studyAreaExtent_prj.shp'

    # Obtain today's date
    now = datetime.now()

    # Get user inputs as raw data
    # Ask the user to decide between downloading only one date of data or a range of multiple dates of data.
    if py3:
        singleOrRange = input("Are you interested in one date or a range of dates?: Type 'One' or 'Range'. \n")
    else:
        singleOrRange = raw_input("Are you interested in one date or a range of dates?: Type 'One' or 'Range'. \n")

    # While loop that continues to prompt user for a new input if original input is invalid.
    while singleOrRange.upper() != "ONE" and singleOrRange.upper() != "RANGE":

        # Ask the user to re-enter downloading data type - one date or range of dates.
        if py3:
            singleOrRange = input(
                "Your input is not recognized. \n Are you interested in one date or a range of dates?: "
                "Type 'One' or 'Range'. \n")
        else:
            singleOrRange = raw_input("Your input is not recognized. \n Are you interested in one date or a range of "
                                      "dates?: Type 'One' or 'Range'. \n")

    # Create the root folder and the 5 sub-folders (Defaulted to: 1_DownloadSNODAS, 2_SetFormat, 3_ClipToExtent,
    # 4_CreateSnowCover, 5_CalculateStatistics [2 sub-folders: StatisticsByBasin, StatisticsByDate]). Check for folder
    # existence. If exiting, the folder is not recreated. Refer to developer documentation for information regarding
    # the types of files contained within each folder.
    download_path = os.path.join(root, name_of_processed_folder, name_of_download_folder)
    setEnvironment_path = os.path.join(root, name_of_processed_folder, name_of_setFormat_folder)
    clip_path = os.path.join(root, name_of_processed_folder, name_of_clip_folder)
    snowCover_path = os.path.join(root, name_of_processed_folder, name_of_createsnowcover_folder)
    results_basin_path = os.path.join(root, name_of_processed_folder, name_of_calculateStatistics_folder + name_of_byBasin_folder)
    results_date_path = os.path.join(root, name_of_processed_folder, name_of_calculateStatistics_folder + name_of_byDate_folder)


    listofFolders = [root, download_path, setEnvironment_path, clip_path, snowCover_path, results_basin_path,
                     results_date_path]

    for folder in listofFolders:
        if os.path.exists(folder) == False:
            os.makedirs(folder)

    # Create and configures logging file
    fileConfig(Configfile)
    logger = logging.getLogger('log02')
    logger.info('SNODASDailyDownload.py: Started \n')

    # Print version information
    print "Running SNODASDaily_Interactive.py Version 1"
    logger.info('Running SNODASDaily_Interactive.py Version 1')

    # After the user chooses the project folder where the data will be stored, they must then choose the dates of
    # interest. If the user is interested in only one date of data.
    if singleOrRange.upper() == "ONE":

        # Ask the user which date of data they would like. Must be in mm/dd/yy format and be within the specified
        # range of available dates. Continues to ask the user for a date if the entered string is not a valid date with
        # correct formatting or if the date chosen is outside the range of available data.
        count = True
        while count:
            try:
                if py3:
                    userIn = input(
                        "\n Which date are you interested in? The date must be of or between 30 September 2003 and today's "
                        "date. \n mm/dd/yy: \n")
                else:
                    userIn = raw_input(
                    "\n Which date are you interested in? The date must be of or between 30 September 2003 and today's "
                    "date. \n mm/dd/yy: \n")
                singleDate = datetime.strptime(userIn, "%m/%d/%y")
                if (datetime(year=2003, month=9, day=29) < singleDate <= now) == False:
                    print ('\n You have chosen an invalid date.')
                    count = True
                else:
                    startDate = singleDate
                    endDate = singleDate
                    count = False
            except ValueError:
                print ('Invalid Format!')

    # If the user is interested in a range of multiple dates.
    else:

        # Ask the user which START date they would like. Must be in mm/dd/yy format and be within the specified
        # range of available dates. Continue to ask the user for a date if the entered string is not a valid date with
        # correct formatting or if the date chosen is outside the range of available data.
        count = True
        while count:
            try:
                if py3:
                    userIn = input(
                    "\n What is the STARTING (earliest) date of data that you are interested in? The date must be of or between "
                    "30 September 2003 and today's date. \n mm/dd/yy: \n")
                else:
                    userIn = raw_input(
                        "\n What is the STARTING (earliest) date of data that you are interested in? The date must be of or between "
                        "30 September 2003 and today's date. \n mm/dd/yy: \n")
                startDate = datetime.strptime(userIn, "%m/%d/%y")
                if (datetime(year=2003, month=9, day=29) < startDate <= now) == False:
                    print ('\n You have chosen an invalid date.')
                    count = True
                else:
                    count = False
            except ValueError:
                print ('Invalid Format!')

        # Ask the user which END date they would like. Must be in mm/dd/yy format and be within the specified
        # range of available dates. Continue to ask the user for a date if the entered string is not a valid date with
        # correct formatting or if the date chosen is outside the range of available data.
        count = True
        while count:
            try:
                if py3:
                    userIn = input(
                    "\n What is the ENDING (most recent) date of data that you are interested in? The date must be between"
                    " %s and today's date. \n mm/dd/yy: \n" % startDate.date())
                else:
                    userIn = raw_input(
                        "\n What is the ENDING (most recent) date of data that you are interested in? The date must be between "
                        " %s and today's date. \n mm/dd/yy: \n" % startDate.date())
                endDate = datetime.strptime(userIn, "%m/%d/%y")
                if (startDate < endDate <= now) == False:
                    print ('\n You have chosen an invalid date.')
                    count = True
                else:
                    count = False
            except ValueError:
                print ('Invalid Format!')


    # ----------------- End of user input. Begin automated script.------------------------------------------------------

    # The start time is used to calculate the elapsed time of the running script. The elapsed time will be displayed at
    # the end of the log file.
    start = time.time()

    # Create an empty list that will contain all dates that failed to download.
    failed_dates_lst = []

    # Iterate through each day of the user-specified range. Refer to:
    # http://stackoverflow.com/questions/6901436/python-expected-an-indented-block
    total_days = (endDate - startDate).days + 1

    # Define the current day depending on the user's interest in one or range of dates.
    for day_number in range(total_days):
        if singleOrRange.upper() == "ONE":
            current = singleDate
        else:
            current = (startDate + timedelta(days=day_number)).date()

        # The start time is used to calculate the elapsed time of the running script. The elapsed time will be
        # displayed at the end of the log file.
        start_day = time.time()

        # Format date into string with format YYYYMMDD
        current_date = SNODAS_utilities.format_date_YYYYMMDD(current)
        current_date_tar = 'SNODAS_' + current_date + '.tar'

        # Check to see if this date of data has already been processed in the folder
        possible_file = os.path.join(download_path, current_date_tar)

        # If date has already been procesed within the folder, the download & zonal statistics are rerun.
        if os.path.exists(possible_file):
            logger.warning ( "\n This date (%s) has already been processed. The files will be reprocessed and "
                              "rewritten." % current_date)

        # Download current date SNODAS .tar file from the FTP site at
        #  ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/masked/
        returnedList = SNODAS_utilities.download_SNODAS(download_path, current)

        failed_dates_lst.append(returnedList[2])

        # Check to see if configuration values for optional statistics 'calculate_SWE_minimum, calculate_SWE_maximum,
        # calculate_SWE_stdDev' (defined in utility function) are valid, If valid, script continues to run. If invalid,
        # error message is printed to consol and log file and script is terminated
        tempList = []
        for stat in returnedList[1]:
            if stat.upper() == 'TRUE' or stat.upper() == 'FALSE':
                tempList.append(1)
            else:
                tempList.append(0)

        if 0 in tempList:
            logger.error(
                '"ERROR: See configuration file. One or more values of the ''OptionalZonalStatistics'' section is '
                'not valid. Please change values to either ''True'' or ''False'' and rerun the script."')
            logging.error(
                '"ERROR: See configuration file. One or more values of the ''OptionalZonalStatistics'' section is '
                'not valid. Please change values to either ''True'' or ''False'' and rerun the script."')
            break

        else:
            # Untar current date's data
            for file in os.listdir(download_path):
                if current_date in str(file):
                    SNODAS_utilities.untar_SNODAS_file(file, download_path, setEnvironment_path)

            # Check to see if configuration file 'Save_allSNODASparameters' value is valid. If valid, script continues
            # to run. If invalid, error message is printed to console and log file and the script is terminated.
            if Save_allSNODASparameters.upper() == 'FALSE' or Save_allSNODASparameters.upper() == 'TRUE':

                # Delete current date's irrelevant files (parameters other than SWE).
                if Save_allSNODASparameters.upper() == 'FALSE':
                    for file in os.listdir(setEnvironment_path):
                        if current_date in str(file):
                            SNODAS_utilities.delete_irrelevant_SNODAS_files(file)

                # Move irrelevant files (parameters other than SWE) to 'OtherSNODASParamaters'.
                else:
                    parameter_path = os.path.join(setEnvironment_path, r'OtherParameters')
                    if os.path.exists(parameter_path) == False:
                        os.makedirs(parameter_path)
                    for file in os.listdir(setEnvironment_path):
                        if current_date in str(file):
                            SNODAS_utilities.move_irrelevant_SNODAS_files(file, parameter_path)

                # Extract current date's .gz files. Each SNODAS parameter files are zipped within a .gz file.
                for file in os.listdir(setEnvironment_path):
                    if current_date in str(file):
                        SNODAS_utilities.extract_SNODAS_gz_file(file)

                # Convert current date's SNODAS SWE .dat file into .bil format.
                for file in os.listdir(setEnvironment_path):
                    if current_date in str(file):
                        SNODAS_utilities.convert_SNODAS_dat_to_bil(file)

                # Create current date's custom .Hdr file. In order to convert today's SNODAS SWE .bil file into a usable
                # .tif file, a custom .Hdr must be created. Refer to the function in the SNODAS_utilities.py for more
                # information on the contents of the custom .HDR file.
                for file in os.listdir(setEnvironment_path):
                    if current_date in str(file):
                        SNODAS_utilities.create_SNODAS_hdr_file(file)

                # Convert current date's .bil files to .tif files
                for file in os.listdir(setEnvironment_path):
                    if current_date in str(file):
                        SNODAS_utilities.convert_SNODAS_bil_to_tif(file, setEnvironment_path)

                # Delete current date's .bil file
                for file in os.listdir(setEnvironment_path):
                    if current_date in str(file):
                        SNODAS_utilities.delete_SNODAS_bil_file(file)

                # Create the extent shapefile if not already created.
                if not os.path.exists(extent_shapefile):
                    SNODAS_utilities.create_extent(basin_shp, static_path)

                # Copy and move current date's .tif file into name_of_clip_folder
                for file in os.listdir(setEnvironment_path):
                    if current_date in str(file):
                        SNODAS_utilities.copy_and_move_SNODAS_tif_file(file, clip_path)

                # Assign datum to current date's .tif file (defaulted to WGS84)
                for file in os.listdir(clip_path):
                    if current_date in str(file):
                        SNODAS_utilities.assign_SNODAS_datum(file, clip_path)

                # Clip current date's .tif file to the extent of the basin shapefile
                for file in os.listdir(clip_path):
                    if current_date in str(file):
                        SNODAS_utilities.SNODAS_raster_clip(file, clip_path, extent_shapefile)

                # Project current date's .tif file into desired projection (defaulted to NAD83 UTM Zone 13N)
                for file in os.listdir(clip_path):
                    if current_date in str(file):
                        SNODAS_utilities.assign_SNODAS_projection(file, clip_path)

                # Create current date's snow cover binary raster
                for file in os.listdir(clip_path):
                    if current_date in str(file):
                        SNODAS_utilities.snowCoverage(file, clip_path, snowCover_path)

                # Create .csv files of byBasin and byDate outputs
                for file in os.listdir(clip_path):
                    if current_date in str(file):
                        SNODAS_utilities.create_csv_files(file, basin_shp, results_date_path, results_basin_path)

                # Delete rows from basin CSV files if the date is being reprocessed
                for file in os.listdir(clip_path):
                    if current_date in str(file):
                        SNODAS_utilities.delete_ByBasinCSV_repeated_rows(file, basin_shp, results_basin_path)

                # Calculate zonal statistics and export results
                for file in os.listdir(clip_path):
                    if current_date in str(file):
                        SNODAS_utilities.zStat_and_export(file, basin_shp, results_basin_path,
                                                                  results_date_path,
                                                                  clip_path, snowCover_path, current,
                                                                returnedList[0], output_CRS_EPSG)

                # If desired, zip files of output shapefile (both today's data and latestDate file)
                if zip_shp.upper() == 'TRUE':
                    for file in os.listdir(results_date_path):
                        if current_date in str(file) and file.endswith('.shp'):
                            SNODAS_utilities.zipShapefile(file, results_date_path, delete_shp_orig)
                        if "LatestDate" in str(file) and file.endswith('.shp'):
                            zip_full_path = os.path.join(results_date_path,
                                                                 "SnowpackStatisticsByDate_LatestDate.zip")
                            if os.path.exists(zip_full_path):
                                os.remove(zip_full_path)

                            SNODAS_utilities.zipShapefile(file, results_date_path, delete_shp_orig)


                # The time series graphs will only be produced after the last date of data is processed.
                if current == endDate or current == endDate.date():
                    SNODAS_utilities.create_SNODAS_SWE_graphs()
                    # Push daily statistics to the web, if configured
                    if UploadResultsToAmazonS3.upper() == 'TRUE':
                        if linux_os:
                            SNODAS_utilities.push_to_GCP()
                        else:
                            SNODAS_utilities.push_to_AWS()
                    else:
                        logger.info('Output files from SNODAS_Tools are not pushed to cloud storage because of'
                                    ' setting in configuration file. ')

            # If config file value SaveAllSNODASparameters is not a valid value (either 'True' or 'False') the remaining
            # script will not run and the following error message will be printed to the console and to the logging file.
            else:
                logging.error(
                            "ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not "
                            "valid. Please type in 'True' or 'False' and rerun the script.")
                logger.error(
                "ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not "
             "valid. Please type in 'True' or 'False' and rerun the script.")

        # Display elapsed time of current date's processing in log.
        end_day = time.time()
        elapsed_day = end_day - start_day
        logger.info('\n %s: Completed.' % current_date)
        logger.info('Elapsed time (date: %s): %d seconds' % (current_date, elapsed_day))

    # Close logging including the elapsed time of the running script in seconds.
    elapsed = time.time() - start
    elapsed_hours = int(elapsed / 3600)
    elapsed_hours_remainder = elapsed % 3600
    elapsed_minutes = int(elapsed_hours_remainder / 60)
    elapsed_seconds = int(elapsed_hours_remainder % 60)
    stringStart = str(startDate)
    stringEnd = str(endDate)
    print '\nSNODASHistoricalDownload.py: Completed. Dates Processed: From %s to %s.' % (stringStart, stringEnd)
    print 'Elapsed time (full script): approximately %d hours, %d minutes and %d seconds\n' % (elapsed_hours,
                                                                                             elapsed_minutes,
                                                                                             elapsed_seconds)

    # If any dates were unsuccessfully downloaded, print those dates to the console and the logging file.
    failed_dates_lst_updated = []
    failed_dates_lst_1Week = []
    for item in failed_dates_lst:
        if item != 'None':
            item_str = str(item)
            item_plus_seven = item + timedelta(days=7)
            item_plus_seven_str = str(item_plus_seven)
            failed_dates_lst_updated.append(item_str)
            failed_dates_lst_1Week.append(item_plus_seven_str)

    if failed_dates_lst_updated == []:
        print 'All dates successfully downloaded!'
        logger.info('All dates successfully downloaded!')
    else:
        print '\nDates unsuccessfully downloaded: '
        logger.info('\nDates unsuccessfully downloaded: ')
        for item in failed_dates_lst_updated:
            print item
            logger.info('%s'% item)
        print "\nDates that will be affected by assigning the 'SNODAS_SWE_Volume_1WeekChange_acft' attribute 'NULL' " \
              "due to the unsuccessful downloads: "
        logger.info("\nDates that will be affected by assigning the 'SNODAS_SWE_Volume_1WeekChange_acft' attribute "
                    "'NULL' due to the unsuccessful downloads: ")
        for item in failed_dates_lst_1Week:
            print item
            logger.info('%s' % item)


    logger.info('\nSNODASHistoricalDownload.py: Completed. Dates Processed: From %s to %s.' % (stringStart, stringEnd))
    logger.info('Elapsed time (full script): approximately %d hours, %d minutes and %d seconds\n' % (elapsed_hours,
                                                                                             elapsed_minutes,
                                                                                             elapsed_seconds))
