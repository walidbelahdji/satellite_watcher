"""Geographic waste search operations."""

import requests
from fastapi import APIRouter, HTTPException, Request, status

from detectorLitter.api.dependencies import settings
from detectorLitter.api.routes.detect import async_detection
from detectorLitter.api.schemas import SearchRequest, WastePos
from detectorLitter.geo.tiles import tile_iter
from detectorLitter.observability import metrics

router = APIRouter()


@router.post("/search", responses={413: {}, 502: {}})
async def search(req: Request, body: SearchRequest) -> list[WastePos]:
    """Search for waste positions inside a geographic area."""

    async def search_tiles(tile_positions):
        for x, y in tile_positions:
            if await req.is_disconnected():
                raise HTTPException(
                    status.HTTP_418_IM_A_TEAPOT, "Client disconnected"
                )
            tile_url = settings.endpoint.format(x=x, y=y, z=settings.zoom)
            response = requests.get(tile_url, stream=True)
            if response.status_code != 200:
                raise HTTPException(status.HTTP_502_BAD_GATEWAY)
            boxes = await async_detection(response.raw.read(), body.conf)
            for box in boxes:
                yield WastePos.from_box((x, y), box, settings.zoom)

    tile_positions = tile_iter(body.start.raw(), body.end.raw(), settings.zoom)
    tile_count = sum(1 for _ in tile_positions)
    metrics.log_request_search(tile_count)
    if tile_count > settings.max_search:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"Request to search {tile_count} tiles, max being {settings.max_search}",
        )

    tile_positions = tile_iter(body.start.raw(), body.end.raw(), settings.zoom)
    return [item async for item in search_tiles(tile_positions)]
