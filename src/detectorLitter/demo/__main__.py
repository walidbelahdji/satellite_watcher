"""Launch the Streamlit demo using its configured listener settings."""

import subprocess
import sys
from pathlib import Path

from detectorLitter.config import DemoConfig

settings = DemoConfig(report=False)
app_path = Path(__file__).with_name("app.py")
subprocess.run(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        f"--server.port={settings.port}",
        f"--server.address={settings.host}",
    ],
    check=True,
)
