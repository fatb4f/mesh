#!/usr/bin/env python3
"""Derive OpenAPI 3.1 component catalog from exported schemas."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "api" / "openapi" / "schemas"
OUT = ROOT / "api" / "openapi" / "openapi.yaml"
PROTO_CANONICAL = "api/proto/mesh/v1/mesh_control.proto"
SCHEMA_CANONICAL = "src/mesh/ssot/schemas/schema.index.json"


def component_name(file_name: str) -> str:
    stem = file_name
    if stem.endswith(".schema.json"):
        stem = stem[: -len(".schema.json")]
    out = []
    upper_next = True
    for ch in stem:
        if ch.isalnum():
            out.append(ch.upper() if upper_next else ch)
            upper_next = False
            continue
        upper_next = True
    return "".join(out) or "Schema"


def main() -> int:
    schema_files = sorted(SCHEMAS_DIR.glob("*.schema.json"))
    if not schema_files:
        raise SystemExit("no schemas found; run scripts/export_schemas.py first")

    lines = [
        "openapi: 3.1.0",
        "info:",
        "  title: mesh control and event contracts",
        "  version: 0.1.0",
        "  description: Derived OpenAPI component catalog for mesh contracts.",
        "servers: []",
        "paths: {}",
        "components:",
        "  schemas:",
    ]

    for path in schema_files:
        lines.append(f"    {component_name(path.name)}:")
        lines.append(f"      $ref: ./schemas/{path.name}")

    lines.extend(
        [
            "x-derived-from:",
            f"  - {SCHEMA_CANONICAL}",
            f"  - {PROTO_CANONICAL}",
            "",
        ]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
