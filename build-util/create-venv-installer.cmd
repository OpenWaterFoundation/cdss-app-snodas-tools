@echo off
rem
rem 2-create-venv-installer.bat
rem
rem TODO smalers 2023-07-16 THIS IS A HACKED-TOGETHER SCRIPT TO BUILD A DEPLOYABLE VENV.
rem More work is needed to turn it into a general tool to build the Windows CDSS Tools venv.
rem
rem Create the Python virtualenv (venv) installer for CDSS SNODAS Tools:
rem - this is a modified copy of the similar OWF GeoProcessor script
rem - creates the venv for Windows QGIS environment
rem - the resulting installer can be deployed to an operational environment

rem Use the following to make sure variables have expected values when parsed, such as in 'for' and complex logic.
setlocal ENABLEDELAYEDEXPANSION

rem Turn on delayed expansion so that loops work:
rem - Seems crazy but see:  https://ss64.com/nt/delayedexpansion.html
rem - Otherwise, for loops and ( ) blocks don't work because variables are not set as expected
rem - Such variables must be surrounded by ! !, rather than % %
set startingFolder=%CD%

rem Get the folder where the script is located (scriptFolder) and the repository folder (repoFolder):
rem - helpful example:  https://wiert.me/2011/08/30/batch-file-to-get-parent-directory-not-the-directory-of-the-batch-file-but-the-parent-of-that-directory/
rem - scriptFolder will have \ at the end
rem - works regardless of where the script/path is entered
set scriptName=%~nx0
set scriptFolder=%~dp0
rem Remove trailing \ from scriptFolder
set scriptFolder=%scriptFolder:~0,-1%
rem Windows ugly way of getting parent folder:
for %%d in (%scriptFolder%) do set repoFolder=%%~dpd
rem Remove trailing \ from repoFolder.
set repoFolder=%repoFolder:~0,-1%

echo scriptName=%scriptName%
echo scriptFolder=%scriptFolder%
echo repoFolder=%repoFolder%

set versionNum=1.2.0
set versionDate=2020-04-02

rem Check command line parameters.

if "%1%"=="-h" goto printUsage
if "%1%"=="/h" goto printUsage
if "%2%"=="-h" goto printUsage
if "%2%"=="/h" goto printUsage

if "%1%"=="-v" goto printVersion
if "%1%"=="/v" goto printVersion
if "%2%"=="-v" goto printVersion
if "%2%"=="/v" goto printVersion

rem If --nozip is specified, DO NOT zip the output (used with 2-update-gp-venv.bat).
set doZip=yes
if "%1%"=="--nozip" (
  echo Detected running with -nozip, will NOT create zip file.
  set doZip=no
)
if "%2%"=="--nozip" (
  echo Detected running with -nozip, will NOT create zip file.
  set doZip=no
)
if "%doZip%"=="yes" (
  echo WILL create zip file installer at the end.
)

rem Running the script with -u command line option will skip creating the
rem virtual environment and just do the update from current source files.
set doUpdateFilesOnly=no
if "%1%"=="-u" (
  echo Detected running with -u, will copy current SNODAS Tools files but not create venv.
  set doUpdateFilesOnly=yes
)
if "%2%"=="-u" (
  echo Detected running with -u, will copy current SNODAS Tools files but not create venv.
  set doUpdateFilesOnly=yes
)

rem Python type to use for virtual environment:
rem - default is to use QGIS
set venvPythonType=qgis
if "%1%"=="--python-dev" (
  echo Detected running with --python-dev, will use development environment Python for venv.
  set venvPythonType=dev
)
if "%2%"=="--python-dev" (
  echo Detected running with --python-dev, will use development environment Python for venv.
  set venvPythonType=dev
)
if "%1%"=="--python-qgis" (
  echo Detected running with --python-qgis, will use QGIS Python for venv.
  set venvPythonType=qgis
)
if "%2%"=="--python-qgis" (
  echo Detected running with --python-qgis, will use QGIS Python for venv.
  set venvPythonType=qgis
)
if "%1%"=="--python-sys" (
  echo Detected running with --python-sys, will use system [py] Python for venv.
  set venvPythonType=sys
)
if "%2%"=="--python-sys" (
  echo Detected running with --python-sys, will use system [py] Python for venv.
  set venvPythonType=sys
)

