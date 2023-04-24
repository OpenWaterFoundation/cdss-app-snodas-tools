# test-custom

*   [Introduction](#introduction)
*   [Development Environment](#development-environment])
    +   [Development Environment Software](#development-environment-software)
    +   [Initialize the Development Environment](#initialize-the-development-environment)
*   [Deployed Environment](#deployed-environment)
    +   [Deployed Environment Software](#deployed-environment-software)
    +   [Initialize the Deployed Environment](#initialize-the-deployed-environment)

----------------

## Introduction ###

This folder contains the test configuration for developing and running a custom SNODAS Tools configuration for a single basin.
The configuration was tested on Windows 11.

## Development Environment ##

This custom configuration was initialized in the development environment as follows.
In this case, the custom configuration is intended to be run and tested within a development environment prior to deploying in production.

### Development Environment Software ###

The following software must be installed in the development environment,
in addition to the software that is used in the production environment.

1.  Install QGIS (see [Production Environment Software](#production-environment-software)).
2.  Install TSTool (see [Production Environment Software](#production-environment-software)).
3.  Install and configure Git for Windows.

### Initialize the Development Environment ###

This custom configuration was initialized in the development environment as followed.
In this case, the custom configuration is intended to be run within the development environment.
Once development and testing are complete, the software will be packaged for the deployed environment.

1.  Clone the repository:
    1.  Clone the [`cdss-app-snodas-tools`](https://github.com/OpenWaterFoundation/cdss-app-snodas-tools)
        Git repository using the folder structure in the repository.
1.  Create initial folders and configuration:
    1.  Create this folder.
    2.  Create this `README.md` file.
    3.  Copy the `test-CDSS/config` folder to the `config` folder.
    4.  Use a text editor to edit the `test-custom/config/SNODAS-Tools-Config.ini` file to change the following properties
        (all other property values can match the original `test-CDSS` configuration file):
        *   `[ProgramInstall]`
            +   `tstool_pathname` - `C:/CDSS/TSTool-14.8.0.dev1/bin/tstool.exe`
        *   `[ProgramInstall]`
            +   `tstool_create-snodas-graphs_pathname` - for example use the location in the local Git repository working files:
                 `D:/Users/steve/cdss-dev/CDSS-SNODAS-Tools/git-repos/cdss-app-snodas-tools/test-custom/TSTool/6_CreateTimeSeriesProducts/create-snodas-swe-graphs.TSTool`
        *   `[Folders]`
            +   `root_dir` - for example the main test folder:
                `D:/Users/steve/cdss-dev/CDSS-SNODAS-Tools/git-repos/cdss-app-snodas-tools/test-custom/`
        *   `[BasinBoundaryShapefile]`
            +   `pathname` - for example:
                `D:/Users/steve/cdss-dev/CDSS-SNODAS-Tools/git-repos/cdss-app-snodas-tools/test-CDSS/staticData/CO_Basins_Albers.shp`
        *   `[OutputLayers]`
            +   `dev_environment` should be `True` if in the development environment, `False` otherwise.
            +   `upload_to_s3` should be `False`
            +   `gcp_upload` should be `False`

## Deployed Environment ##

This custom configuration was initialized in the deployed (also called production) environment as follows.
In this case, the custom configuration is intended to be run within a deployed environment, not the development environment.

### Deployed Environment Software ###

The following software must be installed in the production environment.

1.  QGIS:
    *   See the [Open Water Foundation / Learn QGIS](https://learn.openwaterfoundation.org/owf-learn-qgis/install-qgis/install-qgis/) documentation.
    *   For this example, install QGIS 3.22.16 stand-alone on Windows 11.
        Consequently, QGIS will be installed in `C:\Program Files\QGIS 3.22.16`.
2.  TSTool:
    *   Install the latest TSTool from the [OpenCDSS TSTool downloads page](https://opencdss.state.co.us/tstool/).
        Consequently, TSTool will be installed in `C:\CDSS\TSTool-14.8.0` or similar.

### Initialize the Deployed Environment ###
