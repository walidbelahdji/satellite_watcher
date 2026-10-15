"""Map search over IGN orthophoto tiles."""

import folium
import requests
import streamlit as st
from folium.plugins import Draw

from detectorLitter.demo.common import confidence_slider, settings

HALF_LAT = 0.0015
HALF_LNG = 0.002
COORDINATE_DECIMALS = 5
MAP_KEY = "ign_search_map"


def bounds_from_drawing(
    drawing: dict | None,
) -> tuple[float, float, float, float] | None:
    """Return south, west, north, and east from a drawn GeoJSON rectangle."""
    if not isinstance(drawing, dict):
        return None
    geometry = drawing.get("geometry", drawing)
    if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
        return None
    rings = geometry.get("coordinates") or []
    if not rings or not isinstance(rings[0], list):
        return None

    latitudes: list[float] = []
    longitudes: list[float] = []
    for point in rings[0]:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        longitudes.append(float(point[0]))
        latitudes.append(float(point[1]))
    if not latitudes or not longitudes:
        return None
    return (
        round(min(latitudes), COORDINATE_DECIMALS),
        round(min(longitudes), COORDINATE_DECIMALS),
        round(max(latitudes), COORDINATE_DECIMALS),
        round(max(longitudes), COORDINATE_DECIMALS),
    )


def _ensure_state() -> None:
    if "map_start_lat" not in st.session_state:
        st.session_state.map_start_lat = round(
            settings.default_lat - HALF_LAT, COORDINATE_DECIMALS
        )
        st.session_state.map_start_lng = round(
            settings.default_lng - HALF_LNG, COORDINATE_DECIMALS
        )
        st.session_state.map_end_lat = round(
            settings.default_lat + HALF_LAT, COORDINATE_DECIMALS
        )
        st.session_state.map_end_lng = round(
            settings.default_lng + HALF_LNG, COORDINATE_DECIMALS
        )
    st.session_state.setdefault(
        "map_center", [settings.default_lat, settings.default_lng]
    )
    st.session_state.setdefault("map_zoom", settings.zoom)
    st.session_state.setdefault("map_drawing_signature", "")
    st.session_state.setdefault("map_detections", None)
    st.session_state.setdefault("map_info_cache", {})


def _current_bounds() -> tuple[float, float, float, float]:
    return (
        round(float(st.session_state.map_start_lat), COORDINATE_DECIMALS),
        round(float(st.session_state.map_start_lng), COORDINATE_DECIMALS),
        round(float(st.session_state.map_end_lat), COORDINATE_DECIMALS),
        round(float(st.session_state.map_end_lng), COORDINATE_DECIMALS),
    )


def _clear_detections() -> None:
    st.session_state.map_detections = None


def _coordinate_format() -> str:
    """Retain configured precision while showing enough digits for map bounds."""
    try:
        configured_decimals = int(
            settings.coordinate_format.partition(".")[2].rstrip("f")
        )
    except ValueError:
        configured_decimals = 0
    decimals = max(COORDINATE_DECIMALS, configured_decimals)
    return f"%.{decimals}f"


def _bounds_changed() -> None:
    """Clear old results and keep manually edited bounds in view."""
    _clear_detections()
    start_lat, start_lng, end_lat, end_lng = _current_bounds()
    st.session_state.map_center = [
        (start_lat + end_lat) / 2,
        (start_lng + end_lng) / 2,
    ]


def _payload() -> dict:
    start_lat, start_lng, end_lat, end_lng = _current_bounds()
    return {
        "start": {
            "lat": min(start_lat, end_lat),
            "lng": min(start_lng, end_lng),
        },
        "end": {
            "lat": max(start_lat, end_lat),
            "lng": max(start_lng, end_lng),
        },
    }


def _error_message(response: requests.Response) -> str:
    try:
        message = response.json()["detail"]
    except (ValueError, KeyError, TypeError):
        message = response.text
    return f"Error {response.status_code} : {message}"