rem Virtual environment type to use for virtual environment:
rem - default is to use virtualenv
set venvType=virtualenv
if "%1%"=="--venv" (
  echo Detected running with --venv, will use 'venv' module to create venv.
  set venvType=venv
)
if "%2%"=="--venv" (
  echo Detected running with --venv, will use 'venv' module to create venv.
  set venvType=venv
)
if "%1%"=="--virtualenv" (
  echo Detected running with --virtualenv, will use 'virtualenv' module to create venv.
  set venvType=virtualenv
)
if "%2%"=="--virtualenv" (
  echo Detected running with --virtualenv, will use 'virtualenv' module to create venv.
  set venvType=virtualenv
)

rem Determine the SNODAS Tools version file that includes line similar to:  app_version = "1.1.0":
rem - extract from the version.py file using a Cygwin script
echo.
echo Determining CDSS Tools version from version.py file by running getversion.
set appTempFile=%TMP%\2-create-venv-installer.cmd.tmp

rem TODO smalers 2020-04-01 For now call a cygwin script to get the version:
rem - need to figure out a purely-bat approach but don't have time right now
rem - for now hard code to only work if run standard SNODAS Tools development environment,
rem   for example:  C:\Users\user\cdsss-dev\CDSS-SNODAS-Tools\git-repos\cdss-app-snodas-tools
rem Use the following to confirm file locations:
rem - issue, cygwin /home is not /cygdrive/C/Users
rem TODO smalers 2023-07-16 hard-code these for now but need to have a way specify on command line and do cross checks.
rem - CDSS Tools version should be determined dynamically from the current source files
set appVersion=2.1.0
set qgisTargetVersion=3.22.16
set pythonVersion=39
C:\cygwin64\bin\bash --login -c "echo HOME=$HOME"
C:\cygwin64\bin\bash --login -c "echo USER=$USER"
C:\cygwin64\bin\bash --login -c "echo $(pwd)"
rem set C:\cygwin64\bin\bash --login -c "/cygdrive/C/Users/%USERNAME%/cdss-dev/CDSS-SNODAS-Tools/git-repos/cdss-app-snodas-gools/scripts/getversion" > %appTempFile%
rem set /p appVersion=<%appTempFile%

rem Must query the parts of the version because the full version is created from parts at runtime.
rem The following will result in quoted version such as: "1.2.0dev"
rem findstr /b app_version_major %scriptFolder%\..\geoprocessor\app\version.py > %appTempFile%
rem set /p versionMajor=<%appTempFile%
rem findstr /b app_version_minor %scriptFolder%\..\geoprocessor\app\version.py > %appTempFile%
rem set /p versionMinor=<%appTempFile%
rem findstr /b app_version_micro %scriptFolder%\..\geoprocessor\app\version.py > %appTempFile%
rem set /p versionMicro=<%appTempFile%
rem findstr /b app_version_mod %scriptFolder%\..\geoprocessor\app\version.py > %appTempFile%
rem set /p versionMod=<%appTempFile%
rem set versionFullLine=%versionMajor%.%versionMinor%.%versionMicro%.%versionMod%
rem if "%versionMod%"=="" set versionFullLine=%versionMajor%.%versionMinor%.%versionMicro%

rem echo versionFullLine=%versionFullLine%
rem rem Remove the leading app_version
rem set versionQuoted=%versionFullLine:app_version =%
rem set appVersion=%versionQuoted:~3,-1%
echo.
echo SNODAS Tools version determined to be:  %appVersion%

rem Do some checks here to make sure that valid version information is specified.
if "%appVersion%"=="unknown" (
  echo.
  echo SNODAS Tools version is unknown.  Cannot create installer.
  goto exit1
)
if "!qgisTargetVersion!"=="unknown" (
  echo.
  echo QGIS target version is unknown.  Cannot create installer.
  goto exit1
)
if "%pythonVersion%"=="unknown" (
  echo.
  echo Python version is unknown.  Cannot create installer.
  goto exit1
)

