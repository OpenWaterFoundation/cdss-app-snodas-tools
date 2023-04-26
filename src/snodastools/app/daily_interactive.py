"""
This script allows the user to interactively input historical dates of interest for processing.
The user can decide between a single date and a range of dates.
This script does not allow for the user to pick a list of non-sequential dates.

This program calculates zonal statistics for historical daily SNODAS rasters given the basin boundaries of an
input basin boundary shapefile.
The zonal statistics that are calculated are as follows:

  SWE mean
  SWE minimum
  SWE maximum
  SWE standard deviation
  pixel count
  percentage of snow coverage

The computational functions are located in the snodas_util.py module, which includes function documentation.
"""

# Import necessary modules.
import argparse
import configparser
import glob
import logging
import os
import snodastools.app.version as version
import snodastools.util.config_util as config_util
import snodastools.util.log_util as log_util
import snodastools.util.os_util as os_util
import snodastools.util.snodas_util as snodas_util
import sys
import tempfile
import time

from datetime import date, datetime, timedelta
from logging.config import fileConfig
from pathlib import Path

from qgis.core import QgsApplication

# Assign the values from the configuration file to the Python variables.
# See below for description of each variable obtained by the configuration file.
#
# SNODAS_ROOT: The SNODAS_ROOT folder is the parent folder for all input and output files.
#
# BASIN_SHP_PATH: This is the full pathname to the shapefile holding the vector input (watershed basin boundaries).
# The zonal statistics will be calculated for each feature of this layer.
# The shapefile must be projected into NAD83 Zone 13N.
# This script was originally developed to process Colorado Watershed Basins as the input shapefile.
#
# QGIS_HOME: The full path to QGIS installation on the local machine.
# This is used to initialize QGIS resources & utilities.
# More info at: http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html.
#
# SAVE_ALL_SNODAS_PARAMS: Each daily downloaded .tar SNODAS file contains 8 parameters as follows:
#  (1) Snow Water Equivalent
#  (2) Snow Depth
#  (3) Snow Melt Runoff at the Base of the Snow Pack
#  (4) Sublimation from the Snow Pack
#  (5) Sublimation of Blowing Snow
#  (6) Solid Precipitation
#  (7) Liquid Precipitation and
#  (8) Snow Pack Average Temperature
#
# The default setting, False, will delete all parameters except 'Snow Water Equivalent'.
# The optional setting, True, will move all other parameters to a sub-folder under 1_Download called 'OtherParameters'.
#
# DOWNLOAD_FOLDER: The name of the download folder. Defaulted to '1_DownloadSNODAS'.
# All downloaded SNODAS .tar files are contained here.
#
# SET_FORMAT_FOLDER: The name of the setFormat folder. Defaulted to ' 2_SetFormat'.
# All SNODAS masked .tif files are contained here.
#
# CLIP_FOLDER: The name of the clip folder. Defaulted to '3_ClipToExtnet'.
# All SNODAS clipped (to basin extent) and reprojected .tif files are contained here.
#
# CREATE_SNOW_COVER_FOLDER: The name of the snow cover folder. Defaulted to '4_CreateSnowCover'.
# All binary snow cover .tif files (clipped to basin extent) are contained here.
#
# CALCULATE_STATS_FOLDER: The name of the folder containing statistics results.
# All zonal statistic results in csv format are contained here.
#
# OUTPUT_STATS_BY_DATE_FOLDER: The name of the byDate folder.
# All zonal statistic results in csv format organized by date are contained here.
#
# OUTPUT_STATS_BY_BASIN_FOLDER: The name of the byBasin folder.
# All zonal statistic results in csv format organized by basin are contained here.
#
# KEEP_FILES: Whether to keep intermediate files.
# Set to 'True' to keep all intermediate files or 'False' (default) to clean up to save disk space.


# Declare application variables:
# - these are populated in the set_app_globals() function.
# - TODO smalers 2023-04-24 maybe need a "session" object to manage

# QGIS_HOME or None = None

SNODAS_ROOT: str or None = None
# SHARED_ROOT_DIR: str or None = None
STATIC_FOLDER: str or None = None
PROCESSED_FOLDER: str or None = None
# SHARED_PROCESSED_DATA_DIR: str or None = None
DOWNLOAD_FOLDER: str or None = None
SET_FORMAT_FOLDER: str or None = None
CLIP_FOLDER: str or None = None
CREATE_SNOW_COVER_FOLDER: str or None = None
CALCULATE_STATS_FOLDER: str or None = None
OUTPUT_STATS_BY_DATE_FOLDER: str or None = None
OUTPUT_STATS_BY_BASIN_FOLDER: str or None = None

BASIN_SHP_PATH: str or None = None

OUTPUT_CRS: str or None = None

DEV_ENVIRONMENT: str or None = None
SHP_ZIP: str or None = None
DEL_SHP_ORIG: str or None = None
UPLOAD_TO_S3: str or None = None
UPLOAD_TO_GCP: str or None = None
RUN_DAILY_TSTOOL: str or None = None
RUN_HIST_TSTOOL: str or None = None

SAVE_ALL_SNODAS_PARAMS: str or None = None

KEEP_FILES: str or None = None

