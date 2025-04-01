from fastapi import FastAPI
from detector import Detector

app = FastAPI()
detector = Detector("model.pt")


@app.get("/")
async def root(path: str | None = None):
    if path is None:
        return "Hello from Sky Watcher"
    results = detector(path)
    speed = [result.speed for result in results]
    return speed