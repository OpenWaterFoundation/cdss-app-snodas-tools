@echo off
rem
rem Copy all the necessary data files to the projects.openwaterfoundation.org website.
rem - replace all the files on the web with local files

rem Set --dryrun to test before actually doing
set dryrun=""
rem dryrun="--dryrun"

set s3Folder="s3://projects.openwaterfoundation.org/owf-proj-co-cwcb-2016-snodas/prototype"

if "%$1%" == "" (
	echo ""
	echo "Usage:  copyToOwfAmazonS3 AmazonConfigProfile"
	echo ""
	echo "Copy the site files to the Amazon S3 static website folder:  %s3Folder%"
	echo ""
)

set awsProfile=%1%

rem First build the site so that the "site" folder contains current content.
rem - "mkdocs serve" does not do this

@echo on

rem Now sync the local files up to Amazon S3
rem - apparently can't pass an empty argument so comment out %dryrun%
rem %dryrun%

call aws s3 sync ../processedData/5_CalculateStatistics/SnowpackStatisticsByBasin %s3Folder%/SnowpackStatisticsByBasin --delete --profile %awsProfile%
call aws s3 sync ../processedData/5_CalculateStatistics/SnowpackStatisticsByDate %s3Folder%/SnowpackStatisticsByDate --delete --profile %awsProfile%
call aws s3 sync ../processedData/6_CreateTimeSeriesProducts/SnowpackGraphsByBasin %s3Folder%/SnowpackGraphsByBasin --delete --profile %awsProfile%
