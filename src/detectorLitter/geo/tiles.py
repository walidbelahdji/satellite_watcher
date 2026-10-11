"""Conversion and iteration helpers for geographic tile coordinates."""

from .projection import RESOLUTION, Z0_RES, gps_to_mercator, mercator_to_gps


def gps_to_tile(lat: float, lng: float, zoom_level: int) -> tuple[int, int]:
    """Convert WGS 84 coordinates to Web Mercator tile coordinates."""
    x, y = gps_to_mercator.transform(lng, lat)
    resolution = RESOLUTION[zoom_level]
    row = int((Z0_RES - y) / resolution)
    col = int((x + Z0_RES) / resolution)
    return col, row


def tile_box_to_gps(
    tile: tuple[int, int], box: tuple[float, float], zoom_level: int
) -> tuple[float, float]:
    """Convert a tile-local point to latitude and longitude."""
    col, row = tile
    x, y = box
    resolution = RESOLUTION[zoom_level]
    x_box = ((col + x) * resolution) - Z0_RES
    y_box = Z0_RES - ((row + y) * resolution)
    lng, lat = mercator_to_gps.transform(x_box, y_box)
    return lat, lng


def tile_iter(start: tuple[float, float], end: tuple[float, float], zoom_level: int):
    """Yield tile coordinates covering two latitude/longitude corners."""
    min_lat, max_lat = min(start[0], end[0]), max(start[0], end[0])
    min_lng, max_lng = min(start[1], end[1]), max(start[1], end[1])
    start_row, start_col = gps_to_tile(max_lat, min_lng, zoom_level)
    end_row, end_col = gps_to_tile(min_lat, max_lng, zoom_level)
    return (
        (row, col)
        for row in range(start_row, end_row + 1)
        for col in range(start_col, end_col + 1)
    )
