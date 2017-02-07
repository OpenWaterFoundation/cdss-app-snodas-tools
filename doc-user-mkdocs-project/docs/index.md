# SNODAS Tools / User Manual

This documentation is written for SNODAS tools users, and in particular users of the SNODAS tools data products.

The SNODAS Tools generate water supply data products from SNODAS
to provide data products to State agency and other agency water managers.
The tools are intended to be run daily by technical staff at the Colorado Water Conservation Board, or other State entity.

## Project Background

The SNODAS Tools software is being developed by the [Open Water Foundation](http://openwaterfoundation.org)
for the [Colorado Water Conservation Board](http://cdss.state.co.us).

## Overview of SNODAS Tools

The SNODAS Tools calculate daily approximate snowpack zonal statistics of a given input basin boundary shapefile. They estimate 
daily mean Snow Water Equivalence (SWE), daily minimum SWE, daily maximum SWE, daily SWE standard deviation, pixel count of the basin (with respect 
to the properties of the SNODAS raster), and daily percentage of land covered by snow. The results of the toolset can be manipulated to produce 
visually-enticing choropleth maps displaying the various snowpack statistics. Graphs can also be formed to display temporal changes in the SWE statistics 
across the landscape. These two final visual products are available to display the snowpack landscape over space and time. 

Although the toolset was specifically designed for Colorado watersheds, it can also be utilized to estimate the snowpack statistics of any area in the 
contiguous United States (the bounds of the masked SNODAS data limit the extent of statistical processing – see [SNODAS Data](../data/overview#snodas-data-grids)). 

## About the Colorado Water Conservation Board

The [Colorado Water Conservation Board (CWCB)](http://cwcb.state.co.us) is the State entity responsible for water supply planning policy and programs.

**TODO smalers 2016-12-09 need link from Joe Busto explaining snow programs - Steve emailed Joe**

## About the Open Water Foundation

The Open Water Foundation (OWF, [openwaterfoundation.org](http://openwaterfoundation.org)) is a 501(c)3 social enterprise
nonprofit that focuses on developing and supporting open source software to make better
decisions about water resources.  This documentation is the result of an OWF project funded by the CWCB.

OWF has created this website to facilitate access to documentation about using the SNODAS data products. 

For more information about OWF, visit the [OWF website](http://openwaterfoundation.org).

## How to Use this Documentation

This documentation is organized to explain the SNODAS tools process and data products, including the following main sections:

* [SNODAS Data](data/overview) - background on SNODAS data and comparison to SNOTEL
* [SNODAS Tools Process](process/overview) - explain how raw SNODAS data are processed to create water supply data products that can be used to make decisions
* [SNODAS Tools Products](products/overview) - explanation of each data product, how to access and use

## Contact

**TODO smalers 2016-12-06 need to determine contact for support... State?... OWF?**
