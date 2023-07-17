#!/bin/bash
#
# Copy the site/* contents to the software.openwaterfoundation.org website:
# - replace all the files on the web with local files
# - location is software.openwaterfoundation.org/cdss-snodas-tools in version and/or latest subfolder

# Supporting functions, alphabetized.

# Make sure the MkDocs version is consistent with the documentation content:
# - require that at least version 1.0 is used because of use_directory_urls = True default
# - must use "file.md" in internal links whereas previously "file" would work
# - it is not totally clear whether version 1 is needed but try this out to see if it helps avoid broken links
checkMkdocsVersion() {
  # Required MkDocs version is at least 1.
  requiredMajorVersion="1"
  # On Cygwin, mkdocs --version gives:  mkdocs, version 1.0.4 from /usr/lib/python3.6/site-packages/mkdocs (Python 3.6)
  # On Debian Linux, similar to Cygwin:  mkdocs, version 0.17.3
  # On newer windows: MkDocs --version:  python -m mkdocs, version 1.3.1 from C:\Users\steve\AppData\Local\Programs\Python\Python310\lib\site-packages\mkdocs (Python 3.10)
  # The following should work for any version after a comma.
  mkdocsVersionFull=$(${mkdocsExe} --version | sed -e 's/.*, \(version .*\)/\1/g' | cut -d ' ' -f 2)
  echo "MkDocs --version:  ${mkdocsVersionFull}"
  mkdocsVersion=$(echo "${mkdocsVersionFull}" | cut -d ' ' -f 3)
  echo "MkDocs full version number:  ${mkdocsVersion}"
  mkdocsMajorVersion=$(echo "${mkdocsVersion}" | cut -d '.' -f 1)
  echo "MkDocs major version number:  ${mkdocsMajorVersion}"
  if [ "${mkdocsMajorVersion}" -lt ${requiredMajorVersion} ]; then
    echo ""
    echo "MkDocs version for this documentation must be version ${requiredMajorVersion} or later."
    echo "MkDocs mersion that is found is ${mkdocsMajorVersion}, from full version ${mkdocsVersion}."
    exit 1
  else
    echo ""
    echo "MkDocs major version (${mkdocsMajorVersion}) is OK for this documentation."
  fi
}

