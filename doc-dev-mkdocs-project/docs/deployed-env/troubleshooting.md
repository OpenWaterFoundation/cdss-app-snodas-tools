# Deployed Environment / Troubleshooting

**TODO smalers 2016-12-11 Add discussion of common tasks, such as when download fails and needs to rerun script**

## User Input Error Messages in the Console

If you are experiencing error messages when typing your input into the console while running the userinput script, it could be any of the following: 

- If you are entering a date: The date could be in the improper format. You should enter all dates in the mm/dd/yy format. For example, if you are interested in February 6th of 2005 then you will enter 02/06/05. <br><br>
	* The date could be out of appropriate range. Remember that the SNODAS data is only available on or after October 1st, 2003. If you try to enter a date before then, you will receive an error message. The SNODAS data is
	only available up until today’s date. If you try to enter a date in the future, you will receive an error message. 
	* If you are interested in a range of dates, then your end date must be after your starting date. Make sure that you are entering a date later than the starting date that you entered. Otherwise, you will receive an error. 
	* Make sure that you do not add a space before or after the entered date. After typing in the year, press enter without adding any extra spacing. These extra spaces could cause the script to produce an error. <br><br>
- If you are entering text:<br><br>
	* Make sure that you are typing one of the options that the prompt has asked you to type. If you enter text other than the preset options, you will receive an error. 
	* Make sure that you do not add a space before or after the entered text. After the last character of your input, press enter without adding any extra spacing. These extra spaces could cause the script to produce an error. <br><br>
- If you accidentally choose an option in a prompt that is not the option you wanted:<br><br>
	* If this occurs, there is no way for you to go back to the last question and fix the error. Instead you must shut down the running script and restart a new script. You will be prompted with the first question again. Go through the prompts as usual with the inputs that you want. 

## Interrupting the Script Mid-Process

It is important that once a script is running that it continues until completion without interruption. Interruption can mean two actions. First, it could mean that the script is manually terminated. Secondly, 
it could mean that the userInput  script is running at the same time as the automatedDaily  script. Both actions will most likely result in a corrupted basin boundary shapefile. 

Why does this occur? 

The zStat_and_export function creates new fields in the basin shapefile attribute table for each day of processing. The statistics store under the newly created fields only to be written to a local csv file. 
The script then deletes the newly created fields to allow space for the next day of spatial statistics to be calculated and copied over to a new .csv file. <br>

The script is built to temporarily edit the structure of the basin’s attribute table only to be converted back to its original structure at the end of the script. If the script is interrupted in the middle 
of a process, it is possible that the structure of the basin’s attribute table will permanently corrupt causing the entire script to break and/or the script to calculate inaccurate statistics. Another possible outcome 
of interrupting the script mid-process would be permanent deletion of basin polygon/features within the basin shapefile.  <br>

If the script is interrupted mid-process, there is a fix. This is a semi-complicated process so it is best to avoid this troubleshooting issue altogether. If an interruption has occurred, most likely, the results 
will be inaccurate or incomplete. It is best to delete all results created from the interrupted script (this includes the created .tif files rather than just the .csv result files). The corrupted basin shapefile 
(not the basin extent shapefile) must be overwritten with an original copy. Most likely, the fields of the attribute table are not correct (either too many fields or not enough fields). As mentioned above, some 
polygons/features of the corrupted basin shapefile might also be deleted. <br>

## Enabling Optional SWE Statistics

The SNODAS Tools always calculate and export the [default SWE statistics](). The [optional SWE statisitics](), however, are defaulted to be ignored by
the SNODAS Tools. If desired by the user, the optional statistics can be enabled to be calculated and exported to the [csv files] alongside 
the default SWE statistics. The desired optional statistics can be configured in the [configuration file]() under section ```Desired```. 

The SNODAS Tools export the satistics into two types of csv files, ```byDate``` and ```byBasin```. In both csv files, the statistic name is written 
to the first row, or the header row, as shown below. 

![csvExample](.png)

When an optional statistic is enabled in the configuration file, a new column is added to each of the csv files. For this reason, it is 
mandatory that the configuration of the optional SWE statistics is set *before* the script is first run. If the configuraion of the optional
SWE statistics is changed *after* the first run of the SNODAS Tools (meaning that the csv files have already been created and there
is already data within the csv files), an error will occur within the [```byBasin``` csv file](). 

For example, if the SNODAS Tools originally run with the default settings then the header row of the csv files will 
include the following 7 columns:

||Column Name|Column Description|
|-|---------|--------------|
|1|Date_YYYYMMDD|the date|
|2|LOCAL_ID|the unique local basin ID|
|3|SNODAS_SWE_Mean_in|the SWE mean (inches)|
|4|SNODAS_SWE_Mean_mm|the SWE mean (millimeters)|
|5|Effective_Area|the basin area|
|6|Snow_Cover_percent|the areal snow cover|
|7|SWE_volume_acft|the volume of water stored within the snowpack|
|8|one_week_SWE_volume_change_acft|the week change in water volume stored within the snowpack| 

It is important to understand that a *new* [```byDate``` csv file] is created everytime a *new* date of SNODAS 
data is processed with the SNODAS Tools. However, a new [```byBasin``` csv file] *is not* created everytime a *new*
date of SNODAS data is processed. Instead, the statistics from the new day are *appended* to the original ```byBasin```
csv file. This is why the error occurs within the ```byBasin``` csv file if new statistics are introduced or disabled
after the header row of the ```byBasin``` csv file has already been previously established. 
 
 

**Todo egiles 2/9/2017 explain the optional swe statistics and how to configure them to turn on. Also 
note the errors that occur if a user changes the optional swe statistics after already having a byBasin csv
file. Explain how to fix this problem.**