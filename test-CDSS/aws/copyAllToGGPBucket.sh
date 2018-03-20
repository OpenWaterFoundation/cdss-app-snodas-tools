#! /bin/bash
PATH="$PATH":/usr/bin/gsutil/
# Move the changes SNODAS files from the virtual machine to the GCP Storage Bucket
# Set --dryrun to test before actually doing
dryrun=""
#dryrun="--dryrun"
googleBucket="gs://snodas.cdss.state.co.us"
# Comment the process.
#
echo ""
echo "Usage:  copyAllToGCPBucket"
echo ""
echo "Copy the SNODAS products to the Google Cloud Platform static bucket: $googleBucket"
echo ""
#
# gsutil library command reference: https://cloud.google.com/storage/docs/gsutil/commands/rsync
# Snowpack statistics by basin are relative small so always sync all
sudo gsutil -m rsync -r ../processedData/5_CalculateStatistics/SnowpackStatisticsByBasin gs://snodas.cdss.state.co.us/SnowpackStatisticsByBasin/
# Snowpack graphs by basin are relative small so always sync all
sudo gsutil -m rsync -r ../processedData/6_CreateTimeSeriesProducts/SnowpackGraphsByBasin gs://snodas.cdss.state.co.us/SnowpackStatisticsByBasin/
# Sync static files listed as resources on the Data tab on the website
sudo gsutil -m rsync -r ../staticData/WatershedConnectivity gs://snodas.cdss.state.co.us/StaticData/
# Sync the snowpack statistics by date
sudo gsutil -m rsync -r ../processedData/5_CalculateStatistics/SnowpackStatisticsByDate gs://snodas.cdss.state.co.us/SnowpackStatisticsByDate/