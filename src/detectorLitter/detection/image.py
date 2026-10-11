"""Image decoding and model input preparation."""

from dataclasses import dataclass

import cv2
import numpy as np


class ImgDecodeError(Exception):
    """Raised when OpenCV cannot decode the supplied image bytes."""


@dataclass(frozen=True)
class ImageTransform:
    original_shape: tuple[int, int]
    scale_ratio: float
    pad_x: float
    pad_y: float


def prepare_image(image_bytes: bytes, target_shape: tuple[int, int]):
    """Decode, resize, pad, and normalize image bytes for the ONNX model."""
    image = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    if image is None:
        raise ImgDecodeError()

    image_shape = image.shape[:2]
    scale_ratio = min(
        target_shape[0] / image_shape[0], target_shape[1] / image_shape[1]
    )
    unpad_shape = int(round(image_shape[1] * scale_ratio)), int(
        round(image_shape[0] * scale_ratio)
    )
    if unpad_shape != image_shape:
        image = cv2.resize(image, unpad_shape, interpolation=cv2.INTER_LINEAR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pad_x, pad_y = (target_shape[0] - unpad_shape[0]) / 2, (
        target_shape[1] - unpad_shape[1]
    ) / 2
    top, bottom = int(round(pad_y - 0.1)), int(round(pad_y + 0.1))
    left, right = int(round(pad_x - 0.1)), int(round(pad_x + 0.1))
    image = cv2.copyMakeBorder(
        image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
    )
    model_input = np.expand_dims(image, axis=0).astype(np.float32) / 255.0
    model_input = np.transpose(model_input, (0, 3, 1, 2))
    transform = ImageTransform(image_shape, scale_ratio, pad_x, pad_y)
    return model_input, transform
