"""YOLO output filtering and conversion to image-space bounding boxes."""

import cv2

from .image import ImageTransform


def postprocess(
    output,
    transform: ImageTransform,
    confidence: int | None,
    default_confidence: int,
    nms_score_threshold: float,
    nms_iou_threshold: float,
) -> list[tuple[float, float, float, float, float, float, float]]:
    """Filter model predictions and return boxes with confidence and center."""
    # The ONNX model returns one batch with shape (1, features, predictions).
    output = output[0].transpose()
    boxes = []
    nms_boxes = []
    scores = []
    min_confidence = (default_confidence if confidence is None else confidence) / 100
    image_height, image_width = transform.original_shape

    for row in output:
        score = row[4:].max()
        if score < min_confidence:
            continue
        center_x, center_y, width, height = row[:4]
        center_x = (center_x - transform.pad_x) / transform.scale_ratio
        center_y = (center_y - transform.pad_y) / transform.scale_ratio
        normalized_x = center_x / image_width
        normalized_y = center_y / image_height
        width /= transform.scale_ratio
        height /= transform.scale_ratio
        boxes.append(
            [
                value.item()
                for value in (
                    center_x,
                    center_y,
                    width,
                    height,
                    score,
                    normalized_x,
                    normalized_y,
                )
            ]
        )
        left = int(center_x - width / 2)
        top = int(center_y - height / 2)
        nms_boxes.append([left, top, int(width), int(height)])
        scores.append(score)

    selected = cv2.dnn.NMSBoxes(
        nms_boxes, scores, nms_score_threshold, nms_iou_threshold
    )
    return [boxes[index] for index in selected]
