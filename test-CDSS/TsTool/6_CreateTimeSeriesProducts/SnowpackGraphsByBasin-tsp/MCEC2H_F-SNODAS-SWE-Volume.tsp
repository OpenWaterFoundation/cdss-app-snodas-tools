[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "MCELMO CREEK - NR CO-UT BORDER (MCEC2H_F) SNODAS SWE Volume"
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

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2004]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2004"

[Data 1.2]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2005]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2005"

[Data 1.3]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2006]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2006"

[Data 1.4]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2007]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2007"

[Data 1.5]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2008]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2008"

[Data 1.6]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2009]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2009"

[Data 1.7]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2010]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2010"

[Data 1.8]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2011]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2011"

[Data 1.9]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2012]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2012"

[Data 1.10]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2013]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2013"

[Data 1.11]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2014]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2014"

[Data 1.12]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2015]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2015"

[Data 1.13]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2016]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2016"

[Data 1.14]

TSID = "MCEC2H_F.SNODAS.SWE-Volume.Day[2017]"
TSAlias = "MCEC2H_F-SNODAS-SWE-Volume-Day-2017"

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
Points = 0,8531,100,8531

[Annotation 1.2]

AnnotationID = "MeltoutLineLabel"
Color = black
Order = OnTopOfData
ShapeType = Text
XAxisSystem = Percent
YAxisSystem = Data
Text = 8531 acft = 25% of WY max SWE (34124 acft)
TextPosition = UpperLeft
FontSize = 12
FontStyle = Bold
Point = 100,8531
