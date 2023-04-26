@echo off
rem
rem Batch file to set the environment for and run PyCharm consistent with QGIS 3 environment:
rem - this is a modified version of the OWF GeoProcessor run script
rem - comment out the first line to echo statements
rem - use QGIS Python and libraries
rem - start PyCharm with the configured venv environment (that was created using the QGIS Python)
rem - the QGIS version to be used must be specified so that proper configuration is used
rem - running the OsGEO environment is currently disabled, only the standalone QGIS installation is enabled
rem   (if need to enable compare the logic if this script with gpdev.bat script)
rem - the focus is on the ":runStandaloneQGIS" and later code

rem Turn on delayed expansion so that loops work:
rem - seems crazy but see:  https://ss64.com/nt/delayedexpansion.html
rem - otherwise, for loops and ( ) blocks don't work because variables are not set as expected
rem - such variables must be surrounded by ! !, rather than % %
setlocal EnableDelayedExpansion

rem The following seems to be relevant.
rem See:  http://spatialgalaxy.com/2014/10/09/a-quick-guide-to-getting-started-with-pyqgis-on-windows/
rem The following provides useful background but seems incomplete.
rem See:  http://planet.qgis.org/planet/tag/pycharm/

rem The two main logic blocks start at:
rem   :runOsgeoQgis
rem   :runStandaloneQgis

rem This batch file version can be different from the GeoProcessor Python version:
rem - this version is just used to help track changes to this batch file
set pycharmBatVersion=1.2.0
set pycharmBatVersionDate=2023-03-05

rem Get the current folder, used to specify the path to the project.
set scriptFolder=%~dp0
rem Remove trailing \ from 'scriptFolder'.
set scriptFolder=%scriptFolder:~0,-1%
set scriptName=%~nx0
rem Have to get parent folder using Windows for loop approach:
rem - use 'installFolder' instead of 'repoFolder' so the naming works in the deployed environment
for %%i in (%scriptFolder%) do set installFolder=%%~dpi
rem Remove trailing \ from 'installFolder'.
set installFolder=%installFolder:~0,-1%
rem As of 2023-03-04 the code is located in the 'src' folder under the install folder.
set srcFolder=%installFolder%\src

echo [INFO]
echo [INFO] Startup information:
echo [INFO]   Batch file name is:
echo [INFO]     %scriptName%
echo [INFO]   %scriptName% is located in folder:
echo [INFO]     %scriptFolder%
echo [INFO]   SNODAS Tools development project is located in folder:
echo [INFO]     %installFolder%
echo [INFO]   SNODAS Tools source code is located in folder:
echo [INFO]     %srcFolder%

rem Set the absolute path to PyCharm program:
rem - check the newest first
rem - this assumes that the developer is using the newest version installed for development
rem - include editions that have been specifically used by Open Water Foundation for SNODAS Tools development
rem - currently only support PyCharm installed on C: but could check drives similar to other parts of this script
echo [INFO]
echo [INFO] Determining PyCharm to run.
for %%P in (2022.2.3 2019.3.1 2018.2.6 2018.2.4 2018.1.3) do (
  echo [INFO]   Checking for PyCharm version: %%P
  if exist "C:\Program Files\JetBrains\PyCharm Community Edition %%P\bin\pycharm64.exe" (
    echo [INFO]   Using PyCharm version: %%P
    rem Surround with double quotes when used due to the space.
    set pycharmExe=C:\Program Files\JetBrains\PyCharm Community Edition %%P\bin\pycharm64.exe
    goto pyCharmExists
  )
)

rem Did not find PyCharm version that is supported.
goto noPyCharm

:pyCharmExists

echo [INFO]   Will use latest found Pycharm Community Edition:
echo [INFO]     %pycharmExe%

rem Evaluate command line parameters, using Windows-style options:
rem - have to check %1% and %2% because may be called from another file such as from gpui.bat using -ui
rem - the / options are handled here, consistent with Windows
rem - the /o option will only try to run the OSGeo4W QGIS install,
rem   useful for older development and troubleshooting
rem - the /s option will only try to run the standalone QGIS install,
rem   current default for development, consistent with the deployed environment
rem - OK to include -h and --help since gp*.bat is not called
if "%1"=="/h" goto printUsage
if "%1"=="/help" goto printUsage
if "%1"=="/?" goto printUsage
if "%1"=="-h" goto printUsage
if "%1"=="--help" goto printUsage
if "%2"=="/h" goto printUsage
if "%2"=="/help" goto printUsage
if "%2"=="/?" goto printUsage
if "%2"=="-h" goto printUsage
if "%2"=="--help" goto printUsage

