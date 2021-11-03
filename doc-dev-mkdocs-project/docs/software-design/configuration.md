### SNODAS_Tools/config/

The ```SNODAS-Tools-Config.ini``` is located in the ```SNODAS_Tools/config/``` folder and contains Python input variables and logging settings for the SNODAS Tools.

#### Design of the Configuration File 
 
The configuration file is divided into **sections**. The **sections** are the broad categories of SNODAS configurable variables
and are recognizable by the brackets - [] - that surround them. 

* ['BasinBoundaryShapefile'] is the section header for all configurable variables related to the 
Watershed Basin Shapefile Input.   

Under each section, there are corresponding **options** that relate to the **section**.  

* 'pathname' and 'basin_id_fieldname' are options under the ['BasinBoundaryShapefile'] section. 
* 'pathname' refers to the file location of the Watershed Basin Shapefile Input. 
* 'basin_id_fieldname' refers to the field name of the Watershed Basin Shapefile Input that
uniquely defines each basin.

#### The Sections and Options of the Configuration File 
		
To explain the components of the configuration file, each **section** is represented by a table below. 
The **options** of each **section** are represented by a row in the table. 

**Software Installation**  
Configuration File Section: [ProgramInstall]

| Configurable Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Description | Default |
| ---- | ---- | ---- |
| `qgis_pathname` | The full location to the QGIS installation on the local desktop. | C:/OSGeo4W/apps/qgis |
| `tstool_pathname` | The full location of the TsTool program (TsTool.exe) on the local desktop. | C:/CDSS/TSTool-12.00.00beta/bin/TSTool.exe |
| `tstool_create-snodas-graphs_pathname` | The full location of the create-snodas-swe-graphs.TSTool command file. | D:/SNODAS/bin/create-snodas-swe-graphs.TSTool |

**NSIDC FTP Site**  
Configuration File Section: [SNODAS_FTPSite] 

