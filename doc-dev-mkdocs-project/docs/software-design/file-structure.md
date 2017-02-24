# Table of Contents

 **TODO egiles 2017-01-19 Edit the file structure pathnames to reflect a Linux system**  

The following topics are discussed in this section:<br>

* [Overview](#overview)
* [OSGeo4W64\\](#osgeo4w6492)
* [CDSS\\TsTool-Version\\](#cdss92tstool-version92)
* [CDSS\\SNODASTools\\](#cdss92snodastools92)
	+ [SNODASTools\\bin\\](#snodastools92bin92)
		- [Scripts](#bin92snodastoolslog)
		- [Log files](#bin92snodastoolslog)
	+ [SNODASTools\\staticData\\](#snodastools92staticdata92)
	+ [SNODASTools\\processedData\\](#snodastools92processeddata92)
		- [processedData\\1_DownloadSNODAS\\](#processeddata921_downloadsnodas92)
		- [processedData\\2_SetFormat\\](#processeddata922_setformat92)
		- [processedData\\3_CliptoExtent\\](#processeddata923_cliptoextent92)
		- [processedData\\4_CreateSnowCover\\](#processeddata924_createsnowcover92)
		- [processedData\\5_CalculateStatistics\\](#processeddata925_calculatestatistics92)
			- [5_CalculateStatistics\\StatisticsbyBasin\\](#processeddata925_calculatestatistics92statisticsbybasin92)
			- [5_CalculateStatistics\\StatisticsbyDate\\](#processeddata925_calculatestatistics92statisticsbydate92)
		
	+ [SNODASTools\\SNODASconfig\.ini](#snodastools92snodasconfigini)
	

## Overview

The SNODAS Tools process original SNODAS data files, extracted from a tar file, into zonal statistics for 
watershed basins. [Zonal statistics](https://docs.qgis.org/2.2/en/docs/user_manual/plugins/plugins_zonal_statistics.html)
are statistics calculated by zone where the zones are defined by an input 
zone dataset and the values are defined by a raster grid. For the SNODAS Tools, the input zone dataset is the [watershed 
basin boundary shapefile](#snodastools92staticdata92) and the raster grid is the
[clipped and projected SNODAS daily SWE grid](#processeddata923_cliptoextent92). 
Originally, these tools were developed for processing snowpack statistics for the state of Colorado. 
Therefore, the examples throughout this documentation reference the Colorado study area. 

After the data is processed, final snowpack statistics can easily be viewed in a choropleth map or exported 
in tabular form. Below is an image of the results from the SNODAS Tools displayed as a choropleth map. Right-click on the image 
and click *Open image in new tab* to see a larger view.

![CDSS SNODAS Tools Chloropleth Map](file-structure-images/SNODAS-CDSS-Tools-Map.png)

As explained in the [Processing Workflow](overview.md#processing-workflow) section, the tool iterates through various data-manipulation 
processes (ex: downloading the data, clipping the national grid to the extent of the basins, 
calculating the zonal statistics). Each data-manipulation process can generate one or more output files. The 
majority of intermediate data files are currently saved to allow for process verification, troubleshooting, 
and avoiding re-downloads should the full analysis period need to be rerun due to changes in the software 
(each daily download of the SNODAS national files takes approximately 7 seconds). 

The following illustrates the overall folder structure for the SNODAS Tools, including software and data
files, for Windows. The software is configured using the system\SNODASconfig.ini file, which specifies 
locations of folders and files on the operational system.     
  
*```Nested folders``` are represented by: '---'. *  
*```Files``` are represented by: '--->'.*

 ** File Structure of SNODAS Tools**  
 
  **TODO egiles 2017-01-19 Add system to the folder structure**

```C:\OSGeo4W64\```  
```C:\CDSS\TsTool-Version```  
```C:\CDSS\SNODASTools\``` 
 
--- ```bin\```  
- - - - - > ```SNODASDaily_Automated.py```  
- - - - - > ```SNODASDaily_Interactive.py```  
- - - - - > ```SNODAS_utilities.py```  
- - - - - > ```SNODAS_publishResults.py```   
- - - - - > ```SNODASDaily_Automated_forTaskScheduler.bat```   
- - - - - > ```SNODASTools.log```  

--- ```staticData\```    
- - - - - > ```watershedBasinBoundary.shp```   
- - - - - > ```watershedBasinBoundaryExtent.shp```   
- - - - - > ```watershedBasinBoundary.geojson```  
- - - - - > ```stateBoundary.geojson```
 
--- ```processedData\```   
- - - - -  ```1_DownloadSNODAS\```   
- - - - - - - - > ```SNODAS_YYYYMMDD.tar```  
- - - - -  ```2_SetFormat\```   
- - - - - - - - > ```us_ssmv11034tS__T0001TTNATSYYYYMMDD05HP001.tif```  
- - - - -  ```3_ClipToExtent\```   
- - - - - - - - > ```SNODAS_SWE_ClipAndReprojYYYYMMDD.tif```   
- - - - -  ```4_CreateSnowCover\```    
- - - - - - - - > ```SNODAS_SnowCover_ClipAndReprojYYYYMMDD.tif```   
- - - - -  ```5_CalculateStatistics\```   
- - - - - - - - - ```StatisticsbyBasin\```  
- - - - - - - - - - - > ```SnowpackStatisticsByBasin_LOCALID```  
- - - - - - - - - ```StatisticsbyDate\```  
- - - - - - - - - - - > ```SnowpackStatisticsByDate_YYYYMMDD```  
- - - - - - - - - - - > ```ListOfDates.txt``` 


--> ```SNODASconfig.ini```


## OSGeo4W64\\

**TODO egiles 2017-01-23 need to add content to OSGeo4W64\\ **  

## CDSS\\TsTool-Version\\

**TODO egiles 2017-01-23 need to add content to CDSS\\TsTool-Version\\ **  

## CDSS\\SNODASTools\\
All SNDOAS scripts, input data and output data are stored within the ```CDSS\SNODASTools\``` folder. 

 * The SNODAS Python and batch scripts are contained within the [SNODASTools\\bin\\](#snodastools92bin92) folder. 

 * The SNODAS input data files are contained within the [SNODASTools\\staticData\\](#snodastools92staticdata92) folder.

 * The SNODAS output data files are contained within the [SNODASTools\\processedData\\](#snodastools92processeddata92) folder.

### SNODASTools\\bin\\

The ```C:\CDSS\SNODASTools\bin\``` folder holds all of the SNODAS Tools' scripts and all of the corresponding log files.

#### SNODAS Tools' Scripts

The ```C:\CDSS\SNODASTools\bin\``` folder holds all SNODAS Tools' scripts. In total there are five 
scripts:   

	1. SNODASDaily_Automated.py 
	2. SNODASDaily_Interactive.py 
	3. SNODAS_utilities.py  
	4. SNODAS_publishResults.py
	5. SNODASDaily_Automated_forTaskScheduler.bat

**1. SNODASDaily_Automated.py**	

The ```SNODASDaily_Automated.py``` Python script downloads _the current date's_ SNODAS data from the SNODAS FTP site 
and exports daily snowpack zonal statistics.   

This script only processes the current date's SNODAS data. 
For information on the data processing steps of ```SNODASDaily_Automated.py```, refer to the 
[Processing Workflow](overview.md#processing-workflow) section. For information on the SNODAS FTP site, refer to the
[SNODAS Data](http://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-user/data/overview/) of the user guide. For information on
the output snowpack products, refer to the [SNODAS Tools Products](http://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-user/products/overview/)
section of the user guide.

The ```SNODASDaily_Automated.py``` script is designed to be automatically run using a task scheduler program. Once the task is set 
up, refer to [Task Scheduler](../deployed-env/task-scheduler) section for more information, the script downloads the daily SNODAS data on a daily timer and exports 
the daily zonal statistics to the [processedData\ folder](#folder-snodastools_processeddata). 
 
 **2. SNODASDaily_Interactive.py**	

The ```SNODASDaily_Interactive.py``` script downloads _historical_ SNODAS data from the SNODAS FTP site 
and exports daily snowpack zonal statistics.   

The ```SNODASDaily_Interactive.py``` script is designed to be interactive. Users specify historical dates of 
interest and the script exports the zonal statistics corresponding to those dates. The exported statistics of the 
```SNODASDaily_Interactive.py``` are saved in the [processedData\ folder](#folder-snodastools_processeddata) alongside
the exported statistics of the ```SNODAS_DailyAutomated.py``` script.


For information on the data processing steps of ```SNODASDaily_Interactive.py```, refer to the 
[Processing Workflow](overview.md#processing-workflow) section. For information on the SNODAS FTP site, refer to the
[SNODAS Data](http://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-user/data/overview/) section of the user guide. For information
on the output snowpack products, refer to the [SNODAS Tools Products](http://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-user/products/overview/)
section of the user guide.



The ```SNODASDaily_Interactive.py``` script is to be utilized in the following scenarios:


1. The historical SNODAS repository has not yet been processed. 
	* The temporal coverage of the SNODAS data is Septemeber 28th, 2003 to the current date. The ```SNODASDaily_Automated.py``` 
	script automatically creates an ongoing export of SNODAS zonal statistics, once the 
	```SNODASDaily_Automated_forTaskScheduler.bat``` has been set up with  a task scheduler program. The SNODAS historical repository,
	however, must be created with the ```SNODASDaily_Interactive.py``` script.
	
	
2. The ```SNODASDaily_Automated_forTaskScheduler.bat``` failed to run. 
	* The ```SNODASDaily_Automated_forTaskScheduler.bat``` is designed to automatically run ```SNODASDaily_Automated.py``` 
	everyday. There are instances, however, when the task could fail to run for a single or range of days. This could occur, for 
	example, if the task properties are set to run only when the user is signed in and the user was signed off for one or a range 
	of days. The missed days must then be manually processed with the ```SNODASDaily_Interactive.py``` script.
	
	
3. The SNODAS grid displayed incorrect information. 
	* The SNODAS products for a specific day could require an overwrite if the [National Snow & Ice Data Center](https://nsidc.org/) 
	uploads incorrect SNODAS data, only to reload the correct dataset later. The reprocessing of SNODAS data for that date would be 
	accomplished with the ```SNODASDaily_Interactive.py``` script.

 **3. SNODAS_utilities.py**	

The ```SNODAS_utilities.py``` script contains all of the functions utilized in the ```SNODASDaily_Automated.py```
and the ```SNODASDaily_Interactive.py``` scripts. For descriptions of the individual ```SNODAS_utilities.py``` 
functions refer to the [Tool Utilities and Functions](overview.md#tool-utilities-and-functions) section.

**4. SNODAS_publishResults.py**    

**TODO egiles 2017-01-19 develop publishResults.py script and explain**  

**5. SNODASDaily_Automated_forTaskScheduler.bat**  

The ```SNODASDaily_Automated_forTaskScheduler.bat``` is a batch file to be called by a task scheduler program. It automatically 
runs the ```SNODASDaily_Automated.py``` script everyday with the correct enviroment settings. Refer to the 
[Task Scheduler](../deployed-env/task-scheduler) section for a tutorial on how to 
initially set up the ```SNODASDaily_Automated_forTaskScheduler.bat``` within a task scheduler program.   
** ToDO egiles 2/14/2016 explain the components of the TaskScheduler.bat file**  

#### bin\\SNODASTools.log

The SNODAS Tools are set to export logging messages to aid in troubleshooting. The logging setting for the SNODAS Tools are configured with the
[configuration file format](https://docs.python.org/2.7/library/logging.config.html#configuration-file-format). 

**Levels of Logging Messages**  
The SNODAS Tools are set to export logging messages to both the console and the SNODASTools.log file. Warning and error messages export to both the console and the
SNODASTools.log file. Info messages are defaulted to export *solely* to the SNODASTools.log file. The logging level of messages exported to the 
SNODASTools.log file can be changed from the defaulted ```DEBUG``` level in the [configuration file](#snodastools92snodasconfigini) 
under **section** ```logger_log02``` **option** ```level```.

**Formatting of Logging Messages**  
All logging messages are formatted to the default simpleFormatter. The simpleFormatter outputs the date and local time of the created log record
in the following format" ```YYYY-MM-DD  HH:MM:SS,MSS``` where: 

 |Format|Description|
 |----|------|
 |YYYY|The year when the logging message is created with century as a decimal number.|
 |MM|The month, as a  zero-padded decimal number, when the logging message is created.|
 |DD|The day, as a  zero-padded decimal number, when the logging message is created.|
 |HH|The hour, as a  zero-padded decimal number, when the logging message is created.**Todo egiles 2/14/17 Check to see if (24-hour clock or 12-hour clock)**|
 |MM|The minute, as a  zero-padded decimal number, when the logging message is created.|
 |SS|The second, as a  zero-padded decimal number, when the logging message is created.|
 |MSS|The millisecond,  as a three-digit zero-padded decimal number, when the logging message is created.|
 
 The logging message follows the format: ```SSSS: EEEE: MMMM``` where:
 
 |Format|Description|Example|
 |----|------|---|
 |SSSS|The name of the .py script or function for which the log message is regarding.|_SNODASDaily_Interactive.py:_|
 |EEEE|The logging level of the log message. Only present if the logging level is a warning or an error.|_WARNING:_|
 |MMMM|The logging message.| _SNODAS_20110217.tar has been untarred._|
 
 The format of the logging messages can be changed from the defaulted ```%(asctime)s %(message)s``` in the [configuration file](#snodastools92snodasconfigini)
 under **section** ```formatter_simpleFormatter``` **option** ```format```.


**Timed Rotating File Handler**  
If the SNODASTools.log logging level is set to default ```DEBUG```, all logging messages will be written to the SNODASTools.log file. For each processed day of SNODAS
data, the size of the SNODASTools.log file will increase by approximately 12KB. The SNODAS Tools are designed to run everyday. This high frequency of processing would
quickly cause the SNODASTools.log file to become incredibly large. To address this issue, the SNODASTools.log file is configured to run on a
[Timed Rotating File Handler](https://docs.python.org/2/library/logging.handlers.html#timedrotatingfilehandler).

The timed rotating file handler creates and updates multiple versions of the SNODASTools.log file based upon a configured temporal schedule. After an allotted amount of time
(defaulted to 5 weeks), the oldest version of the SNODASTools.log is deleted and only the most recent log files are available. By default, a new SNODASTools.log 
file is created every Monday, local time. The SNODASTools.log file from the previous week is assigned a suffix of ```.YYYY-MM-DD``` and saved in the ```SNODASTools\bin\``` folder. The 
```.YYYY-MM-DD``` refers to the day that the log file was originally created. Given the default, ```.YYYY-MM-DD``` will always be a Monday. 

 - **Note:**   
 The timed rotating file handler defaults to adding the dated suffix as an extension. For example ```SNODASTools.log``` will become ```SNODASTools.log.YYYY-MM-DD```.
 This locks up the previous log files to be opened and viewed in *Notepad*. However, the previous log files can still be opened and viewed using [*Notepad++*](https://notepad-plus-plus.org/).
 
The default setting saves 5 versions of the 
SNODASTools.log file. This means that any processing from the past 5 weeks can be accessed. SNODASTools.log files older than 5 weeks are deleted. 
The previous 5 versions of the SNODASTools.log are saved under the ```SNODASTools\bin\``` folder. 

As previously mentioned, each processed SNODAS date increases the individual SNODASTools.log file by approximately 12KB. Given the default setting of the timed rotating 
file handler, each log file will be approximately 84KB (daily size of 12KB multiplied by the 7 days of the week). The total size of file space used for SNODAS Tools' 
logging will be approximately 420KB (weekly log file size of 84KB multipled by 5 weeks of backup files).

 - **Note**:  
 The size increase of the SNODASTools.log file will be larger than 12KB for each processed date of SNODAS data if the processed date of SNODAS data is being rerun and 
 the original files are being overwritten. 

The settings of the timed rotating file handler can be changed in the [configuration file](#snodastools92snodasconfigini)
 under **section** ```handler_fileHandler``` **option** ```args```. There are 4 arguments (filename, type of time interval,
 interval, and backupConut) that can be altered within the option ```args```. These 4 editable features are explained below.
 
|Argument|Description|Defaulted to:|
|-----|----|------|
|Filename|The full pathname to the location of the log file.|..SNODASTools/bin/SNODASTools.log **TODO egiles 2/14/17 check to make sure this is accurate**|
|Type of Time Interval|Time interval type when a new log file is to be created. <br> <br> Options: seconds, days, weekdays, etc.|<center>'W0' Monday|
|Interval|Time interval. <br> <br> Example (if type of time interval = 'days'): <br> 1 - every day <br> 2 - every other day <br> 5 - every five days, etc.|<center>1|
|backupCount|The number of previous SNODASTools.log files to be saved.|<center>5|


 Refer to the 
 [Python tutorial documentation on the TimedRotatingFileHandler class](https://docs.python.org/2/library/logging.handlers.html#timedrotatingfilehandler)  
 for further information regarding the argument options.

 **NOTE TO SELF egiles 2/14/17 this is where i left off on post-meeting edits for the file-structure.md**
 
 
### SNODASTools\\staticData\\

Two types of static data, script input data and visualization data, are stored within this folder. 

** Script Input Data**

The SNODAS Tools require the input of two static data files. These two data files should be saved 
within this folder prior to running the scripts. 

1. Watershed Basin Shapefile Input (```watershedBasinBoundary.shp```). This shapefile is a collection of basin features for the 
study area of interest. Originally the SNODAS Tools were developed to perform snowpack analysis for the state of Colorado. Below
is an image of the watershed basin shapefile (displayed in green) used for the watershed basin input. The black, boxed 
outline is the Colorado state boundary. 

	- Zonal statistics are statistics calculated by zone where the zones are defined by an input zone dataset and the values 
	are defined by a raster grid. This shapefile is the input zone dataset. 

	- The clipped SNODAS daily rasters are reprojected into the projection of the Watershed Basin Shapefile Input before the zonal 
	statistics are calculated. 
	
	- The projection of the Watershed Basin Shapefile Input is defaulted to NAD83 Zone13N (EPSG code: 26913). If the Watershed Basin
	Shapefile Input has a projection other than NAD83 Zone13N, the default EPSG code in the [configuration file](#snodastools92snodasconfigini)
	under section ```VectorInputShapefile``` option ```projection_epsg``` must be altered.



![colorado Basins Shapefile](file-structure-images/CO_basin_boundaries.png)

2. Watershed Basin Extent Shapefile Input (```watershedBasinBoundaryExtent.shp```). This single-feature shapefile extends 
slightly beyond the extent of the watershed basin shapefile to ensure all areas of the study area are accurately represented 
by the SNODAS data. Below is an image of the watershed basin extent shapefile (displayed in green) used for the Colorado watershed
 basin extent input. The Colorado watershed basin shapefile is overlaid with a transparent fill. 

	- This shapefile decreases the processing time of the scripts by clipping the national SNODAS grid to the manageable size of the 
	study area. The watershed basin extent shapefile should have the same projection as the natial SNODAS grid in order to create a clean 
	clip of the data.   
	

	- The downloaded SNODAS raster does not have a projection however the ["SNODAS fields are grids of point estimates of snow 
	cover in latitude/longitude coordinates with the horizontal datum WGS84."](http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/)  
	
		
	- The SNODAS Tools assign the SNODAS grids the same projection as the Watershed Basin Extent Shapefile Input (defined in the configuration file).
	The projection of the Watershed Basin Extent Shapefile Input is defaulted to WGS84 (EPSG code: 4326) - this is recommended given the previous bullet point. 
	However, if the Watershed Basin Extent Shapefile Input has a projection other than WGS84, the default EPSG code 
	in the [configuration file](#snodastools92snodasconfigini) under section ```VectorInputExtent``` option ```projection_epsg``` must be altered.

![colorado Basins Extent](file-structure-images/Co_basin_extent.png)
 
** Visualization Data **

As previously mentioned, the output products can be displayed in tabular form or in a choropleth map. The static visualization 
data is used in the choropleth map. The visualization data are .GeoJSON files. 
A [GeoJSON file](http://learn.openwaterfoundation.org/owf-learn-geojson/index.html) is " an open standard format designed for 
representing simple geographical features, along with their non-spatial attributes, based on JavaScript Object Notation." 
- [Wikipedia:GeoJSON](https://en.wikipedia.org/wiki/GeoJSON).


1. Watershed Basin Boundary (```watershedBasinBoundary.geojson```). The watershed basin boundary GeoJSON file is the watershed
basin shapefile input converted into a GeoJSON file. This file displays the individual basin boundaries for which the zonal 
statistics are calculated. In a choropleth map, each basin of the watershed basin boundary GeoJSON file is filled with a 
color representing a daily snowpack statistic. 

2. State Boundary (```stateBoundary.geojson```). The state boundary GeoJSON file gives viewers of the choropleth map a sense of 
location. Note that this file is defined as state boundary only because the SNODAS Tools were originally developed for the state
of Colorado. If the study area is other than state-level, it might be more appropriate to adjust this layer to represent a location 
of corresponding scale (ex: basin extent, study area, etc.).

### SNODASTools\\processedData\\

All output products of ```SNODASDaily_Automated.py``` and ```SNODASDaily_Interactive.py``` are saved within the processedData\ folder. 
For each processed day of data, 6 output products are created. To see a larger view of the images below, right-click on the image and 
click *Open image in new tab*.

1. The originally downloaded national SNODAS .tar file  
	- ```SNODAS_YYYYMMDD.tar``` 
	![download](file-structure-images/download.PNG) 	
2. The reformatted national SNODAS SWE data in .tif format  
	 - ```us_ssmv11034tS__T0001TTNATSYYYYMMDD05HP001.tif```
	 ![SetFormat](file-structure-images/setformat.PNG)
3. The clipped and reprojected SNODAS SWE .tif file  
	- ```SNODAS_SWE_ClipAndReprojYYYYMMDD.tif```  
	![Clip](file-structure-images/clip.PNG)
4. The clipped and reprojected snow cover binary .tif file  
	- ```SNODAS_SnowCover_ClipAndReprojYYYYMMDD.tif```  
	![Snow Cover](file-structure-images/snowcover.PNG)
5. The snowpack statistics in a .csv file organized by basin ID  
	 - ```SnowpackStatisticsByBasin_LOCALID```  
	 ![ByBasin](file-structure-images/statistics.PNG)
6. The snowpack statistics in a .csv file organized by date  
	 - ```SnowpackStatisticsByDate_YYYYMMDD``` 
	 ![ByDate](file-structure-images/statistics.PNG)


The 6 output products are saved within subfolders of the processedData folder. Each subfolder is explained in further detail below. 
The name of each subfolder is described by the default name. However, the following folder names can be edited in the 
[configuration file](#snodastools92snodasconfigini).  

#### processedData\\1_DownloadSNODAS\\

The SNODAS Tools access the [SNODAS FTP site](ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/masked/) and download the daily 
SNODAS .tar file. If the ```SNODASDaily_Automated.py``` script is utilized, the daily SNODAS .tar file is the current date. If the 
```SNODASDaily_Interactive.py``` script is utilized, the daily SNODAS tar file is the date of interest defined by user input. 

The file is downloaded to the 1_DownloadSNODAS folder and is named ```SNODAS_YYYYMMDD.tar``` where ```YYYYMMDD``` represents the date of data. 
Note that the date does not represent the download date but rather the date when the SNODAS data is collected. 

	Example: 
	Downloaded SNODAS file for January 9th, 2013 -> SNODAS_20130109.tar

Refer to the [Processing Workflow](overview/#download-snodas-data) section for a general description of the SNODAS Tools' downloading step. 
Refer to [Tool Utilities and Functions](overview.md#1-download-snodas-data) for detailed information on the Python functions 
called to download the SNODAS data.

#### processedData\\2_SetFormat\\

The SNODAS Tools manipulate the ```SNODASYYYYMMDD.tar``` file to produce a SNODAS Snow Water Equivalent (SWE) national grid in .tif format, 
shown below.

![nationaltif](file-structure-images/nationalTIF.png)
*SNODAS Snow Water Equivalent Masked Grid for January 16th, 2017*

Refer to the [Processing Workflow](overview/#convert-snodas-data-formats) section for a general description of the SNODAS Tools' set format step. 
Refer to [Tool Utilities and Functions](overview.md#2-convert-data-formats) for detailed information on the Python functions 
called to set the format of the SNODAS data.

The manipulated SNODAS SWE .tif file is saved to the 2_SetFormat folder and is named ```us_ssmv11034tS__T0001TTNATSYYYYMMDD05HP001.tif```
where ```YYYYMMDD``` represents the date of data. Note that the date does not represent the download date but rather the date when the 
SNODAS data is collected. 

	Example: 
	SNODAS SWE .tif file for January 9th, 2013 -> us_ssmv11034tS__T0001TTNATS2013010905HP001.tif

The long and cryptic name of this file can be explained with the [NSIDC SNODAS user guide](http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/index.html).   
The naming convention variables are described below:

**us: region of the file**  
'us': United States  
  
**ssm: model used to generate the estimates**  
'ssm': simple snow model  
   
**v1: signifies if the file contains snow model driving data or model output**  
'v1': operational snow model output  

**1034: product code representing the snow parameter represented by the data**  
'1034': snow water equivalent  
 
**tS\__: a vertical integration code that denotes what type of snow pack data are being collected **  
'tS__': integral through all the layers of the snow pack  

**T0001: time integration code**  
'T0001': a one-hour snapshot  
  
**TTNA: detail of snow modeling operations**  
'TTNA': will always be TTNA  
  
**TS: time step code**  
TS is followed by the year, month, day, and hour of the start of the last time step of the 
integration period for which the data applies. For example, the time integration code, 
T0024, and time step code, TS2003102305, are for the time interval 2003-10-22 06 to 
2003-10-23 05.    

**YYYY: 4-digit year**  
'YYYY': dependent on date of data   
  
**MM: 2-digit month**  
'MM': dependent on date of data    

**DD: 2-digit day of month**   
'DD': dependent on date of data  
 
**05: 2-digit hour of day**  
'05': 5th hour of the day  
  
**H: time interval**  
'H': hourly  
 
**P001: offset code referring to where the data applies during a snow model time step in the snow 
model's differencing scheme**  
'P001': field represents a total flux for the entire time step such as precipitation or that a field
represents data at the end of a time step  

-----------------------------------------------------------------------------------------------------

**2_SetFormat\OtherParameters folder**  
There are multiple SNODAS parameters that are included in the downloaded SNODAS .tar file. Those parameters are:

1. Snow Water Equivalent (SWE)
2. Snow Depth
3. Snow Melt Runoff at Base of Snow Pack
4. Sublimation from the Snow Pack
5. Sublimation of Blowing Snow
6. Solid Precipitation
7. Liquid Precipitation
8. Snow Pack Average Temperature  

The SNODAS Tools are defaulted to delete all SNODAS parameters except for Snow Water Equivalent. However, the 
```SaveALLSNODASparameters``` section of the [configuration file](#snodastools92snodasconfigini) allows for users to save all the data from the seven 
other SNODAS parameters. 
If configured, the SNODAS Tools create a new folder called ```OtherParameters``` under the
```2_SetFormat``` folder. All extracted data regarding the SNODAS parameters, other than SWE, is saved within the  ```2_SetFormat\OtherParameters``` folder.  
 
- The SNODAS data files saved in the ```2_SetFormat\OtherParameters``` folder follow the file naming convention described by 
the [NSIDC SNODAS user guide](http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/index.html). 
    


#### processedData\\3_CliptoExtent\\

The SNODAS Tools clip the ```us_ssmv11034tS__T0001TTNATSYYYYMMDD05HP001.tif``` file to the 
[Watershed Basin Extent Shapefile Input](#snodastools92staticdata92) (```watershedBasinBoundaryExtent.shp```).
The clipped file, shown below for the Colorado dataset, is projected into the desired projection configured in the 
[configuration file](#snodastools92snodasconfigini). The projection of the clipped .tif is defaulted to NAD83 Zone 13N. 
It is pertinent to change the desired projection if the study area is outside the appropriate Zone 13N range.

![withExtent](file-structure-images/nationalWExtent.png)  
*Above: The SNODAS Snow Water Equivalent Masked Grid for January 16th, 2017 with the Colorado basin extent outline overlaid in black.*
![clippedtif](file-structure-images/clippedTIF.png)
*Above: The SNODAS Snow Water Equivalent Grid for January 16th, 2017 clipped to the Colorado basin extent. The skewed image is due to reprojections built into the SNODAS Tools.*

The clipped and reprojected SNODAS .tif file is saved to the 3_ClipToExtent folder and is named ```SNODAS_SWE_ClipAndReprojYYYYMMDD.tif``` 
where ```YYYYMMDD``` represents the date of data. Note that the date does not represent the download date but rather the date when the SNODAS 
data is collected. 

	Example: 
	Clipped and reprojected SNODAS file for January 9th, 2013 -> SNODAS_SWE_ClipAndReproj20130109.tif
	
Refer to the [Processing Workflow](overview/#clip-and-project-snodas-national-grids-to-study-area) section for a general description of the SNODAS Tools' clip and reprojecting steps. 
Refer to [Tool Utilities and Functions](overview.md#3-clip-and-project-snodas-national-grids-to-study-area) for detailed information on the Python functions 
called to clip and reproject the SNODAS data.

#### processedData\\4_CreateSnowCover\\

The SNODAS Tools create a daily binary raster grid displaying presence and absence of snow cover. The created snow cover .tif file is saved to the 
4_CreateSnowCover folder and is named ```SNODAS_SnowCover_ClipAndReprojYYYYMMDD.tif``` where ```YYYYMMDD``` represents the date of data. Note 
that the date does not represent the download date but rather the date when the SNODAS data is collected. 

	Example: 
	Clipped and reprojected snow cover file for January 9th, 2013 -> 
	SNODAS_SnowCover_ClipAndReproj20130109.tif

```SNODAS_SnowCover_ClipAndReprojYYYYMMDD.tif```, shown below for the Colorado dataset, is created by iterating through the cells of 
the ```SNODAS_SWE_ClipAndReprojYYYYMMDD.tif``` file and assigning cell values dependent on the following guidelines:

|SNODAS_```SWE```_ClipAndReprojYYYYMMDD|SNODAS_```SnowCover```_ClipAndReprojYYYYMMDD|
| ---------------------------------- | ---------------------------------------- |
| a cell has a value greater than 0 (there is snow on the ground)| the corresponding cell is assigned a value of '1' (presence of snow displayed in blue)|
| a cell has a value equal to 0 (there is no snow on the ground)| the corresponding cell is assigned a value of '0' (absence of snow displayed in brown)|
| a cell has a value equal to -9999 (a null value)| the corresponding cell is assigned a value of '-9999' (a null value displyed in white)|

![snowCover](file-structure-images/snowCoverTIF.png)
*Above: The binary Colorado snow cover grid for January 16th, 2017. Blue = presence of snow. Brown = absence of snow.* 

Refer to the [Processing Workflow](overview/#create-the-binary-snow-cover-raster) section for a general description of the SNODAS Tools' Create Snow Cover step. 
Refer to [Tool Utilities and Functions](overview.md#4-create-the-binary-snow-cover-raster) for detailed information on the Python functions 
called to create the daily snow cover .tif file.

	

#### processedData\\5_CalculateStatistics\\

The SNODAS Tools perform zonal statistics on the ```SNODAS_SWE_ClipAndReprojYYYYMMDD.tif``` file where zones are defined by the individual features of the
[Watershed Basin Shapefile Input](#snodastools92staticdata92) (```watershedBasinBoundary.shp```). The statistics are exported into two types of .csv files. 

** .CSV File Type 1: Snowpack Statistics organized By Basin **  

The zonal statistics are saved by basin where a separate .csv file is saved for each basin of the 
[Watershed Basin Shapefile Input](#snodastools92staticdata92) (```watershedBasinBoundary.shp```). Refer to the 
[processedData\\5_CalculateStatistics\\StatisticsbyBasin\\](#processeddata925_calculatestatistics92statisticsbybasin92) section for more information.  

** .CSV File Type 2: Snowpack Statistics organized By Date **

The zonal statistics are save by date where a separate .csv file is saved for each date processed by the SNODAS Tools. Refer to the 
[processedData\\5_CalculateStatistics\\StatisticsbyDate\\](#processeddata925_calculatestatistics92statisticsbydate92) section for more information.


The default calculated zonal statistics are:

|Statistic|Description|CSV Column Header|
|-------|------------------------|----------|
|SWE Mean (m)| The daily SWE mean in meters for each basin of the watershed basin shapefile input.|SNODAS_SWE_Mean_m|
|cell Count| The number of cells within each basin of the watershed basin shapefile input.|SNODAS_cell_Count|
|Percent of Snow Coverage|The percentage of land within each basin of the watershed basin shapefile input covered by snow.|SNODAS_SnowCover_percent|
|SWE Mean (in)| The daily SWE mean in inches for each basin of the watershed basin shapefile input.|SNODAS_SWE_Mean_in|

**Todo egiles 2/9/17 clean up this section and change all other sections regarding the type of statistics created**

The default calculated zonal statistics, above, cannot be configured. They will be processed and exported to 
the csv files for every day of processed SNODAS data. There are extra statistics, however, that can be enabled in the 
[configuration file](#snodastools92snodasconfigini). These are optional statistics that are, by default, ignored. 
Note that the desired optional statistics must be configured before the script is run. Errors occur within the 
[byBasin csv files](#processeddata925_calculatestatistics92statisticsbybasin92) if the enabling/disabling of the 
optional statistics is changed within the configuration file after the script has already been ran. For information about 
how to change the optional zonal statistics after the script has previously been run refer to the 
[Troubleshooting](../deployed-env/troubleshooting.md#enabling-optional-swe-statistics) section. 

The optional calculated zonal statistics are:

|Statistic|Description|CSV Column Header|
|-------|------------------------|----------|
|SWE Minimum (m)| The daily SWE minimum in meters for each basin of the watershed basin shapefile input.|SNODAS_SWE_Min_m|
|SWE Maximum (m)|The daily SWE maximum in meters for each basin of the watershed basin shapefile input.|SNODAS_SWE_Max_m|
|SWE Standard Deviation (m)|The daily SWE standard deviation in meters for each basin of the watershed basin shapefile input.|SNODAS_SWE_StdDev_m|
|SWE Minimum (in)| The daily SWE minimum in inches for each basin of the watershed basin shapefile input.|SNODAS_SWE_Min_in|
|SWE Maximum (in)|The daily SWE maximum in inches for each basin of the watershed basin shapefile input.|SNODAS_SWE_Max_in|
|SWE Standard Deviation (in)|The daily SWE standard deviation in inches for each basin of the watershed basin shapefile input.|SNODAS_SWE_StdDev_in|

Refer to the [Processing Workflow](overview/#intersect-snodas-colorado-grid-with-colorado-basins-and-calculate-statistics) section for a general description of the SNODAS Tools' calculate statistics step. 
Refer to [Tool Utilities and Functions](overview.md#5-calculate-and-export-zonal-statistics) for detailed information on the Python functions called to create 
the .csv files and calculate and export the zonal statistics.


#### processedData\\5_CalculateStatistics\\StatisticsbyBasin\\
As previously explained, the snowpack zonal statistics are organized and exported into two different types of .csv files, by basin and by date. 
 
There is one SnowpackStatisticsByBasin_XXXX.csv file for **each** feature of the [Watershed Basin Shapefile Input](#snodastools92staticdata92) (```watershedBasinBoundary.shp```).
The statistics organized by basin provide change analysis capabilities because the data show the change in snowpack statistics for a specific basin 
throughout time.  

*'XXXX'* is the unique ID identifying each basin feature. This ID is located as a field within the attribute table of the [Watershed Basin Shapefile Input](#snodastools92staticdata92)
(```watershedBasinBoundary.shp```). It is important to assign the name of the attribute field holding the basin ID information in the 
[configuration file](#snodastools92snodasconfigini) before running the scripts so that the *'XXXX'* field in the naming convention is correctly populated. 
 
	Example: 
	Zonal statistics by basin .csv file for basin 'ALAC2' on January 9th, 2013 -> 
	SnowpackStatisticsByBasin_ALAC2.csv
	
Each SnowpackStatisticsByBasin_XXXX.csv contains rows of snowpack statistics organized by processed date. Every time a new date of SNODAS data is run, each 
SnowpackStatisticsByBasin_XXXX.csv file is updated with a new row of statistics. 

An example of a SnowpackStatisticsByBasin_XXXX.csv file is shown below. You can see that the dates, January 1st through January 5th, 2017, have been 
processed by the SNODAS Tools. The red circle shows that all values under the Local_ID column (the watershed basin ID) are equivalent.
Right-click on the image and click *Open image in new tab* to see a larger view. 

![statsByBasin](file-structure-images/statsbybasin.png)

	
#### processedData\\5_CalculateStatistics\\StatisticsbyDate\\
**Statistics By Date CSV Files**  

As previously explained, the snowpack zonal statistics are organized and exported into two different types of .csv files, by basin and by date. 
 
There is one SnowpackStatisticsByDate_YYYYMMDD.csv file for **each** date of processed SNODAS data where ```YYYYMMDD``` represents the date of data. 
Note that the date does not represent the download date but rather the date when the SNODAS data is collected. The statistics organized by date provide 
landscape comparison capabilities because the data shows the varying daily snowpack statistics for each basin in the study area. 

	Example: 
	Zonal statistics by date .csv file for January 9th, 2013 -> 
	SnowpackStatisticsByDate_20130109.csv
	
Each SnowpackStatisticsByDate_YYYYMMDD.csv contains rows of snowpack statistics organized by basin ID. Each basins' statistics are saved within individual 
rows of the .csv file. 

An example of a SnowpackStatisticsByDate_YYYYMMDD.csv file is shown below. The daily statistics (October 15th, 2014) for all basins of the 
[Watershed Basin Shapefile Input](#snodastools92staticdata92) (```watershedBasinBoundary.shp```) are represented. The red circle shows that all 
values under the Date_YYYYMMDD column are equivalent. Right-click on the image and click *Open image in new tab* to see a larger view. 

![statsByBasin](file-structure-images/statsbydate.png)

**ListOfDates.txt**  

The ListOfDates.txt file is a text file that contains a list of all processed dates of SNODAS data. All dates in the list correspond to 
a SnowpackStatisticsByDate_YYYYMMDD.csv file in the StatisticsbyDate folder. The dates in the ListOfDates.txt file are in the YYYYMMDD format. 
This text file is used in the development of the [Map Application](). 

**ToDO egiles 2/7/2017 point to Kory's application and change the name of 'Map Application' to the actual title of the application**





### SNODASTools\\SNODASconfig.ini		

The ```SNODASconfig.ini``` is located in the ```SNODASTools``` folder and contains Python input variables and logging settings for the SNODAS Tools.   

The configuration file is divided into *sections*. The sections are the broad categories of SNODAS configurables.  

	Example: 
	
	'VectorInputExtent' is the section header for all configurables related to the  
	Watershed Basin Extent Shapefile Input.   

Under each section, there are corresponding *options* that relate to the section.  

	Example: 
	
	'pathname' and 'projection_epsg' are options under the 'VectorInputExtent' section. 
	
	'pathname' refers to the location of the Watershed Basin Extent Shapefile Input. 
	'projection_epsg' refers to the projection of the Watershed Basin Extent Shapefile Input.
	
All configuration file sections and corresponding options are explained in the table below. The defaults of each configuration option is listed in the far-right column. 
The options that are defaulted to 'N/A' are pathnames that are specific to the local computer of the deployed environment.   

Note: The table entries starting at ```loggers:keys``` and ending at ```formatter_simpleFormatter:format``` refer to the configuration of the logging file. For information regarding how
the logging file is configured, reference the [processedData\SNODASTools.log](#processeddata92snodastoolslog) section.

|Configuration File <br> **Section**<br>Option|Description|Defaulted <br> to:|
|--------------------------|------------|---|
|**QGISInstall**<br>pathname|The full pathname to the location of the [QGIS software](../dev-env/qgis.md#qgis-and-bundled-python) on the local computer.|C:/OSGeo4W/apps/qgis|
|**SNODAS_FTPSite**<br>webstite|The SNODAS FTP site url.|sidads.colorado.edu|
|**SNODAS_FTPSite**<br>username|The username used to access the SNODAS FTP site. The defaulted generic username does not need to be changed.|anonymous|
|**SNODAS_FTPSite**<br>password|The password used to access the SNODAS FTP site. The defaulted generic password does not need to be changed.|None|
|**SNODAS_FTPSite**<br>folder|The path to the folder containing the SNODAS masked data files.|/DATASETS/NOAA/G02158/masked/|
|**SNODAS_FTPSite**<br>null_value|The SNODAS data null value. This should remain at default unless NOHRSC changes the null value.|-9999|
|**FolderNames**<br>root_pathname|The full pathname of the [processed data folder](#snodastools92processeddata92). Configurations value must end in CDSS\SNODASTools\processedData\.|N/A|
|**FolderNames**<br>download|The name of the [download folder](#processeddata921_downloadsnodas92) located in the processedData folder.|1_DownloadSNODAS|
|**FolderNames**<br>setformat|The name of the [set format folder](#processeddata922_setformat92) located in the processedData folder.|2_SetFormat|
|**FolderNames**<br>clip|The name of the [clip folder](#processeddata923_cliptoextent92) located in the processedData folder.|3_ClipToExtent|
|**FolderNames**<br>snow_cover|The name of the [create snow cover folder](#processeddata924_createsnowcover92) located in the processedData folder.|4_CreateSnowCover|
|**FolderNames**<br>calculate_statistics|The name of the [calculate statistics folder](#processeddata925_calculatestatistics92) located in the processedData folder.|5_CalculateStatistics|
|**FolderNames**<br>by_date|The name of the [statistics by Date folder](#processeddata925_calculatestatistics92statisticsbydate92) located in the calculate statistics folder.|/StatisticsbyDate|
|**FolderNames**<br>by_basin|The name of the [statistics by Basin folder](#processeddata925_calculatestatistics92statisticsbybasin92) located in the calculate statistics folder.|/StatisticsbyBasin|
|**VectorInputShapefile**<br> pathname|The full pathname to the [Watershed Basin Shapefile Input](#snodastools92staticdata92). Configurations value must end in CDSS\SNODASTools\staticData\watershedBasinBoundary.shp.|N/A|
|**VectorInputShapefile**<br> basin_id|The attribute field name of the [Watershed Basin Shapefile Input](#snodastools92staticdata92) defining each unique feature or basin.|LOCAL_ID|
|**VectorInputExtent**<br> pathname|The full pathname to the [Watershed Basin Extent Shapefile Input](#snodastools92staticdata92). Configurations value must end in CDSS\SNODASTools\staticData\watershedBasinBoundaryExtent.shp.|N/A|
|**Projections**<br>datum_epsg|The numerical EPSG CRS code to assign to the downloaded national SNODAS daily grids.|4326|
|**Projections**<br>calcstats_proj_epsg|The numerical EPSG CRS code to project the SNODAS clipped grids. The statistics will be calculated with this projection, therefore, an equal-area projection is recommended.|102003|
|**Projections**<br>calculate_cellsize_x|The spatial resoulution of the clipped SNODAS grid projected in the ```calculate_stats_projection_epsg``` projection (cell x axis in meters).|766.397796|
|**Projections**<br>calculate_cellsize_y|The spatial resoulution of the clipped SNODAS grid projected in the ```calculate_stats_projection_epsg``` projection (cell y axis in meters).|766.397796|
|**Projections**<br>output_crs_epsg|The numerical EPSG CRS code to project the final output products, the daily geoJSON and the daily shapefile. 
|**OutputGeometry**<br>shp_zip|Exported daily shapefiles are comprised of 6 files with different extnesions. True: SNODAS Tools will compress the 6 files into 1 zipped file. False: SNODAS Tools will not compress the 6 files.|False|
|**OutputGeometry**<br>shp_delete_originals|Exported daily shapefiles are comprised of 6 files with different extnesions. This configuration is only applied if ```shp_zip``` is set to True. True: The 6 files are deleted, leaving only the zipped file. False: The 6 files are saved alongside the zipped file.|False|
|**OutputGeometry**<br>geojson_precision|The number of precision decimal places for the output GeoJSON file.|4|
|**SaveALLSNODAS<br>parameters**<br>value|True: SNODAS Tools save ALL extracted daily SNODAS parameter files in folder [2_SetFormat\\OtherParameters](#processeddata922_setformat92)<br>False: SNODAS Tools delete all SNODAS parameters other than SWE.|False|
|**DesiredZonalStatistics**<br>swe_minimum|True: The SNODAS Tools will calculate the minimum SWE statistic (in both inches and millemeters) and export the results to the csv files. False: This statistic will not be calculated or exported.|False|
|**DesiredZonalStatistics**<br>swe_maximum|True: The SNODAS Tools will calculate the maximum SWE statistic (in both inches and millemeters) and export the results to the csv files. False: This statistic will not be calculated or exported.|False|
|**DesiredZonalStatistics**<br>swe_standard_deviation|True: The SNODAS Tools will calculate the SWE standard deviation statistic (in both inches and millemeters) and export the results to the csv files. False: This statistic will not be calculated or exported.|False|
|**loggers**<br>keys|The available SNODASTools logs. This should not be changed unless a new log configration is to be created.|root, log02|
|**handlers**<br>keys|The available SNODASTools handlers. This should not be changed unless a new handler is to be created.|fileHandler, consoleHandler|
|**formatters**<br>keys|The available SNODASTools formatters. This should not be changed unless a new formatter is to be created.|simpleFormatter|
|**logger_root**<br>level|The log level of the 'root' logger.|WARNING|
|**logger_root**<br>handlers|The handler used for the 'root' logger.|consoleHandler|
|**logger_log02**<br>level|The log level of the 'log02' logger.|DEBUG|
|**logger_log02**<br>handlers|The handler used for the 'log02' logger.|fileHandler|
|**logger_log02**<br>qualname|The name used to call the log in the SNODASTools' applications.|log02|
|**logger_log02**<br>propogate|Propogation setting. <br> 1 to indicate that messages must propagate to handlers higher up the logger hierarchy from this logger, or 0 to indicate that messages are not propagated to handlers up the hierarchy.|0|
|**handler_consoleHandler**<br>class|The class type of the consoleHandler.|StreamHandler|
|**handler_consoleHandler**<br>level|The log level of the consoleHandler.|NOTSET|
|**handler_consoleHandler**<br>formatter|The formatter of the consoleHandler.|simpleFormatter|
|**handler_consoleHandler**<br>args|The location of output log messages for the consoleHandler.|(sys.stdout,)|
|**handler_fileHandler**<br>class|The class type of the fileHandler.|handlers.TimedRotatingFileHandler|
|**handler_fileHandler**<br>level|The log level of the fileHandler.|NOTSET|
|**handler_fileHandler**<br>formatter|The formatter of the fileHandler.|simpleFormatter|
|**handler_fileHandler**<br>args|The options for the TimedRotatingFileHandler (filename, when to rotate, rotation interval, backupCount) |('../processedData/SNODASTools.log', 'W0', 1, 5)|
|**formatter_simpleFormatter**<br>foramt|The format of log messages.|%(asctime)s %(message)s|
