# Development Environment / Overview

The Development Environment documentation sections are envisioned to be used as a reference by the developer that
sets up the project for the first time, and new developers that need to install and configure required software
to maintain and enhance the software.
Steps can be skipped if they have been previously completed on other software development projects.

The software development environment must be appropriately configured to effectively develop SNODAS tools software.
Development environment setup requires some effort before any code can be written
and is typically done the first time by someone that has a good grasp of the technologies.
Failing to understand how to set up the development environment will likely lead to wasted time,
and possibly back-tracking on previous software development work.

The software development environment focuses on compatible QGIS (GIS Python functionality), Python (to run programs), and PyCharm (IDE) versions.
The PyCharm IDE was chosen based on functionality and demonstrated examples of integration with QGIS.
The following general guidelines are followed to install software:

1. Although some developers may desire otherwise, the target deployed environment is Windows 7/10 and therefore
the focus of this documentation and development environment is Windows.
Developers that use alternate development environments such as Linux will need to contribute
suitable content to this documentation and ensure that their efforts do not distract from the core approach.
2. Although software installers may default to installing under a Windows user folder,
the recommended approach is to install in a shared space when possible (such as `C:\Program Files`).
This allows multiple users to see files during operations and troubleshooting.
If this is an issue, it can be resolved in future updates to the software and development environment.
3. The newest versions of software are used if possible, limited by constraints of major components.
For example QGIS used for this project is integrated with Python 2.7 and therefore
Python programs that are part of the operational system use the QGIS Python 2.7 version.

## Development Environment Software

The following is a list of development environment software:

* [Machine](machine) - operating system
* [QGIS and Bundled Python](qgis) - QGIS/pyQGIS/GDAL/OGR software bundled with Python 2.7
* [TSTool](tstool) - software for processing time series products
* [Git](git) - revision control for SNODAS tools software, documentation, tests, etc.
* [Python (for MkDocs)](python) - Python for MkDocs (and other needs separate from QGIS bundled version)
* [PyCharm IDE](pycharm) - IDE used to develop and test Python programs
* [MkDocs](mkdocs) - used to create this documentation

## Portability and Sustainability Considerations

The SNODAS tools are intended to be as portable as possible,
in order to allow multiple software developers to contribute to the software and allow deployment on multiple systems.
However, Windows 7/10 is the primary target operating system at this time.
The following considerations are related to portability and sustainability:

1. Python is generally considered an open and portable technology and supports integration with GIS and other technologies.
2. This documentation is intended to fully describe the development environment.
3. This documentation and the SNODAS tools are saved in a [public GitHub repository](https://github.com/OpenWaterFoundation/cdss-app-snodas-tools).
4. The approach taken for Python programs attempts to follow Python best practices.
Where resources have limited the team's ability to achieve its goals,
documentation includes "TODO" comments.

