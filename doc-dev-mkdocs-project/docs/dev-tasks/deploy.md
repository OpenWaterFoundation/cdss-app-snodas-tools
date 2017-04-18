# Development Tasks / Deploy

The software that is created and tested in the development environment via the PyCharm IDE must be deployed to the
[operational environment](../deployed-env/overview/),
which does not include PyCharm.

# 1. Clone the Repository 
Clone the *Colorado's Decision Support System (CDSS) Snow Data Assimilation System (SNODAS) Tools* from GitHub. 
Step-by-step instructions, provided by [GitHub Help](https://help.github.com/articles/cloning-a-repository/), are listed below.   

1. Open Git Bash.   
2. Change the current working directory to the location where you want the cloned directory to be made.   
3. Type ```git clone``` and then type ```https://github.com/OpenWaterFoundation/cdss-app-snodas-tools.git```.   
4. Press ```Enter```. The repository clone will be created.   
 
# 2. Create Folder/File Structure for Deployed Environment

1. Determine/create the location on the local computer for the deployed version of the SNODAS Tools. Name this folder ```SNODAS_Tools```. 
2. Create the following folders under the ```SNODAS_Tools``` folder.  
	```aws```  
	```config```  
	```scripts```  
	```staticData\WatershedConnectivity```   
	```processedData```  
	```TSTool\6_CreateTimeSeriesProducts\SnowpackGraphsByBasin-tsp```
3. Move the following files from the repository to the deployed environment.

|File in <br>Repository|Location in <br>Deployed Environment|
|-|-|
|pycharm-project\<br>SNODAS_utilities.py|SNODAS_Tools\<br>scripts|
|pycharm-project\<br>SNODASDaily_Automated.py|SNODAS_Tools\<br>scripts|
|pycharm-project\<br>SNODASDaily_Interactive.py|SNODAS_Tools\<br>scripts|
|pycharm-project\<br>SNODASDaily_Automated_forTaskScheduler.bat|SNODAS_Tools\<br>scripts|
|test-CDSS\<br>aws\<br>copyAllToOwfAmazonS3.bat|SNODAS_Tools\<br>aws|
|test-CDSS\<br>config\<br>SNODAS-Tools-Config.ini|SNODAS_Tools\<br>config|
|test-CDSS\<br>staticData\<br>CO_Basins_Albers.shp (and other extensions)|SNODAS_Tools\<br>staticData|
|test-CDSS\<br>staticData\<br>WatershedConnectivity\<br>Watershed_Connectivity_v3.xlsx|SNODAS_Tools\<br>staticData\<br>WatershedConnectivity|
|test-CDSS\<br>TsTool\<br>6_CreateTimeSeriesProducts\<br>create-snodas-swe-graphs.TSTool|SNODAS_Tools\<br>TSTool\<br>6_CreateTimeSeriesProducts|
|test-CDSS\<br>TsTool\<br>6_CreateTimeSeriesProducts\<br>create-snodas-swe-graphs-tstool-control.txt|SNODAS_Tools\<br>TSTool\<br>6_CreateTimeSeriesProducts|
|test-CDSS\<br>TsTool\<br>6_CreateTimeSeriesProducts\<br>snodas-localid-snowcover-graph-template.tsp|SNODAS_Tools\<br>TSTool\<br>6_CreateTimeSeriesProducts|
|test-CDSS\<br>TsTool\<br>6_CreateTimeSeriesProducts\<br>snodas-localid-swe-graph-template.tsp|SNODAS_Tools\<br>TSTool\<br>6_CreateTimeSeriesProducts|
|test-CDSS\<br>TsTool\<br>6_CreateTimeSeriesProducts\<br>snodas-localid-swe-volume-1weekchange-graph-template.tsp|SNODAS_Tools\<br>TSTool\<br>6_CreateTimeSeriesProducts|
|test-CDSS\<br>TsTool\<br>6_CreateTimeSeriesProducts\<br>snodas-localid-swe-volume-gain-cumulative-graph-template.tsp|SNODAS_Tools\<br>TSTool\<br>6_CreateTimeSeriesProducts|
|test-CDSS\<br>TsTool\<br>6_CreateTimeSeriesProducts\<br>snodas-localid-swe-volume-graph-template.tsp|SNODAS_Tools\<br>TSTool\<br>6_CreateTimeSeriesProducts|

# 3. Set Variables in the Configuration File 

1. Open the configuration file ```SNODAS_Tools\config\SNODAS-Tools-Config.ini``` in the deployed environment. 
2. Change all setttings in the configuration file. Settings are explained as comments inside the configuration file as well as in the 
[File Structure section](..\software-design\file-structure\#the-sections-and-options-of-the-configuration-file) of the Developer Documentation. 
3. Make sure that the relative path in **section** ```handler_fileHandler``` **option** ```args``` is set to the location where you want the log 
file to be stored. Recommend that the relative path is set to ```..\processedData\SNODASTools.log```.

# 4. Set Variables in the Task Scheduler Batch File 

1. Open the task scheduler batch file ```SNODAS_Tools\scripts\copyAllToOwfAmazonS3.bat``` in the deployed environment. 
2. Change ```OSGEO4W_ROOT``` to point to the base OSGEO4W install folder. 
3. Change ```PYCHARM``` to point to the pycharm program. 
4. Change ```PYTHON_JOB``` to point to the ```SNODASDaily_Automated.py``` script in the deployed environment. 

# 5. Set Variables in the Python Scripts

1. Open the SNODAS_utilities.py script ```SNODAS_Tools\scripts\SNODAS_utilities.py``` in the deployed environment. 
2. Change ```Configfile``` to the relative path of the configuration file ```SNODAS_Tools\config\SNODAS-Tools-Config.ini```. 
3. Do the same for the SNODASDaily_Automated.py ```SNODAS_Tools\scripts\SNODASDaily_Automated.py``` and the SNODASDaily_Interactive.py
```SNODAS_Tools\scripts\SNODASDaily_Interactive.py```.

