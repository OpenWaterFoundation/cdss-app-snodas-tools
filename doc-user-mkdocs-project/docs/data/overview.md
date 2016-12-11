# SNODAS Tools Data / Overview

The SNODAS tools utilize the Snow Data Assimilation System (SNODAS) national data grids.

## SNODAS Data Grids

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
