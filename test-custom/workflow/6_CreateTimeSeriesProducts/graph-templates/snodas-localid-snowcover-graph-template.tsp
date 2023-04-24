[Product]

ProductType = "Graph"
TotalWidth = "850"
TotalHeight = "600"
MainTitleString = "${BasinName} (${BasinID}) SNODAS Snow Cover"
MainTitleFontSize = 16
MainTitleFontStyle = Bold
SubTitleString = "(Each line corresponds to a Water Year starting Oct 1)"

[SubProduct 1]

GraphType = "Line"
LeftYAxisTitleFontStyle = "Bold"
LeftYAxisTitleFontSize = "16"
LeftYAxisTitlePosition = "LeftOfAxis"
LeftYAxisTitleRotation = "270"
LeftYAxisTitleString = "Snow Cover (percent of non-waterbody basin area)"
LeftYAxisLabelPrecision = "0"
RightYAxisGraphType = "None"
RightYAxisIgnoreUnits = "false"
LayoutYPercent = ""

LeftYAxisLegendPosition = "Right"
LegendFormat = "SNODAS WY %z"

# Properties for each trace, one for each water year
# Colors are random except that the last year is highlighted with line width of 3

<#--
<#list FirstWaterYear..LastWaterYear as waterYear>
-->
<#list LastWaterYear..LastWaterYear as waterYear>
[Data 1.${waterYear_index + 1}]

TSID = "${BasinID}.SNODAS.SnowCover.Day[${waterYear?c}]"
TSAlias = "${BasinID}-SNODAS-SnowCover-Day-${waterYear?c}"

<#if waterYear == LastWaterYear>
Color = "Blue"
LineWidth = 2
</#if>
</#list>