def _search_info() -> dict:
    key = _current_bounds()
    cache: dict = st.session_state.map_info_cache
    if key in cache:
        return cache[key]

    try:
        response = requests.post(
            f"{settings.endpoint.rstrip('/')}/search_info",
            json=_payload(),
            timeout=(10, 30),
        )
    except requests.RequestException:
        return {
            "ok": False,
            "message": (
                "The detection service could not be reached. "
                "Please try again in a moment."
            ),
        }

    if response.status_code != 200:
        return {"ok": False, "message": _error_message(response)}

    try:
        body = response.json()
    except ValueError:
        return {
            "ok": False,
            "message": "The detection service returned an unreadable response.",
        }

    result = {
        "ok": True,
        "nb_tiles": int(body["nb_tiles"]),
        "limit": int(body["limit"]),
        "limited": bool(body["limited"]),
    }
    cache[key] = result
    return result


def _build_map() -> folium.Map:
    south, west, north, east = _current_bounds()
    south, north = sorted((south, north))
    west, east = sorted((west, east))
    frame = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        max_zoom=settings.max_zoom,
        tiles=None,
        control_scale=settings.map_control_scale,
        max_bounds=settings.map_max_bounds,
    )
    folium.TileLayer(
        tiles=settings.tile_endpoint,
        attr=settings.attribution,
        name="IGN orthophotos",
        max_zoom=settings.max_zoom,
        max_native_zoom=settings.max_native_zoom,
        overlay=False,
        control=False,
    ).add_to(frame)
    if south != north or west != east:
        folium.Rectangle(
            bounds=[[south, west], [north, east]],
            color="#26745a",
            weight=2,
            fill=True,
            fill_color="#26745a",
            fill_opacity=0.15,
        ).add_to(frame)

    for detection in st.session_state.map_detections or []:
        folium.CircleMarker(
            location=[detection["lat"], detection["lng"]],
            radius=7,
            color="#153f32",
            weight=2,
            fill=True,
            fill_color="#18B981",
            fill_opacity=0.95,
            tooltip=(
                f"{int(detection['conf'])}% · "
                f"{detection['lat']:.5f}, {detection['lng']:.5f}"
            ),
        ).add_to(frame)

    Draw(
        export=False,
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": False,
            "marker": False,
            "circlemarker": False,
            "rectangle": {"shapeOptions": {"color": "#26745a"}},
        },
        edit_options={"edit": False, "remove": False},
    ).add_to(frame)
    return frame


def _remember_view(state: dict | None) -> None:
    if not state:
        return
    center = state.get("center")
    zoom = state.get("zoom")
    if isinstance(center, dict) and "lat" in center and "lng" in center:
        st.session_state.map_center = [center["lat"], center["lng"]]
    elif isinstance(center, (list, tuple)) and len(center) >= 2:
        st.session_state.map_center = [float(center[0]), float(center[1])]
    if isinstance(zoom, (int, float)):
        st.session_state.map_zoom = int(zoom)


def _apply_drawing(state: dict | None) -> None:
    if not state:
        return
    bounds = bounds_from_drawing(state.get("last_active_drawing"))
    if bounds is None:
        return
    signature = repr(bounds)
    selected_bounds = tuple(
        round(value, COORDINATE_DECIMALS) for value in bounds
    )
    if (
        signature == st.session_state.map_drawing_signature
        and selected_bounds == _current_bounds()
    ):
        return
    st.session_state.map_drawing_signature = signature
    if selected_bounds == _current_bounds():
        return
    (
        st.session_state.map_start_lat,
        st.session_state.map_start_lng,
        st.session_state.map_end_lat,
        st.session_state.map_end_lng,
    ) = selected_bounds
    _clear_detections()
    st.rerun()


def _render_map() -> None:
    from streamlit_folium import st_folium

    with st.container(border=True):
        state = st_folium(
            _build_map(),
            key=MAP_KEY,
            height=640,
            use_container_width=True,
            center=(
                float(st.session_state.map_center[0]),
                float(st.session_state.map_center[1]),
            ),
            zoom=int(st.session_state.map_zoom),
            returned_objects=["last_active_drawing", "center", "zoom"],
        )
    _remember_view(state)
    _apply_drawing(state)


