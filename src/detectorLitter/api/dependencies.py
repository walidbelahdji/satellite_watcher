"""Shared API runtime objects."""

from detectorLitter.config import ServerConfig
from detectorLitter.detection.detector import Detector

settings = ServerConfig()
detector = Detector(
    settings.model_path,
    default_confidence=settings.detection_default_confidence,
    nms_score_threshold=settings.detection_nms_score_threshold,
    nms_iou_threshold=settings.detection_nms_iou_threshold,
)
