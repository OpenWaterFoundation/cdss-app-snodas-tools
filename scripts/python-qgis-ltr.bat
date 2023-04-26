rem @echo off
rem This is a modified version of C:\Program Files\QGIS 3.22.16\bin\python-qgis-ltr.bat:
rem - still run the QGIS bin\o4w_env.bat script
rem - don't run python at the end since other scripts will run

echo [INFO]
echo [INFO]   In python-qgis-ltr.bat
echo [INFO]     QGIS_SA_ROOT = %QGIS_SA_ROOT%

rem Original script is run from the same location as o4w_env.bat.
rem call "%~dp0\o4w_env.bat"
rem SNODAS Tools PyCharm run script is run from SNODAS Tools scripts folder.
call "%QGIS_SA_ROOT%\bin\o4w_env.bat"
echo [INFO]     OSGEO4W_ROOT = %OSGEO4W_ROOT%

path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%

rem Original QGIS script called Python here.
rem python %*
rem SNODAS Tools PyCharm run script calls this for setup and then does additional setup before calling Python.

echo [INFO]   End of python-qgis-ltr.bat
