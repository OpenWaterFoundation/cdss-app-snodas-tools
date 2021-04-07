#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL

#-----------------------------------------------------------------NoticeStart-
# Git Utilities
# Copyright 2017-2019 Open Water Foundation.
# 
# License GPLv3+:  GNU GPL version 3 or later
# 
# There is ABSOLUTELY NO WARRANTY; for details see the
# "Disclaimer of Warranty" section of the GPLv3 license in the LICENSE file.
# This is free software: you are free to change and redistribute it
# under the conditions of the GPLv3 license in the LICENSE file.
#-----------------------------------------------------------------NoticeEnd---
#
# git-check.sh
#
# Check the status of multiple repositories for this project and indicate whether pull
# or push or other action is needed.
# - see the main entry point at the bottom of the script for script configuration
# - currently must adhere to prescribed folder structure
# - useful when multiple repositories form a product
# - this script does not do anything to change repositories
# - warn if any repositories use Cygwin because mixing with Git for Windows can cause confusion in tools
#

# List functions in alphabetical order

# Determine the operating system that is running the script
# - mainly care whether Cygwin
checkOperatingSystem()
{
	if [ ! -z "${operatingSystem}" ]; then
		# Have already checked operating system so return
		return
	fi
	operatingSystem="unknown"
	os=`uname | tr [a-z] [A-Z]`
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
	echo "operatingSystem=$operatingSystem (used to check for Cygwin and filemode compatibility)"
}

# Function to confirm that proper command-line Git client is being used.
# - mainly to confirm that Cygwin is not used when filemode=false
# - in order to see local config associated with a repo must cd into the repo folder
checkCommandLineGitCompatibility()
{
	# Make sure that the operating system has been determined
	# - will set operatingSystem to "cygwin" if cygwin
	checkOperatingSystem
	filemodeLine=`git config --list | grep filemode`
	#echo "${filemodeLine}"
	if [ ! -z "${filemodeLine}" ]; then
		# filemode is usually printed by Git bash but may not be printed by Cygwin
		# - if repo was cloned using Git Bash:  core.filemode=false
		filemode=`echo $filemodeLine | cut --delimiter='=' --fields=2`
		#echo "repository filemode=$filemode"
		if [ "${filemode}" = "true" ] && [ "${operatingSystem}" = "cygwin" ]; then
			# Count Cygwin repos so message can be printed at the end
			cygwinRepoCount=`expr ${cygwinRepoCount} + 1`
			#echo "cygwinRepoCount=${cygwinRepoCount}"
		fi
		if [ "${operatingSystem}" = "linux" ]; then
			# No need for any special logic because no Git Bash or Cygwin
			if [ "${repoCount}" = "0" ]; then
				echo "Detected Linux operating system"
			fi
		elif [ "${operatingSystem}" = "cygwin" ] && [ "${filemode}" = "false" ]; then
			# Probably cloned using Git Bash or other Windows-centric Git client
			${echo2} "${actionWarnColor}DO NOT USE CygWin command line git with this repo (was likely NOT cloned with Cygwin, filemode=false).${colorEnd}"
		elif [ "${operatingSystem}" = "cygwin" ] && [ "${filemode}" = "true" ]; then
			# Probably cloned using Cygwin so consistent with this environment
			# A global warning is printed at the end if mixing filemodes
			echo "USE Cygwin or other filemode=true Git client with this repo (filemode=true)."
		elif [ "${operatingSystem}" = "mingw" ] && [ "${filemode}" = "true" ]; then
			# Probably cloned using Cygwin but for consistency recommend Windows-centric Git client
			echo "${actionWarnColor}USE CygWin command line git with this repo (was likely cloned with Cygwin, filemode=true).${colorEnd}"
		elif [ "${operatingSystem}" = "mingw" ] && [ "${filemode}" = "false" ]; then
			# Probably cloned using Git Bash or other Windows-centric Git client so OK
			echo "USE Git Bash or other Windows Git client with this repo (filemode=false)."
		else
			echo2 "${actionColor}Unhandled operating system ${operatingSystem} - no git client recommendations provided.${colorEnd}"
		fi
	fi
}

