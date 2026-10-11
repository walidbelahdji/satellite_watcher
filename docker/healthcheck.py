"""Container health check using the configured API port."""

import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from dotenv import dotenv_values

env_path = Path(__file__).resolve().parent.parent / ".env"
defaults = dotenv_values(env_path)
port = os.getenv("API_PORT") or defaults.get("API_PORT")
if port is None:
    raise SystemExit(1)
try:
    with urlopen(f"http://127.0.0.1:{port}/health", timeout=8) as response:
        if response.status != 200:
            raise SystemExit(1)
except (OSError, URLError):
    raise SystemExit(1)
