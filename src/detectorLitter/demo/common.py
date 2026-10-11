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


def confidence_slider() -> int:
    return st.slider(
        label="Confidence threshold",
        min_value=0,
        max_value=100,
        value=settings.default_confidence,
        help=(
            "AI models detect objects with a confidence score. A higher score "
            "reduces false positives."
        ),
    )
