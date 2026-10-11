"""Service health operation."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Return the service health status."""
    return "detectorLitter is running"
