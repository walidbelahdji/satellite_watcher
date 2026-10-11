"""Streamlit demo entry point."""

import streamlit as st

from detectorLitter.demo import detect, search

st.title("detectorLitter Demo")
st.write(
    "detectorLitter is a waste detection service from photos or satellite images. "
    "This demo provides a user interface to interact with its API."
)
endpoint = st.selectbox("Choose the API endpoint", ["Detect", "Search"])

if endpoint == "Detect":
    detect.render()
else:
    search.render()
