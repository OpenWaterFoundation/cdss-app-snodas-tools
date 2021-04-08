#!/bin/bash

# Print the script usage/help text.
printUsage() {
  echo "
Usage:
  ./run-pycharm-ce-for-qgis3.bash [options]

Options:
  -h            Show this help message.
  -v            Show script version and exit.
"
  exit 0
}

# Print the script version.
printVersion() {
  echo
  echo "run-pycharm-ce-for-qgis3.bash version: ${pycharmBashVersion} ${pycharmBashVersionDate}"
  echo
  exit 0
}

while getopts :v opt
do
  case "${opt}" in
    h ) printUsage;;
    v ) printVersion;;
    \? ) printUsage;;
  esac
done

# Current script version & date.
pycharmBashVersion='0.0.1'
pycharmBashVersionDate='2021-04-07'
# Get the folder where this script is located since it may have been run from any folder.
scriptFolder=$(cd $(dirname "$0") && pwd)
# repoFolder is cdss-app-snodas-tools.
repoFolder=$(dirname $scriptFolder)
# programName is run-pycharm-ce-for-qgis3.bash.
programName=$(basename $0)
# Array of supported Pycharm versions.
supportedPycharmVersions=("2021.1")

for ver in "${supportedPycharmVersions}"
do
  echo "${ver}"
done
