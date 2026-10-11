"""Download the configured ONNX model artifact."""

import argparse
import os
from pathlib import Path

import requests
from dotenv import dotenv_values, load_dotenv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/model.env")
    parser.add_argument("--output")
    arguments = parser.parse_args()

    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv("config/server.env", override=False)
    config = dotenv_values(arguments.config)
    url = os.getenv("MODEL_URL") or config.get("MODEL_URL")
    output = arguments.output or os.getenv("MODEL_PATH")
    timeout = os.getenv("MODEL_DOWNLOAD_TIMEOUT_SECONDS") or config.get(
        "MODEL_DOWNLOAD_TIMEOUT_SECONDS"
    )
    if not url or not output or not timeout:
        raise ValueError(
            f"MODEL_URL, MODEL_PATH, and MODEL_DOWNLOAD_TIMEOUT_SECONDS must be set "
            f"in {arguments.config} or the environment"
        )

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True, timeout=float(timeout))
    response.raise_for_status()
    with destination.open("wb") as model_file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                model_file.write(chunk)
    print(f"Downloaded model to {destination}")


if __name__ == "__main__":
    main()
