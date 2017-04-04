[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "${BasinName} (${BasinID}) SNODAS SWE"
MainTitleFontSize = 16
MainTitleFontStyle = Bold
SubTitleString = "(Each line corresponds to a Water Year starting Oct 1)"

[SubProduct 1]

GraphType = "Line"
LeftYAxisTitleFontStyle = "Bold"
LeftYAxisTitleFontSize = "16"
LeftYAxisTitlePosition = "LeftOfAxis"
LeftYAxisTitleRotation = "270"
LeftYAxisTitleString = "Snow Water Equivalent, SWE (in)"
LeftYAxisLabelPrecision = "1"
RightYAxisGraphType = "None"
RightYAxisIgnoreUnits = "false"
LayoutYPercent = ""

LeftYAxisLegendPosition = "Left"
LegendFormat = "SNODAS WY %z"

# Properties for each trace, one for each water year
# Colors are random except that the last year is highlighted with line width of 3

<#list FirstWaterYear..LastWaterYear as waterYear>
[Data 1.${waterYear_index + 1}]

TSID = "${BasinID}.SNODAS.SWE.Day[${waterYear?c}]"
TSAlias = "${BasinID}-SNODAS-SWE-Day-${waterYear?c}"

<#if waterYear == LastWaterYear>
Color = "Blue"
LineWidth = 3
</#if>
</#list>
