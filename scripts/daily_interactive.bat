rem @echo off
rem Simple script to run the SNODAS Tools daily_interactive.py program on Windows.
rem This is a modified version of the QGIS bin/python-qgis-ltr.bat batch file.

rem Check whether have previously run the script and don't need to set the environment again.
rem Otherwise, the environment variables get longer and longer until they hit the maximum length and get error:
rem   The input line is too long.
rem
rem If troubleshooting, it may be necessary to re-open a command shell window each time the script is run
rem to make sure that the environment variables are being set correctly.
rem
if "%SNODAS_TOOLS_ENV_SETUP%"=="YES" goto run
 
call "C:\Program Files\QGIS 3.22.16\bin\o4w_env.bat"
rem @echo off
path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins

rem Original...
rem set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%
rem New...
rem scriptFolder has \ at the end
set scriptFolder=%~dp0
rem Remove trailing \ from 'scriptFolder'.
set scriptFolder=%scriptFolder:~0,-1%
rem echo scriptFolder without trailing slash=%scriptFolder%

rem Get PYTHONPATH folders, including development 'src' files and virtual environment ('venv'):
rem - SNODAS TOOLS can be run from source files (development files)
rem   or Scripts folder files installed in the venv (deployed)
rem Development environment.
set SNODAS_TOOLS=%scriptFolder%\..\src;%scriptFolder%\..\venv\venv-qgis-3.22.16-python39\Lib\site-packages
rem Deployed environment.
set SNODAS_TOOLS=%scriptFolder%\..\Lib\site-packages;%SNODAS_TOOLS%
rem Everything else is found in the QGIS installation files.
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins;%SNODAS_TOOLS%;%PYTHONPATH%

rem Set an environment variable to show that the environment has been set up.
set SNODAS_TOOLS_ENV_SETUP=YES
rem Set the window title.
title SNODAS Tools QGIS Shell

rem Output the environment for troubleshooting.
set

:run

rem Run the program.
rem Original...
rem python %*
rem New...
where python
rem python -m %scriptFolder%\snodastools.app.daily_interactive %*
rem The following works in the development environment.
rem python -m snodastools.app.daily_interactive %*
rem The following ensures that the QGIS Python is used.
"C:\Program Files\QGIS 3.22.16\bin\python" -m snodastools.app.daily_interactive %*
