# Comparing old and new QGIS values #

This file describes the steps taken 

## Algorithm Used ##

1. A for loop going through two elements in a list: 'old' and 'new'.
2. A for loop going through all basins in Colorado.
3. Read in the CSV file into a table from either the 'old' GCP VM, or 'new' Ubuntu VM.
4. Create the time series for SWE, Volume, and Snow cover.
5. After both loops have finished, compare using the many time series command by
location and data type, and write the difference to a table.

## Testing ##

Using the dates between 9-30-03 and 04-17-05, there should be about 191,000 entries
for each day for all 332 basins. Different testing properties are as follows (All
start and end times are between the above dates as well):

| Analysis Properties | Differences |
| ---- | ---- |
| Tolerance: .1 | 172,180 |
| Tolerance: 1 | 108,567 |

## Useful Information ##

* In the main tstool script located in `/opt/tstool-13.04.00.dev/bin/`, the line
setting the `javaCommand` variable was changed from `-Xmx1024m` to `-Xmx2048m`,
pushing memory from 1GB to 2GB.

* The local and GCP national tif files seem similar enough when compared, but the
local clipped Colorado tif file contained noticable differences from the VM. The
shown bodies of water seem to be more detailed, and in general more pixels are
dedicated to dislaying bodies of water. This could effect the basin area, and
subsequent equations later on, resulting in slightly different outcomes in acft
and other output properties.

## Outcome ##

The culprit here seems to be that the tif file being downloaded and used
from the NSIDC is different and has been updated to display bodies of water in more
detail. Since more pixels on this raster layer are considered water, that has
slightly changed the computed numbers by PYQGIS. Below are examples of the 'old' and
'new' Colorado tif files, three basins that contain updated/changed water body
boundaries & their statistics, and a close-up example of and 'old' and 'new'

### Colorado Old ###

![Colorado Old](../img/Colorado-old.png)

### Colorado New ###

![Colorado New](../img/Colorado-new.png)

### BMDC2L Basin ###

![BMDC2L Graph & Table](../img/BMDC2L-diff.png)

### BMDC2L Old ###

![BMDC2L Old](../img/BMDC2L-old.png)

### BMDC2L New ###

![BMDC2L New](../img/BMDC2L-new.png)

### TLRC2 Basin ###

![TLRC2](../img/TLRC2-diff.png)

### TPIC2L Basin ###

![TPIC2L](../img/TPIC2L-diff.png)