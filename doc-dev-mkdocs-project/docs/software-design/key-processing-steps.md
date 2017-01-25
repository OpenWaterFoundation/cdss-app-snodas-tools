# Table of Contents 

The following topics are discussed in this section:

* [Overview](#overview)
* [Handling Overlapping Basin Boundaries](#handling-overlapping-basin-boundaries)
* [Handling Pixels Overlapped by Multiple Features](#handling-snodas-pixels-overlapped-by-multiple-features)
* [Handling Large Bodies of Water](#handling-large-bodies-of-water)
* [Handling Missing Values](#handling-missing-snodas-values)
* [Handling Elevation Zones](#handling-elevation-zones)

# Handling Overlapping Basin Boundaries


# Handling SNODAS Pixels Overlapped by Multiple Features

The QGIS Zonal Statistics tool produces correct statistics even if the features of the [Watershed Basin Shapefile Input](file-structure.md#snodastools92staticdata92)
are overlapping. 

Often times watershed basin shapefiles have overlapping polygon features due to the combining of datasets, overlaying of reservoir boundaries, etc. With the ArcGIS 
zonal statistics tool, this overlapping phenomemnon creates inaccurate results. This is because the ArcGIS zonal statisitcs tool converts the vector input zonal dataset 
into a raster grid before processing the statistics. Raster grid pixels can only be classified by one feature of the input zonal dataset. Therefore, if a SNODAS pixel 
is overlapped by two or more basins of the input zonal dataset, only one of the basins will include the pixel's SNODAS value. 

Fortunately, the QGIS Zonal Statistics tool iterates over each feature independently to calculate the statistics creating accurate statistics for both independent and 
overlapping polygons.  The code for the QGIS Zonal Statistics tool can be viewed 
[here](https://github.com/qgis/QGIS/blob/a2f51260db5357917e86b78f1bb2915379d670dd/src/analysis/vector/qgszonalstatistics.cpp).

# Handling Large Bodies of Water
## Calculating SNODAS Statistics
## Calculating Snow Cover Statistics
# Handling Missing SNODAS Values
# Handling Elevation Zones