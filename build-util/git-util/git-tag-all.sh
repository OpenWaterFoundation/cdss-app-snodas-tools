#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
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
# git-tag-all.sh
#
# Tag all repositories
# - interactively prompt for the tag ID and commit message

# Supporting functions, alphabetized

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

# Parse the command parameters
parseCommandLine() {
	local OPTIND g h m N v V
	optstring=":g:hm:N:vV:"
	while getopts $optstring opt; do
		#echo "Command line option is ${opt}"
		case $opt in
			g) # -g gitRepoFolder  Folder containing Git repositories
				gitReposFolder=$OPTARG
				;;
			h) # -h  Print usage
				printUsage
				exit 0
				;;
			m) # -m mainRepoName   Main repo name
				mainRepo=$OPTARG
				;;
			N) # -N productName   Specify product name, used as hint for tag name and commit message
				productName=$OPTARG
				;;
			v) # -v  Print the version
				printVersion
				exit 0
				;;
			V) # -V productVersion  Specify product version, used as hint for tag name and commit message
				productVersion=$OPTARG
				;;
			\?)
				echo "Invalid option:  -$OPTARG" >&2
				exit 1
				;;
			:)
				echo "Option -$OPTARG requires an argument" >&2
				exit 1
				;;
		esac
	done
}

# Print the script usage
printUsage() {
	echo ""
	echo "Usage:  git-tag-all.sh -m productMainRepo -g gitReposFolder -N productName -V productVersion"
	echo ""
	echo "Tag all repositories in a product with tag name and commit message."
	echo ""
	echo "Example:"
	echo "    git-tag-all.sh -m owf-git-util -g $HOME/owf-dev/Util-Git/git-repos -N GitUtil -V 1.0.0"
	echo ""
	echo "-g reposFolder       Specify the folder containing 1+ Git repos for product."
	echo "-h                   Print the usage."
	echo "-m mainRepoName      Specify the main repository name (should match repo folder name)."
	echo "-N productName       Specify the product name used for tag name and commit message hint."
	echo "-v                   Print the version."
	echo "-V productVersion    Specify the product version (e.g., 1.0.0) used for tag name and commit message hint."
	echo ""
}

# Print the script version
printVersion() {
	echo ""
	echo "git-tag-all version ${version}"
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

# Main script entry point

# Variables
dryRun=false # Default is to run operationally
#dryRun=true  # for testing
if [ "$dryRun" = "true" ]; then
	echo ""
	echo "Running in dry run mode."
fi

version="1.0.0 2018-12-27"
# Product version passed in with -V
productVersion=""

# Parse the command line
parseCommandLine "$@"

# Check input
if [ -z "${gitReposFolder}" ]; then
	echo ""
	echo "The Git repositories folder has not been specified with -g.  Exiting."
	printUsage
	exit 1
fi
if [ -z "${productName}" ]; then
	echo ""
	echo "The product name has not been specified with -N.  Exiting."
	printUsage
	exit 1
fi
if [ -z "${productVersion}" ]; then
	echo ""
	echo "The product version has not been specified with -V.  Exiting."
	printUsage
	exit 1
fi

# Git repositories folder is relative to the user's files in a standard development location, for example:
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

# Ask the user for the tag name and commit message
while [ "1" = "1" ]
do
	echo ""
	echo "Product version: ${productVersion}"
	read -p "Enter tag name with no spaces (e.g.: ${productName}-${productVersion}): " tagName
	read -p "Enter commit message (e.g,: ${productName} ${productVersion} release): " tagMessage
	echo ""
	echo "Tag name=${tagName}"
	echo "Commit message=${tagMessage}"
	read -p "Continue with tag commit [y/n]?: " answer
	if [ "${answer}" = "y" ]
	then
		# Want to continue
		break
	else
		# Don't want to continue
		exit 0
	fi
done

# Make sure that the tag name and message are specified
if [ -z "${tagName}" ]
then
	echo "Tag name must be specified.  Exiting."
	exit 1
fi
if [ -z "${tagMessage}" ]
then
	echo "Tag commit message must be specified.  Exiting."
	exit 1
fi

# Commit the tag on each repository in the product
# - read the repository name from each line of the repository list file
while IFS= read -r repoName
do
	# Make sure there are no carriage returns in the string
	# - can happen because file may have Windows-like endings but Git Bash is Linux-like
	# - use sed because it is more likely to be installed than dos2unix
	repoName=`echo ${repoName} | sed 's/\r$//'`
	if [ -z "${repoName}" ]
	then
		# Blank line
		continue
	fi
	firstChar=`expr substr "${repoName}" 1 1` 
	if [ "${firstChar}" = "#" ]
	then
		# Comment line
		continue
	fi
	# Commit the tag
	repoFolder="${gitReposFolder}/${repoName}"
	echo "================================================================================"
	echo "Committing tag for repo:  ${repoName}"
	echo "Repository folder:  ${repoFolder}"
	if [ -d "${repoFolder}" ]
	then
		# The repository folder exists so cd to it and do the tag
		cd "${repoFolder}"
		if [ ${dryRun} = "true" ]
		then
			echo "Dry run:  Adding tag with:  git tag -a \"${tagName}\" -m \"${tagMessage}\""
			echo "Dry run:  git push origin --tags"
		else
			echo "Adding tag with:  git tag -a \"${tagName}\" -m \"${tagMessage}\""
			git tag -a "${tagName}" -m "${tagMessage}"
			git push origin --tags
		fi
	else
		# Git repository folder does not exist so skip
		echo "Repository folder does not exist.  Skipping"
		continue
	fi
done < ${repoListFile}

exit 0
