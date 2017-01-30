# Name: SNODASDaily_Interactive.py
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

# Import necessary modules
import SNODAS_utilities, os, logging, time, configparser, sys
from sys import version_info
from logging.config import fileConfig
from qgis.core import QgsApplication
from datetime import datetime, timedelta

# Read the configuration file to assign variables. Reference the following for code details:
# https://wiki.python.org/moin/ConfigParserExamples
Config = configparser.ConfigParser()
Configfile = "..\SNODASconfig.ini"
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
#   basin_extent: The full pathname to the shapefile of the EXTENT of the vector input. The extent is a
#   rectangular feature representing the bounding box of the input shapefile (watershed basin boundaries). The
#   basin_extent shapefile should be projected in the same projection as the assigned projection of the SNODAS raster.
#   The downloaded SNODAS raster does not have a projection however the "SNODAS fields are grids of point estimates
#   of snow cover in latitude/longitude coordinates with the horizontal datum WGS84." The script is defaulted to
#   assign WGS84 projection to the SNODAS data but this can be changed in the configuration file.
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

root = ConfigSectionMap("RootFolder")['pathname']
basin_extent = ConfigSectionMap("VectorInputExtent")['pathname']
basin_shp = ConfigSectionMap("VectorInputShapefile")['pathname']
QGIS_installation = ConfigSectionMap("QGISInstall")['pathname']
Save_allSNODASparameters = ConfigSectionMap("SaveAllSNODASparameters")['value']
name_of_download_folder = ConfigSectionMap("FolderNames")['download']
name_of_setFormat_folder = ConfigSectionMap("FolderNames")['setformat']
name_of_clip_folder = ConfigSectionMap("FolderNames")['clip']
name_of_createsnowcover_folder = ConfigSectionMap("FolderNames")['snow_cover']
name_of_calculateStatistics_folder = ConfigSectionMap("FolderNames")['calculate_statistics']
name_of_byDate_folder = ConfigSectionMap("FolderNames")['by_date']
name_of_byBasin_folder = ConfigSectionMap("FolderNames")['by_basin']



