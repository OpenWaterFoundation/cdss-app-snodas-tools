rem Bath file to set the environment and runn pycharm consistent with QGIS environment
rem - Use QGIS Python and libraries
rem - Start pycharm with the configured environment
rem
rem The following seems to be more relevant.
rem See:  http://spatialgalaxy.com/2014/10/09/a-quick-guide-to-getting-started-with-pyqgis-on-windows/
rem The following provides useful background but seems incomplete.
rem See:  http://planet.qgis.org/planet/tag/pycharm/

rem Where QGIS is installed
SET OSGEO4W_ROOT=C:\OSGeo4W64
rem Name of QGIS program to run
SET QGISNAME=qgis
rem Absolute path to QGIS program to run
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
rem Not sure what the following is used for but include in case PyCharm or QGIS uses
SET QGIS_PREFIX_PATH=%QGIS%
REM Set the absolute path to PyCharm program - may vary by developer so make a copy of the script for the developer
REM SET PYCHARM="C:\Program Files (x86)\JetBrains\PyCharm 3.0\bin\pycharm.exe"
REM SET PYCHARM="C:\Program Files (x86)\JetBrains\PyCharm Community Edition 2016.2.3\bin\pycharm.exe"
SET PYCHARM="C:\Program Files (x86)\JetBrains\PyCharm Community Edition 2016.3\bin\pycharm.exe"

REM Set the QGIS environment by calling the setup script that is distributed with QGIS
CALL %OSGEO4W_ROOT%\bin\o4w_env.bat

REM Add QGIS to the PATH environmental variable so that all QGIS, GDAL, OGR, etc. programs are found
SET PATH=%PATH%;%QGIS%\bin
REM Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python;
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages

REM Start the PyCharm IDE, /B indicates to use the same windows
REM Command line parameters passed to this script will be passed to PyCharm
start "PyCharm aware of QGIS" /B %PYCHARM% %*
