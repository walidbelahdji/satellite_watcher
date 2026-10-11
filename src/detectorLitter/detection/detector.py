"""ONNX Runtime adapter for waste detection."""

import json
from pathlib import Path

import onnxruntime as ort

from .image import ImgDecodeError, prepare_image
from .postprocess import postprocess


class Detector:
    """Run a YOLOv8 ONNX model on image bytes."""

    def __init__(
        self,
        model: str | Path,
        default_confidence: int,
        nms_score_threshold: float,
        nms_iou_threshold: float,
    ):
        options = ort.SessionOptions()
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(
            str(model), options, ort.get_available_providers()
        )
        metadata = self.session.get_modelmeta().custom_metadata_map
        self.shape = tuple(json.loads(metadata["imgsz"]))
        self.default_confidence = default_confidence
        self.nms_score_threshold = nms_score_threshold
        self.nms_iou_threshold = nms_iou_threshold

    def __call__(self, image: bytes, confidence: int | None = None):
        model_input, transform = prepare_image(image, self.shape)
        model_inputs = self.session.get_inputs()
        outputs = self.session.run(None, {model_inputs[0].name: model_input})
        assert len(outputs) == 1
        return postprocess(
            outputs[0],
            transform,
            confidence,
            self.default_confidence,
            self.nms_score_threshold,
            self.nms_iou_threshold,
        )


__all__ = ["Detector", "ImgDecodeError"]