# Command line absolute path to SNODAS Tools implementation root:
# - this folder will have config as a sub-folder
command_line_snodas_root: str or None = None


def arg_parse() -> None:
    """
    Parse command line arguments. Currently implemented options are:

    -h, --help   Displays help information for the program (auto-generated).
    --version    Displays the SNODAS Tools version.
    """

    parser = argparse.ArgumentParser(prog='daily_interactive', description='SNODAS Tools daily interactive processor.')

    # Define recognized command parameters.
    parser.add_argument('--version', action="store_true", help='Print program version.')

    # Assigns the command file to args.commands:
    # --root snodas-tools-root-folder
    parser.add_argument("--snodas", help="Specify SNODAS Tools implementation root folder.")

    # Parse the command line.
    args, unknown_args = parser.parse_known_args()

    # Handle parsed commands line parameters.
    if args.version:
        # Print the version.
        print_version()

    if args.snodas:
        # The root folder for a SNODAS Tools implementation was specified on the command line.
        global command_line_snodas_root
        command_line_snodas_root = args.snodas


def print_version() -> None:
    """
    Print the program version.
    """
    print("", file=sys.stderr)
    print("daily_automated version " + version.app_version, file=sys.stderr)
    print("", file=sys.stderr)
    print("SNODAS Tools", file=sys.stderr)
    print("Copyright 2017-2023 Colorado Department of Natural Resources.", file=sys.stderr)
    print("", file=sys.stderr)
    print("License GPLv3+:  GNU GPL version 3 or later", file=sys.stderr)
    print("", file=sys.stderr)
    print("There is ABSOLUTELY NO WARRANTY; for details see the", file=sys.stderr)
    print("'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file.", file=sys.stderr)
    print("This is free software: you are free to change and redistribute it", file=sys.stderr)
    print("under the conditions of the GPLv3 license in the LICENSE file.", file=sys.stderr)
    print("", file=sys.stderr)


def set_config_globals() -> None:
    """
    Set application global variables using the configuration file properties that were previously read.
    """
    # Declare variables as global.
    # global QGIS_HOME

    global SNODAS_ROOT
    # global SHARED_ROOT_DIR
    global STATIC_FOLDER
    global PROCESSED_FOLDER
    # global SHARED_PROCESSED_DATA_DIR
    global DOWNLOAD_FOLDER
    global SET_FORMAT_FOLDER
    global CLIP_FOLDER
    global CREATE_SNOW_COVER_FOLDER
    global CALCULATE_STATS_FOLDER
    global OUTPUT_STATS_BY_DATE_FOLDER
    global OUTPUT_STATS_BY_BASIN_FOLDER

    global BASIN_SHP_PATH

    global OUTPUT_CRS

    global DEV_ENVIRONMENT
    global SHP_ZIP
    global DEL_SHP_ORIG
    global UPLOAD_TO_S3
    global UPLOAD_TO_GCP
    global RUN_DAILY_TSTOOL
    global RUN_HIST_TSTOOL

    global SAVE_ALL_SNODAS_PARAMS

    global KEEP_FILES

    # global QGIS_HOME = config_map('ProgramInstall')['qgis_pathname']

    SNODAS_ROOT = config_util.get_config_prop('Folders.root_folder')
    if not SNODAS_ROOT:
        # Try the old syntax.
        SNODAS_ROOT = config_util.get_config_prop('Folders.root_dir')
    # SHARED_ROOT_DIR = config_util.get_config_prop('Folders.shared_root_dir')
    STATIC_FOLDER = config_util.get_config_prop('Folders.static_data_folder')
    if not STATIC_FOLDER:
        # Try the old syntax.
        STATIC_FOLDER = config_util.get_config_prop('Folders.static_data_dir')
    PROCESSED_FOLDER = config_util.get_config_prop('Folders.processed_data_folder')
    # SHARED_PROCESSED_DATA_DIR = config_util.get_config_prop('Folders.shared_processed_data_dir')
    DOWNLOAD_FOLDER = config_util.get_config_prop('Folders.download_snodas_tar_folder')
    SET_FORMAT_FOLDER = config_util.get_config_prop('Folders.untar_snodas_tif_folder')
    CLIP_FOLDER = config_util.get_config_prop('Folders.clip_proj_snodas_tif_folder')
    CREATE_SNOW_COVER_FOLDER = config_util.get_config_prop('Folders.create_snowcover_tif_folder')
    CALCULATE_STATS_FOLDER = config_util.get_config_prop('Folders.calculate_stats_folder')
    OUTPUT_STATS_BY_DATE_FOLDER = config_util.get_config_prop('Folders.output_stats_by_date_folder')
    OUTPUT_STATS_BY_BASIN_FOLDER = config_util.get_config_prop('Folders.output_stats_by_basin_folder')

    BASIN_SHP_PATH = config_util.get_config_prop('BasinBoundaryShapefile.pathname')

    # TODO smalers 2023-04-25 changed for SNODAS Tools 2.1.0.
    #OUTPUT_CRS_EPSG = config_util.get_config_prop('Projections.output_proj_epsg')
    OUTPUT_CRS = config_util.get_config_prop('Projections.output_crs')

    DEV_ENVIRONMENT = config_util.get_config_prop('OutputLayers.dev_environment')
    SHP_ZIP = config_util.get_config_prop('OutputLayers.shp_zip')
    DEL_SHP_ORIG = config_util.get_config_prop('OutputLayers.shp_delete_originals')
    UPLOAD_TO_S3 = config_util.get_config_prop('OutputLayers.upload_to_s3')
    UPLOAD_TO_GCP = config_util.get_config_prop('OutputLayers.gcp_upload')
    RUN_DAILY_TSTOOL = config_util.get_config_prop('OutputLayers.process_daily_tstool_graphs')
    RUN_HIST_TSTOOL = config_util.get_config_prop('OutputLayers.process_historical_tstool_graphs')

    SAVE_ALL_SNODAS_PARAMS = config_util.get_config_prop('SNODASParameters.save_all_parameters')

    KEEP_FILES = config_util.get_config_prop('Troubleshooting.keep_files')


