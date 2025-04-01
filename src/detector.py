from ultralytics import YOLO
from pathlib import Path

# TODO better return types
# TODO raw ONNX https://github.com/ultralytics/ultralytics/tree/main/examples/YOLOv8-ONNXRuntime


class Detector:
    """Waste detector using YOLOv8 model"""

    def __init__(self, model: str | Path = "yolov8n.pt") -> None:
        """Init detector"""
        self.model = YOLO(model)

    def __call__(self, source=None):
        """Detect wastes"""
        return self.model.predict(source, True)