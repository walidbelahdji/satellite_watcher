# detectorLitter

`detectorLitter` is a waste-detection service for photographs and geographic
areas. It runs a YOLOv8 model in ONNX format, accepts satellite imagery from a
configurable tile provider, and includes a Streamlit web demo.


## What it does

- Detects waste in uploaded images and returns confidence scores and bounding
  boxes.
- Searches a geographic rectangle by fetching and analyzing satellite map tiles,
  then returns detected positions as latitude and longitude.
- Provides a browser demo for uploading or taking photos and for choosing a
  search area using GPS coordinates or a Google satellite map.
- Exposes Prometheus metrics and includes Docker Compose, HTTP integration
  fixtures, and a Locust benchmark.

## API

The API uses FastAPI. Interactive and machine-readable documentation is
available at:

- Swagger UI: [`/docs`](https://bmwalide-api.fly.dev/docs)
- ReDoc: [`/redoc`](https://bmwalide-api.fly.dev/redoc)
- OpenAPI schema: [`/openapi.json`](https://bmwalide-api.fly.dev/openapi.json)

| Method and path | Input | Result |
| --- | --- | --- |
| `GET /health` | None | Service health response. |
| `POST /detect` | Multipart image field `data`; optional form field `conf` from 0 to 100. | A list of detections with confidence (`conf`) and pixel bounding-box center and size (`x`, `y`, `w`, `h`). |
| `POST /search_info` | JSON with `start` and `end` latitude/longitude coordinates. | Tile count (`nb_tiles`), configured maximum (`limit`), and whether the area exceeds it (`limited`). |
| `POST /search` | The same coordinates and optional `conf` threshold. | A list of detections with confidence and geographic coordinates (`lat`, `lng`). |

Search coordinates use WGS 84. The service converts the requested rectangle to
Web Mercator tile coordinates, requests tiles from `TILE_ENDPOINT`, and limits
the number of tiles analyzed with `MAX_SEARCH_TILES`. The tile URL must include
the `{z}`, `{x}`, and `{y}` placeholders. Invalid image data returns HTTP 415;
invalid request fields are validated by FastAPI.

The Prometheus exporter is served at `/metrics` when `METRICS_ENABLED` is true.

## Project layout

```text
src/detectorLitter/
  api/             FastAPI app, schemas, and route handlers
  detection/       Image preparation, ONNX inference, and post-processing
  geo/             Coordinate projection and tile calculations
  observability/   Prometheus counters and timing metrics
  demo/            Streamlit app and detect/search pages
config/            API, demo, model-download, and Compose defaults
scripts/           ONNX model download helper
tests/             HTTP fixture runner, fixtures, sample images, and tile cache
benchmarks/        Locust load-test scenario
docker/            Container health check
```

The project metadata and Python package configuration are in `pyproject.toml`;
runtime, demo, test, development, and benchmark dependencies are listed in
`requirements.txt`. The model file is downloaded separately and is not stored in
the repository.

## Run locally

Python 3.10 or newer and [just](https://github.com/casey/just) are required.
Docker is only needed for the Compose option below.

```sh
# Create local settings from the tracked template
cp .env.example .env

# Install dependencies and the package in editable mode
just dep

# Download the ONNX model configured in config/model.env
just model

# Start the API with auto-reload
just dev
```

The API uses `API_HOST` and `API_PORT` (defaults: `0.0.0.0` and `8080`). Open
`http://localhost:8080/docs` for its interactive documentation.

Start the demo in another terminal:

```sh
just demo
```

The demo listens on `DEMO_HOST` and `DEMO_PORT` (defaults: `0.0.0.0` and
`8501`). To have it use the API running locally, set `DEMO_ENDPOINT` to
`http://localhost:8080` in `.env` before starting it.

## Run with Docker Compose

```sh
just compose
```

This builds and starts the API, the demo profile, and a local static tile
server. By default, the host ports are `8000` for the API, `8501` for the demo,
and `8502` for the tile server. Compose configures the API to use the local tile
server and the demo to use the API. To start without the demo profile, run
`docker compose up --build`.

The published ports and the Python base image can be changed with
`API_PUBLISHED_PORT`, `DEMO_PUBLISHED_PORT`, `MAP_PUBLISHED_PORT`, and
`PYTHON_VERSION` in `.env`.

## Configuration

Settings are read from the host environment, `.env` in the current directory,
and the tracked files under `config/`. Existing environment values take
precedence over values loaded from those files. Copy `.env.example` to `.env` to
override defaults for local work.

- `config/server.env` sets API, tile, model-path, metrics, and detection defaults.
- `config/demo.env` sets demo, map, tile display, and default confidence values.
- `config/model.env` supplies the ONNX model URL and download timeout.
- `config/compose-server.env` and `config/compose-demo.env` point Compose
  services at each other and the local tile server.

Useful settings include `TILE_ENDPOINT`, `TILE_ZOOM`, `MAX_SEARCH_TILES`,
`MODEL_PATH`, `API_HOST`, `API_PORT`, `METRICS_ENABLED`, `METRICS_HOST`,
`METRICS_PORT`, `DETECTION_DEFAULT_CONFIDENCE`,
`DETECTION_NMS_SCORE_THRESHOLD`, and `DETECTION_NMS_IOU_THRESHOLD`. The
`DEMO_*` variables configure the demo listener, API endpoint, map display, and
default confidence. `.env.example` provides a full set of starting values; for
example, its search limit is 500 tiles, while the tracked API default is 50.

Set `GOOGLE_MAPS_API_KEY` to enable the interactive Google satellite picker in
the demo. The key is sent to the browser, so restrict it to the Maps JavaScript
API and the domains that host the demo. Google Maps requires an API key and
billing for regular use. Without a key, coordinate entry still works and the
demo provides a link to browse the selected point in Google Maps.
The Google map is used to select the search location; image analysis uses the
API's configured `TILE_ENDPOINT` source.

To use another model source or destination, change `MODEL_URL` or `MODEL_PATH`
and run `just model`. The download helper also accepts `--config` and `--output`
arguments.

## Development

### HTTP integration fixtures

Start the API, then run:

```sh
just test
```

The fixture runner sends requests to `TEST_API_ENDPOINT`, which defaults to
`http://127.0.0.1:8000`. If the API is running on the local default port 8080,
set `TEST_API_ENDPOINT` to `http://127.0.0.1:8080` in your shell before running
the command.

Fixtures are TOML files in `tests/fixtures/`, with one file per endpoint.
Images and cached map tiles used by fixtures are in `tests/data/`. To refresh
the expected results and tile cache after an intentional behavior or model
change, run:

```sh
just test-apply
```

### Formatting and linting

```sh
just pre-commit
```

This runs Black and Ruff.

### Benchmark

With an API server available at `http://localhost:8000`, run:

```sh
just bench
```

The command runs a 60-second, 10-user Locust scenario against the health and
image-detection endpoints and writes `bench.html`.

## Deployment

The repository includes Fly.io configuration for the API (`fly.toml`) and demo
(`demo.fly.toml`). With the Fly CLI configured, use `just deploy` for the API,
`just deploy-demo` for the demo, or `just deploy-all` for both.

The API configuration keeps at least one machine running in its primary region
to avoid cold starts. This means that machine continues to incur running
compute charges while the app is idle. To apply configuration changes, redeploy
the API with `fly deploy --config fly.toml --app bmwalide-api`.
