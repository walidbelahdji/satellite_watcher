"""Shared helpers and settings for the Streamlit pages."""

import requests
import streamlit as st

from detectorLitter.config import DemoConfig

settings = DemoConfig()


def http_error(response: requests.Response) -> bool:
    """Show a readable error and return whether the response succeeded."""
    if response.status_code == 200:
        return True
    try:
        message = response.json()["detail"]
    except Exception:
        message = response.text
    st.error(f"Error {response.status_code} : {message}")
    return False


def confidence_slider(key: str | None = None) -> int:
    slider_args = {"value": settings.default_confidence}
    if key is not None:
        slider_args["key"] = key
        if key in st.session_state:
            slider_args.pop("value")
    return st.slider(
        label="Confidence threshold",
        min_value=0,
        max_value=100,
        help=(
            "AI models detect objects with a confidence score. A higher score "
            "reduces false positives."
        ),
        **slider_args,
    )
