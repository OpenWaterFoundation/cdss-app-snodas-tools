[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "COTTONWOOD CRK (CBVC2) SNODAS SWE Volume"
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

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2004]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2004"

[Data 1.2]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2005]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2005"

[Data 1.3]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2006]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2006"

[Data 1.4]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2007]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2007"

[Data 1.5]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2008]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2008"

[Data 1.6]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2009]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2009"

[Data 1.7]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2010]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2010"

[Data 1.8]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2011]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2011"

[Data 1.9]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2012]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2012"

[Data 1.10]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2013]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2013"

[Data 1.11]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2014]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2014"

[Data 1.12]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2015]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2015"

[Data 1.13]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2016]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2016"

[Data 1.14]

TSID = "CBVC2.SNODAS.SWE-Volume.Day[2017]"
TSAlias = "CBVC2-SNODAS-SWE-Volume-Day-2017"

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
Points = 0,1882.5,100,1882.5

[Annotation 1.2]

AnnotationID = "MeltoutLineLabel"
Color = black
Order = OnTopOfData
ShapeType = Text
XAxisSystem = Percent
YAxisSystem = Data
Text = 1883 acft = 25% of WY max SWE (7530 acft)
TextPosition = UpperLeft
FontSize = 12
FontStyle = Bold
Point = 100,1882.5
