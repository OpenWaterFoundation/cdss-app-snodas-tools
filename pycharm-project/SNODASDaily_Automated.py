# Name: SNODASDaily_Automated.py
# Version: 1
# Author: Emma Giles
# Organization: Open Water Foundation
#
# Purpose: This script outputs zonal statistics for the current date's downloaded SNODAS raster given the basin
# boundaries of the input shapefile. The script was originally created to use Colorado Watershed Basins as the vector
# input. The zonal statistics that are calculated are as follows: SWE mean, SWE minimum, SWE maximum, SWE standard
# deviation, pixel count and percentage of snow coverage. The functions in this script are housed within
# SNODAS_utilities.py. A more detailed description of each function is documented in the SNODAS_utilities.py file.
# This script is intended to be run on a task scheduler program so that the data is automatically processed every day.
# It can also be processed manually if desired.

# Import necessary modules.
import SNODAS_utilities
import configparser
import logging
import os
import sys
import time

from datetime import datetime, timedelta
from logging.config import fileConfig

from qgis.core import QgsApplication


# The start time is used to calculate the elapsed time of the running script. The elapsed time will be displayed at the
# end of the log file.
start = time.time()
# Check platform
if sys.platform == 'linux' or sys.platform == 'linux2' or sys.platform == 'cygwin' or sys.platform == 'darwin':
    LINUX_OS = True
else:
    LINUX_OS = False
# Read the config file to assign variables. Reference the following for code details:
# https://wiki.python.org/moin/ConfigParserExamples
CONFIG = configparser.ConfigParser()
CONFIG_FILE = '../test-CDSS/config/SNODAS-Tools-Config.ini'
CONFIG.read(CONFIG_FILE)


def config_section_map(section) -> dict:
    """ Obtain option values of config file sections. """
    dict1 = {}
    options = CONFIG.options(section)
    for option in options:
        try:
            dict1[option] = CONFIG.get(section, option)
            if dict1[option] == -1:
                print('Skip: {}'.format(option))
        except Exception as e:
            print('Exception on {}: {}'.format(option, e))
            dict1[option] = None
    return dict1

# Assign the values from the configuration file to the python variables. See below for description of each
# variable obtained by the configuration file.
#
#   SNODAS_ROOT: The SNODAS_ROOT folder is the folder housing all output files from this script.
#
#   BASIN_SHP_PATH: This is the full pathname to the shapefile holding the vector input(watershed basin boundaries).
#   The zonal statistics will be calculated for each feature of this layer. The shapefile must be projected into
#   NAD83 Zone 13N. This script was originally developed to process Colorado Watershed Basins as the input shapefile.
#
#   QGIS_HOME: The full path to QGIS installation on the local machine. This is used to initialize QGIS
#   resources & utilities. More info at: http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html.
#
#   SAVE_ALL_SNODAS_PARAMS: Each daily downloaded .tar SNODAS file contains 8 parameters as follows: (1) Snow Water
#   Equivalent (2) Snow Depth (3) Snow Melt Runoff at the Base of the Snow Pack (4) Sublimation from the Snow Pack
#   (5) Sublimation of Blowing Snow (6) Solid Precipitation (7) Liquid Precipitation and (8) Snow Pack Average
#   Temperature. The default setting, False, will delete all parameters except 'Snow Water Equivalent'. The optional
#   setting, True, will move all other parameters to a sub-folder under 1_Download called 'OtherParameters'
#
#   DOWNLOAD_FOLDER: The name of the download folder. Defaulted to '1_DownloadSNODAS'. All downloaded SNODAS
#   .tar files are contained here.
#
#   SET_FORMAT_FOLDER: The name of the setFormat folder. Defaulted to ' 2_SetFormat'. All SNODAS masked .tif
#   files are contained here.
#
#   CLIP_FOLDER: The name of the clip folder. Defaulted to '3_ClipToExtnet'. All SNODAS clipped (to basin
#   extent)and reprojected .tif files are contained here.
#
#   CREATE_SNOW_COVER_FOLDER: The name of the snow cover folder. Defaulted to '4_CreateSnowCover'. All binary
#   snow cover .tif files (clipped to basin extent) are contained here.
#
#   CALCULATE_STATS_FOLDER: The name of the results folder. All zonal statistic results in csv format are
#   contained here.
#
#   OUTPUT_STATS_BY_DATE_FOLDER: The name of the byDate folder. All zonal statistic results in csv format organized by
#   date are contained here.
#
#   OUTPUT_STATS_BY_BASIN_FOLDER: The name of the byBasin folder. All zonal statistic results in csv format organized by
#   basin are contained here.


