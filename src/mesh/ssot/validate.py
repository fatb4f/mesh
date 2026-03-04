"""Schema validation helpers for mesh SSOT.

Prefers `jsonschema` when available. Falls back to built-in validators for the
current mesh schema set so source checkout usage still works without extra deps.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mesh.ssot.registry import load_schema, schema_dir, schema_names

try:
    from jsonschema import Draft202012Validator, RefResolver

    _HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    Draft202012Validator = None  # type: ignore[assignment]
    RefResolver = None  # type: ignore[assignment]
    _HAS_JSONSCHEMA = False


def _build_validator(schema_name: str) -> Draft202012Validator:
    if not _HAS_JSONSCHEMA:
        raise RuntimeError("jsonschema backend unavailable")
    schema = load_schema(schema_name)
    base = schema_dir().resolve().as_uri() + "/"
    resolver = RefResolver(base_uri=base, referrer=schema)
    return Draft202012Validator(schema, resolver=resolver)


def _validate_event_envelope(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValueError("event.envelope: payload must be object")
    required = [
        "schema_name",
        "schema_version",
        "event_id",
        "ts",
        "topic",
        "source",
        "payload",
    ]
    for key in required:
        if key not in payload:
            raise ValueError(f"event.envelope: missing required key `{key}`")
    if payload.get("schema_name") != "event.envelope":
        raise ValueError("event.envelope: schema_name must be `event.envelope`")
    if payload.get("schema_version") != "v1":
        raise ValueError("event.envelope: schema_version must be `v1`")
    if not isinstance(payload.get("payload"), dict):
        raise ValueError("event.envelope: payload field must be object")


def _validate_mesh_signal(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValueError("mesh.signal: payload must be object")
    for key in ("kind", "status"):
        if key not in payload:
            raise ValueError(f"mesh.signal: missing required key `{key}`")
    allowed = {"ok", "warn", "error", "scaffold"}
    status = payload.get("status")
    if status not in allowed:
        raise ValueError(f"mesh.signal: invalid status `{status}`")
    kind = payload.get("kind")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError("mesh.signal: kind must be non-empty string")


def _validate_profile_run(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValueError("profile.run: payload must be object")
    for key in ("profile", "allowed", "status"):
        if key not in payload:
            raise ValueError(f"profile.run: missing required key `{key}`")
    if not isinstance(payload.get("allowed"), bool):
        raise ValueError("profile.run: allowed must be boolean")
    allowed_status = {"scaffold", "pass", "fail", "blocked"}
    status = payload.get("status")
    if status not in allowed_status:
        raise ValueError(f"profile.run: invalid status `{status}`")


def _validate_builtin(schema_name: str, payload: Any) -> None:
    if schema_name == "event.envelope":
        _validate_event_envelope(payload)
        return
    if schema_name == "mesh.signal":
        _validate_mesh_signal(payload)
        return
    if schema_name == "profile.run":
        _validate_profile_run(payload)
        return
    raise ValueError(f"unsupported schema without jsonschema backend: {schema_name}")


def validate_or_raise(schema_name: str, payload: Any) -> None:
    if not _HAS_JSONSCHEMA:
        _validate_builtin(schema_name, payload)
        return
    validator = _build_validator(schema_name)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if not errors:
        return
    first = errors[0]
    path = ".".join(str(p) for p in first.path) or "<root>"
    raise ValueError(f"schema={schema_name} path={path}: {first.message}")


def validate_file(schema_name: str, path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_or_raise(schema_name, payload)


def validate_tree() -> tuple[int, list[str]]:
    checked: list[str] = []
    for name in schema_names():
        if _HAS_JSONSCHEMA:
            _build_validator(name)
        else:
            # Parse-only check if backend is unavailable.
            load_schema(name)
        checked.append(name)
    return len(checked), checked