rem Detect whether the environment should be printed.
set doPrintEnv=no
if "%1"=="/printenv" set doPrintEnv=yes
if "%2"=="/printenv" set doPrintEnv=yes
if "%3"=="/printenv" set doPrintEnv=yes
if "%4"=="/printenv" set doPrintEnv=yes
if "%5"=="/printenv" set doPrintEnv=yes
if "%1"=="--printenv" set doPrintEnv=yes
if "%2"=="--printenv" set doPrintEnv=yes
if "%3"=="--printenv" set doPrintEnv=yes
if "%4"=="--printenv" set doPrintEnv=yes
if "%5"=="--printenv" set doPrintEnv=yes
echo [INFO] doPrintEnv = %doPrintEnv%
if "%doPrintEnv%"=="yes" (
  echo [INFO] Will print the environment before starting the SNODAS Tools.
)

rem Case where the OSGeo version (not standalone version) is run.
if "%1"=="/o" goto runOsgeoQgis
if "%1"=="-o" goto runOsgeoQgis
if "%2"=="/o" goto runOsgeoQgis
if "%2"=="-o" goto runOsgeoQgis
if "%3"=="/o" goto runOsgeoQgis
if "%3"=="-o" goto runOsgeoQgis
if "%4"=="/o" goto runOsgeoQgis
if "%4"=="-o" goto runOsgeoQgis

rem Case where /s is specified without a QGIS version.
set qgisVersion=unknown
set targetQgisVersion=unknown
if "%1"=="/s" goto runStandaloneQgis
if "%1"=="-s" goto runStandaloneQgis
if "%2"=="/s" goto runStandaloneQgis
if "%2"=="-s" goto runStandaloneQgis
if "%3"=="/s" goto runStandaloneQgis
if "%3"=="-s" goto runStandaloneQgis
if "%4"=="/s" goto runStandaloneQgis
if "%4"=="-s" goto runStandaloneQgis

rem Print this script version:
rem - OK to include -v and --version since gp*.bat is not called
if "%1"=="/v" goto printVersion
if "%1"=="-v" goto printVersion
if "%1"=="--version" goto printVersion
if "%2"=="/v" goto printVersion
if "%2"=="-v" goto printVersion
if "%2"=="--version" goto printVersion
if "%3"=="/v" goto printVersion
if "%3"=="-v" goto printVersion
if "%3"=="--version" goto printVersion

rem If here /s was not specified but /sN.N might have been.
rem Options that specify the standalone QGIS version to use:
rem - the requested version will be confirmed below when file existence is checked
rem echo [INFO] Before QGIS version for loop.
echo [INFO]
echo [INFO] Determine the QGIS to run.
echo [INFO]   Check to see if the requested QGIS version matches known versions used with the SNODAS Tools.
echo [INFO]   It is recommended to install the most recent supported long term releases (ltr).
echo [INFO]     3.26.3
echo [INFO]     3.22.16 (ltr)
echo [INFO]     3.12
echo [INFO]     3.10
echo [INFO]     3.4
echo [INFO]   If a different version of QGIS is used, need to update this script.

rem The following could be done better but trying to parse parameters in batch files is painful:
rem - the order is not important because trying to match a requested version
rem - put newest first to match faster
rem - if none are matched "unknown" will be detected
for %%G in (3.26.3 3.22.16 3.12 3.10 3.4 unknown) do (
  rem Set a local variable to make code easier to understand.
  set qgisVersion=%%G
  if "unknown"=="!qgisVersion!" (
    rem Checked all the supported versions and did not have a match.
    goto unknownStandaloneVersion
  )
  echo [INFO]   Checking command arguments for QGIS version /s!qgisVersion!
  if "%1%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo [INFO]     Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
  rem Same logic but for second command parameter (if provided).
  if "%2%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo [INFO]     Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
  rem Same logic but for third command parameter (if provided).
  if "%3%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo [INFO]     Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
)

