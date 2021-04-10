#!/bin/bash

# Print the first empty line to separate the script from the line the command was
# given and set global script variables.
echo ""
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'
INFO="${BLUE}[Info]:${RESET} "
DEBUG="${GREEN}[Debug]:${RESET} "
ERROR="${RED}[Error]:${RESET} "

# Current script version & date.
pycharmBashVersion='0.0.1'
pycharmBashVersionDate='2021-04-07'
# Global variable to hold the path to an installed Pycharm bash script.
PYCHARM=''
# The base path to the directory that contains installed versions of Pycharm.
PYCHARMBASEPATH="/home/$(whoami)/.local/share/JetBrains/Toolbox/apps/PyCharm-C/ch-0"
QGISBASEPATH="/usr/share/qgis"
# Holds the qgisVersion on the system. Might become an array of different versions.
qgisVersion='3.18'
# Get the folder where this script is located since it may have been run from any folder.
scriptFolder=$(cd "$(dirname "${0}")" && pwd)
echo -e "${INFO}Script folder is '${scriptFolder}'"
# repoFolder is cdss-app-snodas-tools.
repoFolder=$(dirname "${scriptFolder}")
echo -e "${INFO}Repository folder is '${repoFolder}'"
# programName is run-pycharm-ce-for-qgis3.bash.
programName=$(basename "${0}")
echo -e "${INFO}Script name is '${programName}'"
# Array of supported Pycharm versions.
supportedPycharmVersions=("211" "203")
# Holds the newest version of Pycharm found on the system.
foundPycharmVersion=""


# The expected pycharm was not found.
noPycharmFound() {
  echo -e "${ERROR}PyCharm was not found in expected location."
  echo -e "${ERROR}May need to update this script for newer versions of PyCharm."
  exit 0
}

# 
setPycharmScript() {
  if [ "${foundPycharmVersion}" = "211" ]; then
    PYCHARM='/home/jkeahey/.local/share/JetBrains/Toolbox/apps/PyCharm-C/ch-0/211.6693.115/bin/pycharm.sh'
  fi
}

# 
findPycharmVersion() {
  # The ! signifies that ${ver} is now an index instead of the element itself.
  for ver in "${supportedPycharmVersions[@]}"
  do
    echo -e "${INFO}Checking for PyCharm version ${ver}."
    foundPycharmVersion=$(cd "${PYCHARMBASEPATH}" && ls -1 | grep -v vmoptions | sort | tail -1 | cut -d '.' -f 1)
    if [ "${ver}" = "${foundPycharmVersion}" ]; then
      echo -e "${INFO}Pycharm version ${ver} found."
      setPycharmScript
      foundPycharmVersion="${ver}"
      break
    else
      noPycharmFound
    fi
  done
}

# Print the script usage/help text.
printUsage() {
  echo "Usage:
  ./run-pycharm-ce-for-qgis3.bash [options]

Options:
  -h                   Show this help message.
  -s <qgis_version>    Run the standalone QGIS install with the given version.
                       (Default is 3.18)
  -v                   Show script version and exit.

"
  exit 0
}

# Print the script version.
printVersion() {
  echo -e "${INFO}run-pycharm-ce-for-qgis3.bash version: ${pycharmBashVersion} ${pycharmBashVersionDate}"
  echo ""
  exit 0
}

# 
setupStandaloneQgis() {
  
  echo "here at setup"
  export SA_PYCHARM_ENV_SETUP="YES"
  echo "${SA_PYCHARM_ENV_SETUP}"
}

# 
runStandaloneQgis() {
  findPycharmVersion
  echo "SA_PYCHARM_ENV_SETUP: ${SA_PYCHARM_ENV_SETUP}"
  if [ "${SA_PYCHARM_ENV_SETUP}" = "" ]; then
    setupStandaloneQgis
  fi
  echo -e "${INFO}Using standalone version of QGIS."
  echo "eval ${PYCHARM}"
  # eval ${PYCHARM}
}

# Check command line options. The ':' at the beginning represents the silent error reporting
# mode, this way the script can handle all errors using the '?' character.
while getopts :hs:v opt
do
  case "${opt}" in
    h ) printUsage;;
    s )
      qgisVersion="${OPTARG}"
      runStandaloneQgis;;
    v ) printVersion;;
    \? ) printUsage;;
    : )
      echo -e "${INFO}No argument given to -s option. Using default version 3.18."
      runStandaloneQgis;;
  esac
done



echo ""
exit 0
