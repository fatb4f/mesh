#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_BIN_HOME="${XDG_BIN_HOME:-$XDG_DATA_HOME/bin}"

uv tool install --editable . --force

UV_BIN_DIR="$(uv tool dir --bin)"
mkdir -p "$XDG_BIN_HOME"

for cmd in meshctl meshd; do
  if [[ ! -e "$UV_BIN_DIR/$cmd" ]]; then
    echo "missing uv tool executable: $UV_BIN_DIR/$cmd" >&2
    exit 1
  fi
  ln -sfn "$UV_BIN_DIR/$cmd" "$XDG_BIN_HOME/$cmd"
  echo "linked: $XDG_BIN_HOME/$cmd -> $UV_BIN_DIR/$cmd"
done

echo "done"