def setup_logging(app_name: str, log_file_path: Path) -> None:
    """
    Setup logging for the application.

    Args:
        app_name:  The application name (Python package).
        log_file_path:  Log file path.

    Returns:
        None.
    """
    # Customized logging config using log file in user's home folder:
    # - for now use default log levels defined by the utility function
    print("Setting up application logging configuration:", file=sys.stderr)
    print("  log file = {}".format(log_file_path), file=sys.stderr)
    initial_file_log_level = logging.DEBUG
    initial_console_log_level = logging.INFO
    logger0 = log_util.initialize_logging(app_name=app_name,
                                          logfile_name=str(log_file_path.absolute()),
                                          logfile_log_level=initial_file_log_level,
                                          console_log_level=initial_console_log_level)

    # Test some logging messages.
    message = 'Opened initial log file: {}'.format(log_file)
    logger0 = logging.getLogger(__name__)
    logger0.info(message)
    # Also print to the console in case the configuration is not working.
    print(message, file=sys.stderr)


if __name__ == '__main__':
    """
    Main program entry point into this program.
    """

    # Parse the command line.
    arg_parse()

    # Determine the configuration file path:
    # - default based on what is found relative to the current folder
    config_file_path = config_util.find_config_file(command_line_snodas_root)
    if not config_file_path:
        print("SNODAS Tools configuration file could not be determined.", file=sys.stderr)
        print("  May need to run with: --snodas snodas-root-folder", file=sys.stderr)
        exit(1)
    elif not config_file_path.exists():
        print("SNODAS Tools configuration file does not exist:", file=sys.stderr)
        print("  {}".format(config_file_path), file=sys.stderr)
        exit(1)
    elif not config_file_path.is_file():
        print("SNODAS Tools configuration path is not a file:", file=sys.stderr)
        print("  {}".format(config_file_path), file=sys.stderr)
        exit(1)

    # Program name to use for logging.
    program_name = 'snodastools.app.daily_interactive'

    # Read the configuration file:
    # - the configuration values are maintained in 'config_util'
    # - use get_config_prop to get a property
    # - TODO smalers 2023-04-24 need to initialize the logger to console only at the start and then do below
    config_util.read_config_file ( config_file_path )

    # Set application variables from the configuration.
    set_config_globals ()

    # Configure logging:
    # - this uses INI property syntax
    # - can't set up the logger until after the configuration file is known from above
    # - default (Linux) is to use the configuration file logging properties
    use_config_for_logging = True
    if not os_util.is_linux_os():
        # When running on Windows, use logging similar to OWF GeoProcessor.
        use_config_for_logging = False

    # Configure logging depending on whether running on Linux or Windows.
    if use_config_for_logging:
        fileConfig(config_file_path)
        logger = logging.getLogger('logger_interactive')
    else:
        processed_data_folder = config_util.get_config_prop("Folders.processed_data_folder")
        if processed_data_folder:
            # The log file is created in the configuration file ${processed_data_folder}/logs folder.
            log_folder = Path(processed_data_folder) / "logs"
            log_file = Path(log_folder) / (program_name + ".log")
            if not log_folder.exists():
                log_folder.mkdir(parents=True)
        else:
            # Use a temporary file:
            # - the following returns an opened file pointer
            # - close it and then reuse the name
            temp_log_file = tempfile.NamedTemporaryFile(suffix=".log")
            log_file = Path(temp_log_file.name)
            temp_log_file.close()
        setup_logging(program_name, log_file)
        logger = logging.getLogger(__name__)

    # Print version information.
    print('Running {}.py version {}'.format(program_name, version.app_version), file=sys.stderr)
    logger.info('Running {}.py version {}'.format(program_name, version.app_version))

    # Initialize QGIS resources.  See:
    # http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html.
    # This block of code allows for the script to utilize QGIS functionality.
    # QgsApplication.setPrefixPath(QGIS_HOME, True)
    QgsApplication.setPrefixPath('/usr', True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    if version.version_uses_new_config():
        # Configuration file for version 2.1 or later uses full paths.
        # Define static folder and extent shapefile:
        # - for example, this is the State of Colorado boundary
        static_path: Path = Path(STATIC_FOLDER)
        extent_shapefile: Path = static_path / 'studyAreaExtent_prj.shp'
    else:
        # Configuration file prior to version 2.1 used incremental file parts.
        # Define static folder and extent shapefile:
        # - for example, this is the State of Colorado boundary
        static_path: Path = Path(SNODAS_ROOT) / STATIC_FOLDER
        extent_shapefile: Path = static_path / 'studyAreaExtent_prj.shp'

    # Get today's date.
    now = datetime.now()

    # Get user inputs as raw data.
    # Ask the user to decide between downloading only one date of data or a range of multiple dates of data.
    prompt = "SNODAS>"
    single_or_range = input('\n' + prompt +
                            ' Process one date or a range of dates ("one" or "range" or "q" to quit)? ')
    if single_or_range == 'q' or single_or_range == 'Q':
        exit(0)

    # While loop that continues to prompt user for a new input if original input is invalid.
    while single_or_range.upper() != 'ONE' and single_or_range.upper() != 'RANGE':

        # Ask the user to re-enter downloading data type - one date or range of dates.
        single_or_range = input('\n' + prompt +
                                ' The input is not recognized. Process one date or a range '
                                'of dates ("one" or "range" or "q" to quite)? ')
        if single_or_range == 'q' or single_or_range == 'Q':
            exit(0)

    logger.info("SNODAS_ROOT={}".format(SNODAS_ROOT))
    if version.version_uses_new_config():
        # Configuration file for version 2.1 or later uses full paths.
        # Create the SNODAS_ROOT folder and the 5 sub-folders
        # (Defaulted to: 1_DownloadSNODAS, 2_SetFormat, 3_ClipToExtent, 4_CreateSnowCover,
        # 5_CalculateStatistics [2 sub-folders: StatisticsByBasin, StatisticsByDate]).
        # Check for folder existence.
        # If exists, the folder is not recreated.
        # Refer to developer documentation for information regarding the types of files contained within each folder.
        root_path = Path(SNODAS_ROOT)
        download_path = Path(DOWNLOAD_FOLDER)
        set_format_path = Path(SET_FORMAT_FOLDER)
        clip_path = Path(CLIP_FOLDER)
        snow_cover_path = Path(CREATE_SNOW_COVER_FOLDER)
        results_basin_path = Path(OUTPUT_STATS_BY_BASIN_FOLDER)
        results_date_path = Path(OUTPUT_STATS_BY_DATE_FOLDER)
    else:
        # Configuration file prior to version 2.1 used incremental file parts.
        # Create the SNODAS_ROOT folder and the 5 sub-folders
        # (Defaulted to: 1_DownloadSNODAS, 2_SetFormat, 3_ClipToExtent, 4_CreateSnowCover,
        # 5_CalculateStatistics [2 sub-folders: StatisticsByBasin, StatisticsByDate]).
        # Check for folder existence.
        # If exiting, the folder is not recreated.
        # Refer to developer documentation for information regarding the types of files contained within each folder.
        root_path = Path(SNODAS_ROOT)
        download_path = Path(SNODAS_ROOT) / PROCESSED_FOLDER / DOWNLOAD_FOLDER
        set_format_path = Path(SNODAS_ROOT) / PROCESSED_FOLDER / SET_FORMAT_FOLDER
        clip_path = Path(SNODAS_ROOT) / PROCESSED_FOLDER / CLIP_FOLDER
        snow_cover_path = Path(SNODAS_ROOT) / PROCESSED_FOLDER / CREATE_SNOW_COVER_FOLDER
        results_basin_path = Path(SNODAS_ROOT) / PROCESSED_FOLDER /\
                             (CALCULATE_STATS_FOLDER + OUTPUT_STATS_BY_BASIN_FOLDER)
        results_date_path = Path(SNODAS_ROOT) / PROCESSED_FOLDER /\
                            (CALCULATE_STATS_FOLDER + OUTPUT_STATS_BY_DATE_FOLDER)

    # All necessary folders are Path instances.
    all_folders = [
        root_path,
        download_path,
        set_format_path,
        clip_path,
        snow_cover_path,
        results_basin_path,
        results_date_path
    ]

    for folder in all_folders:
        if not folder.exists():
            logger.info("  SNODAS Tools folder does not exist, creating:")
            logger.info("    {}".format(folder))
            if os_util.is_linux_os():
                folder.mkdir(mode=777, parents=True, exist_ok=True)
            else:
                folder.mkdir(parents=True)

    single_date = None

    # Earliest date with data.
    earliest_date = date(year=2003, month=9, day=30)

    # After the user chooses the project folder where the data will be stored,
    # they must then choose the date(s) to process.
    if single_or_range.upper() == 'ONE':
        # A single date (single_date) is will be processed.

        # Ask the user which date of data they would like.
        # Must be in mm/dd/yyyy format and be within the specified range of available dates.
        # Continue to ask the user for a date if the input is not a valid date or is outside the data range.
        while True:
            try:
                user_input = input(
                    "\n" + prompt + " Specify a date on or between September 30, 2003 and today "
                                    "(mm/dd/yyyy, q to quit, enter for today): ")
                if user_input == 'q' or user_input == 'Q':
                    exit(0)
                elif not user_input:
                    # Default to today.
                    single_date = now.date()
                else:
                    # Parse the date.
                    try:
                        single_date = datetime.strptime(user_input, '%m/%d/%Y').date()
                    except ValueError:
                        print('\n' + prompt + ' Invalid date format. Try again.')
                        continue
                if single_date < earliest_date:
                    print('\n' + prompt +
                          ' The date ({}) is less than the earliest available date ({}).'.format(single_date,
                                                                                                 earliest_date))
                if single_date > now.date():
                    print('\n' + prompt + ' The date ({}) is after today ({}).'.format(single_date, now.date()))
                else:
                    # Start and end dates are the same date.
                    start_date = single_date
                    end_date = single_date
                    break
            except Exception as e:
                print('\n' + prompt + ' Unexpected error ({}).  Try again.'.format(e))

    else:
        # A range of dates (start_date to end_date) will be processed.
        #
        # Ask the user for the START date to process.
        # Must be in mm/dd/yyyy format and be within the specified range of available dates.
        # Continue to ask the user for a date if the input is not a valid date or is outside the data range.
        while True:
            try:
                user_input = input(
                    "\n" + prompt + " What is the STARTING (earliest) date to process?"
                    "\n" + prompt + " The date must be on or between September 30, 2003 and today "
                                    "(mm/dd/yyyy, q to quit, enter for today): ")
                if user_input == 'q' or user_input == 'Q':
                    exit(0)
                elif not user_input:
                    # Default to today.
                    start_date = now.date()
                else:
                    start_date = datetime.strptime(user_input, '%m/%d/%Y').date()
                if start_date < earliest_date:
                    print('\n' + prompt +
                          ' The start date ({}) is less than the earliest allowed date ({}).'.format(
                              start_date, earliest_date))
                elif start_date > now.date():
                    print('\n' + prompt + ' The start date ({}) is after today ({}).'.format(start_date,
                                                                                             now.date()))
                else:
                    # Start date is OK.
                    break
            except ValueError:
                print('\n' + prompt + ' Invalid date format. Try again.')

        # Ask the user for the END date to process.
        # Must be in mm/dd/yyyy format and be within the specified range of available dates.
        # Continue to ask the user for a date if the input is not a valid date or is outside the data range.
        while True:
            try:
                user_input = input(
                    "\n" + prompt + " What is the ENDING (most recent) date to process?"
                    "\n" + prompt + " The date must be on or between {} and today "
                                    "(mm/dd/yyyy, q to quit, enter for today): ".format(start_date))
                if user_input == 'q' or user_input == 'Q':
                    exit(0)
                elif not user_input:
                    # Default to today.
                    end_date = now.date()
                else:
                    end_date = datetime.strptime(user_input, '%m/%d/%Y').date()
                if end_date < start_date:
                    print('\n' + prompt +
                          ' The end date ({}) is before the start date ({}).'.format(end_date,
                                                                                     start_date))
                elif end_date > now.date():
                    print('\n' + prompt + ' The end date ({}) is after today ({}).'.format(end_date, now.date()))
                else:
                    # End date is OK.
                    break
            except ValueError:
                print('\n' + prompt + ' Invalid date format. Try again.')

    # ----------------- End of user input. Begin automated script.------------------------------------------------------

    # The start time is used to calculate the total elapsed time of the script.
    # The elapsed time will be displayed at the end of the log file.
    # Intermediate times may be printed by steps where the processing time is relatively longer.
    start = time.time()

    # Create an empty list that will contain all dates that failed to download.
    failed_dates_lst = []

    # Iterate through each day of the user-specified range.
    total_days = (end_date - start_date).days + 1

    current = start_date
    first_date = True
    while current <= end_date:
        if first_date:
            # First date so 'current' is the initial value.
            first_date = False
        else:
            # Advance the date.
            current += timedelta(days=1)
            if current > end_date:
                break

        # The start time is used to calculate the elapsed time of the running script.
        # The elapsed time will be displayed at the end of the log file.
        start_time = time.time()

        # Format date into string with format YYYYMMDD:
        # - the current date is used to match files in folders and name output files
        current_date_str = snodas_util.format_date_yyyymmdd(current)
        current_date_tar = 'SNODAS_' + current_date_str + '.tar'
        logger.info("Processing SNODAS for {}".format(current_date_str))
        print("Processing SNODAS for current={}, current_date_str={}".format(current, current_date_str))

        # Check to see if this date for data has already been processed in the folder.
        possible_file = download_path / current_date_tar

        if possible_file.exists():
            # The download & zonal statistics are rerun:
            # - print a message explaining that the old files will be overwritten
            logger.info('This date ({}) has previously been processed.'.format(current_date_str))
            logger.info('The files will be reprocessed and rewritten.')

        # Download current date SNODAS .tar file from the FTP site using configuration file properties:
        # - for example:
        #     ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/masked/
        # - downloadMetadataList is a list of several pieces of information (see the download function for details)
        downloadMetadataList = snodas_util.download_snodas(download_path, current)

        failed_dates_lst.append(downloadMetadataList[2])

        # Check to see if configuration values for optional statistics, as defined in the utility function, are valid:
        #   'calculate_SWE_minimum'
        #   'calculate_SWE_maximum'
        #   'calculate_SWE_stdDev'
        # If valid, the script continues to run.
        # If invalid, an error message is printed to console and the log file and script is terminated.
        valid_list = []
        for stat in downloadMetadataList[1]:
            if stat.upper() == 'TRUE' or stat.upper() == 'FALSE':
                valid_list.append(1)
            else:
                valid_list.append(0)

        if 0 in valid_list:
            logger.error(
                'See configuration file. One or more values of the "OptionalZonalStatistics" section is '
                'not valid. Change values to either "True" or "False" and rerun the script.', exc_info=True)
            break

        else:
            # Untar current date's data:
            # - the filename is like:
            #     SNODAS_20230424.tar
            # - should be only one file but use a loop to simplify logic and have control over file names below
            # - the tar file is not zipped because files within the tar file are zipped and are handled below
            # - the tar file contains multiple SNODAS output data types in separate files
            for tar_file_path in snodas_util.list_dir(download_path, '*' + current_date_str + '*.tar'):
                snodas_util.untar_snodas_file(tar_file_path, download_path, set_format_path)

            # Check to see if configuration file 'SAVE_ALL_SNODAS_PARAMS' value is valid.
            # If valid (true or false), the script continues to run.
            # If invalid, an error message is printed to the console and the log file and the script is terminated.
            #logger.info('Should save all SNODAS parameter data files? {}'.format(SAVE_ALL_SNODAS_PARAMS))
            if SAVE_ALL_SNODAS_PARAMS.upper() == 'FALSE' or SAVE_ALL_SNODAS_PARAMS.upper() == 'TRUE':

                if SAVE_ALL_SNODAS_PARAMS.upper() == 'FALSE':
                    # Delete current date's irrelevant files (parameters other than SWE):
                    # - only files with 1034 in the file name are kept
                    # - this substring does not match any valid date so OK to filter it and 'current_date_str'
                    # - use a for loop because multiple files
                    # TODO smalers 2023-04-25 don't know why the following log message is not printed to console or log.
                    logger.info('Start deleting unused data files (data types are not of interest):')
                    for data_file_path in snodas_util.list_dir(set_format_path, '*' + current_date_str + '*'):
                        snodas_util.delete_irrelevant_snodas_files(data_file_path)
                    logger.info('  Finished deleting unused data files.')
                else:
                    # Move irrelevant files (parameters other than SWE) to 'OtherSNODASParameters':
                    # - want to keep files for data types in addition to SWE
                    # - use a for loop because multiple files
                    # - messages are printed in the called function
                    parameter_path = set_format_path / 'OtherParameters'
                    if not parameter_path.exists():
                        parameter_path.mkdir()
                    for file in snodas_util.list_dir(set_format_path, '*' + current_date_str + '*'):
                        snodas_util.move_irrelevant_snodas_files(file, parameter_path)

                # Extract current date's .gz files:
                # - use a for loop because multiple files
                # - each SNODAS parameter and header files are zipped within a .gz file, for example:
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.dat.gz
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.txt.gz
                # - there is only one file per zip file so the output is, for example:
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.dat
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.txt
                for file in snodas_util.list_dir(set_format_path, '*' + current_date_str + '*.gz'):
                    snodas_util.extract_snodas_gz_file(file)

                # Convert current date's SNODAS SWE .dat file into .bil format:
                # - this just renames the file without any additional changes, so the output is, for example:
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.bil
                # - use a loop until file names are simpler to deal with and may enable other data types
                for file in snodas_util.list_dir(set_format_path, '*' + current_date_str + '*.dat'):
                    snodas_util.convert_snodas_dat_to_bil(file)

                # Create current date's custom .hdr file from the .txt file:
                # - the file name will be like:
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.hdr
                # - to convert a custom .bil file into a .tif file, a custom .hdr with metadata must be created
                # - refer to the function in the snodas_util.py for more information about the custom .hdr file.
                # - use a loop until file names are simpler to deal with and may enable other data types
                for bil_file_path in snodas_util.list_dir(set_format_path, '*' + current_date_str + '*.bil'):
                    snodas_util.create_snodas_hdr_file(bil_file_path)

                # Convert current date's .bil files to .tif files:
                # - just rename to something like:
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.tif
                # - use a loop until file names are simpler to deal with and may enable other data types
                for bil_file_path in snodas_util.list_dir(set_format_path, '*' + current_date_str + '*.bil'):
                    snodas_util.convert_snodas_bil_to_tif(bil_file_path, set_format_path)

                # Delete current date's .bil and .hdr files (default unless keeping).
                if KEEP_FILES.upper() == "TRUE":
                    # Keep the intermediate files, used in troubleshooting.
                    pass
                else:
                    # Delete current date's .bil and .hdr files.
                    for file in snodas_util.list_dir(set_format_path, ['*.bil', '*.hdr', '*.Hdr']):
                        if current_date_str in str(file):
                            snodas_util.delete_snodas_files(file)

                # Create the extent shapefile if not already created.
                if not extent_shapefile.exists():
                    # Extent shapefile does not exist so attempt to create.
                    logger.info("The extent shapefile does not exist so attempt to create:")
                    logger.info("  {}".format(extent_shapefile))
                    if not BASIN_SHP_PATH:
                        # The basin boundaries shapefile does not exist:
                        # - this is a fatal error
                        logger.error("  The basin shapefile configuration property "
                                     "[BasinBoundaryShapefile] pathname is not defined.")
                        exit(1)
                    basin_shp_path = Path(BASIN_SHP_PATH)
                    if not basin_shp_path.exists():
                        # The source basin shapefile path does not exist:
                        # - this is fatal
                        logger.error("  The basin shapefile does not exist: {}")
                        logger.error("    {}".format(basin_shp_path))
                        logger.error("    Confirm that '[BasinBoundaryShapefile] pathname' is defined "
                                     "in the configuration file.")
                        exit(1)
                    else:
                        # Basin boundaries shapefile exists so use it to create the extent file.
                        snodas_util.create_extent(BASIN_SHP_PATH, static_path)

                # Copy the unclipped tif for the current date into CLIP_FOLDER, where it will be clipped:
                # - input is the TIF from above, something like:
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.tif
                # - output is, for example in '3_ClipToExtent':
                #     us_ssmv11034tS__T0001TTNATS2023042405HP001.tif
                # - use a loop until file names are simpler to deal with and may enable other data types
                for tif_file_path in snodas_util.list_dir(set_format_path, '*' + current_date_str + '*.tif'):
                    snodas_util.copy_snodas_tif_to_clip_folder(tif_file_path, clip_path)

                # Assign datum to current date's .tif file (defaulted to WGS84):
                # - input name is something like:
                #     us_ssmv11034tS__T0001TTNATS2003093005HP001.tif
                # - output is something like:
                #     20030930_WGS84.tif
                # - use the specific pattern because if rerunning the same day will have output that does not match
                #   the required input pattern
                # - use a loop until file names are simpler to deal with and may enable other data types
                for tif_file_path in snodas_util.list_dir(clip_path, '*' + current_date_str + '*HP001.tif'):
                    snodas_util.assign_snodas_datum(tif_file_path, clip_path)

                # Clip current date's .tif file to the extent of the basin shapefile.
                # - unclipped input is, for example:
                #     20030930_WGS84.tif
                # - clipped output is, for example:
                #     Clip_20030930.tif
                # - use the specific pattern because if rerunning the same day will have output that does not match
                #   the required input pattern
                # - use a loop to check for existence and because may enable other data types
                for tif_file_path in snodas_util.list_dir(clip_path, '*' + current_date_str + '*WGS84.tif'):
                    snodas_util.snodas_raster_clip(tif_file_path, extent_shapefile)

                # Project current date's .tif file into desired projection:
                # - default to NAD83 UTM Zone 13N for Colorado
                # - input is, for example:
                #     Clip_20030930.tif
                # - output is, for example:
                #     SNODAS_SWE_ClipAndProj_YYYYMMDD.tif
                # - use the specific pattern because if rerunning the same day will have output that does not match
                #   the required input pattern
                # - use a loop to check for existence and because may enable other data types
                for tif_file_path in snodas_util.list_dir(clip_path, 'Clip_*' + current_date_str + '*.tif'):
                    snodas_util.assign_snodas_projection(tif_file_path)

                # Create current date's snow cover binary raster:
                # - use a loop to check for existence and because may enable other data types
                for tif_file_path in snodas_util.list_dir(clip_path, 'SNODAS_SWE*' + current_date_str + '*.tif'):
                     snodas_util.snow_coverage(tif_file_path, snow_cover_path)

                # Create .csv files for ByBasin and ByDate:
                # - use a loop to check for existence and because may enable other data types
                # - use the specific pattern because if rerunning the same day will have output that does not match
                #   the required input pattern
                # - the files will only be created if they don't already exist (otherwise would lose data)
                basin_shp_path = Path(BASIN_SHP_PATH)
                for tif_file_path in snodas_util.list_dir(clip_path, 'SNODAS_SWE*' + current_date_str + '*.tif'):
                    snodas_util.create_empty_csv_files(tif_file_path, basin_shp_path, results_date_path,
                                                       results_basin_path)

                # Delete rows from basin CSV files if the date is being reprocessed:
                # - this ensures that duplicate rows for the current date are not output to results
                # - use the specific pattern because if rerunning the same day will have output that does not match
                #   the required input pattern
                # - use a loop to check for existence and because may enable other data types
                for tif_file_path in snodas_util.list_dir(clip_path, 'SNODAS_SWE*' + current_date_str + '*.tif'):
                    snodas_util.delete_by_basin_csv_rows_for_date(tif_file_path, basin_shp_path, results_basin_path)

                # Calculate zonal statistics and export results:
                # - use the specific pattern because if rerunning the same day will have output that does not match
                #   the required input pattern
                for tif_file_path in snodas_util.list_dir(clip_path, 'SNODAS_SWE*' + current_date_str + '*.tif'):
                    snodas_util.z_stat_and_export(tif_file_path, basin_shp_path, results_basin_path, results_date_path,
                                                  clip_path, snow_cover_path, current,
                                                  downloadMetadataList[0], OUTPUT_CRS)

                # If configured, zip the shapefile files (both today's data and latestDate file).
                if SHP_ZIP.upper() == 'TRUE':
                    for shp_file_path in snodas_util.list_dir(results_date_path, '*.shp'):
                        if current_date_str in str(shp_file_path):
                            snodas_util.zip_shapefile(shp_file_path, results_date_path, DEL_SHP_ORIG)
                        if 'LatestDate' in str(shp_file_path):
                            zip_full_path = results_date_path / 'SnowpackStatisticsByDate_LatestDate.zip'
                            if zip_full_path.exists():
                                zip_full_path.unlink()
                            snodas_util.zip_shapefile(shp_file_path, results_date_path, DEL_SHP_ORIG)

                # If configured, the time series will run for each processed date of data.
                if RUN_DAILY_TSTOOL.upper() == 'TRUE':
                    snodas_util.create_snodas_swe_graphs()

                # If it is the last date in the range, continue.
                if current == end_date:

                    # Remove any duplicates that occurred in the byBasin csv files (rare but could happen).
                    snodas_util.clean_duplicates_from_by_basin_csv(results_basin_path)

                    # If configured, the time series will run for the entire historical range.
                    if RUN_HIST_TSTOOL.upper() == 'TRUE':
                        snodas_util.create_snodas_swe_graphs()

                    # Push daily statistics to the web if configuration property is set to 'True'.
                    if UPLOAD_TO_S3.upper() == 'TRUE':
                        snodas_util.push_to_aws()
                    if UPLOAD_TO_GCP.upper() == 'TRUE':
                        snodas_util.push_to_gcp()
                    if UPLOAD_TO_S3.upper() != 'TRUE' and UPLOAD_TO_GCP.upper() != 'TRUE':
                        print('Neither AWS or GCP configuration properties are True. Skipping the push to the cloud.',
                              file=sys.stderr)
                        logger.info('Output files from SNODAS_Tools are not pushed to cloud storage '
                                    'because of settings in configuration file. ', file=sys.stderr)

            else:
                # If config file value SaveAllSNODASParameters is not a valid value ('True' or 'False'),
                # the remaining script will not run and the following error message will be printed to the console
                # and to the log file.
                logger.error('See configuration file. The value of the SaveAllSNODASParameters section is not '
                             'valid. Change to "True" or "False" and rerun the script.', exc_info=True)

        # Display elapsed time of current date's processing in log.
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info('{}: Completed.'.format(current_date_str))
        logger.info('Elapsed time (date: {}): {} seconds'.format(current_date_str, elapsed_time))

        # TODO: jpkeahey 2021-06-22 - This called the function to mv all files onto the Host OS's shared folder.
        # if DEV_ENVIRONMENT.upper() == 'TRUE':
        #     mv_to_shared_dir([download_path, set_format_path, clip_path, snow_cover_path,
        #                       results_basin_path, results_date_path])

    # Close logging including the elapsed time of the running script in seconds.
    elapsed = time.time() - start
    elapsed_hours = int(elapsed / 3600)
    elapsed_hours_remainder = elapsed % 3600
    elapsed_minutes = int(elapsed_hours_remainder / 60)
    elapsed_seconds = int(elapsed_hours_remainder % 60)
    print('{}.py: Completed. Dates Processed: From {} to {}.'.format(
        program_name, start_date, end_date), file=sys.stderr)
    print('Processing time: approximately {} hours, {} minutes and {} seconds\n'
          .format(elapsed_hours, elapsed_minutes, elapsed_seconds), file=sys.stderr)

    # If any dates were unsuccessfully downloaded, print those dates to the console and the log file.
    failed_dates_lst_updated = []
    failed_dates_lst_1Week = []
    for item in failed_dates_lst:
        if item != 'None':
            item_str = str(item)
            item_plus_seven = item + timedelta(days=7)
            item_plus_seven_str = str(item_plus_seven)
            failed_dates_lst_updated.append(item_str)
            failed_dates_lst_1Week.append(item_plus_seven_str)

    if not failed_dates_lst_updated:
        print('All dates successfully downloaded!', file=sys.stderr)
        logger.info('All dates successfully downloaded!')
    else:
        print('\nDates unsuccessfully downloaded: ', file=sys.stderr)
        logger.info('\nDates unsuccessfully downloaded: ')
        for item in failed_dates_lst_updated:
            print(item, file=sys.stderr)
            logger.info('{}'.format(item))
        print("\nDates that will be affected by assigning the 'SNODAS_SWE_Volume_1WeekChange_acft' attribute 'NULL' "
              "due to the unsuccessful downloads: ", file=sys.stderr)
        logger.info("\nDates that will be affected by assigning the 'SNODAS_SWE_Volume_1WeekChange_acft' attribute "
                    "'NULL' due to the unsuccessful downloads: ")
        for item in failed_dates_lst_1Week:
            print(item, file=sys.stderr)
            logger.info('{}'.format(item))

    logger.info('{}.py: Completed. Dates Processed: From {} to {}.'.format(
        program_name, start_date, end_date))
    logger.info('Processing time: approximately {} hours, {} minutes and {} seconds\n'
                .format(elapsed_hours, elapsed_minutes, elapsed_seconds))
