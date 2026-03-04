#!/usr/bin/env python3
"""Generate API docs from OpenAPI bundle and SSOT schema index."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_BUNDLE_JSON = ROOT / "docs" / "api" / "openapi.bundle.json"
SCHEMA_INDEX_JSON = ROOT / "src" / "mesh" / "ssot" / "schemas" / "schema.index.json"
DOCS_DIR = ROOT / "docs" / "api"


def render_openapi_components(bundle: dict) -> str:
    info = bundle.get("info", {})
    components = bundle.get("components", {})
    schemas = components.get("schemas", {}) if isinstance(components, dict) else {}

    lines = [
        "# OpenAPI Components",
        "",
        f"- Title: `{info.get('title', '')}`",
        f"- Version: `{info.get('version', '')}`",
        "",
        "## Schemas",
        "",
        "| Name | Type | Description |",
        "| --- | --- | --- |",
    ]

    for name in sorted(schemas.keys()):
        if name.endswith(".schema"):
            continue
        schema = schemas[name] if isinstance(schemas[name], dict) else {}
        type_ = schema.get("type", "-")
        description = str(schema.get("description", "-")).replace("\n", " ").strip() or "-"
        lines.append(f"| `{name}` | `{type_}` | {description} |")

    lines.append("")
    return "\n".join(lines)


def render_ssot_registry(index: dict) -> str:
    schema_dir = SCHEMA_INDEX_JSON.parent
    schemas = index.get("schemas", {})
    if not isinstance(schemas, dict):
        schemas = {}

    lines = [
        "# SSOT Schema Registry",
        "",
        f"- Registry: `{index.get('schema_name', '')}`",
        f"- Version: `{index.get('schema_version', '')}`",
        "",
        "## Schemas",
        "",
        "| Name | Title | Description | File |",
        "| --- | --- | --- | --- |",
    ]

    for name in sorted(schemas.keys()):
        item = schemas[name]
        file = item.get("path", "") if isinstance(item, dict) else ""
        title = "-"
        description = "-"
        schema_path = schema_dir / file
        if file and schema_path.exists():
            try:
                doc = json.loads(schema_path.read_text(encoding="utf-8"))
                title = str(doc.get("title", "-")).replace("\n", " ").strip() or "-"
                description = str(doc.get("description", "-")).replace("\n", " ").strip() or "-"
            except Exception:
                pass
        lines.append(f"| `{name}` | {title} | {description} | `{file}` |")

    lines.append("")
    return "\n".join(lines)


def render_readme() -> str:
    return "\n".join(
        [
            "# API Docs",
            "",
            "Generated documentation from OpenAPI and JSON Schema sources.",
            "",
            "## Sources",
            "- OpenAPI root: `api/openapi/openapi.yaml`",
            "- JSON Schema registry: `src/mesh/ssot/schemas/schema.index.json`",
            "- Proto root: `api/proto/mesh/v1/mesh_control.proto`",
            "",
            "## Generated Files",
            "- `docs/api/openapi.bundle.json`",
            "- `docs/api/openapi_components.md`",
            "- `docs/api/ssot_schemas.md`",
            "",
            "## Regenerate",
            "```bash",
            "./scripts/gen_docs.sh",
            "```",
            "",
        ]
    )


def main() -> int:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    bundle = json.loads(OPENAPI_BUNDLE_JSON.read_text(encoding="utf-8"))
    schema_index = json.loads(SCHEMA_INDEX_JSON.read_text(encoding="utf-8"))

    (DOCS_DIR / "openapi_components.md").write_text(
        render_openapi_components(bundle),
        encoding="utf-8",
    )
    (DOCS_DIR / "ssot_schemas.md").write_text(
        render_ssot_registry(schema_index),
        encoding="utf-8",
    )
    (DOCS_DIR / "README.md").write_text(render_readme(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