:unknownStandaloneVersion
rem Get to here if /sN.N or /sN.N.N did not match an installed QGIS in the loop above.
echo [ERROR]
echo [ERROR]  Requested unsupported QGIS version with /sN.N or /sN.N.N (or /s without version).
echo [ERROR]  Need to update this script to handle the requested QGIS version.
echo [ERROR]  Check the versions of QGIS that are installed (e.g., C:\Program Files\QGIS *).
echo [ERROR]  Make sure to run with: /sN.N or /sN.N.N
goto exit1

echo [ERROR]   Did not match /o or /sN.N so trying to run as if /s.
rem Default is to run standalone QGIS:
rem - a warning will be generated if no QGIS version
echo [ERROR]
echo [ERROR]  QGIS install type not specified with /o or /sN.N or /sN.N.N - defaulting to running the standalone QGIS found on the system.
echo [ERROR]  This is not currently handled - must specify /sN.N or /sN.N.N.
rem goto runStandaloneQgis
goto exit1

:runOsgeoQgis

rem Run the OSGeo4W64 version of QGIS.
echo [INFO]
echo [INFO] Using OSGeo4W64 version of QGIS.

rem TODO smalers 2020-03-30 re-enable if needed but for now the code has not been updated to standalone level.
echo [ERROR]
echo [ERROR] OSGeo4W64 GIS version of SNODAS Tools is currently disabled.  Use a standalone QGIS version.
echo [ERROR] Run with /sN.N or /sN.N.N for an installed QGIS version.
goto exit1

:runStandaloneQgis

rem Run the standalone version of QGIS, which is installed in a versioned folder.
echo [INFO]
echo [INFO] Using standalone version of QGIS.

echo [INFO]   Requested target standalone QGIS version = %targetQgisVersion%
if "%targetQgisVersion%"=="unknown" (
  echo [ERROR]
  echo [ERROR]  Requested target standalone QGIS version is unknown.  Run with /sN.N, /sN.N.N, or /o option.
  rem List available standalone versions on all drives, not elegant but OK for now.
  echo [INFO]   Available standalone QGIS versions:
  for %%Z in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set driveLetter=%%Z
    rem debug...
    rem echo [INFO] Checking for existence of:  !driveLetter!:\Program Files\
    if exist "!driveLetter!:\Program Files\" (
      dir /b "!driveLetter!:\Program Files\QGIS*"
    )
  )
  goto printUsage
)

rem Set the Python environment to find the correct run-time libraries:
rem - QGIS Python environment is used and add SNODAS Tools to PYTHONPATH
rem - the SA_GP_ENV_SETUP environment variable is set to YES to indicate that setup has been done
rem - this causes setup to occur only once if rerunning this batch file

if "%SA_PYCHARM_GP_ENV_SETUP%"=="YES" (
  echo [INFO]
  echo [INFO] Environment is already set up for standalone QGIS from previous run.
  echo [INFO] Using the previous settings so that PATH and PYTHONPATH don't accumulate more folders.
  goto runStandaloneQgis2
)

rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell.
echo [INFO]
echo [INFO] Start defining standalone QGIS SNODAS Tools environment.

rem This code is similar to the initial check at the top of the batch file.
echo [INFO]
echo [INFO] Try to find QGIS in ?:\Program Files (may be installed on any drive C or after).
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
  echo [INFO]   Checking for existence of: %%D:\Program Files\QGIS !targetQgisVersion!
  if exist "%%D:\Program Files\QGIS !targetQgisVersion!" (
    SET QGIS_SA_INSTALL_HOME=%%D:\Program Files\QGIS !targetQgisVersion!
    echo [INFO]   Standard QGIS exists in:   !QGIS_SA_INSTALL_HOME!
    goto setupStandalone1b
  )
)
rem If here could not find QGIS.
echo [ERROR]
echo [ERROR]  Could not find QGIS on any drive in:
echo [ERROR]    ?:\Program Files\GGIS !targetQgisVersion!
echo [ERROR]  Cannot continue.
goto exit1

:setupStandalone1b

rem Get the short version of the install home:
rem - TODO smalers 2023-03-02 evaluate whether 8.3 is needed or can long paths with spaces work
echo [INFO]
echo [INFO] Setting QGIS_SA_INSTALL_HOME and QGIS_SA_ROOT.
set QGIS_SA_ROOT=!QGIS_SA_INSTALL_HOME!
echo [INFO]   Standalone install:
echo [INFO]     QGIS_SA_INSTALL_HOME = !QGIS_SA_INSTALL_HOME!
echo [INFO]     QGIS_SA_ROOT = !QGIS_SA_ROOT!

