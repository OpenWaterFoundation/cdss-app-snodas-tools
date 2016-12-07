# Development Tasks / Software Design

The SNODAS tools design meets the following requirements:

* Download historical and new daily SNODAS grids.
* Clip grids to Colorado basins boundary so that original SNODAS grid can be viewed as product later
(results in background layer that can be shown on maps).
* Intersect basin polygons with Colorado SNODAS grid to determine basin statistics including average snow water equivalent over basin
and areal extent of snow cover (allows color-coded basin maps to be shown).
* Create time series for a basin with daily history of statistics for individual basins and groups of basins
(allow graphs to be created for current year and past years).
* Publish the results to State of Colorado platforms to allow web access for water managers.

The above process is described for SNODAS tool users in the [SNODAS Tools User Manual](http://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-user/index.html").
The following diagram illustrates the overall data flow and technologies that are used
(to view the image full size, use the web browser feature to open the image in a new tab - for example, in Chrome right click and ***Open image in new tab***):

![SNODAS Tools System Diagram](software-design-images/SNODAS-Tools-System-Diagram-v1.png)

The following sections describe the data management and processing for each step, for the benefit of software developers and maintainers of implemented systems.

## Technical Approach

The approach for meeting the above requirements is to utilize free and open source QGIS/pyQGIS/GDAL/OGR and Python software
to provide GIS processing functionality and the CDSS TSTool software to provide time series processing functionality.

**TODO smalers 2016-12-06 fill this out with more background **

## SNODAS Tools Configuration

**TODO smalers 2016-12-06 describe how the tools are configured... configuration file, driving basins layer, Excel input, etc.**

## Data Management

**TODO smalers 2016-12-06 describe file structure for data mangement**

## Download SNODAS Data

Historical SNODAS data need to be downloaded for the full historical period to allow analysis of period statistics (how the current year
compares with previous years).  SNODAS data also need to be downloaded each day to create current basin water supply products.
The management of historical and daily downloads are the same, other than scripts are run differently in both cases.
The intent of the software is to allow rerunning the entire process if necessary, such as if installing the software on a new system.

### Download SNODAS Data (Historical)

**TODO smalers 2016-12-06 need to fill this in...describe how to run Python program and what it does**

### Download SNODAS Data (Each New Day)

**TODO smalers 2016-12-06 need to fill this in...describe how to run Python program and what it does**

## Clip SNODAS National Grids to Colorado

**TODO smalers 2016-12-06 need to fill this in...describe how to run Python program and what it does**

## Intersect SNODAS Colorado Grid with Colorado Basins and Calculate Statistics

**TODO smalers 2016-12-06 need to fill this in...describe how to run Python program and what it does**

## Generate Time Series Products

**TODO smalers 2016-12-06 need to fill this in...describe how to run Python program and what it does**

## Publish Results

**TODO smalers 2016-12-06 need to fill this in...describe how to pass the results to State of Colorado platforms including CDSS Map Viewer and Socrata data.colorado.gov**
