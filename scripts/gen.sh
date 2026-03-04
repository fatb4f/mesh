#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

test -f src/mesh/ssot/schemas/schema.index.json
test -f api/proto/mesh/v1/mesh_control.proto

PYTHONPATH=src uv run python scripts/export_schemas.py
PYTHONPATH=src uv run python scripts/derive_openapi.py

echo "gen: ok"