rem Set the folders for builds
rem   appVenvTmpFolder = general work folder for builds, under which versioned builds will be created (... venv-tmp)
rem     appVenvFolderShort = SNODAS Tools installer file name (no leading path, like: snodastools-1.3.0-win-qgis-3.10-venv)
rem     appVenvFolder = full path to folder for specific installer venv (... venv-tmp/snodastools-1.3.0-win-qgis-3.10-venv)
rem       appVenvSitePackagesFolder = path to venv 'Lib\site-packages' folder
rem     appVenvZipFileShort = name of installer zip file without leading path (like: snodastools-1.3.0-win-qgis-3.10-venv.zip)
rem     appQgisVersionFile = filename used to store QGIS version for installer
rem
rem   devVenvFolder = path to development venv (like:  ... venv/venv-qgis-3.10-python39)
rem     devPythonExe = path to development venv exe (like:  venv/venv-qgis-3.10-python39/Scripts/python.exe)
rem   appSrcFolder = path to source snodastools Python files (will be copied into venv 'Lib/site-packages' folder)
rem   scriptsFolder = path to source scripts files (will be copied into venv 'Scripts' folder)
rem
rem   qgisFolder = location where QGIS is installed (like:  C:\Program Files\QGIS 3.10)
rem   qgisPythonFolder = location of QGIS Python for venv base interpreter (like:  C:\Program Files\QGIS 3.10\apps\Python39)
rem   qgisPythonExe = location of QGIS Python executable for venv base interpreter (like:  C:\Program Files\QGIS 3.10\apps\Python39\python.exe)

rem -- venv being created --
set appVenvTmpFolder=%scriptFolder%\venv-tmp
rem Old-style venv folder name did not have QGIS version
rem New-style venv folder includes QGIS version, which can be used to determine the Python version
rem set appVenvFolderShort=snodastools-%appVersion%-win-qgis-%qgisTargetVersion%-venv
set appName=snodastools
set appVenvFolderShort=%appName%-%appVersion%-win-qgis-%qgisTargetVersion%-venv
set appVenvFolder=%appVenvTmpFolder%\%appVenvFolderShort%
set appVenvSitePackagesFolder=%appVenvFolder%\Lib\site-packages
set appVenvZipFileShort=snodastools-%appVersion%-win-qgis-%qgisTargetVersion%-venv.zip
set appVenvCreationLogFile=%appVenvFolder%\venv-creation.log
set appVenvCreationLogFile0=%appVenvTmpFolder%\venv-creation.log
rem -- source files to copy into venv, and Python used to run 'virtualenv' and 'venv' --
set appSrcFolder=%repoFolder%\src\snodastools
set scriptsFolder=%repoFolder%\scripts
set appQgisVersionFileWithPath=%appVenvFolder%\SNODAS-Tools-QGIS-Version.txt
set readmeWithPath=%repoFolder%\resources\runtime\README.txt
set licenseWithPath=%repoFolder%\LICENSE.md
set devVenvFolder=%repoFolder%\venv\venv-qgis-%qgisTargetVersion%-python%pythonVersion%
set devPythonExe=%devVenvFolder%\Scripts\python.exe
rem -- QGIS files for base Python interpreter --
set qgisFolder=C:\Program Files\QGIS %qgisTargetVersion%
set qgisPythonFolder=%qgisFolder%\apps\Python39
set qgisPythonExe=%qgisFolder%\apps\Python39\python.exe

echo.
echo Controlling configuration properties:
echo -- version information --
echo appVersion=%appVersion%
echo qgisTargetVersion=%qgisTargetVersion%
echo pythonVersion=%pythonVersion%
echo -- venv being created --
echo appVenvTmpFolder=%appVenvTmpFolder%
echo appVenvFolderShort=%appVenvFolderShort%
echo appVenvFolder=%appVenvFolder%
echo appVenvSitePackagesFolder=%appVenvSitePackagesFolder%
echo appVenvZipFileShort=%appVenvZipFileShort%
echo appVenvCreationLogFile=%appVenvCreationLogFile%
echo appVenvCreationLogFile0=%appVenvCreationLogFile0%
echo -- source files to copy into venv, and Python used to run 'virtualenv' and 'venv' --
echo appSrcFolder=%appSrcFolder%
echo scriptsFolder=%scriptsFolder%
echo appQgisVersionFileWithPath=%appQgisVersionFileWithPath%
echo readmeWithPath=%readmeWithPath%
echo licenseWithPath=%licenseWithPath%
echo devVenvFolder=%devVenvFolder%
echo devPythonExe=%devPythonExe%
echo -- QGIS files for base Python interpreter --
echo qgisFolder=%qgisFolder%
echo qgisPythonFolder=%qgisPythonFolder%
echo qgisPythonExe=%qgisPythonExe%
echo.
rem Prompt is different whether -u was specified on command line
if "%doUpdateFilesOnly%"=="yes" (
  set /p answer2="Continue updating existing venv [y/q]? "
) else (
  set /p answer2="Continue creating new venv [y/q]? "
)
if not "%answer2%"=="y" (
  goto exit0
)

