@echo off
rem Simple script to run the SNODAS Tools daily_interactive.py program on Windows.
rem This is a modified version of the QGIS bin/python-qgis-ltr.bat batch file.

rem Check whether have previously ran the script and don't need to set the environment again.
rem Otherwise, the environment variables get longer and longer until they hit the maximum length and get error:
rem   The input line is too long.
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

rem Get PYTHONPATH folders, including development 'src' files and virtual environment ('venv'):
rem - SNODAS TOOLS can be run from source files or files installed in the venv
set SNODAS_TOOLS=%scriptFolder%\..\src;%scriptFolder%\..\venv\venv-qgis-3.22.16-python39\Lib\site-packages
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins;%SNODAS_TOOLS%;%PYTHONPATH%

rem Set an environment variable to show that the environment has been set up.
set SNODAS_TOOLS_ENV_SETUP=YES
rem Set the window title.
title SNODAS Tools QGIS Shell

:run

rem Run the program.
rem Original...
rem python %*
rem New...
python -m snodastools.app.daily_interactive %*