if __name__ == "__main__":

    #Boolean vairable used to test python version throughout script.
    py3 = version_info[0] > 2

    # Get total number of arguments passed to SNODASDaily_Interactive.py through command parameters
    totalArg = len(sys.argv)

    # Get the arguments list
    cmdargs = str(sys.argv)

    # Print
    print ("Total number of args passed to the SNODASDaily_Interactive.py script: %d") % totalArg
    print ("Argument list: %s") % cmdargs

    # Initialize QGIS resources: more info at
    # http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html. This block of code allows for the
    # script to utilize QGIS functionality.
    QgsApplication.setPrefixPath(QGIS_installation, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

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

    if os.path.exists(root) == False:
        os.makedirs(root)

    download_path = os.path.join(root, name_of_download_folder)
    if os.path.exists(download_path) == False:
        os.makedirs(download_path)

    setEnvironment_path = os.path.join(root, name_of_setFormat_folder)
    if os.path.exists(setEnvironment_path) == False:
        os.makedirs(setEnvironment_path)

    clip_path = os.path.join(root, name_of_clip_folder)
    if os.path.exists(clip_path) == False:
        os.makedirs(clip_path)

    snowCover_path = os.path.join(root, name_of_createsnowcover_folder)
    if os.path.exists(snowCover_path) == False:
        os.makedirs(snowCover_path)

    results_basin_path = os.path.join(root, name_of_calculateStatistics_folder + name_of_byBasin_folder)
    if os.path.exists(results_basin_path) == False:
        os.makedirs(results_basin_path)

    results_date_path = os.path.join(root, name_of_calculateStatistics_folder + name_of_byDate_folder)
    if os.path.exists(results_date_path) == False:
        os.makedirs(results_date_path)

    # Create and configures logging file
    fileConfig(Configfile)
    logger = logging.getLogger()
    logging.info('SNODASDailyDownload.py: Started \n')
    logFile = root + '\SNODAS_log.txt'

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
                        "\n Which date are you interested in? The date must be of or between 01 October 2003 and today's "
                        "date. \n mm/dd/yy: \n")
                else:
                    userIn = raw_input(
                    "\n Which date are you interested in? The date must be of or between 01 October 2003 and today's "
                    "date. \n mm/dd/yy: \n")
                singleDate = datetime.strptime(userIn, "%m/%d/%y")
                if (datetime(year=2003, month=9, day=30) < singleDate <= now) == False:
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
                    "\n What is the STARTING date of data that you are interested in? The date must be of or between "
                    "01 October 2003 and today's date. \n mm/dd/yy: \n")
                else:
                    userIn = raw_input(
                        "\n What is the STARTING date of data that you are interested in? The date must be of or between "
                        "01 October 2003 and today's date. \n mm/dd/yy: \n")
                startDate = datetime.strptime(userIn, "%m/%d/%y")
                if (datetime(year=2003, month=9, day=30) < startDate <= now) == False:
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
                    "\n What is the ENDING date of data that you are interested in? The date must be between "
                    " %s and today's date. \n mm/dd/yy: \n" % startDate.date())
                else:
                    userIn = raw_input(
                        "\n What is the ENDING date of data that you are interested in? The date must be between "
                        " %s and today's date. \n mm/dd/yy: \n" % startDate.date())
                endDate = datetime.strptime(userIn, "%m/%d/%y")
                if (startDate < endDate <= now) == False:
                    print ('\n You have chosen an invalid date.')
                    count = True
                else:
                    count = False
            except ValueError:
                print ('Invalid Format!')


    ###### End of user input. Begin automated script.

    # The start time is used to calculate the elapsed time of the running script. The elapsed time will be displayed at
    # the end of the log file.
    start = time.time()

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
            logging.warning ( "\n This date (%s) has already been processed. The files will be reproecessed and "
                              "rewritten." % current_date)

        # Download current date SNODAS .tar file from the FTP site at
        #  ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/masked/
        SNODAS_utilities.download_SNODAS(download_path, current)

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

            # Copy and move current date's .tif file into name_of_clip_folder
            for file in os.listdir(setEnvironment_path):
                if current_date in str(file):
                    SNODAS_utilities.copy_and_move_SNODAS_tif_file(file, clip_path)

            # Assign projection to current date's .tif file (defaulted to WGS84)
            for file in os.listdir(clip_path):
                if current_date in str(file):
                    SNODAS_utilities.assign_SNODAS_projection(file, clip_path)

            # Clip current date's .tif file to the extent of the basin shapefile
            for file in os.listdir(clip_path):
                if current_date in str(file):
                    SNODAS_utilities.SNODAS_raster_clip(file, clip_path, basin_extent)

            # Reproject current date's .tif file into desired projection (defaulted to NAD83)
            for file in os.listdir(clip_path):
                if current_date in str(file):
                    SNODAS_utilities.SNODAS_raster_reproject_NAD83(file, clip_path)

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
                                                                  clip_path, snowCover_path)

            # Display elapsed time of current date's processing in log.
            end_day = time.time()
            elapsed_day = end_day - start_day
            logging.info('\n %s: Completed.' % current_date)
            logging.info('Elapsed time (date: %s): %d seconds' % (current_date,elapsed_day))

        # If config file value SaveAllSNODASparameters is not a valid value (either 'True' or 'False') the remaining
        # script will not run and the following error message will be printed to the console and to the logging file.
        else:
            print ('ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not valid. " \
                              "Please type in \'True\' or \'False\' and rerun this script.')
            logging.error(
                            "ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not "
                            "valid. Please type in 'True' or 'False' and rerun the script.")

    # Close logging including the elapsed time of the running script in seconds.
    end = time.time()
    elapsed = end - start
    logging.info('\n SNODASHistoricalDownload.py: Completed.')
    logging.info('Elapsed time (full script): %d seconds' % elapsed)
