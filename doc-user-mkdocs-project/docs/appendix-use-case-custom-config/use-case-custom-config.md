# SNODAS Tools / Appendix - Use Case for Custom Configuration

This appendix describes how to install, configure and run SNODAS Tools for a custom configuration.
This example was created based on work to model a single water supply basin for Snowmass Water and Sanitation District.
The use case is expected to run on Windows and changes have not been migrated to the
State of Colorado SNODAS configuration.

*   [Install Software](#install-software):
    +    [Install QGIS](#install-qgis)
    +    [Install TSTool](#install-tstool)
    +    [Install CDSS SNODAS Tools](#install-cdss-snodas-tools)
+   [Configure CDSS SNODAS Tools](#configure-cdss-snodas-tools)
+   [Run CDSS SNODAS Tools](#run-cdss-snodas-tools)

-------

## Install Software ##

The following software should be installed to run the analysis.

### Install QGIS ###

The open source QGIS software and PyQGIS Python tools are used to perform spatial data analysis.
A recent stable version of QGIS has been chosen.

*   See the [Open Water Foundation / Learn QGIS](https://learn.openwaterfoundation.org/owf-learn-qgis/install-qgis/install-qgis/) documentation.
*   For this use case, install QGIS 3.22.16 stand-alone long term release (LTR) on Windows 11.
    Consequently, QGIS will be installed in `C:\Program Files\QGIS 3.22.16`.

### Install TSTool ###

The open source TSTool software, which is part of Colorado's Decision Support Systems,
is used to process time series information products.

*   Install the latest TSTool from the [OpenCDSS TSTool downloads page](https://opencdss.state.co.us/tstool/).
    Consequently, TSTool will be installed in `C:\CDSS\TSTool-14.8.0` or similar.

### Install CDSS SNODAS Tools ###

CDSS SNODAS Tools software was originally developed to run unattended on a cloud server and process SNODAS data every day.

For this use case, SNODAS Tools has been packaged as a Python virtual environment,
which is created from the QGIS Python and contains SNODAS Tools application files.
This ensures that the QGIS and SNODAS Tools Python environments are separate.

To install:

1.  Create a folder where SNODAS Tools will be run, for example `C:\Projects\snodastools`.
    Avoid spaces in the folder, which can cause issues for some software.
    **This is referred to as the "Project Folder".**
2.  Into this folder, download the SNODAS Tools virtual environment (venv) zip file,
    which will have a name similar to `snodastools-2.1.0-win-qgis-3.22.16-venv.zip`.
    Unzip or use Windows explorer to copy the `snodas-2.1.0-win-qgis-3.22.16-venv` folder into the project folder.

## Configure CDSS SNODAS Tools ##

The SNODAS Tools analysis uses a configuration file to control execution.
For this use case, the `config`, `staticData`, and `workflow` folders and their contents
need to be created in the project folder.
The files can be downloaded from the
[GitHub repository](https://github.com/OpenWaterFoundation/cdss-app-snodas-tools/blob/master/test-custom/)
into the folder.

The SNODAS Tools software will automatically detect the location of the configuration file
and other paths will be relative to the configuration file.

Edit the configuration file for the installation, in particular:

*   Check that `tstool_path` points to a valid TSTool installation.

## Run CDSS SNODAS Tools ##

Open a Windows command shell window and change into the
`snodas-2.1.0-win-qgis-3.22.16-venv/Scripts` folder.

Run the `daily_interactive.bat` file and enter dates to process.
Experience has shown that trying to run the entire historical period can have issues.
It is recommended to run smaller periods of 1-5 years.

The output graphs will not process correctly until a few months of data are available.