rem Running the script with -u command line option will skip creating the
rem virtual environment and just do the update from current source files.
if "%doUpdateFilesOnly%"=="yes" (
  echo Running with -u, skipping to file copy but not creating venv
  goto copyGeoProcessorFiles
)

rem Create the version-specific virtual environment folder.
if exist "%appVenvFolder%" goto deleteappVenvFolder
goto createappVenv

:deleteappVenvFolder

rem Delete the existing virtual environment folder.
echo.
echo Deleting old installer venv folder:  %appVenvFolder%
set /p answer="Delete old installer venv folder and continue [y/q]? "
if not "%answer%"=="y" (
  goto exit0
)
rmdir /s/q %appVenvFolder%
goto createappVenv

:createappVenvFolder

rem Create the new virtual environment folder:
rem - not needed, delete when test out
echo.
echo Creating new venv folder:  %appVenvFolder%
mkdir %appVenvFolder%

:createappVenv

rem Initialize a virtual environment by using a combination that works:
rem - TODO smalers 2020-04-02 for some reason, this has been an issue of late so add batch file options to test
rem - maybe it was because the batch file was using virtualenv rather than venv?

if "!venvType!"=="venv" (
  goto doVenv
) else (
    if "!venvType!"=="virtualenv" (
      goto doVirtualenv
    ) else (
        echo.
        echo Virtual environment type '!venvType!' is not recognized.  Exiting.
        goto exit1
      )
  )

:doVenv

echo.
echo Use venv to create the virtual environment.
rem   Which Python type:
rem      Dev = PyCharm development venv (Scripts\python.exe)
rem      Qgis = standalone QGIS (*:\Program Files\QGIS 3.10\aps\Python39\python.exe)
rem      User = User-installed Python (typically AppData...Scripts\python.exe)
rem
rem For logging, have to log to an initial log file and because the receiving folder does not exist.
rem Then copy this initial log below and continue writing to it.
echo The following major steps were used to create the initial Python virtual environment.>"%appVenvCreationLogFile0%"
echo Subsequent changes to the virtual environment are not recorded here.>>"%appVenvCreationLogFile0%"
echo Using virtual environment type:  %venvType%
echo Using virtual environment type:  %venvType%>>"%appVenvCreationLogFile0%"
echo Using virtual environment python type:  %venvPythonType%
echo Using virtual environment python type:  %venvPythonType%>>"%appVenvCreationLogFile0%"
if "!venvPythonType!"=="dev" (
  rem TODO smalers 2020-04-01 Use the development environment Python.
  echo Creating virtual environment using development environment Python:  %devPythonExe%
  echo Creating virtual environment using development environment Python:  %devPythonExe%>>"%appVenvCreationLogFile0%"
  echo.
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%>>"%appVenvCreationLogFile0%"
  if not exist "%devPythonExe%" goto noDevPythonExe
  "%devPythonExe%" -m venv "%appVenvFolder%"
  rem Run Dev Python.
  rem Update the creation log so know how the venv was created.
  echo "%devPythonExe%" -m venv "%appVenvFolder%">>"%appVenvCreationLogFile0%"
) else (
    if "!venvPythonType!"=="qgis" (
      rem TODO smalers 2020-04-01 Use the development environment Python.
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%>>"%appVenvCreationLogFile0%"
      echo.
      echo Checking for existence of QGIS Python:  %qgisPythonExe%
      echo Checking for existence of QGIS Python:  %qgisPythonExe%>>"%appVenvCreationLogFile0%"
      if not exist "%qgisPythonExe%" goto noQgisPythonExe

      "%qgisPythonExe%" -m venv "%appVenvFolder%"
      rem Run Dev Python.
      rem Update the creation log so know how the venv was created.
      echo "%qgisPythonExe%" -m venv "%appVenvFolder%">>"%appVenvCreationLogFile0%"
    ) else (
        if "!venvPythonType!"=="sys" (
          set pythonDotVersion=3.7
          rem Not needed.
          rem set userPythonExe=%USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe
          echo Creating virtual environment using system 'py' Python.
          echo Creating virtual environment using system 'py' Python>>"%appVenvCreationLogFile0%"

          rem Use a user Python for base interpreter, which will be used to install additional packages.
          echo py -!pythonDotVersion! -m venv "%appVenvFolder%"
          echo py -!pythonDotVersion! -m venv "%appVenvFolder%">>"%appVenvCreationLogFile0%"
          py -!pythonDotVersion! -m venv "%appVenvFolder%"
        ) else (
            rem Fall through case that is not handled.
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.>>"%appVenvCreationLogFile0%"
            goto exit1
          )
      )
  )
