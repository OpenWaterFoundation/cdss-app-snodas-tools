# SNODAS Tools / Developer Manual

This documentation is written for SNODAS tools software developers.
The software project is aligned with [Colorado's Decision Support Systems (CDSS)](https://cdss.colorado.gov/).

The SNODAS Tools generate water supply data products from SNODAS
to provide data products to State agency and other agency water managers.
The tools are intended to be run daily by technical staff at the Colorado Water Conservation Board, or other State entity,
Open Water Foundation, and other entities that are interested in daily snow products.
Ideally, the products will be generated and hosted by the State.  OWF is working through deployment details.

*   [Project Background](#project-background)
*   [How to Use this Documentation](#how-to-use-this-documentation)
*   [Technology Stack](#technology-stack)
    *   [Latest Windows Development Environment](#latest-windows-development-environment)
    *   [Linux Development Environment](#linux-development-environment)
    *   [Original Windows Development Environment](#original-windows-development-environment)

-------------

## Project Background ##

The SNODAS Tools software was originally developed by the [Open Water Foundation](https://openwaterfoundation.org)
for the [Colorado Water Conservation Board](https://cwcb.colorado.gov/)
and has been updated over time for additional applications.

Background for this project is included in the
[SNODAS Tools User Manual](https://software.openwaterfoundation.org/cdss-app-snodas-tools/latest/doc-user/).
Technical approach and design are discussed in the
[Development Tasks / Software Design](dev-tasks/software-design.md) section of this documentation.

## How to Use this Documentation ##

This documentation is organized by major phases of software development, including:

*   [Release Notes](release-notes/release-notes.md) - release notes for SNODAS Tools software product,
    including changes to software and documentation
*   [New Developer Setup](dev-new/overview.md) - steps that a new developer must take to set up the project so they can contribute to development
*   [Development Environment](dev-env/overview.md) - configure software tools needed in the developer environment (but don't set up the project yet)
*   [Initial Project Setup](project-init/overview.md) - steps to set up the project the first time, using software installed in the development environment
*   [Deployed Environment](deployed-env/overview.md) - steps to set up a deployed environment for SNODAS tools
*   [Development Tasks](dev-tasks/overview.md) - background on SNODAS tools software design and guidelines for common recurring development tasks

## Technology Stack ##

The tools are implemented using the following technology stack,
which supports deployment on Windows and Linux computers.
This technology stack was chosen to utilize free and open source software,
run on State of Colorado computer infrastructure,
and be maintainable using an open source project approach.

### Latest Windows Development Environment ###

*   Operating system:
    *   Windows 11
*   Software for operating system:
    *   QGIS 3.22.16 stand alone for spatial data processing
*   Software for development environment:
    *   Git (latest version)
    *   PyCharm Community Edition 2022.2.3 Python IDE
    *   MkDocs 1.4.2 and Python 3.10 for documentation

### Linux Development Environment ###

Need to document.

### Original Windows Development Environment ###

*   Operating system:
    *   Windows 7/10 64-bit
*   Software for operating system:
    *   QGIS 2.16.2 for spatial data processing
*   Software for development environment:
    *   Git (latest version)
    *   PyCharm Community Edition 2016.2.3 Python IDE
    *   MkDocs and Python 3.5 for documentation