# Check whether any working files are different from commits in the repo
# - have to include function before it is called
# - print a message if so
# - assumes that the current folder is a Git repository of interest
# - see:  https://stackoverflow.com/questions/3882838/whats-an-easy-way-to-detect-modified-files-in-a-git-workspace
checkWorkingFiles()
{
	# The following won't work if run in Cygwin shell for non-Cygwin repo clone, or the other way
	git diff-index --quiet HEAD
	# Therefore, use the following (although this could ignore newline cleanup that needs to be committed)
	# - however, even though --quiet is specified, the following outputs a bunch of messages like:
	#   warning:  CRLF will be replaced by LF in ...
	#   The file will have its original line endings in your working directory.
	#git diff-index --ignore-cr-at-eol --quiet HEAD
	exitCode=$?
	#echo "exitCode=$exitCode"
	if [ $exitCode -eq 1 ]; then
		${echo2} "${actionColor}Working files contain modified files that need to be committed, or staged files.${colorEnd}"
	fi
	# The above won't detect untracked files but the following will find those
	# - the following will return a value of 0 or greater
	untrackedFilesCount=`git ls-files -o --directory --exclude-standard | wc -l`
	if [ ${untrackedFilesCount} -ne "0" ]; then
		${echo2} "${actionColor}Working files contain ${untrackedFilesCount} untracked files that need to be committed.${colorEnd}"
	fi
	if [ $exitCode -eq 1 -o ${untrackedFilesCount} -ne "0" ]; then
		localChangesRepoCount=`expr ${localChangesRepoCount} + 1`
	fi
}

# Function to check the status of local compared to remote repository
# - see:  https://stackoverflow.com/questions/3258243/check-if-pull-needed-in-git
# - Code from above was used as is with some additional lines for checks out output messages
checkRepoStatus()
{
	# Current branch
	currentRepo=`git branch | grep \* | cut -d ' ' -f2`
	# Repo that is the master, to which all work flows - used to check whether on a branch
	masterRepo="master"

	if [ ! "${currentRepo}" = "${masterRepo}" ]; then
		${echo2} "${actionColor}Checked out branch:  ${currentRepo}${colorEnd}"
		${echo2} "${actionColor}May need to pull remote before merging this branch.  Rerun check on master before merging this branch.${colorEnd}"
	else
		echo "Checked out branch:  ${masterRepo}"
	fi

	# Get the remote information
	git remote update
	# Start code from above StackOverflow article
	errorCount=0
	UPSTREAM=${1:-'@{u}'}
	LOCAL=$(git rev-parse @)
	if [ "$?" -ne "0" ]; then
		errorCount=`expr ${errorCount} + 1`
	fi
	REMOTE=$(git rev-parse "$UPSTREAM")
	if [ "$?" -ne "0" ]; then
		errorCount=`expr ${errorCount} + 1`
	fi
	BASE=$(git merge-base @ "$UPSTREAM")
	if [ "$?" -ne "0" ]; then
		errorCount=`expr ${errorCount} + 1`
	fi

	# There may be errors in the Git commands if working in a branch but there is no remote.
	# For example, this might be a local feature/topic branch that is checked out from master.
	if [ "${errorCount}" -ne "0" ]; then
		${echo2} "${actionColor}Error checking upstream repository.${colorEnd}"
		${echo2} "${actionColor}May be a local branch that has not been pushed to remote.${colorEnd}"
		${echo2} "${actionColor}Remote repository name may have changed.${colorEnd}"
	fi

	repoCount=`expr ${repoCount} + 1`
	if [ "$LOCAL" = "$REMOTE" ]; then
		echo "------------------"
		${echo2} "${okColor}Up-to-date${colorEnd}"
		checkWorkingFiles
		upToDateRepoCount=`expr ${upToDateRepoCount} + 1`
		echo "------------------"
	elif [ "$LOCAL" = "$BASE" ]; then
		echo "------------------"
		${echo2} "${actionColor}Need to pull${colorEnd}"
		checkWorkingFiles
		needToPullRepoCount=`expr ${needToPullRepoCount} + 1`
		echo "------------------"
	elif [ "$REMOTE" = "$BASE" ]; then
		echo "------------------"
		${echo2} "${actionColor}Need to push${colorEnd}"
		checkWorkingFiles
		needToPushRepoCount=`expr ${needToPushRepoCount} + 1`
		echo "------------------"
	else
		echo "------------------"
		${echo2} "${actionColor}Diverged${colorEnd}"
		checkWorkingFiles
		divergedRepoCount=`expr ${divergedRepoCount} + 1`
		echo "------------------"
	fi
	# End code from above StackOverflow article
}

# Parse the command parameters
parseCommandLine() {
	local OPTIND opt g h m p v
	optstring=":g:hm:p:v"
	while getopts $optstring opt; do
		#echo "Command line option is ${opt}"
		case $opt in
			g) # -g  Specify folder containing Git repositories
				gitReposFolder=$OPTARG
				;;
			h) # -h  Print the program usage
				printUsage
				exit 0
				;;
			m) # -m mainRepoName  Specify the main repository name, assumed that repository name will match folder for repository
				mainRepo=$OPTARG
				;;
			p) # -p productHome   Specify the product home, relative to $HOME, being phased out
				echo "" 
				echo "-p is obsolete.  Use -g instead." 
				exit 1
				;;
			v) # -v  Print the program version
				printVersion
				exit 0
				;;
			\?)
				echo "" 
				echo "Invalid option:  -$OPTARG" >&2
				printUsage
				exit 1
				;;
			:)
				echo "" 
				echo "Option -$OPTARG requires an argument" >&2
				printUsage
				exit 1
				;;
		esac
	done
}

