# SNODAS Tools / Developer Manual

This documentation is written for SNODAS tools software developers.
The software project is loosely aligned with [Colorado's Decision Support Systems (CDSS)](http://cdss.state.co.us),
in particular because the Open Water Foundation is working to move CDSS tools to open source licensing and that
effort may result in a template for how to manage many software projects developed for the State of Colorado.

The SNODAS Tools generate water supply data products from SNODAS
to provide data products to State agency and other agency water managers.
The tools are intended to be run daily by technical staff at the Colorado Water Conservation Board, or other State entity,
Open Water Foundation, and other entities that are interested in daily snow products.
Ideally, the products will be generated and hosted by the State.  OWF is working through deployment details.

## Project Background

The SNODAS Tools software is being developed by the [Open Water Foundation](http://openwaterfoundation.org)
for the [Colorado Water Conservation Board](http://cdss.state.co.us).

Background for this project is included in the [SNODAS Tools User Manual](http://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-user/).
Technical approach and design are discussed in the [Development Tasks / Software Design](dev-tasks/software-design/) section of this documentation.

## How to Use this Documentation

This documentation is organized by major phases of software development, including:

* [New Developer Setup](dev-new/overview) - steps that a new developer must take to set up the project so they can contribute to development
* [Development Environment](dev-env/overview) - configure software tools needed in the developer environment (but don't set up the project yet)
* [Initial Project Setup](project-init/overview) - steps to set up the project the first time, using software installed in the development environment
* [Deployed Environment](deployed-env/overview) - steps to set up a deployed environment for SNODAS tools
* [Development Tasks](dev-tasks/overview) - background on SNODAS tools software design and guidelines for common recurring development tasks

## Importance of This Documentation

This documentation is the main resource for developers of the SNODAS tools.
**Developers that work on the software must keep the documentation up to date and accurate for the benefit
of other developers.**

The documentation exists as Markdown files in the doc-dev-mkdocs-project folder under the Git repository.

## Technology Stack

The tools are implemented using the following technology stack,
which supports deployment on WIndows 7/10 computers (and potentially others with configuration changes).
This technology stack was chosen to utilize free and open source software, run on State of Colorado computer infrastructure,
and be maintainable using an open source project approach.

* Operating system:
	* Windows 7/10 64-bit (although 32-bit could also be used) 
* Software for operating system:
	* QGIS 2.16.2 for spatial data processing
* Software for development environment:
	* Git (latest version)
	* PyCharm Community Edition 2016.2.3 Python IDE
	* MkDocs and Python 3.5 for documentation

Additional details can be found in the [Development Tasks / Software Design](dev-tasks/software-design/) section of this documentation.
