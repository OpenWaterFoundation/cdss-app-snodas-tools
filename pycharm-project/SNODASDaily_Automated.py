# Name: SNODASDaily_Automated.py
# Author: Emma Giles
# Organization: Open Water Foundation
#
# Purpose: This script outputs zonal statistics for the current date's downloaded SNODAS raster given the basin
#   boundaries of the input shapefile. The script was originally created to use Colorado Watershed Basins as the vector
#   input. The zonal statistics that are calculated are as follows: SWE mean, SWE minimum, SWE maximum, SWE standard
#   deviation, pixel count and percentage of snow coverage. The functions in this script are housed within
#   SNODAS_utilities.py. A more detailed description of each function is documented in the SNODAS_utilities.py file.
#   This script is intended to be run on a task scheduler program so that the data is automatically processed every day.
#   It can also be processed manually if desired.

# Import necessary modules.
import SNODAS_utilities, os, logging, configparser, time
from qgis.core import QgsApplication
from logging.config import fileConfig
from datetime import datetime

# The start time is used to calculate the elapsed time of the running script. The elapsed time will be displayed at the
# end of the log file.
start = time.time()

# Read the config file to assign variables. Reference the following for code details:
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
    logger = logging.getLogger('log02')
    logger.info('SNODASDailyDownload.py: Started \n')


    # Initialize QGIS resources to utilize QGIS functionality.
    # More information at: http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html.
    QgsApplication.setPrefixPath(QGIS_installation, True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # Get today's date in string format
    today = datetime.now()
    today_date = SNODAS_utilities.format_date_YYYYMMDD(today)

    # Download today's SNODAS .tar file from SNODAS FTP site at ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/masked/
    optstats = SNODAS_utilities.download_SNODAS(download_path, today)

    # Check to see if configuration values for optional statistics 'calculate_SWE_minimum, calculate_SWE_maximum,
    # calculate_SWE_stdDev' (defined in utility function) are valid, If valid, script continues to run. If invalid,
    # error message is printed to consol and log file and script is terminated
    tempList = []
    for stat in optstats:
        if stat.upper() == 'TRUE' or stat.upper() == 'FALSE':
            tempList.append(1)
        else:
            tempList.append(0)

    if 0 in tempList:
        logger.error('"ERROR: See configuration file. One or more values of the ''DesiredZonalStatistics'' section is '
                     'not valid. Please change values to either ''True'' or ''False'' and rerun the script."')
        logging.error('"ERROR: See configuration file. One or more values of the ''DesiredZonalStatistics'' section is '
                     'not valid. Please change values to either ''True'' or ''False'' and rerun the script."')

    else:
        # Untar today's data
        for file in os.listdir(download_path):
            if today_date in str(file):
                SNODAS_utilities.untar_SNODAS_file(file, download_path, setEnvironment_path)

        # Check to see if configuration file 'Save_allSNODASparameters' value is valid. If valid, script continues to run.
        # If invalid, error message is printed to console and log file and the script is terminated.
        if Save_allSNODASparameters.upper() == 'FALSE' or Save_allSNODASparameters.upper() == 'TRUE':

            # Delete today's irrelevant files (parameters other than SWE).
            if Save_allSNODASparameters.upper() == 'FALSE':
                for file in os.listdir(setEnvironment_path):
                    if today_date in str(file):
                        SNODAS_utilities.delete_irrelevant_SNODAS_files(file)

            # Move irrelevant files (parameters other than SWE) to 'OtherSNODASParamaters'.
            else:
                parameter_path = os.path.join(setEnvironment_path, r'OtherParameters')
                if os.path.exists(parameter_path) == False:
                    os.makedirs(parameter_path)
                for file in os.listdir(setEnvironment_path):
                    if today_date in str(file):
                        SNODAS_utilities.move_irrelevant_SNODAS_files(file, parameter_path)

            # Extract today's .gz files. Each SNODAS parameter files are zipped within a .gz file.
            for file in os.listdir(setEnvironment_path):
                if today_date in str(file):
                    SNODAS_utilities.extract_SNODAS_gz_file(file)

            # Convert today's SNODAS SWE .dat file into .bil format.
            for file in os.listdir(setEnvironment_path):
                if today_date in str(file):
                    SNODAS_utilities.convert_SNODAS_dat_to_bil(file)

            # Create today's custom .Hdr file. In order to convert today's SNODAS SWE .bil file into a usable .tif
            # file, a custom .Hdr must be created. Refer to the function in the SNODAS_utilities.py for more
            # information on the contents of the custom .HDR file.
            for file in os.listdir(setEnvironment_path):
                if today_date in str(file):
                    SNODAS_utilities.create_SNODAS_hdr_file(file)

            # Convert today's .bil files to .tif files
            for file in os.listdir(setEnvironment_path):
                if today_date in str(file):
                    SNODAS_utilities.convert_SNODAS_bil_to_tif(file, setEnvironment_path)

            # Delete today's .bil file
            for file in os.listdir(setEnvironment_path):
                if today_date in str(file):
                    SNODAS_utilities.delete_SNODAS_bil_file(file)

            # Copy and move today's .tif file into name_of_clip_folder
            for file in os.listdir(setEnvironment_path):
                if today_date in str(file):
                    SNODAS_utilities.copy_and_move_SNODAS_tif_file(file, clip_path)

            # Assign datum to today's .tif file (defaulted to WGS84)
            for file in os.listdir(clip_path):
                if today_date in str(file):
                    SNODAS_utilities.assign_SNODAS_datum(file, clip_path)

            # Clip today's .tif file to the extent of the basin shapefile
            for file in os.listdir(clip_path):
                if today_date in str(file):
                    SNODAS_utilities.SNODAS_raster_clip(file, clip_path, basin_extent)

            # Project today's .tif file into desired projection (defaulted to NAD83 UTM Zone 13N)
            for file in os.listdir(clip_path):
                if today_date in str(file):
                    SNODAS_utilities.assign_SNODAS_projection(file, clip_path)

            # Create today's snow cover binary raster
            for file in os.listdir(clip_path):
                if today_date in str(file):
                    SNODAS_utilities.snowCoverage(file, clip_path, snowCover_path)

            # Create .csv files of byBasin and byDate outputs
            for file in os.listdir(clip_path):
                if today_date in str(file):
                    SNODAS_utilities.create_csv_files(file, basin_shp, results_date_path,results_basin_path)

            # Delete rows from basin CSV files if the date is being reprocessed
            for file in os.listdir(clip_path):
                if today_date in str(file):
                    SNODAS_utilities.delete_ByBasinCSV_repeated_rows(file, basin_shp, results_basin_path)

            # Calculate zonal statistics and export results
            for file in os.listdir(clip_path):
                if today_date in str(file):
                    SNODAS_utilities.zStat_and_export(file, basin_shp, results_basin_path, results_date_path,
                                                      clip_path, snowCover_path)

        # If configuration file value SaveAllSNODASparameters is not a valid value (either 'True' or 'False') the remaining
        # script will not run and the following error message will be printed to the console and to the logging file.
        else:
            logger.error("ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not valid."
                      "Please type in 'True' or 'False' and rerun the script.")
            logging.error("ERROR: See configuration file. The value of the SaveAllSNODASparameters section is not valid."
                      "Please type in 'True' or 'False' and rerun the script.")

    # Close logging including the elapsed time of the running script in seconds.
    end = time.time()
    elapsed = end - start
    logger.info('\n')
    logger.info('\n SNODASDailyDownload.py: Completed.')
    logger.info('Elapsed time: %d seconds' % elapsed)
    print ('Elapsed time: %d seconds' % elapsed)