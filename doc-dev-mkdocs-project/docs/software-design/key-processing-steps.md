# Table of Contents 

The following topics are discussed in this section:

* [Handling Overlapping Basin Boundaries](#handling-overlapping-basin-boundaries)
* [Handling Cells Overlapped by Multiple Features](#handling-snodas-cells-overlapped-by-multiple-features)
* [Handling Large Bodies of Water](#handling-large-bodies-of-water)	
	- [Calculating SNODAS SWE Statistics](#calculating-snodas-swe-statistics)
	- [Calculating Snow Cover Statistics](#calculating-snow-cover-statistics)
* [Handling Missing Values](#handling-missing-snodas-values)
* [Handling Elevation Zones](#handling-elevation-zones)


# Handling Overlapping Basin Boundaries

The QGIS Zonal Statistics tool produces correct statistics even if the features of the [Watershed Basin Shapefile Input](file-structure.md#snodastools92staticdata92)
are overlapping.   

Below is an example of overlapping features in a shapefile. The dark grey lines represent basin boundaries and the red circles pinpoint the areas of overlap. 

<center>![Overlapping Features](key-processing-images/overlaps.png)</center>

Often watershed basin shapefiles have overlapping polygon features due to the combining of datasets, overlaying of reservoir boundaries, etc. With the ArcGIS 
zonal statistics tool, this overlapping phenomenon creates inaccurate results. This is because the ArcGIS zonal statistics tool converts the vector input zonal dataset 
into a raster grid before processing the statistics. Raster grid cells can only be classified by one feature of the input zonal dataset. Therefore, if a SNODAS cell 
is overlapped by two or more basins of the input zonal dataset, only one of the basins will include the cell's SNODAS value. 

Fortunately, the QGIS Zonal Statistics tool iterates over each feature independently to calculate the statistics creating accurate statistics for both independent and 
overlapping polygons.  The code for the QGIS Zonal Statistics tool can be viewed 
[here](https://github.com/qgis/QGIS/blob/a2f51260db5357917e86b78f1bb2915379d670dd/src/analysis/vector/qgszonalstatistics.cpp).


# Handling SNODAS cells Overlapped by Multiple Features

The QGIS Zonal Statistic tool calculates statistics on the daily SNODAS raster cells inside of each basin feature. There are scenarios, however, where a SNODAS cell is 
split by a basin boundary causing the cell to be in two different polygon features at once. However, each raster cell can only be assigned to one polygon. QGIS zonal statistics
use the location of the cell's center to determine which polygon the cell "belongs".The only scenario where this is not true is if the cell resolution is larger than the 
polygon area. In that scenario the statistics are based off of weighted proportions. For more infomation about weighted proportions, reference 
[line 329](https://github.com/qgis/QGIS/blob/a2f51260db5357917e86b78f1bb2915379d670dd/src/analysis/vector/qgszonalstatistics.cpp#L329) of the QGIS Zonal Statistics 
code. 

An example of the daily SNODAS cells overlapped by multiple features is shown below. The red line is a basin boundary. The green dots represent the center point of each cell.
Using the cell center technique, cell 1 is used to calculate the zonal statistics of the lower-right basin whereas cell 2 is used to calculate the zonal statistics of the 
upper-left basin.

<center>![Overlapped Cells](key-processing-images/assign-pixel.png)</center>

# Handling Large Bodies of Water

Snowfall on large bodies of water, like a lake or reservoir, will react considerably differently than snowfall on ground. 


### Calculating SNODAS SWE Statistics

To mitigate data errors due to this phenomenon the SNODAS model applies an open water mask to the landscape assigning open water cells a null value of '55527'. 
 The QGIS Zonal Statistics tool disregards cells with no-data values when calculating all output statisiics - count, mean, etc. 
 The SWE statistics, therefore, are only representative of non-water areas.

The aerial image on the top is of the Eleven Mile Reservoir in Colorado (the basin is outlined in red). The image on the bottom is Eleven Mile Reservoir atop a daily SNODAS 
raster grid. The grid is set to color null values as white. As shown, the open water body is not included in the SNODAS grid. 
 
 <center>![Aerial Imagery](key-processing-images/water-null-image.png)</center>   
  
 <center>![Raster SNODAS](key-processing-images/water-null-raster.png)</center> 
 
### Calculating Snow Cover Statistics

For each basin, the areal snow cover statistic is calculated by dividing:  
<center> _the sum of cells covered by snow_ in the basin  
 by  
 _the total count of cells_ in the basin.  </center>  
 
*The sum of cells covered by snow* is calculated by using the QGIS Zonal Statisitcs sum tool on the 
[binary ```SNODAS_SnowCover_ClipandReprjYYYYMMDD.tif``` raster](file-structure.md#processeddata924_createsnowcover92).
The binary snow cover raster contains the value of ```1``` for any cell with a SWE value ```greater than 0``` (there is some presence of snow on 
the ground). Therefore, the sum of the cells within each basin is indicative of how many cells within each basin are covered by snow. Cells that are
not included in the sum are those valued at ```0``` (SWE values of ```0```) and those of no-data value. 

*The total count of cells* in each basin is calculated by using the QGIS Zonal Statistics count tool on the [```SNODAS_SWE_ClipAndReprojYYYMMDD.tif``` raster](file-structure.md#processeddata923_cliptoextent92).
The QGIS Zonal Statisics tool does not count cells of no-data values. 

Cells representing large bodies of water are not included in either the *sum of cells covered by snow* or the *total count of cells*. The aeral snow cover statistic, therfore, 
describes the approximate percentage of land in each basin (non-water) covered by some value of snow. 

# Handling Missing SNODAS Values

The no-data value of SNDOAS products is set to -9999. This is set in the SNODAS Tools' [configuration file](file-structure.md#snodastools92snodasconfigini). 
If the SNODAS no-data value is changed, it is pertinent that the new value is entered in the configuration file under section ```SNODAS_FTPSite``` option ```null_value```. 
The configured null_value variable is used in the [SNODAS_raster_clip](overview.md#3-clip-and-project-snodas-national-grids-to-study-area) function and the 
[SNODAS_raster_reproject_NAD83](overview.md#3-clip-and-project-snodas-national-grids-to-study-area) function of the 
```SNODAS_utilities.py``` script to set the no-data value of the clipped SNODAS grid to the original no-data value of the SNODAS national dataset.

# Handling Elevation Zones

** egiles TODO 1/26/17 add elevation zones content - there has been discussion on how we want to work with local_id vs total_id. I am going to wait to write this content
until we further discuss the topic with Amy on 2/8**