echo Done creating Python venv using 'venv' module.
echo Done creating Python venv using 'venv' module.>>"%appVenvCreationLogFile0%"
goto copyGeoProcessorFiles

:doVirtualenv

rem Use virtualenv to create the virtual environment.
echo.
rem   Which Python type:
rem      Dev = PyCharm development venv (Scripts\python.exe)
rem      Qgis = standalone QGIS (*:\Program Files\QGIS 3.10\aps\Python39\python.exe)
rem      User = User-installed Python (typically AppData...Scripts\python.exe)
rem
rem For logging, have to log to an initial log file and because the receiving folder does not exist.
rem Then copy this initial log below and continue writing to it.
echo The following major steps were used to create the initial Python virtual environment.>"%appVenvCreationLogFile0%"
echo Subsequent changes to the virtual environment are not recorded here.>>"%appVenvCreationLogFile0%"
echo Using virtual environment type:  %venvType%
echo Using virtual environment type:  %venvType%>>"%appVenvCreationLogFile0%"
echo Using virtual environment python type:  %venvPythonType%
echo Using virtual environment python type:  %venvPythonType%>>"%appVenvCreationLogFile0%"
if "!venvPythonType!"=="dev" (
  rem TODO smalers 2020-04-01 Use the development environment Python.
  echo Creating virtual environment using development environment Python:  %devPythonExe%
  echo Creating virtual environment using development environment Python:  %devPythonExe%>>"%appVenvCreationLogFile0%"
  echo.
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%>>"%appVenvCreationLogFile0%"
  if not exist "%devPythonExe%" goto noDevPythonExe
  echo "%devPythonExe%" -m virtualenv "%appVenvFolder%"
  "%devPythonExe%" -m virtualenv "%appVenvFolder%"
  rem Run Dev Python.
  rem Update the creation log so know how the venv was created.
  echo "%devPythonExe%" -m virtualenv "%appVenvFolder%">>"%appVenvCreationLogFile0%"
) else (
    if "!venvPythonType!"=="qgis" (
      rem TODO smalers 2020-04-01 Use the development environment Python.
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%>>"%appVenvCreationLogFile0%"

      echo.
      echo Checking for existence of QGIS Python:  %qgisPythonExe%
      if not exist "%qgisPythonExe%" goto noQgisPythonExe
      echo "%qgisPythonExe%" -m virtualenv "%appVenvFolder%"
      "%qgisPythonExe%" -m virtualenv "%appVenvFolder%"
      rem Run Dev Python.
      rem Update the creation log so know how the venv was created.
      echo "%qgisPythonExe%" -m virtualenv "%appVenvFolder%">>"%appVenvCreationLogFile0%"
    ) else (
        if "!venvPythonType!"=="sys" (
          set pythonDotVersion=3.9
          rem Not needed.
          rem set userPythonExe=%USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe
          echo Creating virtual environment using system 'py' Python.
          echo Creating virtual environment using system 'py' Python>>"%appVenvCreationLogFile0%"

          rem Use a user Python for base interpreter, which will be used to install additional packages.
          echo py -!pythonDotVersion! -m virtualenv "%appVenvFolder%"
          echo py -!pythonDotVersion! -m virtualenv "%appVenvFolder%">>"%appVenvCreationLogFile0%"
          py -!pythonDotVersion! -m virtualenv "%appVenvFolder%"
        ) else (
            rem Fall through case that is not handled.
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.>>"%appVenvCreationLogFile0%"
            goto exit1
          )
      )
  )
echo Done creating Python venv using 'virtualenv' module.
echo Done creating Python venv using 'virtualenv' module.>>"%appVenvCreationLogFile0%"
rem goto copyGeoProcessorFiles

