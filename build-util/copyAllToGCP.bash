#!/bin/bash

# Determine the operating system that is running the script
# - mainly care whether Cygwin or MINGW (Git Bash)
checkOperatingSystem() {
  if [ -n "${operatingSystem}" ]; then
    # Have already checked operating system so return
    return
  fi
  operatingSystem="unknown"
  os=$(uname | tr '[:lower:]' '[:upper:]')
  case "${os}" in
    CYGWIN*)
      operatingSystem="cygwin"
      ;;
    LINUX*)
      operatingSystem="linux"
      ;;
    MINGW*)
      operatingSystem="mingw"
      ;;
  esac
}

# Echo to stderr
# - if necessary, quote the string to be printed
# - this function is called to print various message types
echoStderr() {
  echo "$@" 1>&2
}

# Get the user's login.
# - Git Bash apparently does not set $USER environment variable, not an issue on Cygwin
# - Set USER as script variable only if environment variable is not already set
# - See: https://unix.stackexchange.com/questions/76354/who-sets-user-and-username-environment-variables
getUserLogin() {
  if [ -z "${USER}" ]; then
    if [ -n "${LOGNAME}" ]; then
      USER=${LOGNAME}
    fi
  fi
  if [ -z "${USER}" ]; then
    USER=$(logname)
  fi
  # Else - not critical since used for temporary files
}

# Get the SNODAS application version.
# - the version is in the 'web/app-config.json' file in format:  "version": "0.7.0.dev (2020-04-24)"
# - the Info Mapper software version in 'assets/version.json' with format similar to above
getVersion() {
    # Application version
    if [ ! -f "${snodasToolsVersionedFile}" ]; then
    logError "Application version file does not exist: ${snodasToolsVersionedFile}"
    logError "Exiting."
    exit 1
    fi
    appVersion=$(grep 'Version:' "${snodasToolsVersionedFile}" | cut -d ":" -f 2 | cut -d "(" -f 1 | tr -d '"' | tr -d ' ' | tr -d ',')
}

# Print an ERROR message, currently prints to stderr.
logError() {
   echoStderr "[ERROR] $*"
}

# Print an INFO message, currently prints to stderr.
logInfo() {
   echoStderr "[INFO] $*"
}

# Parse the command parameters
# - use the getopt command line program so long options can be handled
parseCommandLine() {
  # Single character options.
  optstring="hv"
  # Long options.
  optstringLong="help,nobuild,noupload,nooptimization,upload-assets,version"
  # Parse the options using getopt command.
  GETOPT_OUT=$(getopt --options ${optstring} --longoptions ${optstringLong} -- "$@")
  exitCode=$?
  if [ ${exitCode} -ne 0 ]; then
    # Error parsing the parameters such as unrecognized parameter.
    echoStderr ""
    printUsage
    exit 1
  fi
  # The following constructs the command by concatenating arguments.
  eval set -- "${GETOPT_OUT}"
  # Loop over the options
  while true; do
    #logDebug "Command line option is ${opt}"
    case "$1" in
      # --dryrun) # --dryrun  Indicate to GCP commands to do a dryrun but not actually upload.
      #   logInfo "--dryrun detected - will not change files on GCP"
      #   dryrun="--dryrun"
      #   shift 1
      #   ;;
      -h|--help) # -h or --help  Print the program usage
        printUsage
        exit 0
        ;;
      --noupload) # --noupload  Indicate to create staging area dist but not upload
        logInfo "--noupload detected - will not upload 'dist' folder"
        doUpload="no"
        shift 1
        ;;
      -v|--version) # -v or --version  Print the program version
        printVersion
        exit 0
        ;;
      --) # No more arguments
        shift
        break
        ;;
      *) # Unknown option
        logError ""
        logError "Invalid option $1." >&2
        printUsage
        exit 1
        ;;
    esac
  done
}

# Print the program usage to stderr.
# - calling code must exit with appropriate code.
printUsage() {
  echoStderr ""
  echoStderr "Usage:  ${programName}"
  echoStderr ""
  echoStderr "Copy the SNODAS back end application files to the Google Cloud Platform static bucket folder(s),"
  echoStderr "using the GCP sync capabilities."
  echoStderr ""
  echoStderr "               ${GCPDataUrl}"
  echoStderr ""
  echoStderr "-h or --help            Print the usage."
  echoStderr "--noupload              Do not upload the staging area 'dist' folder contents, useful for testing."
  echoStderr "-v or --version         Print the version and copyright/license notice."
  echoStderr ""
}

# Print the script version and copyright/license notices to stderr.
# - calling code must exit with appropriate code.
printVersion() {
  echoStderr ""
  echoStderr "${programName} version ${programVersion} ${programVersionDate}"
  echoStderr ""
  echoStderr "SNODAS Tools"
  echoStderr "Copyright 2017-2021 Open Water Foundation."
  echoStderr ""
  echoStderr "License GPLv3+:  GNU GPL version 3 or later"
  echoStderr ""
  echoStderr "There is ABSOLUTELY NO WARRANTY; for details see the"
  echoStderr "'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file."
  echoStderr "This is free software: you are free to change and redistribute it"
  echoStderr "under the conditions of the GPLv3 license in the LICENSE file."
  echoStderr ""
}