if [] == [!QGIS_SA_ROOT!] (
  echo [ERROR]
  echo [ERROR] QGIS_SA_ROOT is not defined.
  echo [ERROR] Cannot set up the QGIS environment.
  goto exit1
)
if not exist !QGIS_SA_ROOT! (
  echo [ERROR]
  echo [ERROR] QGIS root folder does not exist:
  echo [ERROR]   !QGIS_SA_ROOT!
  echo [ERROR] Cannot set up the QGIS environment.
  goto exit1
)

rem Convert important folders to 8.3 notation.
set use83Paths=true
if "%use83Paths%" == "true" (
  rem TODO smalers 2020-04-01 Try using 8.3 names.
  for %%H in ("!QGIS_SA_INSTALL_HOME!") do set QGIS_SA_INSTALL_HOME_83=%%~sH
  set QGIS_SA_INSTALL_HOME=!QGIS_SA_INSTALL_HOME_83!
  set QGIS_SA_ROOT=!QGIS_SA_INSTALL_HOME_83!
  echo [INFO]   After conversion to 8.3 to avoid spaces in path:
  echo [INFO]     Standalone install home QGIS_SA_INSTALL_HOME = !QGIS_SA_INSTALL_HOME!
  echo [INFO]     Standalone install root QGIS_SA_ROOT = !QGIS_SA_ROOT!
)

echo [INFO]
echo [INFO]   Running SNODAS Tools using standalone QGIS in:  !QGIS_SA_INSTALL_HOME!

rem Where QGIS is installed.
if not exist "!QGIS_SA_INSTALL_HOME!" (
  echo [ERROR] QGIS_SA_INSTALL_HOME does not exist:
  echo [ERROR]   !QGIS_SA_INSTALL_HOME!
  goto noStandaloneQgis
)
if not exist "!QGIS_SA_ROOT!" (
  echo [ERROR] QGIS_SA_ROOT does not exist:
  echo [ERROR]   !QGIS_SA_ROOT!
  goto noStandaloneQgis
)

rem The following sets up the QGIS environment for Python:
rem - handles QGIS, Python, and Qt setup
rem - same batch file name as for OSGeo4W install

echo [INFO]
echo [INFO] Setting QGIS Python and Qt environment variables.
rem Replace "build-util" with "scripts" to find the file.
set scriptsFolder=%scriptFolder:build-util=scripts%
echo [INFO]
echo [INFO]  scriptsFolder=!scriptsFolder!
if exist "!scriptsFolder!\python-qgis-ltr.bat" (
  echo [INFO]   Calling QGIS Python setup batch file from SNODAS Tools:
  echo [INFO]     !scriptsFolder!\python-qgis-ltr.bat
  call "!scriptsFolder!\python-qgis-ltr.bat"
  if errorlevel 1 (
    echo [ERROR]  Error calling python-qgis-ltr.bat.  Cannot continue.
    goto exit1
  )
  goto qgisEnvStandalone
)
rem If here the python-qgis-ltr.bat file was not found, which is a major problem.
echo [ERROR]
echo [ERROR]  python-qgis-ltr.bat file was not found:
echo [ERROR]    %scriptsFolder%\python-qgis-ltr.bat
echo [ERROR]  Cannot setup QGIS Python environment.
goto exit1

:qgisEnvStandalone

rem Add QGIS 'python' and 'plugins' folders to the PYTHONPATH:
rem - the qgis-ltr folder needs to be checked first because for a long term release
rem - the qgis-ltr/python and qgis/python folders each exist, but qgis/python is empty
rem - 'qgis-ltr' is used in several environment variables
rem - the latest release (under development) does not seem to include qgis-ltr
echo [INFO]
echo [INFO] Setting the QGIS Python app files environment variables.
for %%Q in (qgis-ltr qgis qgis-dev) do (
  if exist !QGIS_SA_ROOT!\apps\%%Q\python (
    echo [INFO]   Found QGIS Python application files:
    echo [INFO]     !QGIS_SA_ROOT!

    rem The following is "python/plugins", not just "plugins".
    set PYTHONPATH_QGIS_PLUGINS=!QGIS_SA_ROOT!\apps\%%Q\python\plugins
    echo [INFO]   Adding standalone QGIS plugins to front of PYTHONPATH:
    echo [INFO]     !PYTHONPATH_QGIS_PLUGINS!
    set PYTHONPATH=!PYTHONPATH_QGIS_PLUGINS!;!PYTHONPATH!

    goto standalonePathSet
  )
)
rem If here the application variables could not bet set.
echo [ERROR]
echo [ERROR]  Could not find QGIS Python files in any of the following:
echo [ERROR]    !QGIS_SA_ROOT!\apps\qgis-ltr\python
echo [ERROR]    !QGIS_SA_ROOT!\apps\qgis\python
echo [ERROR]    !QGIS_SA_ROOT!\apps\qgis-dev\python
echo [ERROR]  Cannot setup QGIS Python application environment.
goto exit1

