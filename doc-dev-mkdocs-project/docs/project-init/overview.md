# Initial Project Setup / Overview

The Initial Project Setup documentation sections are a record of how the project was set up the first time.
This documentation is a useful reference in case the project needs to be reinitialized or other similar projects need to be configured.

* Sections of this documentation are also referenced by the [New Developer Setup](../dev-new/overview/) documentation,
such as creating the development folder structure, because these tasks need to occur for any new developer.
* See also the [Deployed Environment](../deployed-env/overview/) for a description of folder structure in the deployed system.

The SNODAS Tools project results in Python scripts that are deployed to the operational system
and are run in the normal fashion by the Python interpreter.
There is a heavy dependence on the QGIS/pyQGIS installed environment.
Several Python programs have been created that call pyQGIS modules and make system calls to `gdal`, `ogr2ogr`, and other programs.

## Development Folder Structure

The approach described in this documentation for development project initialization is to set up a folder structure as follows.
Individual software developers may choose to follow this approach closely, or use a variation based on their preferences
and multiple software projects that they are working on.
However, any deviation from this approach will mean that the project will not be consistent with this documentation
and the developer's environment may be more difficult to support.
The recommendations shown below are based on experience setting up the developer environment and creating this documentation.
Backslashes are used to indicate folder levels, consistent with the target Windows 7/10 environment.

```text
C:\Program Files\                             (normal software install location for 64-bit software)
C:\Program Files (x86)\                       (normal software install location for 32-bit software)
  JetBrains\PyCharm Community Edition 2016.3  (PyCharm IDE used to edit and run Python code during development)

C:\CDSS\TSTool-Version\                       (CDSS TSTool software install location)
C:\OSGeo4W64\                                 (QGIS sofware install location, includes bundled Python 2.7)

C:\Users\user\                                (software developer's home folder on Windows)
  cdss-dev\                                   (umbrella software folder for CDSS development projects)
    CDSS-SNODAS-Tool\                         (folder for SNODAS Tools development)
      git-repos\                              (Git repositories, may be one or more repositories under here,
        cdss-app-snodas-tools\                (all the code, documentation, tests, and other files
	                                       that are part of this development project)
          doc-dev-mkdocs-project\             (MkDocs project for developer documentation)
          doc-user-mkdocs-project\            (MkDocs project for user documentation)
          pycharm-project\                    (PyCharm project for PyThon code)
		  test-CDSS\						  (folder for CDSS project-specific code and products)
```

PyCharm stores some project configuration files a hidden folder
`C:\Users\user\cdss-dev\CDSS-SNODAS-Tool\git-repos\cdss-app-snodas-tools\pycharm-project\.idea`.

