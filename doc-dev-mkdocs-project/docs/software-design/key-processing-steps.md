# Table of Contents 

The following topics are discussed in this section:

* [Overview](#overview)
* [Handling Overlapping Basin Boundaries](#handling-overlapping-basin-boundaries)
* [Handling Cells Overlapped by Multiple Features](#handling-snodas-cells-overlapped-by-multiple-features)
* [Handling Large Bodies of Water](#handling-large-bodies-of-water)
* [Handling Missing Values](#handling-missing-snodas-values)
* [Handling Elevation Zones](#handling-elevation-zones)

# Overview

** egiles TODO 1/26/17 add overview content**

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
split by a basin boundary causing the cell to be in two different polygon features at once. The entire cell, however, must be assigned to only one polygon feature.
The QGIS Zonal Statistics tool assigns the raster cell to the polygon that has the largest proportion of the cell within its boundaries.  

An example of the daily SNODAS cells overlapped by multiple features is shown below. The red line is a basin boundary. Using the largest proportion technique, cell 1
is used to calculate the zonal statistics of the lower-right basin whereas cell 2 is used to calculate the zonal statistics of the upper-left basin.

<center>![Overlapped Cells](key-processing-images/assign-pixel.png)</center>

# Handling Large Bodies of Water

Snowfall on large bodies of water, like a lake or reservoir, will react considerably differently than snowfall on ground. 


## Calculating SNODAS Statistics

To mitigate data errors due to this phenomenon
the SNODAS model applies an open water mask to the landscape assigning open water cells a null value of '55527'. The SWE statistics, therefore, are only representative 
of non-water areas. 

The aerial image on the top is of the Eleven Mile Reservoir in Colorado (the basin is outlined in red). The image on the bottom is Eleven Mile Reservoir atop a daily SNODAS 
raster grid. The grid is set to color null values as white. As shown, the open water body is not included in the SNODAS grid. 
 
 <center>![Aerial Imagery](key-processing-images/water-null-image.png)</center>   
  
 <center>![Raster SNODAS](key-processing-images/water-null-raster.png)</center> 
 
## Calculating Snow Cover Statistics

** egiles TODO 1/26/17 explain the Snow Coverage percentage statistics and how it is affected by the open water mask. I need to talk to Steve first. The way I have the snow
cover statistic now is that the valuation of presence/absence of snow comes from the SWE grid (so null bodies of water will not be included in the snow cover area.). But
to calculate the statistic, the total cells with presence is divided over the total count of cells in the polygon. This will mean that even null values are included in 
the total sum and will therefore make some basin snow coverage percent never to reach 100%** 

# Handling Missing SNODAS Values

** egiles TODO 1/26/17 add missing SNODAS values content - i have done initial research on this and can only find a few sources. Need to talk to Steve about the objectives
of this topic. All I know to include is that null values are included as -9999.**

# Handling Elevation Zones

** egiles TODO 1/26/17 add elevation zones content - there has been discussion on how we want to work with local_id vs total_id. I am going to wait to write this content
until we further discuss the topic with Amy**