# Print the script usage
# - calling code must exist with appropriate code
printUsage() {
	echo ""
	echo "Usage:  git-check.sh -m product-main-repo -g gitReposFolder"
	echo ""
	echo "Check the status of all repositories that comprise a product."
	echo ""
	echo "Example:"
	echo '  git-check.sh -m owf-util-git -g $HOME/owf-dev/Util-Git/git-repos'
	echo ""
	echo "-g specify the folder containing 1+ Git repos for product."
	echo "-h print the usage"
	echo "-m specify the main repo name."
	echo "-v print the version"
	echo ""
}

# Print the script version and copyright/license notices
# - calling code must exist with appropriate code
printVersion() {
	echo ""
	echo "git-check version ${version}"
	echo ""
	echo "Git Utilities"
	echo "Copyright 2017-2019 Open Water Foundation."
	echo ""
	echo "License GPLv3+:  GNU GPL version 3 or later"
	echo ""
	echo "There is ABSOLUTELY NO WARRANTY; for details see the"
	echo "'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file."
	echo "This is free software: you are free to change and redistribute it"
	echo "under the conditions of the GPLv3 license in the LICENSE file."
	echo ""
}

# Entry point into main script
# - call functions from above as needed

version="1.7.0 2018-12-27"

# Determine which echo to use, needs to support -e to output colored text
# - normally built-in shell echo is OK, but on Debian Linux dash is used, and it does not support -e
echo2='echo -e'
testEcho=`echo -e test`
if [ "${testEcho}" = '-e test' ]; then
	# The -e option did not work as intended.
	# -using the normal /bin/echo should work
	# -printf is also an option
	echo2='/bin/echo -e'
	# The following does not seem to work
	#echo2='printf'
fi

# Parse the command line
parseCommandLine "$@"

# Output some blank lines to make it easier to scroll back in window to see the start of output

echo ""
echo ""

# Strings to change colors on output, to make it easier to indicate when actions are needed
# - Colors in Git Bash:  https://stackoverflow.com/questions/21243172/how-to-change-rgb-colors-in-git-bash-for-windows
# - Useful info:  http://webhome.csc.uvic.ca/~sae/seng265/fall04/tips/s265s047-tips/bash-using-colors.html
# - See colors:  https://en.wikipedia.org/wiki/ANSI_escape_code#Unix-like_systems
# - Set the background to black to eensure that white background window will clearly show colors contrasting on black.
# - Yellow "33" in Linux can show as brown, see:  https://unix.stackexchange.com/questions/192660/yellow-appears-as-brown-in-konsole
# - Tried to use RGB but could not get it to work - for now live with "yellow" as it is
actionColor='\e[0;40;33m' # user needs to do something, 40=background black, 33=yellow
actionWarnColor='\e[0;40;31m' # serious issue, 40=background black, 31=red
okColor='\e[0;40;32m' # status is good, 40=background black, 32=green
colorEnd='\e[0m' # To switch back to default color

# Check the operating system
checkOperatingSystem

if [ -z "${gitReposFolder}" ]; then
	echo ""
	echo "The Git repositories folder is not specified with -g.  Exiting."
	printUsage
	exit 1
fi

# Git repsitories folder is relative to the user's files in a standard development location, for example:
# $HOME/                     User's files.
#    DevFiles/               Development files grouped by a system, product line, etc.
#      ProductHome/          Development files for a specific product.
#        git-repos/          Git repositories that comprise the product.
#          repo-name1/       Git repository folders (each containing .git, etc.)
#          repo-name2/
#          ...
#
# Main repository in a group of repositories for a product
# - this is where the product repository list file will live
mainRepoAbs="${gitReposFolder}/${mainRepo}"
# The following is a list of repositories including the main repository
# - one repo per line, no URL, just the repo name
# - repositories must have previously been cloned to local files
repoListFile="${mainRepoAbs}/build-util/product-repo-list.txt"

# Check for local folder existence and exit if not as expected
# - ensures that other logic will work as expected in folder structure

if [ ! -d "${mainRepoAbs}" ]; then
	echo ""
	echo "Main repo folder does not exist:  ${mainRepoAbs}"
	echo "Exiting."
	echo ""
	exit 1
