"""Runtime path and environment helpers for mesh."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from xdg_base_dirs import xdg_cache_home as _xdg_cache_home_fn
    from xdg_base_dirs import xdg_config_home as _xdg_config_home_fn
    from xdg_base_dirs import xdg_state_home as _xdg_state_home_fn
except ImportError:  # pragma: no cover
    _xdg_cache_home_fn = None
    _xdg_config_home_fn = None
    _xdg_state_home_fn = None


def _systemd_directory(env_name: str) -> Path | None:
    value = os.environ.get(env_name, "").strip()
    if not value:
        return None
    first = value.split(":", 1)[0].strip()
    if not first:
        return None
    return Path(first).expanduser()


def xdg_state_home() -> Path:
    if _xdg_state_home_fn is not None:
        return _xdg_state_home_fn()
    return Path(os.environ.get("XDG_STATE_HOME", "~/.local/state")).expanduser()


def xdg_cache_home() -> Path:
    if _xdg_cache_home_fn is not None:
        return _xdg_cache_home_fn()
    return Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser()


def xdg_config_home() -> Path:
    if _xdg_config_home_fn is not None:
        return _xdg_config_home_fn()
    return Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()


def state_root() -> Path:
    root = _systemd_directory("STATE_DIRECTORY")
    if root is None:
        root = xdg_state_home() / "mesh"
    root.mkdir(parents=True, exist_ok=True)
    return root


def cache_root() -> Path:
    root = _systemd_directory("CACHE_DIRECTORY")
    if root is None:
        root = xdg_cache_home() / "mesh"
    root.mkdir(parents=True, exist_ok=True)
    return root


def config_root() -> Path:
    root = _systemd_directory("CONFIGURATION_DIRECTORY")
    if root is None:
        root = xdg_config_home() / "mesh"
    root.mkdir(parents=True, exist_ok=True)
    return root
