"""HTTP fixture execution and JSON comparison."""

import json
from pathlib import Path

import requests


def json_pretty(value: str) -> str:
    return json.dumps(json.loads(value), indent=2)


def test_item(
    item: dict,
    name: str,
    endpoint: str,
    data_dir: Path,
) -> None:
    """Send one fixture request and compare its status and JSON response."""
    if "path" in item or "json" in item:
        if "path" in item:
            image_path = data_dir / item["path"]
            with image_path.open("rb") as image_file:
                response = requests.post(
                    f"{endpoint}/{name}",
                    files={"data": image_file},
                    data=json.loads(item["json"]) if "json" in item else None,
                )
        else:
            response = requests.post(
                f"{endpoint}/{name}",
                data=item["json"],
                headers={"Content-Type": "application/json"},
            )
    else:
        response = requests.get(f"{endpoint}/{name}")

    expected_status = item.get("status", 200)
    assert response.status_code == expected_status, (
        f"Expected status code {expected_status} got {response.status_code}:\n"
        f"{response.text}"
    )

    expected = item.get("result", "")
    result = response.json()
    if response.status_code == 422 and "detail" in result:
        for detail in result["detail"]:
            detail.pop("url", None)
    actual = json.dumps(result)
    if actual != expected:
        item["result"] = actual
        raise Exception((json_pretty(expected), json_pretty(actual)))
