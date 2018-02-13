@echo off
rem
rem
rem Copy the site/* contents to the software.openwaterfoundation.org website.
rem - replace all the files on the web with local files
rem - location is software.openwaterfoundation.org/cdss-app-snodas-tools-doc-dev

rem Set --dryrun to test before actually doing
set dryrun=""
rem dryrun="--dryrun"
set s3Folder="s3://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-dev"

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

cd ..
mkdocs build --clean
cd build-util

rem Now sync the local files up to Amazon S3
rem - apparently can't pass an empty argument so comment out %dryrun%
rem %dryrun%
aws s3 sync ../site %s3Folder% --delete --profile %awsProfile%