| Configurable Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Description | Default |
| ---- | ---- | ---- |
| `host` | The FTP site hosting the SNODAS data. | sidads.colorado.edu |
| `username` | Sidads.colorado.edu is a public site so the <br> username can remain 'anonymous'. | anonymous |
| `password` | Sidads.colorado.edu is a public site so the <br> password can remain 'None'. | None |
| `folder_path` | The pathname to the SNODAS data <br> (defaulted to 'masked' data). | /DATASETS/NOAA/G02158/masked/ |
| `null_value` | The no data value of the SNODAS data. This information can be found in this [PDF]( http://nsidc.org/pubs/documents/special/nsidc_special_report_11.pdf). | -9999 |

**The Watershed Basin Shapefile Input**  
Configuration File Section: [BasinBoundaryShapefile]

| Configurable Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Description | Default |
| ---- | ---- | ---- |
| `pathname` | Location and name of the Watershed Basin Shapefile Input. The shapefile should be stored in the [Static Data Folder](file-structure.md#snodasstaticdata). | N/A |
| `basin_id_fieldname` | The name of the field in the shapefile attribute table that uniquely identifies each basin. The values of this field will be exported to the output statistics csv files. | LOCAL_ID |

**Projections**   
Configuration File Section: [Projections]  

| Configurable Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Description | Default |
| ---- | ----| ---- |
| `datum_epsg` | The EPSG code of the datum used to define the national SNODAS daily grid. WGS84 (EPSG 4326) is recommended. | 4326 |
| `calcstats_proj_epsg` | The EPSG code of the projection used to calculate the zonal statistics, an equal-area projection is recommended. This should be the same projection as that of the Watershed Basin Shapefile Input. | 102003 |
| `calculate_cellsize_x` | The desired cell size (x axis) to resample the daily SNODAS grid before calculating the zonal statistics. Remember to apply units used in the calcstats_proj_epsg projection. | 463.1475 |
| `calculate_cellsize_y` | The desired cell size (y axis) to resample the daily SNODAS grid before calculating the zonal statistics. Remember to apply units used in the calcstats_proj_epsg projection. | 463.1475 |
| `output_proj_epsg` | The EPSG code of the desired projection for the output layers, the daily GeoJSON and the daily shapefile. | 26913 |


**Output Folders**  
Configuration File Section: [Folders] 

| Configurable Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Description | Default |
| ---- | ---- | ---- |
| `root_pathname` | Location and name of root folder. Contains the following 2 folders. | D:/SNODAS/ |
| `static_data_folder` | Name of folder containing the static data, including the Watershed Basin Shapefile Input. | staticData/ |
| `processed_data_folder` | Name of folder containing all of the processed data. Contains the following 5 folders. | processedData/ |
| `download_snodas_tar_folder` | Name of folder containing all daily SNODAS .tar files downloaded from FTP site. | 1_DownloadSNODAS |
| `untar_snodas_tif_folder` | Name of folder containing national daily SNODAS .tif files. | 2_SetFormat | 1_DownloadSNODAS |
| `clip_proj_snodas_tif_folder` | Name of folder containing clipped and projected daily SNODAS .tif files. | 3_ClipToExtent |
| `create_snowvover_tif_folder` | Name of folder containing clipped binary snow cover .tif files. | 4_CreateSnowCover |
| `calculate_stats_folder` | Name of folder containing the output products. Contains the following 2 folders. | 5_CalculateStatistics/ |
| `output_stats_by_date_folder` | Name of folder containing the output zonal snowpack statistics organized by date. Also contains the daily output GeoJSONs & shapefiles. | SnowpackStatisticsByDate |
| `output_stats_by_basin_folder` | Name of folder containing the output zonal snowpack statistics organized by basin. | SnowpackStatisticsByBasin |


**Output Layers**  
Configuration File Section: [OutputLayers]

| Configurable Parameter | Description | Default |
| ---- | ---- | ---- |
| `shp_zip` | Boolean logic to determine if the output shapefile files should be zipped. <br><br> `True`: Shapefile files are zipped. <br> `False`: Shapefile files are left independent. | `True` |
| `shp_delete_orginals` | Boolean logic to determine if unzipped shapefile files should be deleted. Only applied if shp_zip = True. <br><br> `True`: Independent shapefile files are deleted. <br> `False`: Independent shapefile files are saved along with the zipped file. | `True` |
| `geojson_precision` | The number of decimal places included in the GeoJSON output geometry. The more decimal places, the more accurate the geometry and the larger the file size. | 5 |  
| `tsgraph_weekly_update` | Boolean logic to determine whether or not to update the snowpack time series graphs daily or weekly. <br><br> True: Time series graphs are updated weekly, based on tsgraph_weekly_update_date setting. <br> False: Time series graphs are updated daily. | False |
| `tsgraph_weekly_update_date` | The day of the week that the snowpack time series graphs are set to update (Monday: 0, Tuesday: 1 ...). Only applied if tsgraph_weekly_update = True. <br><br> Note that the SNODAS Tools must be run on this set day in order for the graphs to update. The graphs will not update automatically if one of the SNODAS Tools' scripts is not run. | 0 | 
| `upload_to_s3` | Boolean showing whether to upload the SNODAS_Tools results to the S3 Amazon Web Service given the specifics of the batch file input in function 'push_to_AWS' in 'SNODAS_utilities.py'. | False |
| `gcp_upload` | Boolean showing whether to upload the SNODAS_Tools results to the State of Colorado maintained Google Cloud Platform bucket. | False |

**Daily SNODAS Parameters**  
Configuration File Section: [SNODASparameters] 

| Configurable Parameter | Description | Default |
|---- | ---- | ---- |
| `save_all_parameters` | The downloaded daily SNODAS .tar file contains 8 snowpack parameters. The SNODAS Tools only compute statistics from the SWE parameter. Boolean logic to determine whether or not to delete the other 7 national grids of SNODAS parameters. <br><br> `True`: The daily 7 national grids of SNODAS parameters (other than SWE) are saved in a folder called download_snodas_tar_folder/OtherParameters. <br> `False`: The daily 7 national grids of SNODAS parameters are deleted. | False |


**Optional Statistics**   
Configuration File Section: [OptionalZonalStatistics]

| Configurable Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Description | Default |
| ---- | ---- | ---- |
| `calculate_swe_minimum` | Boolean logic to enable calculation of the daily minimum SWE zonal statistic (mm and in). <br><br> `True`: Enable. <br> `False`: Disable. | False |
| `calculate_swe_maximum` | Boolean logic to enable calculation of the daily maximum SWE zonal statistic (mm and in). <br><br> `True`: Enable. <br> `False`: Disable. | False |
| `calculate_swe_standard_deviation` | Boolean logic to enable calculation of the SWE standard deviation zonal statistic (mm and in). <br><br> `True`: Enable. <br> `False`: Disable. | False |

**The Logging Files**  
The configuration of the [logging files](#processeddatasnodastoolslog) is slightly more complicated than the other **sections** of the configuration file. 
The configuration of the logging files is set up with multiple **sections**, following the design provided by 
[the Python Software Foundation - Logging HOWTO](https://docs.python.org/2/howto/logging.html#configuring-logging).

The following table differs than the previous tables in that there are multiple **sections** represented in the table 
(instead of just one). In the first column, the **section** AND the **option** are listed (instead of just the **option**). 
All of the **sections** and **options** in the following table are in reference to configuring the logging files. 

| **Section**<br>Option | Description | Default |
| ---- | ---- | ---- |
| **loggers**<br>keys | The available SNODASTools logs. This should not be changed unless a new log configuration is to be created. | root, log02 |
| **handlers**<br>keys | The available SNODASTools handlers. This should not be changed unless a new handler is to be created. | fileHandler, consoleHandler |
| **formatters**<br>keys | The available SNODASTools formatters. This should not be changed unless a new formatter is to be created. | simpleFormatter|
| **logger_root**<br>level | The log level of the 'root' logger. | WARNING |
| **logger_root**<br>handlers | The handler used for the 'root' logger. | consoleHandler |
| **logger_log02**<br>level | The log level of the 'log02' logger. | DEBUG |
| **logger_log02**<br>handlers | The handler used for the 'log02' logger. | fileHandler |
| **logger_log02**<br>qualname | The name used to call the log in the SNODASTools' applications. | log02 |
| **logger_log02**<br>propogate | Propogation setting. <br> 1 to indicate that messages must propagate to handlers higher up the logger hierarchy from this logger, or 0 to indicate that messages are not propagated to handlers up the hierarchy. | 0 |
| **handler_consoleHandler**<br>class | The class type of the consoleHandler. | StreamHandler |
| **handler_consoleHandler**<br>level | The log level of the consoleHandler. | NOTSET |
| **handler_consoleHandler**<br>formatter | The formatter of the consoleHandler. | simpleFormatter |
| **handler_consoleHandler**<br>args | The location of output log messages for the consoleHandler. | (sys.stdout,) |
| **handler_fileHandler**<br>class | The class type of the fileHandler. | handlers.TimedRotatingFileHandler |
| **handler_fileHandler**<br>level | The log level of the fileHandler. | NOTSET |
| **handler_fileHandler**<br>formatter | The formatter of the fileHandler. | simpleFormatter |
| **handler_fileHandler**<br>args | The options for the TimedRotatingFileHandler (filename, when to rotate, rotation interval, backupCount) | ('../processedData/SNODASTools.log', 'W0', 1, 5) |
| **formatter_simpleFormatter**<br>foramt | The format of log messages. | %(asctime)s %(message)s |
