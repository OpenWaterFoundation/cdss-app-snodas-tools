[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "${BasinName} (${BasinID}) SNODAS SWE Volume"
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

LeftYAxisLegendPosition = "Right"
LegendFormat = "SNODAS WY %z"

# Properties for each trace, one for each water year
# Colors are random except that the last year is highlighted with line width of 3

<#list FirstWaterYear..LastWaterYear as waterYear>
[Data 1.${waterYear_index + 1}]

TSID = "${BasinID}.SNODAS.SWE-Volume.Day[${waterYear?c}]"
TSAlias = "${BasinID}-SNODAS-SWE-Volume-Day-${waterYear?c}"

<#if waterYear == LastWaterYear>
Color = "Blue"
LineWidth = 3
</#if>
</#list>

<#if SNODASSWEVolume25PercentComputed == "true">
[Annotation 1.1]

AnnotationID = "MeltoutLine"
Color = black
Order = BehindData
ShapeType = Line
XAxisSystem = Percent
YAxisSystem = Data
LineStyle = Solid
LineWidth = 2
Points = 0,${CurrentWaterYearMaxSNODASSWEVolume_25Percent?c},100,${CurrentWaterYearMaxSNODASSWEVolume_25Percent?c}

[Annotation 1.2]

AnnotationID = "MeltoutLineLabel"
Color = black
Order = OnTopOfData
ShapeType = Text
XAxisSystem = Percent
YAxisSystem = Data
Text = ${AnnotationLabel25PercentVolume}
TextPosition = UpperLeft
FontSize = 12
FontStyle = Bold
Point = 100,${CurrentWaterYearMaxSNODASSWEVolume_25Percent?c}
</#if>
