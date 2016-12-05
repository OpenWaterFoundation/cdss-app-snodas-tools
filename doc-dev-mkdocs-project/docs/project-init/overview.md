# Initial Project Setup / Overview

The Initial Project Setup documentation sections are a record of how the project was set up the first time.
This documentation is a useful reference in case the project needs to be reinitialized or other similar projects need to be configured.
Sections of this documentation are also referenced by the [New Developer Setup](../dev-new/overview/) documentation,
such as configuring the PyCharm workspace, because these tasks need to occur for any new developer.

**TODO smalers 2016-12-04 need to understand how PyCharm manages a project**

The SNODAS Tools project results in Python scripts that are deployed to the operational system
and are run in the normal fashion by the Python interpreter.
There is a heavy dependence on the QGIS/pyQGIS installed environment.
Several Python programs have been created that call pyQGIS modules and make system calls to `gdal`, `ogr2ogr`, and other programs.

**TODO smalers 2016-12-04 need to finalize deployed environment.
Probably no need to install into site packages?  Just run out of a specific folder.**

## Development Folder Structure

The approach described in this documentation for development project initialization is to set up a folder structure as follows.
Individual software developers may choose to follow this approach closely, or use a variation based on their preferences
and multiple software projects that they are working on.
However, any deviation from this approach will mean that the project will not be consistent with this documentation
and the developer's environment may be more difficult to support.
The recommendations shown below are based on experience setting up the developer environment and creating this documentation.
Backslashes are used to indicate folder levels, consistent with the target Windows 7/10 environment.

** TODO smalers 2016-12-04 need to include all software and components used in the project.**

```text
C:\Program Files \                          (normal software install location for 64-bit software)
C:\Program Files (x86) \                    (normal software install location for 32-bit software)

C:\???\                                     (QGIS sofware install location)

C:\Users\user\                              (software developer's home folder on Windows)
  cdss-dev\                                 (umbrella software folder for CDSS development projects)
    CDSS-SNODAS-Tool\                       (folder for SNODAS Tools development)
      bin\                                  (folder for scripts used in development files)
      git-repos\                            (Git repositories, may be one or more repositories under here,
        cdss-app-snodas-tools\              (all the code, documentation, tests, and other files
	                                     that are part of this development project)
      tools\                                (folder under which additional project-specific software can be installed)
```

PyCharm stores files in the following locations:

1. **TODO smalers 2016-12-04 need to understand PyCharm and which files are in repository - document them below**
