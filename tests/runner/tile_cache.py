"""Download tile images referenced by geographic search fixtures."""

import json
import shutil
from pathlib import Path

import requests

from detectorLitter.config import ServerConfig
from detectorLitter.geo.tiles import tile_iter


def scrape_tiles(fixtures: list[tuple[dict, Path]], data_dir: Path) -> None:
    """Refresh the offline tile cache needed by the search fixtures."""
    tile_dir = data_dir / "tiles"
    try:
        shutil.rmtree(tile_dir)
        tile_dir.mkdir(parents=True)
    except FileNotFoundError:
        tile_dir.mkdir(parents=True, exist_ok=True)

    search_fixture = next(
        fixture for fixture, path in fixtures if path.name == "search.toml"
    )
    settings = ServerConfig(report=False)
    tiles = set()
    for item in search_fixture["test"]:
        if "status" in item or "json" not in item:
            continue
        bounds = json.loads(item["json"])
        if "start" in bounds and "end" in bounds:
            tiles.update(
                tile_iter(
                    (bounds["start"]["lat"], bounds["start"]["lng"]),
                    (bounds["end"]["lat"], bounds["end"]["lng"]),
                    settings.zoom,
                )
            )

    for x, y in tiles:
        tile_url = settings.endpoint.format(x=x, y=y, z=settings.zoom)
        response = requests.get(tile_url, stream=True)
        assert response.status_code == 200, (
            f"HTTP error {response.status_code} for {tile_url}:\n{response.text}"
        )
        tile_path = tile_dir / f"{settings.zoom}-{x}-{y}.png"
        with tile_path.open("wb") as tile_file:
            tile_file.write(response.raw.read())
