#!/bin/bash
#
# Create a new test folder for running SNODAS Tools.
# - this is useful for setting up new SNODAS Tools test environments
# - this needs to be run from a folder where 'config/SNODAS-Tools-Config.ini' exists.
# - it will create the main folders so that typos are avoided
# - this also checks the configuration file for errors (missing properties)

# Supporting functions, alphabetized.

# Check that the configuration file exists.
checkConfigFileExists () {
  # Check that the configuration file exists.
  if [ -z "${configFilePath}" ]; then
    logWarning "The SNODAS Tools configuration file variable is not defined."
    logWarning "  Check the script code."
    # This is an error in configuration.
    exit 1
  elif [ ! -e "${configFilePath}" ]; then
    # Check that this script is being run from a test folder that includes the configuration file.
    logError ""
    logError "It does not appear that this script is being run from a SNODAS Tools root folder."
    logError "  The configuration file does not exist:"
    logError "    ${configFilePath}"
    logError "  The root folder should have already been created and contain a valid configuration file."
    logError ""
    exit 1
  fi
  return 0
}

# Check that the processed data folder is defined and exist:
# - the global 'processedDataFolder' variable will be defined
# - the global 'processedDataFolderLinux' variable will be defined
checkProcessedDataFolder() {
  processedDataFolder=$(getConfigProperty "Folders" "processed_data_folder")

  if [ -z "${processedDataFolder}" ]; then
    logError "SNODAS Tools processed data folder '[Folders].processed_data_folder' is not defined in the configuration file."
    exit 1
  fi

  # Set the Linux version of the folder.
  processedDataFolderLinux=$(cygpath -u ${processedDataFolder})
  logInfo "SNODAS Tools processed_data_folder:"
  logInfo "          configuration: ${processedDataFolder}"
  logInfo "  configuration (linux): ${processedDataFolderLinux}"

  if [ -d "${processedDataFolderLinux}" ]; then
    logInfo "SNODAS Tools processed data folder exists:"
    logInfo "  ${processedDataFolderLinux}"
  else
    logInfo "SNODAS Tools processed data folder does not exist:"
    logInfo "  ${processedDataFolderLinux}"
    mkdir "${processedDataFolderLinux}"
    if [ $? -ne 0 ]; then
      logError "Error creating processed data folder:"
      logError "  ${processedDataFolderLinux}"
      exit 1
    fi
    logInfo "  Created it."
  fi

  # Check the processed data sub-folders, typically:
  #   processedData/
  #     1_DownloadSNODAS
  #     2_SetFormat
  #     3_ClipToExtent
  return 0
}

# Check that the static folder is defined and exists:
# - the global 'staticDataFolder' variable will be defined
# - the global 'staticDataFolderLinux' variable will be defined
checkStaticDataFolder() {
  staticDataFolder=$(getConfigProperty "Folders" "static_data_dir")

  if [ -z "${staticDataFolder}" ]; then
    logError "SNODAS Tools static data folder '[Folders].static_data_dir' is not defined in the configuration file."
    exit 1
  fi

  # Set the Linux version of the folder.
  staticDataFolderLinux=$(cygpath -u ${staticDataFolder})
  logInfo "SNODAS Tools static_data_dir:"
  logInfo "          configuration: ${staticDataFolder}"
  logInfo "  configuration (linux): ${staticDataFolderLinux}"

  if [ -d "${staticDataFolderLinux}" ]; then
    logInfo "SNODAS Tools static data folder exists:"
    logInfo "  ${staticDataFolderLinux}"
  else
    logInfo "SNODAS Tools static data folder does not exist:"
    logInfo "  ${staticDataFolderLinux}"
    mkdir "${staticDataFolderLinux}"
    if [ $? -ne 0 ]; then
      logError "Error creating static data folder:"
      logError "  ${staticDataFolderLinux}"
      exit 1
    fi
    logInfo "  Created it."
  fi
  return 0
}

# Check that the root folder is defined and exists:
# - the global 'rootFolder' variable will be defined
# - the global 'rootFolderLinux' variable will be defined
checkRootFolder() {
  rootFolder=$(getConfigProperty "Folders" "root_folder")

  if [ -z "${rootFolder}" ]; then
    logError "SNODAS Tools root folder '[Folders].root_folder' is not defined in the configuration file."
    exit 1
  fi

  # Get the root folder as Linux.
  rootFolderLinux=$(cygpath -u ${rootFolder})
  logInfo "SNODAS Tools root_dir:"
  logInfo "          configuration: ${rootFolder}"
  logInfo "  configuration (linux): ${rootFolderLinux}"

  # The following should not happen since the root folder is where the configuration file is found.
  if [ ! -d "${rootFolder}" ]; then
    logError "SNODAS Tools root folder does not exist:"
    logError "  ${rootFolder}"
    exit 1
  fi
  # The current folder should match the root folder:
  # - make sure both end in / for comparison for example:
  # - ${currentFolder} probably does not end in 
  if [ "${rootFolderLinux}" != "${currentFolder}" -a "${rootFolderLinux}" != "${currentFolder}/" ]; then
    logError "SNODAS Tools configuration 'root_dir' does not match current folder as linux (with or without /):"
    logError "         configuration: ${rootFolder}"
    logError " configuration (linux): ${rootFolderLinux}"
    logError "               current: ${currentFolder}"
    logError "              current/: ${currentFolder}/"
    exit 1
  fi
  return 0
}