:copyGeoProcessorFiles

rem Copy the geoprocessor package files:
rem - the `geoprocessor` folder is copied into the `Lib/site-packages` folder that was created above
rem - do not use * on source because the destination folder does not exist
rem - do this before running pip for additional packages so that the printenv.py script can be run within
rem   activated venv environment

rem Above log messages could not write the venv folder because it did not exist.
rem Now, copy the initial log into the venv and then append to the final log file.
copy "%appVenvCreationLogFile0%" "%appVenvCreationLogFile%"

echo.
echo Copying SNODAS Tools development files to venv.
echo Copying SNODAS Tools development files to venv.>>"%appVenvCreationLogFile%"
echo Copying %appSrcFolder% to %appVenvSitePackagesFolder%\snodastools
echo Copying %appSrcFolder% to %appVenvSitePackagesFolder%\snodastools>>"%appVenvCreationLogFile%"
echo robocopy %appSrcFolder% %appVenvSitePackagesFolder%\snodastools /E
echo robocopy %appSrcFolder% %appVenvSitePackagesFolder%\snodastools /E>>"%appVenvCreationLogFile%"
robocopy %appSrcFolder% %appVenvSitePackagesFolder%\snodastools /E

rem Copy the scripts files:
rem - the `Scripts` folder contents is copied into the `Scripts` folder that was created above
rem - copy specific Windows scripts, could be more precise but get it working
echo.
echo Copying CDSS Tools script files from %ScriptsFolder% to %appVenvFolder%\Scripts
echo Copying CDSS Tools script files  from %ScriptsFolder% to %appVenvFolder%\Scripts>>"%appVenvCreationLogFile%"
copy %scriptsFolder%\daily_interactive.bat %appVenvFolder%\Scripts
copy %scriptsFolder%\python-qgis-ltr.bat %appVenvFolder%\Scripts

rem Create the file that contains the QGIS version.
echo Creating version info file:  %appQgisVersionFileWithPath%
echo Creating version info file:  %appQgisVersionFileWithPath%>>"%appVenvCreationLogFile%"
echo # This file is created by the CDSS Tools installer build batch file - DO NOT EDIT THIS FILE.> %appQgisVersionFileWithPath%
echo #>> %appQgisVersionFileWithPath%
echo # This file indicates the stand-alone QGIS version that was used to build the CDSS Tools installer.>> %appQgisVersionFileWithPath%
echo # The CDSS Tools QGIS version should agree with the stand-alone QGIS this is available.>> %appQgisVersionFileWithPath%
rem echo # The gp.bat batch files will check for this file in order to ensure that the runtime environment is correct.>> %appQgisVersionFileWithPath%
echo # The version is the Major.Minor version corresponding to QGIS "C:\Program Files\QGIS Major.Minor" folder.>> %appQgisVersionFileWithPath%
echo #>> %appQgisVersionFileWithPath%
echo %qgisTargetVersion%>> %appQgisVersionFileWithPath%

rem Copy the README file into the main venv folder.
echo Copying the main README file: %readmeWithPath%
echo Copying the main README file: %readmeWithPath%>>"%appVenvCreationLogFile%"
copy %readmeWithPath% %appVenvFolder%

rem Copy the LICENSE file into the main venv folder.
echo Copying the LICENSE file: %licenseWithPath%
echo Copying the LICENSE file: %licenseWithPath%>>"%appVenvCreationLogFile%"
copy %licenseWithPath% %appVenvFolder%

if "%doUpdateFilesOnly%"=="yes" (
  goto finalMessage
)

:installAdditionalPackages