def _coordinate_inputs() -> None:
    st.caption(
        "Draw a rectangle on the map, or edit the corners. " "Coordinates are WGS 84."
    )
    coordinate_format = _coordinate_format()
    start_lat, start_lng, end_lat, end_lng = st.columns(4)
    with start_lat:
        st.number_input(
            "Start latitude",
            min_value=-90.0,
            max_value=90.0,
            step=settings.coordinate_step,
            format=coordinate_format,
            key="map_start_lat",
            on_change=_bounds_changed,
        )
    with start_lng:
        st.number_input(
            "Start longitude",
            min_value=-180.0,
            max_value=180.0,
            step=settings.coordinate_step,
            format=coordinate_format,
            key="map_start_lng",
            on_change=_bounds_changed,
        )
    with end_lat:
        st.number_input(
            "End latitude",
            min_value=-90.0,
            max_value=90.0,
            step=settings.coordinate_step,
            format=coordinate_format,
            key="map_end_lat",
            on_change=_bounds_changed,
        )
    with end_lng:
        st.number_input(
            "End longitude",
            min_value=-180.0,
            max_value=180.0,
            step=settings.coordinate_step,
            format=coordinate_format,
            key="map_end_lng",
            on_change=_bounds_changed,
        )


def _render_results() -> None:
    detections = st.session_state.map_detections
    if detections is None:
        return
    if not detections:
        st.info(
            "No litter was detected in this area at this confidence threshold. "
            "Try a larger area or a lower threshold."
        )
        return

    average = round(sum(int(item["conf"]) for item in detections) / len(detections))
    count_column, confidence_column = st.columns(2)
    count_column.metric("Possible litter items", len(detections))
    confidence_column.metric("Average confidence", f"{average}%")
    st.dataframe(
        [
            {
                "Confidence": int(item["conf"]),
                "Latitude": item["lat"],
                "Longitude": item["lng"],
            }
            for item in detections
        ],
        width="stretch",
        hide_index=True,
    )


def _detections_in_bounds(detections: list[dict]) -> list[dict]:
    """Keep only detections whose point falls inside the selected rectangle."""
    start_lat, start_lng, end_lat, end_lng = _current_bounds()
    south, north = sorted((start_lat, end_lat))
    west, east = sorted((start_lng, end_lng))
    return [
        item
        for item in detections
        if south <= float(item["lat"]) <= north
        and west <= float(item["lng"]) <= east
    ]


def render() -> None:
    """Render the IGN map, the selected rectangle, and geographic search."""
    _ensure_state()
    st.markdown(
        """
        <div class="section-heading">
            <div class="section-kicker">Geographic search</div>
            <h2>Search litter on a map</h2>
            <p class="section-copy">
                Browse IGN Géoportail orthophotos, draw a rectangle, and search
                that area. Results are latitude and longitude points.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(settings.attribution, unsafe_allow_html=True)
    _render_map()
    _coordinate_inputs()

    info = _search_info()
    confidence = confidence_slider("map_confidence")
    if not info["ok"]:
        st.error(info["message"])
        return

    tile_column, limit_column = st.columns(2)
    tile_column.metric("Tiles in this area", info["nb_tiles"])
    limit_column.metric("Tile limit", info["limit"])
    if info["limited"]:
        st.warning(
            f"This area covers {info['nb_tiles']} tiles. "
            f"The limit is {info['limit']} tiles. Draw a smaller rectangle."
        )

    if st.button(
        "Search this area",
        type="primary",
        disabled=info["limited"],
        width="stretch",
    ):
        with st.spinner("Fetching satellite tiles and scanning them for litter..."):
            try:
                response = requests.post(
                    f"{settings.endpoint.rstrip('/')}/search",
                    json={**_payload(), "conf": confidence},
                    timeout=(10, 300),
                )
            except requests.RequestException:
                st.error(
                    "The detection service could not be reached. "
                    "Please try again in a moment."
                )
                return
        if response.status_code != 200:
            st.error(_error_message(response))
            return
        try:
            detections = response.json()
            if not isinstance(detections, list):
                raise ValueError("Expected a list of detections")
            st.session_state.map_detections = _detections_in_bounds(detections)
        except (ValueError, KeyError, TypeError):
            st.error("The detection service returned an unreadable response.")
            return
        st.rerun()

    _render_results()
