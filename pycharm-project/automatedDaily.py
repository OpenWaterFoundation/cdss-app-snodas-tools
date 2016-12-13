# Name: automatedDailyP1.1.py
# Author: Emma Giles
# Organization: Open Water Foundation
# Date Created: 11/21/2016
# Last Updated: 11/22/2016
#
#
# Purpose: This script will output zonal statistics for today's SNODAS raster given the basin boundaries of the
#   Colorado Watershed Basins. The zonal statistics that are calculated are as follows: SWE mean, SWE minimum, SWE
#   maximum, SWE standard deviation, pixel count and percentage of snow coverage. The functions in this script are
#   housed within SNODAS_utilities.py. A more detailed description of each function is documented in the
#   SNODAS_utilities.py file. This script is intended to be run on a task scheduler program so that the data can be
#   processed every day without the manual help of a user.

# Import necessary modules.
import SNODAS_utilities
import ftplib, os, tarfile, gzip, gdal, csv, logging
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsZonalStatistics
from qgis.core import QgsRasterLayer, QgsApplication, QgsVectorLayer, QgsField, QgsExpression
from PyQt4.QtCore import QVariant
from datetime import datetime, timedelta
from time import strptime
from shutil import copy


# Define the full pathnames of the following variables.
# root: The root folder will be the folder that will house all outputs from this script. Within the root folder, ensure
# that the following 5 folders are created: download, setEnvironment, clip, results and logging. Within the results
# folder, ensure that the following 2 folders are created: byBasin and byDate. This script will not function properly
# if these folder settings are not addressed before the script is run.
# basin_extent_WGS84: This is the full pathname to the shapefile of the EXTENT of the Colorado Watershed Basins. This
# shapefile should be one rectangular feature representing the bounding box of the Colorado Watershed Basins shapefile.
# Ensure that this shapefile is projected into WGS84
# basin_shp_NAD83 = This is the full pathname to the shapefile holding the boundaries of the Colorado Watershed Basins.
# The zonal statistics will be calculated for each feature. Ensure that the shapefile is projected into NAD83 Zone 13N.
root = r'D:\SNODAS\Raster\automated_daily'
basin_extent_WGS84 = r"D:\SNODAS\Vector\basin_extent_WGS84.shp"
basin_shp_NAD83 = r"D:\SNODAS\Vector\orig_watersheds_nad83.shp"





if __name__ == "__main__":

    # Sets full pathnames of folders. The download folder will hold the originally-downloaded national SNODAS .tar
    # files. The setEnvironment folder will hold the national SNOADAS .tif files. The clip folder will hold the
    # reprojected (NAD83), clipped SNODAS .tif files. The results folder will hold two folders, byBasin and byDate. The
    # byBasin folder will hold the basin-specific zonal statistics results in .csv format. The byDate folder will hold
    # the date-specific zonal statistics results in .csv format. The logging folder will hold a .txt file containing
    # all logging notes created throughout the script.
    download_path = os.path.join(root, r'download')
    setEnvironment_path = os.path.join(root, r'setEnvironment')
    clip_path = os.path.join(root, r'clip')
    results_basin_path = os.path.join(root, r'results\byBasin')
    results_date_path = os.path.join(root, r'results\byDate')
    snowCover_path = os.path.join(root, r'snowCover')
    logging_output_path = os.path.join(root, r'logging\logging.txt')

    # Set up logging configuration
    logging.basicConfig(filename=logging_output_path, level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Started')

    # Initializes QGIS resources: more info at http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html.
    # This block of code allows for the script to utilize QGIS functionality.
    QgsApplication.setPrefixPath("C:/OSGeo4W/apps/qgis", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # Downloads today's SNODAS .tar file from the FTP site
    SNODAS_utilities.download_today_SNODAS(download_path)

    # Get today's date in string format
    today = datetime.now()
    today_date = SNODAS_utilities.get_date_string(today)


   # Untar's today's data
    for file in os.listdir(download_path):
        if today_date in str(file):
            SNODAS_utilities.untar_SNODAS_file(file, download_path, setEnvironment_path)
        else:
            pass


    # Delete today's irrelevant files
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.delete_irrelevant_SNODAS_files(file)
        else:
            pass


    # Extract today's .gz files
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.extract_SNODAS_gz_file(file)
        else:
            pass

    # Convert today's .dat files into .bil format
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.convert_SNODAS_dat_to_bil(file)
        else:
            pass

    # Create today's custom .Hdr file
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.create_SNODAS_hdr_file(file)
        else:
            pass

    # Delete any created .txt files
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.delete_any_SNODAS_txt_files(file)
        else:
            pass

    # Convert today's .bil files to .tif files
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.convert_SNODAS_bil_to_tif(file, setEnvironment_path)
        else:
            pass

    # Delete today's .bil file
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.delete_SNODAS_bil_file(file)
        else:
            pass

    # Copy and move today's .tif file into clip folder
    for file in os.listdir(setEnvironment_path):
        if today_date in str(file):
            SNODAS_utilities.copy_and_move_SNODAS_tif_file(file, clip_path)
        else:
            pass

    # Assign WGS84 projection to today's .tif file
    for file in os.listdir(clip_path):
        if today_date in str(file):
            SNODAS_utilities.assign_SNODAS_projection_WGS84(file, clip_path)
        else:
            pass


    # Clip today's .tif file to the extent of the Colorado Basin shapefile (WGS84)
    for file in os.listdir(clip_path):
        if today_date in str(file):
            SNODAS_utilities.SNODAS_raster_clip_WGS84(file, clip_path, basin_extent_WGS84)
        else:
            pass

    # Reproject today's .tif file into NAD83
    for file in os.listdir(clip_path):
        if today_date in str(file):
            SNODAS_utilities.SNODAS_raster_reproject_NAD83(file, clip_path)
        else:
            pass

    # Create today's snow cover binary raster
    for file in os.listdir(clip_path):
        if today_date in str(file):
            SNODAS_utilities.snowCoverage(file, clip_path, snowCover_path)
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

    # Close logging
    logging.info('Finished')



















