#!/bin/bash

# Get the folder where this script is located since it may have been run from any folder. (abs path)
scriptFolder=$(cd "$(dirname "$0")" && pwd)
# repoFolder is cdss-app-snodas-tools. (abs path)
repoFolder=$(dirname "${scriptFolder}")
# The buildsFolder is the absolute path to the SNODAS Tools builds directory, used for storing
# versioned tar files.
buildsFolder="${scriptFolder}/builds/"

# Attempt to change directories to the top-level repo folder.
cd "${repoFolder}" || exit

# Find the version of code by looking at the SNODAS_utilities.py file.
version=$(cat "${repoFolder}/pycharm-project/SNODAS_utilities.py" | grep "Version:" | cut -b 12-)

# Create and compress the tar file
tar -czvf "${buildsFolder}/cdss-tools-${version}.tar.gz" pycharm-project test-CDSS