fi
if [ ! -f "${repoListFile}" ]; then
	echo ""
	echo "Product repo list file does not exist:  ${repoListFile}"
	echo "Exiting."
	echo ""
	exit 1
fi

# Count the number of Cygwin repositories so can remind developer at the end
cygwinRepoCount=0
repoCount=0
upToDateRepoCount=0
needToPullRepoCount=0
needToPushRepoCount=0
divergedRepoCount=0
localChangesRepoCount=0

# Change folders to each repository and run the function to check that repository status
# against its upstream repository.
# - use syntax that does not use pipe so that internal variables are in same scope as main script
#   and can be processed after the loop
# - ignore comment lines starting with #
while IFS= read -r repoName
do
	# Make sure there are no carriage returns in the string
	# - can happen because file may have Windows-like endings but Git Bash is Linux-like
	#- use sed because it is more likely to be installed than dos2unix
	repoName=`echo ${repoName} | sed 's/\r$//'`
	if [ -z "${repoName}" ]; then
		# Blank line
		continue
	fi
	firstChar=`expr substr "${repoName}" 1 1` 
	if [ "${firstChar}" = "#" ]; then
		# Comment line
		continue
	fi
	# Check the status on the specific repository
	productRepoFolder="${gitReposFolder}/${repoName}"
	echo "================================================================================"
	echo "Checking status of repo:  $repoName"
	if [ ! -d "${productRepoFolder}" ]; then
		echo ""
		echo "Product repo folder does not exist:  ${productRepoFolder}"
		echo "Skipping."
		continue
	else
		# Change to repo folder (otherwise Git commands don't know what to do)
		cd ${productRepoFolder}
		checkRepoStatus
		# Check to make sure that proper Git command line tool is being used
		# - filemode=false indicates that Cygwin should not be used
		checkCommandLineGitCompatibility
	fi
#done 
done < ${repoListFile}

echo ""
echo "================================================================================"
echo "Summary of all repositories - see above for details"
# Print a message to encourage not using Cygwin to clone repositories
if [ "${operatingSystem}" != "linux" ]; then
	# On windows so make sure that Cygwin and Git Bash is not mixed
	# because can lead to confusion and technical issues
	if [ "${cygwinRepoCount}" -ne "0" ] && [ "${repoCount}" -ne "${cygwinRepoCount}" ]; then
		${echo2} "${actionColor}Number of Cygwin-cloned repos (filemode=true) is ${cygwinRepoCount}, which is not = the repo count ${repoCount}.${colorEnd}"
		${echo2} "${actionColor}Mixing Cygwin (filemode=true) and Git Bash (filemode=false) can cause issues.${colorEnd}"
	fi
fi
# Print message to alert about attention needed on any repository
# Don't need to color the number of repositories
echo "Product Git repositories folder: ${gitReposFolder}"
echo "Repository repository list file: ${repoListFile}"
echo "================================================================================"
echo "Number of repositories:                                                   ${repoCount}"
if [ "${upToDateRepoCount}" -eq "${repoCount}" ]; then
	${echo2} "Number of up-to-date repositories:                                        ${okColor}${upToDateRepoCount}${colorEnd}"
else
	${echo2} "Number of up-to-date repositories:                                        ${actionColor}${upToDateRepoCount}${colorEnd}"
fi
if [ "${needToPullRepoCount}" = "0" ]; then
	${echo2} "Number of 'need to pull' repositories (remote commits available):         ${okColor}${needToPullRepoCount}${colorEnd}"
else
	${echo2} "Number of 'need to pull' repositories (remote commits available):         ${actionColor}${needToPullRepoCount}${colorEnd}"
fi
if [ "${needToPushRepoCount}" = "0" ]; then
	${echo2} "Number of 'need to push' repositories (local commits saved):              ${okColor}${needToPushRepoCount}${colorEnd}"
else
	${echo2} "Number of 'need to push' repositories (local commits saved):              ${actionColor}${needToPushRepoCount}${colorEnd}"
fi
if [ "${divergedRepoCount}" = "0" ]; then
	${echo2} "Number of diverged repositories (need to pull and push):                  ${okColor}${divergedRepoCount}${colorEnd}"
else
	${echo2} "Number of diverged repositories (need to pull and push):                  ${actionColor}${divergedRepoCount}${colorEnd}"
fi
if [ "${localChangesRepoCount}" = "0" ]; then
	${echo2} "Number of repositories with local changes (working and/or staged files):  ${okColor}${localChangesRepoCount}${colorEnd}"
else
	${echo2} "Number of repositories with local changes (working and/or staged files):  ${actionColor}${localChangesRepoCount}${colorEnd}"
fi
echo "================================================================================"

# Done
exit 0
