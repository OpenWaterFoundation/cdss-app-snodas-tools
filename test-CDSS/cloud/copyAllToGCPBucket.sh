#! /bin/bash
PATH="${PATH}":/usr/bin/gsutil/
# Move the changes SNODAS files from the virtual machine to the GCP Storage Bucket
# Set --dryrun to test before actually doing
dryrun=""

useNewFolder="true"
#dryrun="--dryrun"
googleBucket="gs://snodas.cdss.state.co.us"
# Comment the process.
#
echo ""
echo "Usage:  copyAllToGCPBucket"
echo ""
echo "Copying  SNODAS products to the Google Cloud Platform static bucket: ${googleBucket}"
echo ""

if [ "${useNewFolder}" = "true" ]; then
    # Snowpack statistics by basin are relative small so always sync all.
    sudo gsutil -m rsync -r ../processedData/5_CalculateStatistics/SnowpackStatisticsByBasin "${googleBucket}"/data/SnowpackStatisticsByBasin/
    # Snowpack graphs by basin are relative small so always sync all.
    sudo gsutil -m rsync -r ../processedData/6_CreateTimeSeriesProducts/SnowpackGraphsByBasin "${googleBucket}"/data/SnowpackGraphsByBasin/
    # Snowpack statistics by date.
    sudo gsutil -m rsync -r ../processedData/5_CalculateStatistics/SnowpackStatisticsByDate "${googleBucket}"/data/SnowpackStatisticsByDate/
    # All static data files.
    sudo gsutil -m rsync -r ../staticData "${googleBucket}"/data/StaticData/
else
    #
    # gsutil library command reference: https://cloud.google.com/storage/docs/gsutil/commands/rsync
    # Snowpack statistics by basin are relative small so always sync all
    # sudo gsutil -m rsync -r ../processedData/5_CalculateStatistics/SnowpackStatisticsByBasin "${googleBucket}"/app/SnowpackStatisticsByBasin/
    # Snowpack graphs by basin are relative small so always sync all
    # sudo gsutil -m rsync -r ../processedData/6_CreateTimeSeriesProducts/SnowpackGraphsByBasin "${googleBucket}"/app/SnowpackGraphsByBasin/
    # Sync static files listed as resources on the Data tab on the website
    # sudo gsutil -m rsync -r ../staticData/WatershedConnectivity "${googleBucket}"/app/StaticData/
    # Sync the snowpack statistics by date
    # sudo gsutil -m rsync -r ../processedData/5_CalculateStatistics/SnowpackStatisticsByDate "${googleBucket}"/app/SnowpackStatisticsByDate/
    :
fi
