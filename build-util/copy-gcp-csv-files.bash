#!/bin/bash

# This simple script downloads all CSV files under the SnowpackStatisticsByDate
# folder in the snodas.cdss.state.co.us GCP bucket.
# -m enables parallel multi-threaded/multi-processing when copying a large number of files.
gsutil -m cp gs://snodas.cdss.state.co.us/app/SnowpackStatisticsByDate/*.csv /media/SNODAS2/SNODAS_Tools/cloud/GCP-csv-files/
