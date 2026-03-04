"""Shared CLI objects."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console

console = Console(stderr=False)
error_console = Console(stderr=True, style="bold red")


def print_json(payload: dict[str, Any]) -> None:
    console.print_json(json.dumps(payload, sort_keys=True))


def print_error(message: str) -> None:
    error_console.print(message)
