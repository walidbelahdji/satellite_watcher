"""Image upload and litter-detection result display."""

from io import BytesIO
from pathlib import Path

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from detectorLitter.demo.common import confidence_slider, http_error, settings


IMAGE_TYPES = ("jpg", "jpeg", "png", "webp")
EXAMPLE_IMAGE_PATH = Path(__file__).parent / "assets" / "litter_detection_example.png"
EXAMPLE_IMAGE_NAME = "litter_detection_example.png"


def _select_example_image() -> None:
    """Select the bundled example in the image-source radio."""
    st.session_state["image_source"] = "Use the example image"


def _annotate(image: Image.Image, detections: list[dict]) -> Image.Image:
    """Return an image with each detected litter box and score highlighted."""
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default()
    stroke = max(3, round(min(annotated.size) / 320))

    for detection in detections:
        center_x = float(detection["x"])
        center_y = float(detection["y"])
        box_width = float(detection["w"])
        box_height = float(detection["h"])

        left = max(0, round(center_x - box_width / 2))
        top = max(0, round(center_y - box_height / 2))
        right = min(annotated.width - 1, round(center_x + box_width / 2))
        bottom = min(annotated.height - 1, round(center_y + box_height / 2))
        if right <= left or bottom <= top:
            continue

        draw.rectangle((left, top, right, bottom), outline="#18B981", width=stroke)

        label = f"LITTER  {int(detection['conf'])}%"
        text_bounds = draw.textbbox((0, 0), label, font=font)
        label_width = text_bounds[2] - text_bounds[0] + 14
        label_height = text_bounds[3] - text_bounds[1] + 10
        label_top = max(0, top - label_height)
        label_right = min(annotated.width - 1, left + label_width)
        draw.rounded_rectangle(
            (left, label_top, label_right, label_top + label_height),
            radius=5,
            fill="#153F32",
        )
        draw.text(
            (left + 7, label_top + 4),
            label,
            font=font,
            fill="#FFFFFF",
        )

    return annotated


def render() -> None:
    """Render a single-image upload flow and its detection results."""
    with st.container(border=True):
        st.markdown("#### Choose an image")
        image_source = st.radio(
            "Image source",
            ("Upload a photo", "Use the example image"),
            horizontal=True,
            label_visibility="collapsed",
            key="image_source",
        )

        if image_source == "Use the example image":
            image_data = EXAMPLE_IMAGE_PATH.read_bytes()
            image_name = EXAMPLE_IMAGE_NAME
            image_type = "image/png"
        else:
            uploaded_file = st.file_uploader(
                "Browse or drag an image here",
                type=IMAGE_TYPES,
                accept_multiple_files=False,
                help="Supported formats: JPG, JPEG, PNG, and WEBP.",
            )
            st.caption("JPG / PNG / WEBP  |  One image per detection")

            if uploaded_file is None:
                note_column, example_column = st.columns([1, 0.9], gap="large")
                with note_column:
                    st.markdown(
                        '<div class="empty-note">Upload a photo, or select '
                        "Use the example image above to try the detector. "
                        "Results include highlighted boxes and confidence scores.</div>",
                        unsafe_allow_html=True,
                    )
                with example_column:
                    st.image(
                        EXAMPLE_IMAGE_PATH,
                        caption="Example image",
                        use_container_width=True,
                    )
                    st.button(
                        "Use this example",
                        on_click=_select_example_image,
                        use_container_width=True,
                    )
                return

            image_data = uploaded_file.getvalue()
            image_name = uploaded_file.name
            image_type = uploaded_file.type or "application/octet-stream"

        try:
            image = Image.open(BytesIO(image_data)).convert("RGB")
        except (UnidentifiedImageError, OSError):
            st.error("This file could not be opened as an image. Choose a JPG, PNG, or WEBP file.")
            return

        image_column, control_column = st.columns([1.35, 0.85], gap="large")
        with image_column:
            st.image(
                image,
                caption=f"Ready to scan - {image_name}",
                use_container_width=True,
            )
        with control_column:
            st.markdown("#### Detection settings")
            st.write(
                "Set the minimum confidence for detections included in the results."
            )
            confidence = confidence_slider()
            run_detection = st.button(
                "Detect litter",
                type="primary",
                use_container_width=True,
            )

        if not run_detection:
            return

        with st.spinner("Scanning the image for possible litter..."):
            try:
                response = requests.post(
                    f"{settings.endpoint.rstrip('/')}/detect",
                    files={
                        "data": (
                            image_name,
                            image_data,
                            image_type,
                        )
                    },
                    data={"conf": confidence},
                    timeout=(10, 120),
                )
            except requests.RequestException:
                st.error(
                    "The detection service could not be reached. Please try again in a moment."
                )
                return

        if not http_error(response):
            return

        try:
            detections = response.json()
        except ValueError:
            st.error("The detection service returned an unreadable response. Please try again.")
            return

        st.markdown(
            '<div class="result-heading"><div class="result-kicker">Analysis complete</div>'
            "<h2>Detection results</h2></div>",
            unsafe_allow_html=True,
        )

        if not detections:
            st.info(
                "No litter was detected at this confidence threshold. Try a clearer "
                "or closer image, or lower the threshold and scan again."
            )
            st.image(image, caption="Selected image", use_container_width=True)
            return

        average_confidence = round(
            sum(int(item["conf"]) for item in detections) / len(detections)
        )
        count_column, confidence_column, size_column = st.columns(3)
        count_column.metric("Possible litter items", len(detections))
        confidence_column.metric("Average confidence", f"{average_confidence}%")
        size_column.metric("Image size", f"{image.width} x {image.height}")

        st.image(
            _annotate(image, detections),
            caption="Green boxes mark detected litter. Scores show model confidence.",
            use_container_width=True,
        )