:standalonePathSet
rem If here the PYTHONPATH was set above for PyQGIS.

rem Add additional packages to PYTHONPATH located in PyCharm development venv.
rem List the following in order so most recent Python for target version is found first:
rem - cannot get 'if else if' to work so use goto
echo [INFO]
echo [INFO] Adding venv site packages to PYTHONPATH.
for %%T in (39 38 37 36) do (
  echo [INFO]   Checking for existence of %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T
  if exist %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\ (
    set PYTHONPATH_PYCHARM_SITEPACKAGES=%installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\Lib\site-packages
    echo [INFO]   Adding venv PyCharm Python%%T 'Lib\site-packages' to front of PYTHONPATH:
    echo [INFO]     !PYTHONPATH_PYCHARM_SITEPACKAGES!
    set PYTHONPATH=!PYTHONPATH_PYCHARM_SITEPACKAGES!;!PYTHONPATH!
    goto setupStandalone2
  )
)
rem Warning because could not find PyCharm venv Python.
echo [ERROR]  Could not find venv folder for python:39, Python38, Python37, or Python36 in:
echo [ERROR]    %installFolder%\venv\venv-qgis-!targetQgisVersion! for site-packages.
goto exit1

:setupStandalone2

rem Add the SNODAS Tools Python code to the PYTHONPATH:
rem - OK to put at the front because should not conflict with anything else
rem - the Python main specifies just uses root to load the module
set SNODAS_TOOLS_HOME=%srcFolder%
echo [INFO]
echo [INFO] Adding SNODAS Tools Python source folder code to PYTHONPATH.
if exist %SNODAS_TOOLS_HOME% (
  echo [INFO]   Adding SNODAS Tools Python source folder code to start of PYTHONPATH:
  echo [INFO]     %SNODAS_TOOLS_HOME%
  set PYTHONPATH=%SNODAS_TOOLS_HOME%;!PYTHONPATH!
  goto pycharmSetupComplete
)
echo [ERROR] SNODAS Tools home folder does not exist:  %SNODAS_TOOLS_HOME%
echo [ERROR] Cannot continue.
goto exit1

:pycharmSetupComplete

rem Indicate that the setup has been completed:
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
rem - not sure if this is necessary if exit /b is used because environment will be reset each time the script is run
set SA_PYCHARM_GP_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion.
title SNODAS Tools standalone QGIS development environment for PyCharm
echo [INFO]
echo [INFO] Done defining QGIS SNODAS Tools environment.
goto runStandaloneQgis2

rem ========== END SNODAS Tools setup steps to be done once ===========================
rem ===================================================================================

:noStandaloneQgis

rem QGIS install folder was not found.
echo [INFO] QGIS standard installation folder was not found:  !QGIS_SA_INSTALL_HOME!
goto exit1

:runStandaloneQgis2

rem Echo environment variables for troubleshooting.
echo [INFO]
echo [INFO] After all setup:
echo [INFO]   Using Python3/standalone QGIS3 for SNODAS Tools.
echo [INFO]   Environment for Python/SNODAS Tools:
echo [INFO]     QGIS_SA_INSTALL_HOME=!QGIS_SA_INSTALL_HOME!
echo [INFO]     QGIS_SA_ROOT=!QGIS_SA_ROOT!
echo [INFO]     OSGEO4W_ROOT=!OSGEO4W_ROOT!
echo [INFO]     PATH=%PATH%
echo [INFO]     PYTHONHOME=!PYTHONHOME!
echo [INFO]     PYTHONPATH=!PYTHONPATH!
echo [INFO]     QGIS_PREFIX_PATH=!QGIS_PREFIX_PATH!
echo [INFO]     QT_PLUGIN_PATH=!QT_PLUGIN_PATH!

