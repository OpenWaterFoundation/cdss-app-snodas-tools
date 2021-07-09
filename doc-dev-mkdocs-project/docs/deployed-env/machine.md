# Deployed Environment / Machine

The following sections describe how to install necessary software on a computer that will run the SNODAS tools.

### Linux Virtual Machine Computer

The target computer environment is as follows, in order to provide suitable processing capabilities, minimize ongoing cost,
and allow for system support:

* The Linux Ubuntu 20.04 LTS VM will be used - this will be stable and provide several years of support:
	+ Windowing environment for administration/support - Gnome? Mate? XFCE?
* Open Water Foundation needs access to install the software and provide support - sudo privileges would be good.
* Decent processor speed to run daily scheduled task - this machine will not initially be responding to real-time requests
(could expand to this in the future depending on success of the project)
* Local disk space for historical SNODAS grids and daily output snow products, to allow software to process - estimate is
~37 GB/year for years 2003+ and into the future, which through 2025 would be ~820 GB - start with 1 or 2 TB capacity?
Note that a nearly equivalent amount of space would be required in the Google Site to archive products for public access.
The local files are needed to process and static archive is used to provide public access.
* Network configuration needs to support pushing data to Google Site,
CDSS Map Viewer, and Colorado Information Marketplace, as discussed in upcoming sections.