# QGIS_HOME = config_section_map("ProgramInstall")['qgis_pathname']

SNODAS_ROOT = config_section_map("Folders")['root_pathname']
STATIC_FOLDER = config_section_map("Folders")['static_data_folder']
PROCESSED_FOLDER = config_section_map("Folders")['processed_data_folder']
DOWNLOAD_FOLDER = config_section_map("Folders")['download_snodas_tar_folder']
SET_FORMAT_FOLDER = config_section_map("Folders")['untar_snodas_tif_folder']
CLIP_FOLDER = config_section_map("Folders")['clip_proj_snodas_tif_folder']
CREATE_SNOW_COVER_FOLDER = config_section_map("Folders")['create_snowcover_tif_folder']
CALCULATE_STATS_FOLDER = config_section_map("Folders")['calculate_stats_folder']
OUTPUT_STATS_BY_DATE_FOLDER = config_section_map("Folders")['output_stats_by_date_folder']
OUTPUT_STATS_BY_BASIN_FOLDER = config_section_map("Folders")['output_stats_by_basin_folder']
TS_FOLDER = config_section_map("Folders")['timeseries_folder']
TS_GRAPH_BY_BASIN_FOLDER = config_section_map("Folders")['timeseries_graph_png_folder']

BASIN_SHP_PATH = config_section_map("BasinBoundaryShapefile")['pathname']

OUTPUT_CRS_EPSG = config_section_map("Projections")['output_proj_epsg']

SHP_ZIP = config_section_map("OutputLayers")['shp_zip']
DEL_SHP_ORIG = config_section_map("OutputLayers")['shp_delete_originals']
UPLOAD_TO_AMAZON_S3 = config_section_map("OutputLayers")['upload_results_to_amazon_s3']
RUN_DAILY_TSTOOL = config_section_map("OutputLayers")['process_daily_tstool_graphs']
RUN_HIST_TSTOOL = config_section_map("OutputLayers")['process_historical_tstool_graphs']

SAVE_ALL_SNODAS_PARAMS = config_section_map("SNODASparameters")['save_all_parameters']


