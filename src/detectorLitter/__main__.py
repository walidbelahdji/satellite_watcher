"""Run the API with its configured host and port."""

import argparse

import uvicorn

from detectorLitter.config import ServerConfig

settings = ServerConfig(report=False)
parser = argparse.ArgumentParser(description="Run the detectorLitter API")
parser.add_argument("--reload", action="store_true")
arguments = parser.parse_args()
uvicorn.run(
    "detectorLitter.api.app:app",
    host=settings.api_host,
    port=settings.api_port,
    reload=arguments.reload,
)
