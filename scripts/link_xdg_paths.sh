#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"

mkdir -p "${XDG_CONFIG_HOME}/mesh" "${XDG_DATA_HOME}/mesh"

ln -sfn "${XDG_CONFIG_HOME}/mesh" "${ROOT}/config"
ln -sfn "${XDG_DATA_HOME}/mesh" "${ROOT}/data"

echo "linked:"
echo "  ${ROOT}/config -> ${XDG_CONFIG_HOME}/mesh"
echo "  ${ROOT}/data   -> ${XDG_DATA_HOME}/mesh"
