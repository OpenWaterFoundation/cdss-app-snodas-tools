[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "Arkansas River at Pueblo Dam, CO (PDAC2) SNODAS SWE Volume"
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

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2004]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2004"

[Data 1.2]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2005]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2005"

[Data 1.3]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2006]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2006"

[Data 1.4]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2007]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2007"

[Data 1.5]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2008]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2008"

[Data 1.6]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2009]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2009"

[Data 1.7]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2010]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2010"

[Data 1.8]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2011]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2011"

[Data 1.9]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2012]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2012"

[Data 1.10]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2013]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2013"

[Data 1.11]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2014]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2014"

[Data 1.12]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2015]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2015"

[Data 1.13]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2016]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2016"

[Data 1.14]

TSID = "PDAC2.SNODAS.SWE-Volume.Day[2017]"
TSAlias = "PDAC2-SNODAS-SWE-Volume-Day-2017"

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
Points = 0,19,100,19

[Annotation 1.2]

AnnotationID = "MeltoutLineLabel"
Color = black
Order = OnTopOfData
ShapeType = Text
XAxisSystem = Percent
YAxisSystem = Data
Text = 19 acft = 25% of WY max SWE (76 acft)
TextPosition = UpperLeft
FontSize = 12
FontStyle = Bold
Point = 100,19
