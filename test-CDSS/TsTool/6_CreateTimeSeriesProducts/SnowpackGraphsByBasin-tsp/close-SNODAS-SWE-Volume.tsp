[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "CLOSED BASIN (close) SNODAS SWE Volume"
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

TSID = "close.SNODAS.SWE-Volume.Day[2004]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2004"

[Data 1.2]

TSID = "close.SNODAS.SWE-Volume.Day[2005]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2005"

[Data 1.3]

TSID = "close.SNODAS.SWE-Volume.Day[2006]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2006"

[Data 1.4]

TSID = "close.SNODAS.SWE-Volume.Day[2007]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2007"

[Data 1.5]

TSID = "close.SNODAS.SWE-Volume.Day[2008]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2008"

[Data 1.6]

TSID = "close.SNODAS.SWE-Volume.Day[2009]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2009"

[Data 1.7]

TSID = "close.SNODAS.SWE-Volume.Day[2010]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2010"

[Data 1.8]

TSID = "close.SNODAS.SWE-Volume.Day[2011]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2011"

[Data 1.9]

TSID = "close.SNODAS.SWE-Volume.Day[2012]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2012"

[Data 1.10]

TSID = "close.SNODAS.SWE-Volume.Day[2013]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2013"

[Data 1.11]

TSID = "close.SNODAS.SWE-Volume.Day[2014]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2014"

[Data 1.12]

TSID = "close.SNODAS.SWE-Volume.Day[2015]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2015"

[Data 1.13]

TSID = "close.SNODAS.SWE-Volume.Day[2016]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2016"

[Data 1.14]

TSID = "close.SNODAS.SWE-Volume.Day[2017]"
TSAlias = "close-SNODAS-SWE-Volume-Day-2017"

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
Points = 0,85499.25,100,85499.25

[Annotation 1.2]

AnnotationID = "MeltoutLineLabel"
Color = black
Order = OnTopOfData
ShapeType = Text
XAxisSystem = Percent
YAxisSystem = Data
Text = 85499 acft = 25% of WY max SWE (341997 acft)
TextPosition = UpperLeft
FontSize = 12
FontStyle = Bold
Point = 100,85499.25
