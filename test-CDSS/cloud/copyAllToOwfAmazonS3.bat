@echo off
rem
rem Copy all the necessary data files to the projects.openwaterfoundation.org website.
rem - replace all the files on the web with local files

rem Set --dryrun to test before actually doing
set dryrun=""
rem dryrun="--dryrun"

set s3Folder=s3://projects.openwaterfoundation.org/owf-proj-co-cwcb-2016-snodas/prototype

if "%$1%" == "" (
	echo ""
	echo "Usage:  copyToOwfAmazonS3 AmazonConfigProfile"
	echo ""
	echo "Copy the site files to the Amazon S3 static website folder:  %s3Folder%"
	echo ""
)

rem Variables to indicate how to copy
rem set awsProfile=%1%
set awsProfile=cdss-snodas-tools
rem The above lower-case version should work
rem awsProfile=CDSS-SNODAS-Tools
set snodasRoot=D:\SNODAS\SNODAS_Tools

rem Now sync the local files up to Amazon S3
rem - apparently can't pass an empty argument so comment out %dryrun%
rem %dryrun%

@echo on
rem
rem Snowpack statistics by basin are relative small so always sync all
call aws s3 sync %snodasRoot%\processedData\5_CalculateStatistics\SnowpackStatisticsByBasin %s3Folder%/SnowpackStatisticsByBasin --delete --profile %awsProfile%
rem
rem Snowpack graphs by basin are relative small so always sync all
call aws s3 sync %snodasRoot%\processedData\6_CreateTimeSeriesProducts\SnowpackGraphsByBasin %s3Folder%/SnowpackGraphsByBasin --delete --profile %awsProfile%
rem
rem Sync static files listed as resources on the Data tab on the website
call aws s3 sync %snodasRoot%\staticData\WatershedConnectivity %s3Folder%/StaticData --exclude * --include Watershed_Connectivity_v3.xlsx --delete --profile %awsProfile%
rem
rem The following take the most space
rem -load all years just to see how AWS performas and what the cost is so can let the State know
rem -the ListOfDates.txt file will have the full period and if someone selects a date without data the map will be blank
rem -use one command so that the --exclude, --include, and --delete play nice together
rem -note any years that are omitted will be deleted on S3 if they arleady exist there
call aws s3 sync %snodasRoot%\processedData\5_CalculateStatistics\SnowpackStatisticsByDate %s3Folder%/SnowpackStatisticsByDate --exclude * --include ListOfDates.txt --include *LatestDate* --include *2023* --include *2022* --include *2021* --include *2020* --include *2019* --include *2018* --include *2017* --include *2016* --include *2015* --include *2014* --include *2013* --include *2012* --include *2011* --include *2010* --include *2009* --include *2008* --include *2007* --include *2006* --include *2005* --include *2004* --include *2003* --delete --profile %awsProfile%
