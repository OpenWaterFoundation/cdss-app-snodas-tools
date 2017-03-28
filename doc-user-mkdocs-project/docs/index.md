# SNODAS Tools / User Manual

This documentation is written for SNODAS Tools users, and in particular users of the SNODAS Tools data products.

The SNODAS Tools generate water supply data products from SNODAS data
to provide data products to State agency and other agency water managers.
The tools are intended to be run daily by technical staff at the Colorado Water Conservation Board, or other State entity.

## Project Background

The SNODAS Tools software is developed by the [Open Water Foundation](http://openwaterfoundation.org)
for the [Colorado Water Conservation Board](http://cdss.state.co.us).

## Overview of SNODAS Tools

The SNODAS Tools calculate daily approximate snowpack zonal statistics of a given input basin boundary shapefile. For each feature, or basin, of the 
input basin boundary shapefile, the SNODAS Tools estimate the following statistics:

|<center>Daily Statistic|<center>Default <br> or <br> Optional</center>|<center>Description|<center>Units|
|-|-|-|-|
|Mean Snow Water Equivalent (SWE)|Default|The mean amount of water contained within the snowpack.|Inches and Millimeters|
|Effective Area|Default|The approximate area excluding large bodies of water.|Square Miles|
|Percent of Snow Cover|Default|The percent of effective area covered by snow.|Unitless|
|Snow Volume|Default|The amount of water contained in the entire basin's snowpack. Calculated by multiplying the daily mean SWE value by the daily effective area value.|Acre Feet|
|1 Week Change in Snow Volume|Default|The difference between the current date's snow volume value compared to the snow volume value calculated 7 days prior. If positive, the snowpack volume has increased. If negative, the snowpack volume has decreased.| Acre Feet|
|Minimum SWE|Optional|The daily minimum SWE value.| Inches and Millimeters|
|Maximum SWE|Optional|The daily maximum SWE value.|Inches and Millimeters|
|Standard Deviation of SWE|Optional|A measurement of variation in the basin's daily SWE values.|Inches and Millimeters|

*Note* - *The optional statistics will not be calculated unless they are configured in the [configuration file](http://software.openwaterfoundation.org/cdss-app-snodas-tools-doc-dev/software-design/file-structure/#snodastools92snodasconfigini)
prior to utilizing the SNODAS Tools.*

The results of the SNODAS Tools can be manipulated to produce 
visually-enticing choropleth maps displaying the various snowpack statistics. The SNODAS tools also create time-series graphs
displaying changes in the snowpack statistics over time.  

Although specifically designed for Colorado watersheds, the SNODAS Tools can be utilized to estimate snowpack statistics for any area in the 
contiguous United States (the bounds of the masked SNODAS data limit the extent of statistical processing – see 
the [Input Data](../data/data#snodas-data-grids) section for further details).

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
