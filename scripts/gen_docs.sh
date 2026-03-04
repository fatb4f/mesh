#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

./scripts/gen.sh

mkdir -p docs/api

npx -y @redocly/cli@latest bundle \
  api/openapi/openapi.yaml \
  --dereferenced \
  -o docs/api/openapi.bundle.json

PYTHONPATH=src uv run python scripts/gen_docs.py

echo "gen-docs: ok"
