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
3. **Should have been completed above:** [Install Python](../dev-env/python/) - needed by MkDocs
4. **Should have been completed above:** [Install `pip`](../dev-env/pip/) - used to install MkDocs
5. **Should have been completed above:** [Install MkDocs](../dev-env/mkdocs/) - used for documentation
6. [Install QGIS bundled with QGIS](../dev-env/qgis/) - QGIS/pyQGIS/GDAL/OGR software tools to run SNODAS tools
7. [Install PyCharm IDE](../dev-env/pycharm/) - IDE used to edit and run SNODAS tools during development
8. [Install TSTool](../dev-env/tstool/) - needed to create time series products

The remaining steps below refer to other documentation and provides specific direction for new developer project setup.

## Setup PyCharm Project

The [initial project setup configured a PyCharm project](../project-init/pycharm-project/) in the following folder:
`C:\Users\user\cdss-dev\CDSS-SNODAS-Tools\git-repos\cdss-app-snodas-tools\pycharm-project`.
This folder will have been cloned with other Git files.

## Configure PyCharm to Use QGIS Python

It is recommended that a script be used to run PyCharm consistent with QQIS.
See [Configure PyCharm to work with QGIS](../dev-env/pycharm#configure-pycharm-to-work-with-qgis).

The default script created for SNODAS Tools development an be used as if the installed PyCharm version
is consistent with the script.  Otherwise, copy the script to a new name and change as needed.
Note that the script will be saved to Git unless it is copied to a folder outside of Git.
Be careful to not clobber the default file with changes for a specific user.

## Next Steps - Development

At this point it should be possible to use PyCharm to run and edit the Python programs.
The [Development Tasks](../dev-tasks/overview/) can be followed to do development.

Once scripts run in the development environment, they can be deployed using a more limited set of installed software (mainly QGIS).
