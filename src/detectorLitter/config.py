"""Runtime settings loaded from environment variables and dotenv files."""

import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env", override=False)
load_dotenv(
    os.getenv("DETECTORLITTER_SERVER_ENV", "config/server.env"), override=False
)
load_dotenv(os.getenv("DETECTORLITTER_DEMO_ENV", "config/demo.env"), override=False)


def expect(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing config value {name}")
    return value


def integer(name: str) -> int:
    value = expect(name)
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"Config value {name}: expected integer got {value}") from error


def decimal(name: str) -> float:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing config value {name}")
    try:
        result = float(value)
    except ValueError as error:
        raise ValueError(f"Config value {name}: expected number got {value}") from error
    if not 0 <= result <= 1:
        raise ValueError(f"Config value {name}: expected a number between 0 and 1")
    return result


def number(name: str) -> float:
    value = expect(name)
    try:
        return float(value)
    except ValueError as error:
        raise ValueError(f"Config value {name}: expected number got {value}") from error


def boolean(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing config value {name}")
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Config value {name}: expected a boolean got {value}")


def url(name: str) -> str:
    value = expect(name)
    try:
        urlparse(value)
        return value
    except ValueError as error:
        raise ValueError(f"Config value {name}: expected url got {value}") from error


class ServerConfig:
    """Configuration used by the API server."""

    def __init__(self, report: bool = True):
        self.zoom = integer("TILE_ZOOM")
        self.endpoint = url("TILE_ENDPOINT")
        self.max_search = integer("MAX_SEARCH_TILES")
        self.model_path = Path(expect("MODEL_PATH"))
        self.detection_default_confidence = integer("DETECTION_DEFAULT_CONFIDENCE")
        self.detection_nms_score_threshold = decimal(
            "DETECTION_NMS_SCORE_THRESHOLD"
        )
        self.detection_nms_iou_threshold = decimal("DETECTION_NMS_IOU_THRESHOLD")
        self.api_host = expect("API_HOST")
        self.api_port = integer("API_PORT")
        self.api_title = expect("API_TITLE")
        self.api_version = expect("API_VERSION")
        self.api_summary = expect("API_SUMMARY")
        self.metrics_enabled = boolean("METRICS_ENABLED")
        self.metrics_host = expect("METRICS_HOST")
        self.metrics_port = integer("METRICS_PORT")
        if report:
            print(f"tiles zoom:     {self.zoom}")
            print(f"tiles endpoint: {self.endpoint}")
            print(f"search limit:   {self.max_search}")
            print(f"model path:     {self.model_path}")


class DemoConfig:
    """Configuration used by the Streamlit demo."""

    def __init__(self, report: bool = True):
        self.tile_endpoint = url("TILE_ENDPOINT")
        self.endpoint = url("DEMO_ENDPOINT")
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
        self.attribution = expect("DEMO_TILE_ATTRIBUTION")
        self.default_lat = number("DEMO_DEFAULT_LAT")
        self.default_lng = number("DEMO_DEFAULT_LNG")
        self.zoom = integer("DEMO_MAP_ZOOM")
        self.max_native_zoom = integer("DEMO_MAP_MAX_NATIVE_ZOOM")
        self.max_zoom = integer("DEMO_MAP_MAX_ZOOM")
        self.coordinate_step = number("DEMO_COORDINATE_STEP")
        self.coordinate_format = expect("DEMO_COORDINATE_FORMAT")
        self.map_control_scale = boolean("DEMO_MAP_CONTROL_SCALE")
        self.map_max_bounds = boolean("DEMO_MAP_MAX_BOUNDS")
        self.default_confidence = integer("DEMO_DEFAULT_CONFIDENCE")
        self.host = expect("DEMO_HOST")
        self.port = integer("DEMO_PORT")
        if report:
            print(f"tiles endpoint: {self.tile_endpoint}")
            print(f"tiles attribution: {self.attribution}")
            print(f"demo endpoint:  {self.endpoint}")