if __name__ == "__main__":

    # Define static folder and extent shapefile
    static_path = os.path.join(SNODAS_ROOT, STATIC_FOLDER)
    extent_shapefile = static_path + 'studyAreaExtent_prj.shp'

    # Create the SNODAS_ROOT folder and the 7 sub-folders
    download_path = os.path.join(SNODAS_ROOT, PROCESSED_FOLDER, DOWNLOAD_FOLDER)
    setEnvironment_path = os.path.join(SNODAS_ROOT, PROCESSED_FOLDER, SET_FORMAT_FOLDER)
    clip_path = os.path.join(SNODAS_ROOT, PROCESSED_FOLDER, CLIP_FOLDER)
    snowCover_path = os.path.join(SNODAS_ROOT, PROCESSED_FOLDER, CREATE_SNOW_COVER_FOLDER)
    results_basin_path = os.path.join(SNODAS_ROOT, PROCESSED_FOLDER,
                                      CALCULATE_STATS_FOLDER + OUTPUT_STATS_BY_BASIN_FOLDER)
    results_date_path = os.path.join(SNODAS_ROOT, PROCESSED_FOLDER,
                                     CALCULATE_STATS_FOLDER + OUTPUT_STATS_BY_DATE_FOLDER)
    timeSeries_path = os.path.join(SNODAS_ROOT, PROCESSED_FOLDER,
                                   TS_FOLDER + TS_GRAPH_BY_BASIN_FOLDER)

    all_folders = [SNODAS_ROOT, download_path, setEnvironment_path, clip_path, snowCover_path,
                   results_basin_path, results_date_path, timeSeries_path]

    # Check for folder existence. If not exiting, the folder is created.
    for folder in all_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Create and configures logging file
    fileConfig(CONFIG_FILE)
    logger = logging.getLogger('log02')
    logger.info('SNODASDailyDownload.py: Started \n')

    # Print version information
    print("Running SNODASDaily_Automated.py Version 1")
    logger.info('Running SNODASDaily_Automated.py Version 1')

    # Initialize QGIS resources to utilize QGIS functionality.
    # More information at: http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html.
    if LINUX_OS:
        qgs = QgsApplication([], False, None)
        qgs.setPrefixPath("/usr", True)
        qgs.initQgis()
        sys.path.append('/usr/share/qgis/python/plugins')
    # else:
        # QgsApplication.setPrefixPath(QGIS_HOME, True)
        # qgs = QgsApplication([], False)
        # qgs.initQgis()

    # Get today's date in string format
    today = datetime.now()
    today_date = SNODAS_utilities.format_date_yyyymmdd(today)
    # Set the DateTextFile path outside the for loop so there's no chance it's undefined when used by both 'with open'
    # statements below
    DateTextFile = os.path.join(results_date_path, 'ListOfDates.txt')
    datesToProcess = []

    # Check if the past seven dates of SNODAS data was properly processed. If a date is missing, then process that date.
    for dayAgoNum in range(1, 7):
        pastDay = datetime.today() - timedelta(dayAgoNum)
        pastDay_string = pastDay.strftime('%Y%m%d')

        with open(DateTextFile, 'r') as TextFile:
            foundPastDay = False
            for line in TextFile:
                if pastDay_string in line:
                    logger.info('{} day ago was processed.'.format(dayAgoNum))
                    foundPastDay = True
                    TextFile.close()
                    break
            if not foundPastDay:
                datesToProcess.append(pastDay_string)

    # Check to see if today's date was processed.
    with open(DateTextFile, 'r') as TextFile:
        foundToday = False
        for line in TextFile:
            if str(today_date) in line:
                logger.info('Today has already been processed.')
                print('Today has already been processed.')
                foundToday = True
                TextFile.close()
                break
        if not foundToday:
            datesToProcess.append(today_date)

    # Log which dates will be processed with this run of the script.
    if datesToProcess:
        # The dates must be sorted from latest to most recent so that the change in SWE values can be correctly
        # calculated
        datesToProcess = sorted(datesToProcess)
        logger.info("These dates were not previously processed and will be processed now: {}".format(datesToProcess))
        print("These dates were not previously processed and will be processed now: {}".format(datesToProcess))
    else:
        logger.info("Today's date and the past seven days have already been processed.")
        print("Today's date and the past seven days have already been processed.")
        datesToProcess = ['None']

    # Keeps track of the dates that failed to download.
    list_of_download_fails = []

    for date in datesToProcess:

        # Only process the rest of the script if there are dates that have not previously been processed.
        if date != 'None':

            date_dateTimeFormat = datetime.strptime(date, '%Y%m%d')

            # Download today's SNODAS .tar file from SNODAS FTP site at
            # ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/masked/. Returned list contains a download timestamp and
            # information on the values of the configurable optional statistics.
            returnedList = SNODAS_utilities.download_snodas(download_path, date_dateTimeFormat)
            # Determine if the date failed to download and store in list_of_download_fails for future use.
            list_of_download_fails.append(returnedList[2])

            # Check to see if config values for optional statistics 'calculate_SWE_minimum, calculate_SWE_maximum,
            # calculate_SWE_stdDev' (defined in utility function) are valid. If valid, script continues to run. If
            # invalid, error message is printed to console and log file and script is terminated.
            tempList = []
            for stat in returnedList[1]:
                if stat.upper() == 'TRUE' or stat.upper() == 'FALSE':
                    tempList.append(1)
                else:
                    tempList.append(0)

            if 0 in tempList:
                logger.error('ERROR: See configuration file. One or more values of the OptionalZonalStatistics'
                             'section is not valid. Please change values to either True or False and rerun the script.')
                logging.error('ERROR: See configuration file. One or more values of the DesiredZonalStatistics section'
                              'is not valid. Please change values to either True or False and rerun the script.')

            else:

                # Untar today's data
                for file in os.listdir(download_path):
                    if date in str(file):
                        download_time_start = time.time()
                        SNODAS_utilities.untar_snodas_file(file, download_path, setEnvironment_path)
                        download_time_end = time.time()
                        elapsed_download = download_time_end - download_time_start

                # Check to see if configuration file 'SAVE_ALL_SNODAS_PARAMS' value is valid. If valid, script
                # continues to run. If invalid, error message is printed and log file and the script is terminated.
                if SAVE_ALL_SNODAS_PARAMS.upper() == 'FALSE' or SAVE_ALL_SNODAS_PARAMS.upper() == 'TRUE':

                    setEnvironment_time_start = time.time()
                    # Delete today's irrelevant files (parameters other than SWE).
                    if SAVE_ALL_SNODAS_PARAMS.upper() == 'FALSE':
                        for file in os.listdir(setEnvironment_path):
                            if date in str(file):
                                SNODAS_utilities.delete_irrelevant_snodas_files(file)

                    # Move irrelevant files (parameters other than SWE) to 'OtherSNODASParamaters'.
                    else:
                        parameter_path = os.path.join(setEnvironment_path, r'OtherParameters')
                        if not os.path.exists(parameter_path):
                            os.makedirs(parameter_path)
                        for file in os.listdir(setEnvironment_path):
                            if date in str(file):
                                SNODAS_utilities.move_irrelevant_snodas_files(file, parameter_path)

                    # Extract today's .gz files. Each SNODAS parameter files are zipped within a .gz file.
                    for file in os.listdir(setEnvironment_path):
                        if date in str(file):
                            SNODAS_utilities.extract_snodas_gz_file(file)

                    # Convert today's SNODAS SWE .dat file into .bil format.
                    for file in os.listdir(setEnvironment_path):
                        if date in str(file):
                            SNODAS_utilities.convert_snodas_dat_to_bil(file)

                    # Create today's custom .Hdr file. In order to convert today's SNODAS SWE .bil file into a usable
                    # .tif file, a custom .Hdr must be created. Refer to the function in the SNODAS_utilities.py for
                    # more information on the contents of the custom .HDR file.
                    for file in os.listdir(setEnvironment_path):
                        if date in str(file):
                            SNODAS_utilities.create_snodas_hdr_file(file)

                    # Convert today's .bil files to .tif files
                    for file in os.listdir(setEnvironment_path):
                        if date in str(file):
                            SNODAS_utilities.convert_snodas_bil_to_tif(file, setEnvironment_path)

                    # Delete today's .bil file
                    for file in os.listdir(setEnvironment_path):
                        if date in str(file):
                            SNODAS_utilities.delete_snodas_bil_file(file)
                    setEnvironment_time_end = time.time()
                    elapsed_setEnvironment = setEnvironment_time_end - setEnvironment_time_start

                    # Create the extent shapefile if not already created.
                    if not os.path.exists(extent_shapefile):
                        SNODAS_utilities.create_extent(BASIN_SHP_PATH, static_path)

                    clip_time_start = time.time()
                    # Copy and move today's .tif file into CLIP_FOLDER
                    for file in os.listdir(setEnvironment_path):
                        if date in str(file):
                            SNODAS_utilities.copy_and_move_snodas_tif_file(file, clip_path)

                    # Assign datum to today's .tif file (defaulted to WGS84)
                    for file in os.listdir(clip_path):
                        if date in str(file):
                            SNODAS_utilities.assign_snodas_datum(file, clip_path)

                    # Clip today's .tif file to the extent of the basin shapefile
                    for file in os.listdir(clip_path):
                        if date in str(file):
                            SNODAS_utilities.snodas_raster_clip(file, clip_path, extent_shapefile)

                    # Project today's .tif file into desired projection (defaulted to Albers Equal Area)
                    for file in os.listdir(clip_path):
                        if date in str(file):
                            SNODAS_utilities.assign_snodas_projection(file, clip_path)
                    clip_time_end = time.time()
                    elapsed_clip = clip_time_end - clip_time_start

                    snowCover_time_start = time.time()
                    # Create today's snow cover binary raster
                    for file in os.listdir(clip_path):
                        if date in str(file):
                            SNODAS_utilities.snow_coverage(file, clip_path, snowCover_path)
                    snowCover_time_end = time.time()
                    elapsed_snowCover = snowCover_time_end - snowCover_time_start

                    manipulateCSV_time_start = time.time()
                    # Create .csv files of byBasin and byDate outputs
                    for file in os.listdir(clip_path):
                        if date in str(file):
                            SNODAS_utilities.create_csv_files(file, BASIN_SHP_PATH, results_date_path, results_basin_path)

                    # Delete rows from basin CSV files if the date is being reprocessed
                    for file in os.listdir(clip_path):
                        if date in str(file):
                            SNODAS_utilities.delete_by_basin_csv_repeated_rows(file, BASIN_SHP_PATH, results_basin_path)
                    manipulateCSV_time_end = time.time()
                    elapsed_manipulateCSV = manipulateCSV_time_end - manipulateCSV_time_start

                    zStats_time_start = time.time()
                    # Calculate zonal statistics and export results
                    for file in os.listdir(clip_path):
                        if date in str(file):
                            SNODAS_utilities.z_stat_and_export(file, BASIN_SHP_PATH, results_basin_path, results_date_path,
                                                               clip_path, snowCover_path, date_dateTimeFormat,
                                                               returnedList[0], OUTPUT_CRS_EPSG)
                    zStats_time_end = time.time()
                    elapsed_zStats = zStats_time_end - zStats_time_start

                    # If desired, zip files of output shapefile (both today's data and latestDate file)
                    if SHP_ZIP.upper() == 'TRUE':
                        for file in os.listdir(results_date_path):
                            if date in str(file) and file.endswith('.shp'):
                                SNODAS_utilities.zip_shapefile(file, results_date_path, DEL_SHP_ORIG)
                            if "LatestDate" in str(file) and file.endswith('.shp'):
                                zip_full_path = os.path.join(results_date_path,
                                                             "SnowpackStatisticsByDate_LatestDate.zip")

                                if os.path.exists(zip_full_path):
                                    os.remove(zip_full_path)

                                SNODAS_utilities.zip_shapefile(file, results_date_path, DEL_SHP_ORIG)

                    # If desired, run TSTool for the day.
                    if RUN_DAILY_TSTOOL.upper() == "TRUE":

                        # Create SNODAS SWE time series graph with TsTool program.
                        TsTool_time_start = time.time()
                        SNODAS_utilities.create_snodas_swe_graphs()
                        TsTool_time_end = time.time()
                        elapsed_TsTool = TsTool_time_end - TsTool_time_start

                # If configuration file value SaveAllSNODASparameters is not a valid value (either 'True' or 'False')
                # the remaining script will not run and the following error message will be printed to the console and
                # to the logging file.
                else:
                    logger.error(
                        "ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not valid."
                        "Please type in 'True' or 'False' and rerun the script.")
                    logging.error(
                        "ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not valid."
                        "Please type in 'True' or 'False' and rerun the script.")

    # Log list_of_download_fails for troubleshooting purposes.
    logger.info("list_of_download_fails is: %s" % list_of_download_fails)
    logging.info("list_of_download_fails is: %s" % list_of_download_fails)

    # Remove any duplicates that occurred in the byBasin csv files (this scenario is rare but could happen.)
    SNODAS_utilities.clean_duplicates_from_by_basin_csv(results_basin_path)

    # If the RUN_DAILY_TSTOOL is set to False, run the historical processing of TSTool.
    if 'None' in list_of_download_fails and RUN_HIST_TSTOOL.upper() == "TRUE":
        # Create SNODAS SWE time series graph with TsTool program.
        TsTool_time_start = time.time()
        SNODAS_utilities.create_snodas_swe_graphs()
        TsTool_time_end = time.time()
        elapsed_TsTool = TsTool_time_end - TsTool_time_start

    # Push daily statistics to the web, if configured
    if UPLOAD_TO_AMAZON_S3.upper() == 'TRUE':
        if LINUX_OS:
            print('push_to_gcp: Pushing to AWS is currently disabled for testing purposes.')
            logger.info('push_to_gcp: Pushing to AWS is currently disabled for testing purposes.')
            # SNODAS_utilities.push_to_gcp()
        else:
            SNODAS_utilities.push_to_aws()
    else:
        logger.info('Output files from SNODAS_Tools are not pushed to cloud storage because of setting in configuration'
                    'file. ')

    # Close logging including the elapsed time of the running script in seconds.
    elapsed = time.time() - start
    elapsed_hours = int(elapsed / 3600)
    elapsed_hours_remainder = elapsed % 3600
    elapsed_minutes = int(elapsed_hours_remainder / 60)
    elapsed_seconds = int(elapsed_hours_remainder % 60)

    # Remove the provider and layer registries from memory
    qgs.exitQgis()

    # Remove temp files in ByDate folder
    for file in os.listdir(results_date_path):
        if file.endswith('.tmp'):
            os.remove(os.path.join(results_date_path, file))

    logger.info('\n SNODASDailyDownload.py: Completed.')
    logger.info('Elapsed time: {} hours, {} minutes and {} seconds'
                .format(elapsed_hours, elapsed_minutes, elapsed_seconds))
    logging.info('Elapsed time: {} hours, {} minutes and {} seconds'
                 .format(elapsed_hours, elapsed_minutes, elapsed_seconds))
    print('Elapsed time: {} hours, {} minutes and {} seconds'.format(elapsed_hours, elapsed_minutes, elapsed_seconds))
