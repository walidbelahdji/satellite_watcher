"""Prometheus metrics used by API operations."""

from prometheus_client import Counter, Histogram, start_http_server
from prometheus_client.context_managers import Timer

_request_search_count = Counter(
    "requests_search_count", "Number of processed search requests"
)
_request_detect_count = Counter(
    "requests_detect_count", "Number of processed detect requests"
)
_detection_duration = Histogram("detection_seconds", "Detection time in seconds")
_search_tile_count = Histogram("nb_search_tiles", "Number of tiles per search request")


def log_request_search(nb_tiles: int) -> None:
    _request_search_count.inc()
    _search_tile_count.observe(nb_tiles)


def log_request_detect() -> None:
    _request_detect_count.inc()


def time_detection() -> Timer:
    return _detection_duration.time()


def start_metrics_server(host: str, port: int) -> None:
    """Start the Prometheus exporter on the configured address."""
    start_http_server(port, addr=host)
