"""Image waste detection operation."""

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from detectorLitter.api.dependencies import detector
from detectorLitter.api.schemas import WasteBox
from detectorLitter.detection.image import ImgDecodeError
from detectorLitter.observability import metrics

router = APIRouter()


async def async_detection(
    data: bytes, confidence: int | None = None
) -> list[tuple[float, float, float, float, float, float, float]]:
    @metrics.time_detection()
    def run_detection():
        try:
            return detector(data, confidence)
        except ImgDecodeError:
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE) from None

    return await run_in_threadpool(run_detection)


@router.post("/detect", responses={415: {}})
async def detect(
    data: Annotated[bytes, File(title="data", description="raw image bytes")],
    conf: Annotated[
        int | None,
        Form(
            title="confidence",
            description="detection confidence threshold",
            ge=0,
            le=100,
            examples=[75],
        ),
    ] = None,
) -> list[WasteBox]:
    """Find waste bounding boxes in a photo."""
    metrics.log_request_detect()
    result = await async_detection(data, conf)
    return [WasteBox.from_box(box) for box in result]