# Determine the operating system that is running the script:
# - mainly care whether Cygwin or MINGW
checkOperatingSystem() {
  if [ -n "${operatingSystem}" ]; then
    # Have already checked operating system so return.
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

# Check the source files for issues
# - the main issue is internal links need to use [](file.md), not [](file)
checkSourceDocs() {
  # Currently don't do anything but could check the above
  # Need one line to not cause an error
  :
}

# Determine which echo to use, needs to support -e to output colored text
# - normally built-in shell echo is OK, but on Debian Linux dash is used, and it does not support -e
configureEcho() {
  echo2='echo -e'
  testEcho=$(echo -e test)
  if [ "${testEcho}" = '-e test' ]; then
    # The -e option did not work as intended:
    # -using the normal /bin/echo should work
    # -printf is also an option
    echo2='/bin/echo -e'
    # The following does not seem to work
    #echo2='printf'
  fi

  # Strings to change colors on output, to make it easier to indicate when actions are needed
  # - Colors in Git Bash:  https://stackoverflow.com/questions/21243172/how-to-change-rgb-colors-in-git-bash-for-windows
  # - Useful info:  http://webhome.csc.uvic.ca/~sae/seng265/fall04/tips/s265s047-tips/bash-using-colors.html
  # - See colors:  https://en.wikipedia.org/wiki/ANSI_escape_code#Unix-like_systems
  # - Set the background to black to eensure that white background window will clearly show colors contrasting on black.
  # - Yellow "33" in Linux can show as brown, see:  https://unix.stackexchange.com/questions/192660/yellow-appears-as-brown-in-konsole
  # - Tried to use RGB but could not get it to work - for now live with "yellow" as it is
  warnColor='\e[1;40;93m' # user needs to do something, 40=background black, 33=yellow, 93=bright yellow
  errorColor='\e[0;40;31m' # serious issue, 40=background black, 31=red
  menuColor='\e[1;40;36m' # menu highlight 40=background black, 36=light cyan
  okColor='\e[1;40;32m' # status is good, 40=background black, 32=green
  endColor='\e[0m' # To switch back to default color
}

# Echo a string to standard error (stderr).
echoStderr() {
  ${echo2} "$@" >&2
}

# Get the CDSS TSTool product version:
# - the semantic version (e.g., 1.2.3) is echoed to stdout and can be assigned to a variable
getProductVersion() {
  local versionFile versionFromFile

  versionFile="${srcFolder}/snodastools/app/version.py"
  if [ -f "${versionFile}" ]; then
    appVersionMajor=$(grep 'app_version_major =' ${versionFile} | cut -d '=' -f 2 | tr -d ' ')
    appVersionMinor=$(grep 'app_version_minor =' ${versionFile} | cut -d '=' -f 2 | tr -d ' ')
    appVersionMicro=$(grep 'app_version_micro =' ${versionFile} | cut -d '=' -f 2 | tr -d ' ')
    appVersionMod=$(grep 'app_version_mod =' ${versionFile} | cut -d '=' -f 2 | tr -d ' ' | tr -d '"')
    if [ "${appVersionMod}" = "" ]; then
      # No modifier.
      versionFromFile="${appVersionMajor}.${appVersionMinor}.${appVersionMicro}"
    else
      # Have modifier.
      versionFromFile="${appVersionMajor}.${appVersionMinor}.${appVersionMicro}.${appVersionMod}"
    fi
  else
    versionFromFile=""
  fi
  echo "${versionFromFile}"
}

# Print a DEBUG message, currently prints to stderr.
logDebug() {
   echoStderr "[DEBUG] $@"
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

# Set the AWS executable:
# - handle different operating systems
# - for AWS CLI V2, can call an executable
# - for AWS CLI V1, have to deal with Python
# - once set, use ${awsExe} as the command to run, followed by necessary command parameters
setAwsExe() {
  if [ "${operatingSystem}" = "mingw" ]; then
    # "mingw" is Git Bash:
    # - the following should work for V2
    # - if "aws" is in path, use it
    awsExe=$(command -v aws)
    if [ -n "${awsExe}" ]; then
      # Found aws in the PATH.
      awsExe="aws"
    else
      # Might be older V1.
      # Figure out the Python installation path.
      pythonExePath=$(py -c "import sys; print(sys.executable)")
      if [ -n "${pythonExePath}" ]; then
        # Path will be something like:  C:\Users\sam\AppData\Local\Programs\Python\Python37\python.exe
        # - so strip off the exe and substitute Scripts
        # - convert the path to posix first
        pythonExePathPosix="/$(echo "${pythonExePath}" | sed 's/\\/\//g' | sed 's/://')"
        pythonScriptsFolder="$(dirname "${pythonExePathPosix}")/Scripts"
        echo "${pythonScriptsFolder}"
        awsExe="${pythonScriptsFolder}/aws"
      else
        echo "[ERROR] Unable to find Python installation location to find 'aws' script"
        echo "[ERROR] Make sure Python 3.x is installed on Windows so 'py' is available in PATH"
        exit 1
      fi
    fi
  else
    # For other Linux, including Cygwin, just try to run.
    awsExe="aws"
  fi
}

# Set the MkDocs executable to use, depending operating system and PATH:
# - sets the global ${mkdocsExe} variable
# - return 0 if the executable is found, exit with 1 if not
setMkDocsExe() {
  if [ "${operatingSystem}" = "cygwin" -o "${operatingSystem}" = "linux" ]; then
    # Is usually in the PATH.
    mkdocsExe="mkdocs"
    if hash py 2>/dev/null; then
      echo "mkdocs is not found (not in PATH)."
      exit 1
    fi
  elif [ "${operatingSystem}" = "mingw" ]; then
    # This is used by Git Bash:
    # - calling 'hash' is a way to determine if the executable is in the path
    if hash py 2>/dev/null; then
      mkdocsExe="py -m mkdocs"
    else
      # Try adding the Windows folder to the PATH and rerun:
      # - not sure why C:\Windows is not in the path in the first place
      PATH=/C/Windows:${PATH}
      if hash py 2>/dev/null; then
        mkdocsExe="py -m mkdocs"
      else
        echo 'mkdocs is not found in C:\Windows.'
        exit 1
      fi
    fi
  fi
  return 0
}

# Wait on an invalidation until it is complete:
# - first parameter is the CloudFront distribution ID
# - second parameter is the CloudFront invalidation ID
waitOnInvalidation () {
  local distributionId invalidationId output totalTime
  local inProgressCount totalTime waitSeconds

  distributionId=$1
  invalidationId=$2
  if [ -z "${distributionId}" ]; then
    logError "No distribution ID provided."
    return 1
  fi
  if [ -z "${invalidationId}" ]; then
    logError "No invalidation ID provided."
    return 1
  fi

  # Output looks like this:
  #   INVALIDATIONLIST        False           100     67
  #   ITEMS   2022-12-03T07:00:47.490000+00:00        I3UE1HOF68YV8W  InProgress
  #   ITEMS   2022-12-03T07:00:17.684000+00:00        I30WL0RTQ51PXW  Completed
  #   ITEMS   2022-12-03T00:46:38.567000+00:00        IFMPVDA8EX53R   Completed

  totalTime=0
  waitSeconds=5
  logInfo "Waiting on invalidation for distribution ${distributionId} invalidation ${invalidationId} to complete..."
  while true; do
    # The following should always return 0 or greater.
    #logInfo "Running: ${awsExe} cloudfront list-invalidations --distribution-id \"${cloudFrontDistributionId}\" --no-paginate --output text --profile \"${awsProfile}\""
    #${awsExe} cloudfront list-invalidations --distribution-id "${cloudFrontDistributionId}" --no-paginate --output text --profile "${awsProfile}"
    inProgressCount=$(${awsExe} cloudfront list-invalidations --distribution-id "${cloudFrontDistributionId}" --no-paginate --output text --profile "${awsProfile}" | grep "${invalidationId}" | grep InProgress | wc -l)
    #logInfo "inProgressCount=${inProgressCount}"

    if [ -z "${inProgressCount}" ]; then
      # This should not happen?
      logError "No output from listing invalidations for distribution ID:  ${cloudFrontDistributionId}"
      return 1
    fi

    if [ ${inProgressCount} -gt 0 ]; then
      logInfo "Invalidation status is InProgress.  Waiting ${waitSeconds} seconds (${totalTime} seconds total)..."
      sleep ${waitSeconds}
    else
      # Done with invalidation.
      break
    fi

    # Increment the total time.
    totalTime=$(( ${totalTime} + ${waitSeconds} ))
  done

  logInfo "Invalidation is complete (${totalTime} seconds total)."

  return 0
}

# Entry point into the script.

# Configure the echo command to output color.
configureEcho

# Check the operating system.
checkOperatingSystem

# Set the 'aws' program to use:
# - must set after the operating system is set
setAwsExe

# Set the MkDocs executable:
# - will exit if MkDocs is not found
setMkDocsExe

# Make sure the MkDocs version is OK.
checkMkdocsVersion

# Check the source files for issues.
checkSourceDocs

# Get the folder where this script is located since it may have been run from any folder.
scriptFolder=$(cd $(dirname "$0") && pwd)
repoFolder=$(dirname $(dirname ${scriptFolder}))
srcFolder="${repoFolder}/src"
echo "Script folder = ${scriptFolder}"
# Change to the folder where the script is since other actions below are relative to that.
cd ${scriptFolder}

# Get the SNODAS tools version, which is used in the installer file name.
productVersion=$(getProductVersion)
if [ -z "${productVersion}" ]; then
  echoStderr "[ERROR] ${errorColor}Unable to determine product version.${endColor}"
  exit 1
else
  echoStderr "[INFO] Product version:  ${productVersion}"
fi

# Set --dryrun to test before actually doing.
dryrun=""
#dryrun="--dryrun"
s3VersionFolder="s3://software.openwaterfoundation.org/cdss-snodas-tools/${productVersion}/doc-user"
s3LatestFolder="s3://software.openwaterfoundation.org/cdss-snodas-tools/latest/doc-user"

if [ "$1" == "" ]; then
  echo ""
  echo "Usage:  $0 AmazonConfigProfile"
  echo ""
  echo "Copy the site files to the Amazon S3 static website folders:"
  echo "  ${s3VersionFolder}"
  echo "  ${s3LatestFolder}"
  echo ""
  exit 0
fi

awsProfile="$1"

# First build the site so that the "site" folder contains current content:
# - "mkdocs serve" does not do this

echo "Building mkdocs-project/site folder..."
#cd ../mkdocs-project
cd ..
${mkdocsExe} build --clean
if [ $? -ne 0 ]; then
  echoStderr "[ERROR] Error running MkDocs."
  exit 1
fi
cd ${scriptFolder}

# Now sync the local files up to Amazon S3.
if [ -n "${productVersion}" ]; then
  # Upload documentation to the versioned folder.
  echo "Uploading documentation to:  ${s3VersionFolder}"
  read -p "Continue [Y/n/q]? " answer
  if [ -z "${answer}" -o "${answer}" = "y" -o "${answer}" = "Y" ]; then 
    echo ${awsExe} s3 sync ../site ${s3VersionFolder} ${dryrun} --delete --profile "${awsProfile}"
    ${awsExe} s3 sync ../site ${s3VersionFolder} ${dryrun} --delete --profile "${awsProfile}"
    exitStatusVersion=$?
  elif [ "${answer}" = "q" ]; then 
    exit 0
  fi

  # Also invalidate the CloudFront distribution so that new version will be displayed:
  # - see:  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html
  # - save the output to a temporary file and then extract the invalidation ID progress can be checked
  # Determine the distribution ID:
  # The distribution list contains a line like the following (the actual distribution ID is not included here):
  # ITEMS   arn:aws:cloudfront::132345689123:distribution/E1234567891234    software.openwaterfoundation.org  something.cloudfront.net    True    HTTP2   E1234567891334  True    2022-01-06T19:02:50.640Z        PriceClass_100Deployed
  tmpFile=$(mktemp)
  subdomain="software.openwaterfoundation.org"
  cloudFrontDistributionId=$(${awsExe} cloudfront list-distributions --output text --profile "${awsProfile}" | grep ${subdomain} | grep "arn" | awk '{print $2}' | cut -d ':' -f 6 | cut -d '/' -f 2)
  if [ -z "${cloudFrontDistributionId}" ]; then
    logError "Unable to find CloudFront distribution ID."
    exit 1
  else
    logInfo "Found CloudFront distribution ID: ${cloudFrontDistributionId}"
  fi
  logInfo "Invalidating files so that CloudFront will make new files available..."
  if [ "${operatingSystem}" = "mingw" ]; then
     MSYS_NO_PATHCONV=1 ${awsExe} cloudfront create-invalidation --distribution-id ${cloudFrontDistributionId} --paths "/cdss-snodas-tools/${productVersion}/doc-user/*" --output json --profile "${awsProfile}" | tee ${tmpFile}
  else
     ${awsExe} cloudfront create-invalidation --distribution-id ${cloudFrontDistributionId} --paths "/cdss-snodas-tools/${productVersion}/doc-user/*" --output json --profile "${awsProfile}" | tee ${tmpFile}
  fi
  errorCode=${PIPESTATUS[0]}
  if [ $errorCode -ne 0 ]; then
    logError " "
    logError "Error invalidating CloudFront file(s)."
    exit 1
  else
    logInfo "Success invalidating CloudFront file(s)."
    invalidationId=$(cat ${tmpFile} | grep '"Id":' | cut -d ':' -f 2 | tr -d ' ' | tr -d '"' | tr -d ',')
    # Wait on the invalidation.
    waitOnInvalidation ${cloudFrontDistributionId} ${invalidationId}
  fi
fi

read -p "Also copy documentation to 'latest' [y/n/q]? " answer
exitStatusLatest=0
if [ "${answer}" = "y" ]; then 
  echo "Uploading documentation to:  ${s3LatestFolder}"
  read -p "Continue [Y/n/q]? " answer
  if [ -z "${answer}" -o "${answer}" = "y" -o "${answer}" = "Y" ]; then 
    ${awsExe} s3 sync ../site ${s3LatestFolder} ${dryrun} --delete --profile "${awsProfile}"
    exitStatusLatest=$?
  elif [ "${answer}" = "q" ]; then 
    exit 0
  fi

  # Also invalidate the CloudFront distribution so that new version will be displayed:
  # - see:  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html
  # - save the output to a temporary file and then extract the invalidation ID progress can be checked
  # Determine the distribution ID:
  # The distribution list contains a line like the following (the actual distribution ID is not included here):
  # ITEMS   arn:aws:cloudfront::132345689123:distribution/E1234567891234    software.openwaterfoundation.org  something.cloudfront.net    True    HTTP2   E1234567891334  True    2022-01-06T19:02:50.640Z        PriceClass_100Deployed
  tmpFile=$(mktemp)
  subdomain="software.openwaterfoundation.org"
  cloudFrontDistributionId=$(${awsExe} cloudfront list-distributions --output text --profile "${awsProfile}" | grep ${subdomain} | grep "arn" | awk '{print $2}' | cut -d ':' -f 6 | cut -d '/' -f 2)
  if [ -z "${cloudFrontDistributionId}" ]; then
    logError "Unable to find CloudFront distribution ID."
    exit 1
  else
    logInfo "Found CloudFront distribution ID: ${distributionId}"
  fi
  # Invalidate for CloudFront so that new version will be displayed:
  # - see:  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html
  # - TODO smalers 2020-04-13 for some reason invalidating /index.html does not work, have to do /index.html*
  logInfo "Invalidating files so that CloudFront will make new files available..."
  if [ "${operatingSystem}" = "mingw" ]; then
    # The following is needed to avoid MinGW mangling the paths, just in case a path without * is used:
    # - tried to use a variable for the prefix but that did not work
    MSYS_NO_PATHCONV=1 ${awsExe} cloudfront create-invalidation --distribution-id ${cloudFrontDistributionId} --paths "/cdss-snodas-tools/latest/doc-user/*" --output json --profile "${awsProfile}" | tee ${tmpFile}
  else
    ${awsExe} cloudfront create-invalidation --distribution-id ${cloudFrontDistributionId} --paths "/cdss-snodas-tools/latest/doc-user/*" --output json --profile "${awsProfile}" | tee ${tmpFile}
  fi
  errorCode=${PIPESTATUS[0]}
  if [ $errorCode -ne 0 ]; then
    logError " "
    logError "Error invalidating CloudFront file(s)."
    exit 1
  else
    logInfo "Success invalidating CloudFront file(s)."
    invalidationId=$(cat ${tmpFile} | grep '"Id":' | cut -d ':' -f 2 | tr -d ' ' | tr -d '"' | tr -d ',')
    # Wait on the invalidation.
    waitOnInvalidation ${cloudFrontDistributionId} ${invalidationId}
  fi
fi

exitStatus=$(( ${exitStatusVersion} + ${exitStatusLatest} ))
