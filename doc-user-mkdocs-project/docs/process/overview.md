**Overview**

This section is provided to explain the process implemented by the SNODAS Tools,
to allow users of the data products to better understand features and limitations of the data and processes.
Note that the SNODAS Tools can be used to calculate snowpack statistics for study areas other than Colorado. For 
the purpose of this documentation, however, the process of the SNODAS Tools is explained using Colorado data 
for which the SNODAS Tools were originally designed. Refer to the `SNODAS Tools Developer Manual`
for information regarding how to use the SNODAS Tools to calculate snowpack statistics for other study areas. 

In broad terms, the SNODAS Tools perform the following steps:

1. [Download Daily SNODAS Data](processing-steps.md#download-snodas-data)
2. [Clip National SNODAS Grid to Colorado](processing-steps.md#clip-national-snodas-grid-to-colorado)
3. [Intersect SNODAS Colorado Grid with Colorado Basins and Calculate Snowpack Statistics](processing-steps.md#intersect-snodas-colorado-grid-with-colorado-basins-and-calculate-statistics)
4. [Generate Time Series Snowpack Products](processing-steps.md#generate-time-series-snowpack-products)

These steps are performed using the free and open source Geographic Information System (GIS) software [QGIS/pyQGIS/GDAS/OGR software](http://www.qgis.org/en/site/).
Detailed information about the SNODAS Tools software can be found in the SNODAS Tools Developer Manual.



