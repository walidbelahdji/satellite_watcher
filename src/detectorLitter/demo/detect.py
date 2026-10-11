"""Photo upload and bounding-box visualization page."""

import requests
import streamlit as st
from PIL import Image, ImageDraw

from detectorLitter.demo.common import confidence_slider, http_error, settings


def render() -> None:
    st.write("The detect endpoint finds waste bounding boxes in photos.")
    st.write("Load files or take a photo, then click on detect to launch detection.")
    with st.form("detect"):
        files = st.file_uploader("Load files", accept_multiple_files=True)
        photo = st.camera_input("Take a photo")
        inputs = ([photo] if photo is not None else []) + (files or [])
        confidence = confidence_slider()
        st.form_submit_button("Detect", "Run detection on loaded photos")

    progress = st.progress(0, text="Detection in progress...")
    for index, uploaded_file in enumerate(inputs):
        response = requests.post(
            f"{settings.endpoint}/detect",
            files={"data": uploaded_file},
            data={"conf": confidence},
        )
        progress.progress((index + 1) / len(inputs))
        with st.status(uploaded_file.name) as status:
            success = http_error(response)
            if success:
                result = response.json()
                st.write(result)
                status.update(state="complete")
            else:
                status.update(state="error", expanded=True)
        if success:
            image = Image.open(uploaded_file)
            draw = ImageDraw.Draw(image)
            for box in result:
                x, y, width, height = (
                    box["x"],
                    box["y"],
                    box["w"] / 2,
                    box["h"] / 2,
                )
                draw.rectangle(
                    (x - width, y - height, x + width, y + height),
                    outline="red",
                    width=2,
                )
            for box in result:
                x, y, height = box["x"], box["y"], box["h"] / 2
                draw.text((x - height, y + height), f"{box['conf']}%")
            st.image(image)
        if index != len(inputs) - 1:
            st.divider()
    progress.empty()
