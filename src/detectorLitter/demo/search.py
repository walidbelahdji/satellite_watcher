"""Geographic area selection and search result visualization page."""

import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

from detectorLitter.demo.common import confidence_slider, http_error, settings


def _map(group: folium.FeatureGroup | None = None):
    map_view = folium.Map(
        location=[settings.default_lat, settings.default_lng],
        zoom_start=settings.zoom,
        tiles=folium.TileLayer(
            settings.tile_endpoint,
            max_native_zoom=settings.max_native_zoom,
            max_zoom=settings.max_zoom,
            attr=settings.attribution,
        ),  # type: ignore
        control_scale=settings.map_control_scale,
        max_bounds=settings.map_max_bounds,
    )
    if group is not None:
        group.add_to(map_view)
        map_view.fit_bounds(group.get_bounds())
    return map_view


def _select_bounds() -> tuple[float, float, float, float]:
    choice = st.radio(
        label="Input",
        options=["Map", "GPS"],
        horizontal=True,
        label_visibility="collapsed",
    )
    with st.form("bounds"):
        if choice == "GPS":
            columns = st.columns(2)
            args = {
                "label_visibility": "collapsed",
                "step": settings.coordinate_step,
                "format": settings.coordinate_format,
            }
            with columns[0]:
                lat0 = st.number_input(
                    "lat0", -90.0, 90.0, settings.default_lat, **args
                )
                lat1 = st.number_input(
                    "lat1", -90.0, 90.0, settings.default_lat, **args
                )
            with columns[1]:
                lng0 = st.number_input(
                    "lng0", -180.0, 180.0, settings.default_lng, **args
                )
                lng1 = st.number_input(
                    "lng1", -180.0, 180.0, settings.default_lng, **args
                )
        else:
            data = st_folium(
                _map(), returned_objects=["bounds"], use_container_width=True
            )
            bounds = data.get("bounds") or {}
            southwest = bounds.get("_southWest", {})
            northeast = bounds.get("_northEast", {})
            lat0 = southwest.get("lat") or 0
            lng0 = southwest.get("lng") or 0
            lat1 = northeast.get("lat") or 0
            lng1 = northeast.get("lng") or 0
        st.form_submit_button(
            "Apply", "Use the currently selected geographical area"
        )

    if choice == "GPS":
        group = folium.FeatureGroup()
        folium.Rectangle(
            bounds=[(lat0, lng0), (lat1, lng1)],
            color="#ff7800",
            fill=True,
            fill_color="#ffff00",
            fill_opacity=0.2,
        ).add_to(group)
        st_folium(_map(group), returned_objects=[], use_container_width=True)
    else:
        columns = st.columns(2)
        with columns[0]:
            st.write(round(lat0, 5))
            st.write(round(lat1, 5))
        with columns[1]:
            st.write(round(lng0, 5))
            st.write(round(lng1, 5))
    return lat0, lng0, lat1, lng1


@st.cache_data
def _get_search_info(bounds: dict):
    return requests.post(f"{settings.endpoint}/search_info", json=bounds)


def _show_search_results(
    bounds: dict, coordinates: tuple[float, float, float, float]
):
    lat0, lng0, lat1, lng1 = coordinates
    with st.form("search"):
        confidence = confidence_slider()
        search = st.form_submit_button(
            "Search", "Run search on chosen graphical area"
        )

    if not search:
        return
    with st.status("Searching...") as status:
        response = requests.post(
            f"{settings.endpoint}/search",
            json={"conf": confidence, **bounds},
        )
        success = http_error(response)
        if success:
            result = response.json()
            st.write(result)
            status.update(state="complete")
        else:
            status.update(state="error", expanded=True)

    if not success:
        return
    group = folium.FeatureGroup()
    for waste in result:
        folium.Marker(
            [waste["lat"], waste["lng"]], tooltip=f"{waste['conf']}%"
        ).add_to(group)
    folium.Rectangle(
        bounds=[(lat0, lng0), (lat1, lng1)], color="#00000000"
    ).add_to(group)
    st_folium(
        _map(group), "result_map", returned_objects=[], use_container_width=True
    )


def render() -> None:
    st.write("The search endpoint finds waste positions within a geographical area.")
    st.write(
        "Choose an area on the map or enter GPS coordinates, then apply the area "
        "to see how many tiles will be searched."
    )
    coordinates = _select_bounds()
    lat0, lng0, lat1, lng1 = coordinates
    bounds = {
        "start": {"lat": lat0, "lng": lng0},
        "end": {"lat": lat1, "lng": lng1},
    }

    response = _get_search_info(bounds)
    if not http_error(response):
        return
    info = response.json()
    if info["limited"]:
        st.warning(
            f"{info['nb_tiles']} / {info['limit']} - too many tiles for a single request"
        )
    else:
        st.info(
            f"{info['nb_tiles']} / {info['limit']} - few enough tiles for a single request"
        )
    _show_search_results(bounds, coordinates)
