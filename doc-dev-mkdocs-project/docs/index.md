# CDSS SNODAS Tools / Developer Manual

This documentation is written for CDSS SNODAS tools software developers.

The CDSS SNODAS Tools generate water supply data products from SNODAS
to provide data products to State agency and other agency water managers.
The tools are intended to be run daily by technical staff at the Colorado Water Conservation Board, or other State entity,
Open Water Foundation, and other entities that are interested in daily snow products.
Ideally, the products will be generated and hosted by the State.  OWF is working through deployment detials.

Major sections of this documentation include:

* [Development Environment](dev-env/overview) - configure software tools needed in the developer environment (but don't set up the project yet)
* [Initial Project Setup](project-init/overview) - steps to set up the project the first time
* [New Developer Setup](dev-new/overview) - steps that a new developer must take to set up the project to use and contribute to the project
* [CDSS SNODAS Tools](code/overview) - design and coding background and guidance
* [Development Tasks](dev-tasks/overview) - guidelines for common development tasks

## Importance of This Documentation

This documentation is the main resource for developers of the CDSS SNODAS tools.
**Developers that work on the software must keep the documentation up to date and accurate for the benefit
of other developers.**

The documentation exists as Markdown files in the doc-dev-mkdocs-project folder under Git repository.

## SNODAS Background

**TODO smalers 2016-12-04 Need to provide here an overview of SNODAS, including providing links to source data and agencies,
links to background documents, etc.**

## Functionality Overview

The tools perform the following functions:

1. Download SNODAS national grids (historical period for historical analysis and each day for daily updates).
2. **TODO smalers 2016-12-04 need to fill in**

## Technology Stack

The tools are implemented using the following technology stack,
which supports deployment on WIndows 7/10 computers (and potentially others with configuration changes).
This technology stack was chosen to utilize free and open source software, run on State of Colorado computer infrastructure,
and be maintainable using an open source project approach.

**TODO smalers 2016-12-04 need to list all tools**

* Operating system:
	* Windows 7/10 64-bit (although 32-bit could also be used) **TODO smalers 2016-12-04 need to confirm with Carolyn Fritz**
* Software for operating system:
	* QGIS ?.? for spatial data processing
* Software for development environment:
	* Git (latest version)
	* PyCharm ?.? Python IDE
	* MkDocs and Python 3.5 for documentation
* Python libraries installed with `pip`:
	* pytest ?.?, for automated testing

## Tool Overview

**TODO smalers 2016-12-04 need to provide overview of the specific scripts.  Need to figure out where to put the usage.
This provides context to developers so they know what script to work on for specific functionality.**