# Sync the data files to the GCP data bucket.
syncData() {
    # Add an upload log file to the dist, useful to know who did an upload.
    # uploadLogFile="${snodasToolsExternalMainFolder}/upload.log.txt"
    # echo "UploadUser = ${USER}" > "${uploadLogFile}"
    # now=$(date "+%Y-%m-%d %H:%M:%S %z")
    # {
    #     echo "UploadTime = ${now}"
    #     echo "UploaderName = ${programName}"
    #     echo "UploaderVersion = ${programVersion} ${programVersionDate}"
    #     echo "AppVersion = ${appVersion}"
    # } >> "${uploadLogFile}"

    echo "Ready to upload all SNODAS Tools data folders to GCP"
    echo "  from: ${snodasToolsExternalDataFolder}/processedData/5_CalculateStatistics/SnowpackStatisticsByBasin,"
    echo "        ${snodasToolsExternalDataFolder}/processedData/5_CalculateStatistics/SnowpackStatisticsByDate,"
    echo "        ${snodasToolsExternalDataFolder}/processedData/6_CreateTimeSeriesProducts/SnowpackGraphsByBasin,"
    echo "        ${snodasToolsExternalDataFolder}/staticData"
    echo "    to: ${GCPDataUrl}"

    read -r -p "Continue [Y/n/q]? " answer
    if [ "${answer}" = "q" ] || [ "${answer}" = "Q" ] || [ "${answer}" = "n" ] || [ "${answer}" = "N" ]; then
        exit 0
    elif [ -z "${answer}" ] || [ "${answer}" = "y" ] || [ "${answer}" = "Y" ]; then
        logInfo "Starting GCP sync of data folders..."
        # gsutil library command reference: https://cloud.google.com/storage/docs/gsutil/commands/rsync
        # Snowpack statistics by basin are relative small so always sync all
        sudo gsutil -m rsync -r "${snodasToolsExternalDataFolder}"/processedData/5_CalculateStatistics/SnowpackStatisticsByBasin "${GCPDataUrl}"/SnowpackStatisticsByBasin
        # Snowpack graphs by basin are relative small so always sync all
        sudo gsutil -m rsync -r "${snodasToolsExternalDataFolder}"/processedData/6_CreateTimeSeriesProducts/SnowpackGraphsByBasin "${GCPDataUrl}"/SnowpackGraphsByBasin
        # Sync static files listed as resources on the Data tab on the website
        sudo gsutil -m rsync -r "${snodasToolsExternalDataFolder}"/staticData/WatershedConnectivity "${GCPDataUrl}"/StaticData
        # Sync the snowpack statistics by date
        sudo gsutil -m rsync -r "${snodasToolsExternalDataFolder}"/processedData/5_CalculateStatistics/SnowpackStatisticsByDate "${GCPDataUrl}"/SnowpackStatisticsByDate
        logInfo "...done with GCP sync of data folders."
    fi
}


# Entry point into the script.

# Check the operating system
checkOperatingSystem

getUserLogin

# Get the folder where this script is located since it may have been run from any folder (abs path).
scriptFolder=$(cd "$(dirname "$0")" && pwd)
# snodasToolsRepoFolder is cdss-app-snodas-tools (abs path).
snodasToolsRepoFolder=$(dirname "${scriptFolder}")
# The folder containing the data folders to be synced with GCP.
snodasToolsExternalDataFolder="/media/SNODAS2/SNODAS_Tools"
# The top level folder of the external HDD.
# snodasToolsExternalMainFolder="/media/SNODAS2"
# File containing the SNODAS Tools version.
snodasToolsVersionedFile="${snodasToolsRepoFolder}/pycharm-project/SNODAS_utilities.py"
# Populate this program's variables.
programName=$(basename "$0")
programVersion="1.7.0"
programVersionDate="2021-11-01"

logInfo "scriptFolder:             ${scriptFolder}"
logInfo "Program name:             ${programName}"
logInfo "snodasToolsRepoFolder:    ${snodasToolsRepoFolder}"
logInfo "snodasToolsExternalDataFolder:    ${snodasToolsExternalDataFolder}"
logInfo "snodasToolsVersionedFile: ${snodasToolsVersionedFile}"

# - Put before parseCommandLine so can be used in print usage, etc.
getVersion
logInfo "SNODAS Tools version:  ${appVersion}"

# The URL to the base data folder in the Google bucket.
GCPDataUrl="gs://snodas.cdss.state.co.us/data"

# Default is to upload to GCP.
doUpload="yes"

# Parse the command line arguments.
parseCommandLine "$@"

logInfo "Changing to:  ${snodasToolsExternalDataFolder}"
cd "${snodasToolsExternalDataFolder}" || exit

# Upload the distribution to GCP.
if [ "${doUpload}" = "yes" ]; then
  syncData
fi

echo ""
logInfo "Successfully synced to GCP."
exit 0