"""Locust file to benchmark sky-watcher server"""

from locust import HttpUser, task


def load_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


no_waste = load_file("data/no_waste.png")
with_wastes = load_file("data/with_wastes.png")


class User(HttpUser):
    @task
    def detect(self):
        self.client.post("/detect", files={"data": no_waste})
        self.client.post("/detect", files={"data": with_wastes})

    @task
    def health(self):
        self.client.get("/health")
