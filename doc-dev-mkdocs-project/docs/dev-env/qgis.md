# Development Environment / QGIS and Bundled Python

The free and open source QGIS software provides pyQGIS Python libraries to process spatial data.
The version of QGIS used for this project is 2.18.1 (**TODO smalers 2016-12-11 Emma confirm**).
QGIS is bundled with Python 2.7 to ensure that Python integration performs as intended.

## Download and Install QGIS

Download and install [QGIS for Advanced Users](http://www.qgis.org/en/site/forusers/download.html) for Windows,
selecting ***OsGeo4W Network Installer (64 bit)*** for Windows 7 or 10 machine.

Run the installer with administrator privileges, which will have a name similar to `osgeo4w-setup-x86_64.exe`.

As instructed on the website, choose ***Desktop Express Install*** and select QGIS to install the latest release.

The following images illustrate the install process on a Windows 10 computer.  All of the defaults were accepted.

![QGIS install 1](qgis-images/qgis-install-1.png)

![QGIS install 2](qgis-images/qgis-install-2.png)

![QGIS install 3](qgis-images/qgis-install-3.png)

![QGIS install 4](qgis-images/qgis-install-4.png)

![QGIS install 5](qgis-images/qgis-install-5.png)

![QGIS install 6](qgis-images/qgis-install-6.png)

![QGIS install 7](qgis-images/qgis-install-7.png)

![QGIS install 8](qgis-images/qgis-install-8.png)

![QGIS install 9](qgis-images/qgis-install-9.png)

## Run QGIS

To run QGIS use the ***OSGeo4W*** start menu shown below:

![QGIS install 10](qgis-images/qgis-install-10.png)

Running ***QGIS Desktop 2.18.1*** displays the user interface similar to below:

![QGIS install 11](qgis-images/qgis-install-11.png)

The ***Help / About*** menu displays the software version information, which is useful when troubleshooting:

![QGIS install 11](qgis-images/qgis-install-12.png)

## Next Steps

After installing QGIS it is possible to [install and configure PyCharm](pycharm/) to use the QGIS version of Python 2.7 and access
the pyQGIS libraries for spatial processing.
However, installing PyCharm is only needed if doing software development.
The operational SNODAS Tools system can be run from the command line or using a scheduled process without needing PyCharm.