rem Change into the virtual environment, activate, and install additional packages:
rem - Note that the venv (and virtualenv) packages 'activate' and 'deactivate' have hard-coded
rem   lines to the path where the venv was originally created by this batch file.
rem   It needs to be changed in the operational environment if the venv is to be activated,
rem   but this NOT NEEDED to run the SNODAS Tools.
rem   PYTHONHOME and PYTHONPATH.
echo Changing to folder %appVenvFolder%
echo Changing to folder %appVenvFolder%>>"%appVenvCreationLogFile%"
cd "%appVenvFolder%"
echo Activating the virtual environment
echo Activating the virtual environment>>"%appVenvCreationLogFile%"
if not exist "Scripts\activate.bat" goto missingActivateScriptError
call Scripts\activate.bat
rem Make sure that SSL libraries are available to allow pip to work:
rem - they seem to not be automatically created in a new venv
rem - they exist in the development venv because pip required for additional packages
rem - seems like these live in DLLs folder in Widows Python but virtualenv does not have
rem - the dlls are removed later because they break the run-time distribution
rem - see clues:  https://github.com/numpy/numpy/issues/12667
set repoCryptoLib=%repoFolder%\resources\installer\win\ssl\libcrypto-1_1-x64.dll
set repoSslLib=%repoFolder%\resources\installer\win\ssl\libssl-1_1-x64.dll
set venvCryptoLib=%appVenvFolder%\Scripts\libcrypto-1_1-x64.dll
set venvSslLib=%appVenvFolder%\Scripts\libssl-1_1-x64.dll
if not exist "%appVenvFolder%\Scripts\libcrypto-1_1-x64.dll" (
  echo Copying libcrypto-1_1-x64.dll from dev to new venv so pip SSL/TLS will work: %repoCryptoLib%
  echo Copying libcrypto-1_1-x64.dll from dev to new venv so pip SSL/TLS will work>>"%appVenvCreationLogFile%"
  copy "%repoCryptoLib%" "%appVenvFolder%\Scripts"
  echo copy "%repoCryptoLib%" "%appVenvFolder%\Scripts">>"%appVenvCreationLogFile%"
)
if not exist "%appVenvFolder%\Scripts\libssl-1_1-x64.dll" (
  echo Copying libssl-1_1-x64.dll from dev to new venv so pip SSL/TLS will work: %repoSslLib%
  echo Copying libssl-1_1-x64.dll from dev to new venv so pip SSL/TLS will work>>"%appVenvCreationLogFile%"
  copy "%repoSslLib%" "%appVenvFolder%\Scripts"
  echo copy "%repoSslLib%" "%appVenvFolder%\Scripts">>"%appVenvCreationLogFile%"
)
rem The following use generic Python name (not py) because
rem the virtual environment uses the name generically.
echo Installing necessary Python packages in venv for deployed environment
echo - these are the same as documented in CDSS Tools new developer Python install
echo - pip packages include: pandas, openpyxl, requests[security], SQLAlchemy
echo Installing necessary Python packages in venv for deployed environment>>"%appVenvCreationLogFile%"
echo - these are the same as documented in CDSS Tools new developer Python install>>"%appVenvCreationLogFile%"
echo - pip packages include: pandas, openpyxl, requests[security], SQLAlchemy>>"%appVenvCreationLogFile%"
rem TODO smalers 2023-07-16 these are not needed by SNODAS Tools
rem pip3 install pandas
rem pip3 install openpyxl
rem pip3 install requests[security]
rem pip3 install SQLAlchemy

rem Run the Python script to print the environment, to confirm the venv environment used for pip installs.
rem echo Environment within activated venv:
rem python "%appVenvFolder%\Lib\site-packages\snodastools\app\printenv.py"

rem Deactivate the virtual environment.
echo Deactivating the virtual environment
echo Deactivating the virtual environment>>"%appVenvCreationLogFile%"
call Scripts\deactivate.bat

:removeDlls

rem The dlls, if left in the Scripts folder, interfere with QGIS Python.
if exist "!venvCryptoLib!" (
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvCryptoLib!
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvCryptoLib!>>"%appVenvCreationLogFile%"
  del "!venvCryptoLib!"
)
if exist "!venvSslLib!" (
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvSslLib!
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvSslLib!>>"%appVenvCreationLogFile%"
  del "!venvSslLib!"
)

rem Skip zipping if -z was specified on the command line.
if "!doZip!"=="no" goto skipZip
rem Zip the files:
rem - use 7zip.exe
echo.
echo Zipping the venv distribution...
echo Zipping the venv distribution...>>"%appVenvCreationLogFile%"
set sevenZipExe=C:\Program Files\7-Zip\7z.exe
if exist "%sevenZipExe%" goto zipVenv
goto noSevenZip

:zipVenv

