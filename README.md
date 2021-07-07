# cdss-app-snodas-tools

This repository contains the server-side application for
Colorado's Decision Support Systems (CDSS) Snow Data Assimilation System (SNODAS) Tools.
Recent work is to update the original development environment from Windows QGIS 2 environment
to Linux/Ubuntu QGIS 3 environment.

This repository contains Python code and supporting files for
CDSS SNODAS tools, which provide the ability to process SNODAS grids into products suitable
for water supply decision-making in Colorado.

Refer to the developer manual for information about configuring the development environment
and performing development tasks.

The following illustrates the recommended organization of repository files for software development environment.
Additional information is provided to recommend steps for new developers.
Development environment setup needs to occur before development tasks can be performed.
This repository corresponds to the `C:/Users/user/owf-dev/CDSS-SNODAS-Tools/git-repos/cdss-app-snodas-tools/` folder.

```
C:\Users\user\                         Developer's home folder for Windows.
/C/Users/user/                         Developer's home folder for Git Bash (MinGW).
/cygdrive/C/Users/user/                Developer's home folder for Cygwin.
/home/user/                            Developer's home folder for Linux.
  cdss-dev/                            Folder where CDSS development projects live.
    CDSS-SNODAS-Tools/                 Development files for SNODAS tools
==================== above folders are recommended, below are required ===============================
      git-repos/                       Git repositories for SNODAS tools for each major component.
                                       Currently all are managed in OWF GitHub account.
        cdss-app-snodas-tools/         Server-side component files.
          .git/                        Git repository files - use 'git' commands to modify.
          .gitattributes               Git properties for repository.
          .gitignore                   Main ignore file (other files exist where needed).
          build-util/                  Useful build/development utilities.
          dev-util/                    Need to move the 'build-util'.
          doc-dev-mkdocs-project/      MkDocs documentation for software developments.
          doc-user-mkdocs-project/     MkDocs documentation for users.
          pycharm-project/             PyCharm project files and source code for current development.
                                       - QGIS 3.x
                                       - Python 3
                                       - Developed on VirtualBox Ubuntu and deployed to GCP Ubuntu 20.4
          pycharm-project-qgis2/       Archive of PyCharm project files based on QGIS 2.x environment,
                                       which was the original version of SNODAS tools.
                                       - QGIS 2.x
                                       - Python 2
                                       - Developed on Windows and deployed to GCP Ubuntu 16.x
          README.md                    This file.
          test-CDSS/                   Test workflow to process SNODAS data for CDSS.
        cdss-webapp-snodas-tools/      Legacy web application based on HTML/JavaScript.
        owf-app-snodas-ng/             OWF-developed SNODAS UI using Angular.
``` 

# New Developer Setup / Overview

**Need to update this for latest QGIS3 environment.**

A new developer that will contribute to the SNODAS tools must configure a development environment
consistent with the [Initial Project Setup](../project-init/overview/).
The standard development folder structure should be followed to minimize potential for issues,
especially given the number of components and setup steps.

The setup involves performing some of the same tasks as the initial project setup, but some tasks do not need to be repeated,
because the Git repository contains results of the initial project setup.

**Note that the following sections are copied from the New Developer Setup documentation in the MkDocs documentation
described below.  Refer to the full documentation once MkDocs has been enabled in the development environment.**

## Configure Machine for Development

**Need to update this for latest Ubuntu 20.04 environment.**

This documentation has been written assuming that development will occur on a Windows 7/10 64-bit computer,
with deployment to similar environment.
Any changes in the deployed environment should hopefully be handled simply by installing an alternate
QGIS and Python version (Python programs resulting from this project will hopefully not need to be modified).

Development files will be created in `C:\Users\user\cdss-dev\CDSS-SNODAS-Tools` as discussed in the following sections.

If development occurs on other than Windows 7/10, then this section may be modified to describe setting up a Virtual Machine (VM).

## Create Folder for Development Files

**Need to confirm that this is up to date.**

[Create a development folder consistent with the initial project setup](../project-init/dev-folder/) - this is an umbrella folder for all development files,
including copies of software should the developer choose to use this approach.

## Install Git Software

The Git software is needed to clone the repository (next step).

See the [Git installation instructions](../dev-env/git/).

## Clone Git Repository

**Need to update this for Linux development.**

The Git repository contains the SNODAS tools software project files.
It also contains this documentation.
The repository will be referenced by the PyCharm IDE sofware.

Clone the repository files using Git BASH:

```bash
$ cd /c/Users/user/CDSS-SNODAS-Tools
$ mkdir git-repos
$ cd git-repos
$ git clone https://github.com/OpenWaterFoundation/cdss-app-snodas-tools.git
```

If prompted, specify the GitHub account credentials.

## View Developer Documentation with MkDocs

**Need to confirm that this works for Linux.**

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
