"""Request and response schemas for the HTTP API."""

from pydantic import BaseModel, Field


class Fields:
    """Shared annotated OpenAPI fields."""

    CONF: int = Field(
        title="confidence",
        description="detection confidence score",
        ge=0,
        le=100,
        examples=[75],
    )
    LAT: float = Field(
        title="latitude",
        description="latitude coordinate in WGS 84",
        ge=-90,
        le=90,
        examples=[48.8583],
    )
    LNG: float = Field(
        title="longitude",
        description="longitude coordinate in WGS 84",
        ge=-180,
        le=180,
        examples=[2.2945],
    )
    START: "LatLng" = Field(
        title="start",
        description="starting area coordinate",
        examples=[{"lat": 48.8583, "lng": 2.2945}],
    )
    END: "LatLng" = Field(
        title="end",
        description="ending area coordinate",
        examples=[{"lat": 48.8573, "lng": 2.2955}],
    )


class WasteBox(BaseModel):
    """Bounding box coordinates of detected waste."""

    conf: int = Fields.CONF
    x: int = Field(
        title="center x", description="center x coordinate in pixels", ge=0, examples=[35]
    )
    y: int = Field(
        title="center y", description="center y coordinate in pixels", ge=0, examples=[23]
    )
    w: int = Field(title="width", description="width in pixels", ge=0, examples=[45])
    h: int = Field(title="height", description="height in pixels", ge=0, examples=[23])

    @staticmethod
    def from_box(box) -> "WasteBox":
        x, y, width, height = (round(value) for value in box[:4])
        confidence = round(box[4] * 100)
        return WasteBox(conf=confidence, x=x, y=y, w=width, h=height)


class WastePos(BaseModel):
    """GPS coordinate of a detected waste."""

    conf: int = Fields.CONF
    lat: float = Fields.LAT
    lng: float = Fields.LNG

    @staticmethod
    def from_box(tile, box, zoom: int) -> "WastePos":
        from detectorLitter.geo.tiles import tile_box_to_gps

        normalized_x, normalized_y = box[5:]
        lat, lng = tile_box_to_gps(tile, (normalized_x, normalized_y), zoom)
        return WastePos(
            conf=round(box[4] * 100), lat=round(lat, 5), lng=round(lng, 5)
        )


class SearchInfo(BaseModel):
    """Summary of the tiles required by a search request."""

    nb_tiles: int = Field(
        title="nb tiles", description="number of tiles to fetch and analyze", ge=0
    )
    limit: int = Field(
        title="limit",
        description="maximum number of tiles processed in one request",
        ge=0,
    )
    limited: bool = Field(
        title="limited", description="whether the search exceeds its limit"
    )


class LatLng(BaseModel):
    lat: float = Fields.LAT
    lng: float = Fields.LNG

    def raw(self) -> tuple[float, float]:
        return self.lat, self.lng


class SearchRequest(BaseModel):
    start: LatLng = Fields.START
    end: LatLng = Fields.END
    conf: int | None = Field(
        title="confidence",
        description="detection confidence threshold",
        ge=0,
        le=100,
        default=None,
        examples=[75],
    )


class SearchInfoRequest(BaseModel):
    start: LatLng = Fields.START
    end: LatLng = Fields.END
