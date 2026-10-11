"""FastAPI application setup."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from detectorLitter.api.dependencies import settings
from detectorLitter.api.routes import detect, health, root, search, search_info
from detectorLitter.observability.metrics import start_metrics_server


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.metrics_enabled:
        start_metrics_server(settings.metrics_host, settings.metrics_port)
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    summary=settings.api_summary,
    lifespan=lifespan,
)
app.include_router(root.router)
app.include_router(health.router)
app.include_router(detect.router)
app.include_router(search.router)
app.include_router(search_info.router)
