"""Coordinate reference systems and Web Mercator tile constants."""

import pyproj

wgs84 = pyproj.CRS("EPSG:4326")
web_mercator = pyproj.CRS("EPSG:3857")
gps_to_mercator = pyproj.Transformer.from_crs(wgs84, web_mercator, always_xy=True)
mercator_to_gps = pyproj.Transformer.from_crs(web_mercator, wgs84, always_xy=True)

RESOLUTION = [40075017 / 2**zoom for zoom in range(0, 21)]
Z0_RES = RESOLUTION[0] / 2
