"""Search size information operation."""

from fastapi import APIRouter

from detectorLitter.api.dependencies import settings
from detectorLitter.api.schemas import SearchInfo, SearchInfoRequest
from detectorLitter.geo.tiles import tile_iter

router = APIRouter()


@router.post("/search_info")
async def search_info(body: SearchInfoRequest) -> SearchInfo:
    """Report the tile count and whether the search exceeds its limit."""
    tile_positions = tile_iter(body.start.raw(), body.end.raw(), settings.zoom)
    tile_count = sum(1 for _ in tile_positions)
    return SearchInfo(
        nb_tiles=tile_count,
        limit=settings.max_search,
        limited=tile_count > settings.max_search,
    )
