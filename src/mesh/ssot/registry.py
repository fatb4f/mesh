"""Schema registry loader for mesh."""

from __future__ import annotations

import json
from pathlib import Path


def schema_dir() -> Path:
    return Path(__file__).resolve().parent / "schemas"


def index_path() -> Path:
    return schema_dir() / "schema.index.json"


def load_index() -> dict:
    return json.loads(index_path().read_text(encoding="utf-8"))


def schema_names() -> list[str]:
    idx = load_index()
    items = idx.get("schemas", {})
    if not isinstance(items, dict):
        return []
    return sorted(items.keys())


def schema_path(name: str) -> Path:
    idx = load_index()
    schemas = idx.get("schemas", {})
    if not isinstance(schemas, dict) or name not in schemas:
        raise KeyError(f"unknown schema: {name}")
    rel = schemas[name].get("path")
    if not isinstance(rel, str) or not rel:
        raise KeyError(f"invalid schema path for: {name}")
    return schema_dir() / rel


def load_schema(name: str) -> dict:
    path = schema_path(name)
    return json.loads(path.read_text(encoding="utf-8"))
