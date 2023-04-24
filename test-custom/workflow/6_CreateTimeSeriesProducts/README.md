# 6_CreateTimeSeriesProducts #

This folder contains the files needed by TSTool software to generate graphical data products.
The output products are placed in the
`../../processesData/6_CreateTimeSeriesProducts/SnowpackGraphsByBasin` folder.

This allows the workflow files that don't often change to be maintained separately from the dynamic output files.
This folders files include:

| **File** | **Description** |
| -- | -- |
| | **TSTool command file** |
| `create-snodas-swe-graphs.tstool` | TSTool command file to create graph image files from the SNODAS analysis results. |
| `create-snodas-swe-graphs-tstool-control.txt` | Use this file to set the current day to a historical day, if graphs should be generated as if a historical date.  Comment out the properties to ignore values in the file. |
| | **Graph template files in `graph-templates/` folder** |
| `snodas-localid-snowcover-graph-template.tsp` | Time series product template file for the snow cover graph. |
| `snodas-localid-swe-graph-template.tsp` | Time series product template file for the snow water equivalent (SWE) basin average depth (inches) graph. |
| `snodas-localid-swe-volume-graph-template.tsp` | Time series product template file for the snow water equivalent (SWE) basin volume (acre-feet) graph. |
| `snodas-localid-swe-volume-1weekchange-graph-template.tsp` | Time series product template file for the snow water equivalent (SWE) basin volume 1-week change (acre-feet) graph. |
| `snodas-localid-swe-volume-gain-cumulative-graph-template.tsp` | Time series product template file for the snow water equivalent (SWE) basin cumulative volume gain (acre-feet) graph. |
| `snodas-localid-upstreamtotal-swe-volume-graph-template.tsp` | Time series product template file for the snow water equivalent (SWE) basin and upstream basins volume (acre-feet) graph. |
| `snodas-localid-upstreamtotal-swe-volume-gain-cumulative-graph-template.tsp` | Time series product template file for the snow water equivalent (SWE) basin and upstream basins cumulative volume gain (acre-feet) graph. |

