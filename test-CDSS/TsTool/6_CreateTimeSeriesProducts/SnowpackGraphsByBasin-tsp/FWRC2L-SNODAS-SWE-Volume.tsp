[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "APISHAPA RVR (FWRC2L) SNODAS SWE Volume"
MainTitleFontSize = 16
MainTitleFontStyle = Bold
SubTitleString = "(Each line corresponds to a Water Year starting Oct 1)"

[SubProduct 1]

GraphType = "Line"
LeftYAxisTitleFontStyle = "Bold"
LeftYAxisTitleFontSize = "16"
LeftYAxisTitlePosition = "LeftOfAxis"
LeftYAxisTitleRotation = "270"
LeftYAxisTitleString = "Snow Water Equivalent (SWE) Volume (acft)"
LeftYAxisLabelPrecision = "0"
RightYAxisGraphType = "None"
RightYAxisIgnoreUnits = "false"
LayoutYPercent = ""

LeftYAxisLegendPosition = "Left"
LegendFormat = "SNODAS WY %z"

# Properties for each trace, one for each water year
# Colors are random except that the last year is highlighted with line width of 3

[Data 1.1]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2004]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2004"

[Data 1.2]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2005]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2005"

[Data 1.3]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2006]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2006"

[Data 1.4]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2007]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2007"

[Data 1.5]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2008]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2008"

[Data 1.6]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2009]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2009"

[Data 1.7]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2010]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2010"

[Data 1.8]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2011]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2011"

[Data 1.9]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2012]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2012"

[Data 1.10]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2013]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2013"

[Data 1.11]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2014]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2014"

[Data 1.12]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2015]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2015"

[Data 1.13]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2016]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2016"

[Data 1.14]

TSID = "FWRC2L.SNODAS.SWE-Volume.Day[2017]"
TSAlias = "FWRC2L-SNODAS-SWE-Volume-Day-2017"

Color = "Blue"
LineWidth = 3

[Annotation 1.1]

AnnotationID = "MeltoutLine"
Color = black
Order = BehindData
ShapeType = Line
XAxisSystem = Percent
YAxisSystem = Data
LineStyle = Solid
LineWidth = 2
Points = 0,9934.5,100,9934.5

[Annotation 1.2]

AnnotationID = "MeltoutLineLabel"
Color = black
Order = OnTopOfData
ShapeType = Text
XAxisSystem = Percent
YAxisSystem = Data
Text = 9935 acft = 25% of WY max SWE (39738 acft)
TextPosition = UpperLeft
FontSize = 12
FontStyle = Bold
Point = 100,9934.5
