"""CLI for running and updating HTTP integration fixtures."""

import os
import sys
from pathlib import Path

import click
import toml

from tests.runner.client import test_item
from tests.runner.style import ANSI, diff_strings
from tests.runner.tile_cache import scrape_tiles

FIXTURE_PATH = Path(os.getenv("TEST_FIXTURE_DIR", "tests/fixtures"))
DATA_PATH = Path(os.getenv("TEST_DATA_DIR", "tests/data"))
ENDPOINT = os.getenv("TEST_API_ENDPOINT", "http://127.0.0.1:8000")


def run_item(item: dict, name: str, apply: bool) -> bool:
    print(item["name"], end="")
    try:
        test_item(item, name, ENDPOINT, DATA_PATH)
        print(f"{ANSI.GREEN} OK{ANSI.RESET}")
        return True
    except Exception as error:
        first_arg = error.args[0] if error.args else None
        if isinstance(first_arg, tuple):
            expected, actual = first_arg
            diff = diff_strings(expected, actual)
            if apply:
                print(f"{ANSI.GREEN} UPDATE{ANSI.RESET}\n{diff}")
            else:
                print(f"{ANSI.RED} ERR - Unexpected Result{ANSI.RESET}\n{diff}")
        else:
            print(f"{ANSI.RED} ERR\n{ANSI.GRAY}{error}{ANSI.RESET}")
        return False


@click.command()
@click.option("--apply", is_flag=True, default=False)
def run(apply: bool) -> None:
    successful = True
    paths = sorted(FIXTURE_PATH.glob("*.toml"))
    fixtures = [(toml.load(path), path) for path in paths]
    if apply:
        print(f"{ANSI.MAGENTA}Scrape tiles{ANSI.RESET}")
        scrape_tiles(fixtures, DATA_PATH)
    for fixture, path in fixtures:
        name = path.stem
        print(f"{ANSI.MAGENTA}{name}{ANSI.RESET}")
        for item in fixture["test"]:
            successful &= run_item(item, name, apply)
        if apply:
            with path.open("w", encoding="utf-8") as fixture_file:
                toml.dump(fixture, fixture_file)
    if not successful:
        sys.exit(1)


if __name__ == "__main__":
    run()