# TODO smalers 2023-04-21 need to only remove surrounding quotes from property values.
# Get a configuration property value.
# - the first argument is the configuration property section (e.g., ProgramInstall for [ProgramInstall])
# - the second argument is the configuration property name (e.g., tstool_pathname)
# - the configuration file must be in global configFilePath variable
# - the property value is echoed and can be assigned to a variable
# - an empty string is echoed if the property is not found
getConfigProperty() {
  local section sectionReq
  local proeprtyName propertyNameReq
  local line lineTrimmed
  sectionReq=$1
  propertyNameReq=$2

  if [ -z "${sectionReq}" ]; then
    logWarning "The section is not specified in call to 'getConfigProperty'." 
  elif [ -z "${propertyNameReq}" ]; then
    logWarning "The property name is not specified in call to 'getConfigProperty'." 
  else
    # Can parse the file.
    while IFS= read -r line; do
      lineTrimmed=$(echo ${line} | tr -d ' ')
      if [[ ${lineTrimmed} =~ ^#.* ]]; then
        # Comment.
        continue
      elif [[ ${lineTrimmed} =~ ^\[.* ]]; then
        # Section is what is between [].
        section=$(echo ${lineTrimmed} | cut -d '[' -f 2 | cut -d ']' -f 1)
        logDebug "Found section: ${section}"
        continue
      elif [[ ${lineTrimmed} =~ ^.*=.* ]]; then
        # property=value.
        propertyName=$(echo ${lineTrimmed} | cut -d '=' -f 1 | tr -d "'\" " )
        propertyValue=$(echo ${lineTrimmed} | cut -d '=' -f 2 | tr -d "'\" ")
        logDebug "  Found property: ${propertyName}=${propertyValue}"
        if [ "${section}" = "${sectionReq}" -a "${propertyName}" = "${propertyNameReq}" ]; then
          # Have found the requested property.
          echo "${propertyValue}"
          return 0
        fi
      fi
    done < "${configFilePath}"
  fi

  # Default is to echo an empty string.
  echo ""
  # For now this is not an error.
  return 0
}

# Start logging functions.

# Echo a string to standard error (stderr).
# This is done so that TSTool results output printed to stdout is not mixed with stderr.
# For example, TSTool may be run headless on a server to output to CGI,
# where stdout formatting is important.
echoStderr() {
  echo "$@" >&2
}

# Print a DEBUG message, currently prints to stderr.
logDebug() {
   if [ "${debug}" = "true" ]; then
     echoStderr "[DEBUG] $@"
   fi
}

# Print an ERROR message, currently prints to stderr.
logError() {
   echoStderr "[ERROR] $@"
}

# Print an INFO message, currently prints to stderr.
logInfo() {
   echoStderr "[INFO] $@"
}

# Print an WARNING message, currently prints to stderr.
logWarning() {
   echoStderr "[WARNING] $@"
}

# End logging functions.

# Parse the command parameters:
# - use the getopt command line program so long options can be handled
parseCommandLine() {
  # Single character options.
  optstring="dhv"
  # Long options.
  optstringLong="debug,help,version"
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
  # Loop over the options:
  while true; do
    logDebug "Command line option is ${opt}"
    case "$1" in
      -d|--debug) # -d or --debug  Turn on debug.
        debug=true
        ;;
      -h|--help) # -h or --help  Print the program usage.
        printUsage
        exit 0
        ;;
      -v|--version) # -v or --version  Print the program version.
        printVersion
        exit 0
        ;;
      --) # No more arguments.
        shift
        break
        ;;
      *) # Unknown option.
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
  echoStderr "Create and/or check a SNODAS Tools folder structure for a new dataset."
  echoStderr ""
  echoStderr "-d or --debug           Turn on debug."
  echoStderr "-h or --help            Print the usage."
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
  echoStderr "SNODAS Tools is part of Colorado's Decision Support Systems"
  echoStderr "and has been enhanced by the Open Water Foundation."
  echoStderr "Copyright (C) 1994-2023 Colorado Department of Natural Resources"
  echoStderr "and the Open Water Foundation."
  echoStderr ""
  echoStderr "SNODAS Tools is free software:  you can redistribute it and/or modify"
  echoStderr "    it under the terms of the GNU General Public License as published by"
  echoStderr "    the Free Software Foundation, either version 3 of the License, or"
  echoStderr "    (at your option) any later version."
  echoStderr ""
  echoStderr "    SNODAS Tools is distributed in the hope that it will be useful,"
  echoStderr "    but WITHOUT ANY WARRANTY; without even the implied warranty of"
  echoStderr "    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
  echoStderr "    GNU General Public License for more details."
  echoStderr ""
  echoStderr "    You should have received a copy of the GNU General Public License"
  echoStderr "    along with SNODAS Tools.  If not, see <https://www.gnu.org/licenses/>."
  echoStderr ""
}

# Entry point into the script.

# Set to true if want debug messages to be printed:
# - use the command parameter -d or --debug
debug=false

# Get the path where this script is located since it may have been run from any folder.
scriptFolder=$(cd "$(dirname "$0")" && pwd)
programName=$(basename $0)
programVersion="1.0.0"
programVersionDate="2023-04-20"
currentFolder=$(pwd)
configFilePath="${currentFolder}/config/SNODAS-Tools-Config.ini"

# Parse the command line.
parseCommandLine "$@"

logInfo ""
logInfo "Running in folder:"
logInfo "  ${scriptFolder}"
logInfo "Configuration file (based on the run folder):"
logInfo "  ${configFilePath}"

# Check that the configuration file exists.
checkConfigFileExists

# Check the root folder.
checkRootFolder

# Check the static data folder.
checkStaticDataFolder

# Check the processed data folder.
checkProcessedDataFolder

# Exit with success.
exit 0