rem Set the window title again because running commands in the window resets the title.
title SNODAS Tools standalone QGIS development environment for PyCharm

if "!doPrintEnv!"=="yes" (
  rem Run the geoprocessor.app.printenv program, useful for troubleshooting.
  rem - this can be used with other program parameters
  rem echo [INFO] Running printenv.py to print the environment.
  rem "!OSGEO4W_ROOT!\bin\python.exe" -m geoprocessor.app.printenv %*
  echo printenv option is currently not enabled.
)

rem Start the PyCharm IDE, /B indicates to use the same windows:
rem - command line parameters passed to this script will be passed to PyCharm
rem - PyCharm will use the Python interpreter configured for the project
rem - specify the folder for the project so it does not default to some other project that was opened last
rem - the project folder is the same as the repository folder (use PyCharm exclude feature to exclude non-source folders)
rem echo [INFO] Starting PyCharm using:  start ... /B %pycharmExe% %GP_PROJECT_DIR% %*
SET GP_PROJECT_DIR=%installFolder%
echo [INFO]
echo [INFO] Starting PyCharm.
echo [INFO]   PYCHARM = %pycharmExe%
echo [INFO]   GP_PROJECT_DIR = %GP_PROJECT_DIR%
rem TODO smalers 2020-03-30 need to figure out how to strip out /s3.10, etc. from %* so PyCharm won't complain.
echo [INFO]   Starting PyCharm using:
echo [INFO]     start "Pycharm aware of QGIS" /B "%pycharmExe%" "%GP_PROJECT_DIR%" %*
echo [INFO]     Command shell prompt will display and PyCharm may take a few seconds to start.
rem See the 'start' program documentation:
rem   https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/start
rem   title
rem   /b - runs in the same command shell
rem   /wait - waits before exiting (prompt does not immediately come back)
rem   program to run
rem   program command line parameters
rem if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /b "%pycharmExe%" "%GP_PROJECT_DIR%" %*
if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /b /wait "%pycharmExe%" "%GP_PROJECT_DIR%"
if not exist %GP_PROJECT_DIR% goto noproject

rem Successful startup.
goto exit0

rem =======================================================================
rem Below here are one-off goto targets that each end with exit.

:noproject
rem No project directory (should not happen).
echo [ERROR]   PyCharm project folder does not exist:  %GP_PROJECT_DIR%
echo [ERROR]   Not starting PyCharm.
goto exit1

:noPyCharm
rem Expected PyCharm was not found.
echo [ERROR]   PyCharm was not found in expected location C:\Program Files\JetBrains\PyCharm Community Edition NNNN.N.N\bin\pycharm64.exe
echo [ERROR]   May need to update this script for newer versions of PyCharm.
goto exit1

:noqgisbat
rem qgis.bat was not found.
echo [INFO]   QGIS batch file not found:  %OSGEO4W_ROOT%/bin/qgis.bat
goto exit1

:printUsage
rem Print the program usage.
echo.
echo Usage:  %scriptName% [options]
echo.
echo Run PyCharm to develop the SNODAS Tools.
echo This batch file sets up the development environment and calls PyCharm.
echo.
echo /f       Use for first-time setup of PyCharm when venv does not exist.
echo /h       Print usage of this batch file.
echo /o       Use the OSGeo4W version of QGIS, CURRENTLY DISABLED.
echo /s       Use the standalone version of QGIS - default rather than /o.
echo /sN.N    Use the standalone version N.N of QGIS (for example 3.10).
echo /sN.N.N  Use the standalone version N.N.N of QGIS (for example 3.22.16).
echo /v       Print version of this batch file.
echo.
goto exit0

:printVersion
rem Print the program version.
echo.
echo %scriptName% version: %pycharmBatVersion% %pycharmBatVersionDate%
echo.
goto exit0

:exit0
rem Exit with normal (0) exit code:
rem - put this at the end of the batch file
echo [INFO] Success.  Exiting with status 0.  PyCharm should be running.
exit /b 0

:exit1
rem Exit with general error (1) exit code:
rem - put this at the end of the batch file
echo [ERROR] An error of some type occurred [see previous messages].  Exiting with status 1.  PyCharm did not start.
exit /b 1
