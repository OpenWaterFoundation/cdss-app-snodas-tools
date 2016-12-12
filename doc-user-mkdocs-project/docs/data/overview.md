# SNODAS Tools Data / Overview

The SNODAS tools utilize the Snow Data Assimilation System (SNODAS) national data grids.

## SNODAS Data Grids

The Snow Data Assimilation System (SNODAS) Data Products are hosted by the National Snow and Ice Data Center (NSIDC) and 
developed by the NOAA National Weather Service’s National Operational Hydrologic Remote Sensing Center (NOHRSC).  For the 
purpose of this documentation, the relevant information regarding this specific project will be explained. All of this 
information and more is described in detail at [http://nsidc.org/data/docs/noaa/g02158_snodas_snow_cover_model/]

Multiple national raster grids have been and continue to be created for each day. There are 8 parameters of data that are 
produced – Snow Water Equivalent (SWE), Snow Depth, Snow Melt Runoff at the Base of Snow Pack, Sublimation from the Snow Pack, 
Sublimation of Blowing Snow, Solid Precipitation, Liquid Precipitation, and Snow Pack Average Temperature. For the purpose 
of this project, the only interested parameter is that of Snow Water Equivalence. 

The data is packaaged in two formats: masked or unmasked data. The masked data is clipped to the contiguous US while the unmasked 
data extends to cover a larger area. For the purpose of this project, the unmasked data was the more appropriate size and was 
the chosen avenue for data assimilation. 

The temporal coverage of the data begins on October 01, 2003 and extends to the 
current date. For the purpose of this project, all available data file were downloaded starting in October of 2003. 

The raster datasets are stored on the following FTP site: [ftp://sidads.colorado.edu] under the pathname /DATASETS/NOAA/G02158/masked/]. 
This directory has folders indicating the years of which the data temporally covers. In each year’s folder, there are folders indicating 
each month of the year. The 8 daily rasters store within zipped daily .tar files located in each specific month.  The .tar files follow the 
naming convention of ‘SNODAS_YYYYMMDD.tar’. 


**TODO smalers 2016-12-10 provide SNODAS resources and links and explain generally what SNODAS is,
as well as benefits and limitations, mention that SNODAS is distributed whereas SNOTEL and snow course are measurements at sites.
Note that people want to correlate SNOTEL with SNODAS but that can be difficult.
Explain that SNODAS grids are national at X km scale, etc.
Explain how SNODAS model and data file format has changed over time and this project converts to consistent format.
This project does the intersection with basin data because the SNODAS basins changed over time - see original proposal language.
Split into sections as appropriate.**

## Colorado Basins

**TODO smalers 2016-12-11 explain that basins are small HUC-?? and align with National Weather Service (NWS) forecast basins.
Smaller basins are aggregated to larger totals.
Elevation zones are used in the basins included in the Northern Colorado Water Conservancy District boundary (Upper Colorado and Poudre Basins),
and are also accumuated to produce a total for a basin.  Provide a screen shot and ability to download.**

The basin boundaries for Colorado were defined using input from four NWS River Forecast Centers.
The separate boundary spatial data layers were adjusted to ensure that basin boundaries did not overlap or have gaps.
This ensures that SNODAS values are not under or over-counted.
Where adjustments were made, edits were documented in the **TODO smalers need to indicate how the edits are tracked**.

The basin boundary layers are available from the following links:

* **TODO smalers 2016-12-11 Include URL for the Colorado basins layer**
* **TODO smalers 2016-12-11 Include URL for the basin list Excel file and CSV file if available**
* **TODO smalers 2016-12-11 Include URL for each RFC's original layer**
