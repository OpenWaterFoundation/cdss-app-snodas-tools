# Convert layer CRS to Albers equal area (EPSG 102003) for use in SNODAS Tools.
ReadGeoLayerFromShapefile(InputFile="globalwatershed.shp",GeoLayerID="BasinBoundary",Description="Basin boundary for SNODAS Tools")
SetGeoLayerCRS(GeoLayerID="BasinBoundary",CRS="ESRI:102003")
# Add an attribute LOCAL_ID that is the basin identifier:
# - HUC14 code is 140100051606 but is ugly so use a human-readable name
# - see: https://water.usgs.gov/lookup/getwbd?140100051606
SetGeoLayerAttribute(GeoLayerID="BasinBoundary",AttributeName="LOCAL_ID",AttributeValue="MonumentCreek")
# Write the updated shapefile.
WriteGeoLayerToShapefile(GeoLayerID="BasinBoundary",OutputFile="../globalwatershed-Albers.shp")
WriteGeoLayerToGeoJSON(GeoLayerID="BasinBoundary",OutputFile="../globalwatershed.geojson")