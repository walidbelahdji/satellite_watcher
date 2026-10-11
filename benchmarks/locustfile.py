"""Locust scenarios for the detectorLitter API."""

import os
from pathlib import Path

from locust import HttpUser, task


def load_file(path: Path) -> bytes:
    with path.open("rb") as image_file:
        return image_file.read()


data_dir = Path(os.getenv("BENCH_DATA_DIR", "tests/data"))
no_waste_path = Path(
    os.getenv("BENCH_NO_WASTE_IMAGE", str(data_dir / "no_waste.png"))
)
no_waste = load_file(no_waste_path)
with_wastes = load_file(
    Path(os.getenv("BENCH_WASTE_IMAGE", str(data_dir / "with_wastes.png")))
)


class User(HttpUser):
    @task
    def detect(self):
        self.client.post("/detect", files={"data": no_waste})
        self.client.post("/detect", files={"data": with_wastes})

    @task
    def health(self):
        self.client.get("/health")
