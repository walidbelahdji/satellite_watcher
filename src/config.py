"""Env config parser"""

import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def expect(name: str) -> str:
    env = os.getenv(name)
    assert env is not None, f"Missing config value {name}"
    return env


def integer(name: str) -> int:
    env = expect(name)
    assert env.isdigit(), f"Config value {name}: expected integer got {env}"
    return int(env)


def url(name: str) -> str:
    env = expect(name)
    try:
        urlparse(env)
        return env
    except ValueError:
        raise Exception(f"Config value {name}: expected url got {env}")


class ServerConfig:
    """sky-watcher server config"""

    zoom: int
    endpoint: str

    def __init__(self, report: bool = True):
        self.zoom = integer("TILE_ZOOM")
        self.endpoint = url("TILE_ENDPOINT")
        self.max_search = integer("MAX_SEARCH_TILES")
        if report:
            print(f"tiles zoom:     {self.zoom}")
            print(f"tiles endpoint: {self.endpoint}")
            print(f"search limit:   {self.max_search}")


class DemoConfig:
    """sky-watcher demo server config"""

    endpoint: str
    tile_endpoint: str
    attribution: str

    def __init__(self, report: bool = True):
        self.tile_endpoint = url("TILE_ENDPOINT")
        self.endpoint = url("DEMO_ENDPOINT")
        self.attribution = expect("DEMO_TILE_ATTRIBUTION")

        if report:
            print(f"tiles endpoint: {self.tile_endpoint}")
            print(f"tiles attribution: {self.attribution}")
            print(f"demo endpoint:  {self.endpoint}")
