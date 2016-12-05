# New Developer Setup / Overview

A new developer that will contribute to the SNODAS Tools must configure a development environment
consistent with the [Initial Project Setup](../project-init/overview/).
The standard development folder structure should be followed to minimize potential for issues,
especially given the number of components and setup steps.

The setup involves performing some of the same tasks as the initial project setup.
However, some tasks do not need to be repeated because the Git repository contains results of the initial project setup.

Setup a new development environment by performing the steps in the following sections, in order.

## Configure Machine for Development

This documentation has been written assuming that development will occur on a Windows 7/10 64-bit computer,
with deployment to similar environment.
Any changes in the deployed environment should hopefully be handled simply by installing an alternate
QGIS and Python version (Python programs resulting from this project will hopefully not need to be modified).

Development files will be created in `C:\Users\user\cdss-dev\CDSS-SNODAS-Tools` as discussed in the following sections.

If development occurs on other than Windows 7/10, then this section may be modified to describe setting up a Virtual Machine (VM).

## Create Folder for Development Files

[Create a development folder consistent with the initial project setup](../project-init/dev-folder/) - this is an umbrella folder for all development files,
including copies of software should the developer choose to use this approach.

## Install Git Software

The Git software is needed to clone the repository (next step).

See the [Git installation instructions](../dev-env/git/).

## Clone Git Repository

The Git repository contains the SNODAS tools software project files.
It also contains this documentation.
The repository will be referenced by the PyCharm IDE sofware.
**TODO smalers 2016-12-04 need to figure out how PyCharm manages files.**

Clone the repository files using Git BASH:

```bash
$ cd /c/Users/user/CDSS-SNODAS-Tools
$ mkdir git-repos
$ cd git-repos
$ git clone https://github.com/OpenWaterFoundation/cdss-app-snodas-tools.git
```

If prompted, specify the GitHub account credentials.

## View Developer Documentation with MkDocs

Developer documentation is created with MkDocs, which uses Markdown to create a static HTML website.
First install necessary Python 3.5 and MkDocs software, if not already installed:

* [install Python](../dev-env/python/).
* [install `pip`](../dev-env/pip/).
* [install MkDocs](../dev-env/mkdocs/).

MkDocs can then be used to run a local web server to view the full documentation.
Run the following in a Windows Command Shell:

```com
> cd C:\Users\user\cdss-dev\CDSS-SNODAS-Tools\git-repos\cdss-app-snodas-tools\doc-dev-mkdocs-project
> mkdocs serve

INFO    -  Building documentation...
INFO    -  Cleaning site directory
[I 161205 02:11:49 server:283] Serving on http://127.0.0.1:8000
[I 161205 02:11:49 handlers:60] Start watching changes
[I 161205 02:11:49 handlers:62] Start detecting changes
```

Then view the `localhost:8080` web page in a web browser.
Follow the instructions in the ***New Developer Setup*** documentation.

## Install Development Software Tools

The following is a summary of new developer setup for all the developer tools,
with links to other documentation for reference.
Software installation steps can be skipped if they have already been completed.

1. **Should have been completed above:** [determine Windows 10 64-bit computer](../dev-env/machine/) - this is the target environment
2. **Should have been completed above:** [Install Git software](../dev-env/git/) - needed to check out repository
2. **Should have been completed above:** [Install Python](../dev-env/python/) - needed by MkDocs
2. **Should have been completed above:** [Install `pip`](../dev-env/pip/) - used to install MkDocs
2. **Should have been completed above:** [Install MkDocs](../dev-env/mkdocs/) - used for documentation
4. [Install QGIS bundled with QGIS](../dev-env/qgis/) - QGIS/pyQGIS/GDAL/OGR software tools to run SNODAS tools
4. [Install PyCharm IDE](../dev-env/pycharm/) - IDE used to edit and run SNODAS tools during development
3. [Install TSTool](../dev-env/tstool/) - needed to create time series products
3. [Install pytest](../dev-env/pytest/) - needed to run automated Python tests

The remaining steps below refer to other documentation and provides specific direction for new developer project setup.

## Setup PyCharm Workspace

[Create a PyCharm workspace](../project-init/pycharm-workspace/).
This step is the same as the initial project setup.

**TODO smalers 2016-12-04 Need to document how PyCharm gets setup.**

## Import the Existing Git Repository Folder into PyCharm

**TODO smalers 2016-12-04 Need to complete this assume that PyCharm needs to be told about he Git repository**

## Configure PyCharm to Use QGIS Python

[Configure PyCharm to use QGIS Python](../project-init/pycharm-config-python/).

**TODO smales 2016-12-04 need to document how PyCharm is configured to use QGIS Python - is this configuration stored in the repository?**

## Configure SNODAS Tools

**TODO smalers 2016-12-04 Is any configuration needed to point the software to SNODAS data, etc., output folders, etc?**

## Next Steps - Development

At this point it should be possible to use PyCharm to run and edit the Python programs.
The development tasks can be followed to do development.
