# Table of Contents

 - [Overview](#overview)
 - [Alignment of Basin Boundaries](#alignment-of-basin-boundaries)
 - [Handling of Water Bodies](#handling-of-water-bodies)
 - [Handling Elevation Zones](#handling-elevation-zones)
 - [Calculating Totals for Basin Groups](#calculating-totals-for-basin-groups)
 - [Calculating Percent of Melt-Out](#calculating-percent-of-melt-out)

## Overview
 
Details of calculations are not presented in this User Manual but are documented in the software code.
In most cases the calculations involve standard GIS features.  However, the following processing steps require more explanation.

## Alignment of Basin Boundaries

The alignment of basin boundaries is discussed in the [SNODAS Tools Data](../data/overview/) documentation.
Basin boundaries were adjusted to prevent double-counting and under-counting in snowpack statistics due to overlapping boundaries.

## Handling of Water Bodies



## Handling Elevation Zones

Elevation zones are used for basins in the Northern Colorado Water Conservancy District area because these zones are used
in streamflow forecast models.
The boundaries of the elevation zones do not overlap each other.
Therefore, each elevation zone can be considered as if a separate sub-basin within the larger basin.
The totals for the larger basin are calculated first by adding up elevations zones for a basin, and then basins are added to provide totals for a basin group.

## Calculating Totals for Basin Groups

Each smaller basin polygon (and elevation zones) in the basin layer is used to calculate snowpack statistics.
These statistics are used to visualize snowpack conditions in maps and graphs.
However, it is also useful to calculate totals for a group of basins, in order to align with streamflow forecast points that are used for water supply planning and decisions.

**TODO smalers 2016-12-11 need to describe how the data are configured to control these calculations and how the calculations occur.
Are the same statistics represented in the totals or are additional calculations done, such as converting SWE depth to ACFT volume?**

## Calculating Percent of Melt-Out

**TODO smalers 2016-12-11 Joe Busto indicated an interest in a graph showing percent of melt-out.  Steve needs to discuss with him to get an example.**