rem Zip the virtual environment folder:
rem - change to the venv-tmp folder so zip will be relative
rem - also use filenames with no path to avoid issues with spaces in full path
echo.
echo Changing to folder %appVenvTmpFolder%
cd "%appVenvTmpFolder%"
rem Remove the old zip file if it exists.
if exist %appVenvZipFileShort% (
  echo Deleting existing zip file:  %appVenvZipFileShort%
  del /s/q %appVenvZipFileShort%
)
rem Now create the new venv zip file.
echo Zipping up the virtual environment folder %appVenvFolderShort% to create zip file %appVenvZipFileShort%
"%sevenZipExe%" a -tzip %appVenvZipFileShort% %appVenvFolderShort%
rem Change back to script folder.
cd "%startingFolder%"
echo.
echo Created zip file for deployment: %appVenvTmpFolder%\%appVenvZipFileShort%
goto finalMessage

:skipZip

echo.
echo Skipping zip file creation because -z option specified.
goto finalMessage

:finalMessage

if "%doUpdateFilesOnly%"=="yes" (
  echo Since running !scriptName! -u:
  echo - Run gpui.bat in the virtual environment folder to run the GeoProcessor UI prior to deployment
  echo     %appVenvFolder%
  echo - When ready, run 2-create-gp-venv.bat to fully create virtual environment and installer zip file for deployment.
) else (
  echo - Rerun 2-create-gp-venv.bat to fully create virtual environment and installer zip file for deployment.
)
echo - Run 3-copy-gp-to-amazon-s3.sh in Cygwin to upload the Windows and Cygwin installers to public cloud.
goto exit0

rem Below here are targets that perform single actions and then exit.

rem Error due to missing Scripts\activate.bat script.
:missingActivateScriptError
echo.
echo "Missing %appVenvFolder%\Scripts\activate.bat"
rem Change back to script folder>
cd "%startingFolder%"
goto exit1

rem No python.exe to create the virtual environment.
rem:noPythonForVenv
:noDevPythonExe
echo.
rem echo No development environment venv python.exe was found to initialize the virtual environment.
echo No python.exe was found to create new venv, expecting:  %devPythonExe%
rem Change back to script folder.
cd "%startingFolder%"
goto exit1

rem No QGIS python.exe for venv base interpreter.
:noQgisPythonExe
echo.
rem echo No QGIS python.exe was found to initialize the virtual environment.
echo No QGIS Python was found for new venv base interpreter, expecting:  %qgisPythonExe%
rem Change back to script folder.
cd "%startingFolder%"
goto exit1

:noSevenZip
rem No 7zip software.
echo.
echo No %sevenZipExe% was found to zip the virtual environment
rem Change back to script folder.
cd "%startingFolder%"
goto exit1

:printUsage
rem Print the program usage.
echo.
echo Usage:  %scriptName% [options]
echo.
echo Create or update a staging Python virtual environment [venv] for CDSS SNODAS Tools
echo The versioned staging virtual environment is created in 'build-util/venv-tmp'
echo for the current development environment configuration.
echo The default is to create a zip file to distribute on Windows.
echo Run periodically with -u to update the staging venv with latest development files.
echo Run with defaults to create the staging venv from the current development files.
echo Prompts will be displayed to confirm important actions.
echo.
echo -h, /h            Print usage of this %scriptName% batch file.
echo -u, /u            Only copy files from development venv to the
echo                   existing staging venv.  Do not initialize venv or create zip file.
echo -v, /v            Print version of this %scriptName% batch file.
echo --nozip, /nozi    DO NOT create the zip file (default is to create).
echo --python-dev      Use the development environment Python for the venv. 
echo --python-qgis     Use the QGIS Python for the venv (default).
echo --python-sys      Use the system Python (py) for the venv.
echo --venv            Use the venv module to create the virtual environment.
echo --virtualenv      Use the virtualenv module to create the virtual environment (default).
echo.
rem Don't call exit0 since no need to go to starting folder.
exit /b 0

:printVersion
rem Print the program version.
echo.
echo %scriptName% version: %versionNum% %versionDate%
echo.
rem Don't call exit0 since no need to go to starting folder.
exit /b 0

:exit0
rem Exit with normal (0) exit code:
rem - put this at the end of the batch file
echo Changing back to starting folder %startingFolder%
echo Success.  Exiting with status 0.
cd "%startingFolder%"
exit /b 0

:exit1
rem Exit with general error (1) exit code:
rem - put this at the end of the batch file
echo Changing back to starting folder %startingFolder%
echo Error.  An error of some type occurred [see previous messages].  Exiting with status 1.
cd "%startingFolder%"
exit /b 1
