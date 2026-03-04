"""meshd daemon substrate."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
import tomllib
import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from mesh.runtime_context import config_root, state_root
from mesh.ssot.validate import validate_or_raise

try:
    from dataconfy import ConfigManager
except ImportError:  # pragma: no cover
    ConfigManager = None


class MeshRuntimeModel(BaseModel):
    router_log: str
    profile_log: str
    allowed_profiles: list[str] = Field(default_factory=list)


class MeshConfigModel(BaseModel):
    runtime: MeshRuntimeModel


def default_config_path() -> Path:
    return config_root() / "meshd.toml"


def default_values() -> dict[str, Any]:
    root = state_root()
    return {
        "runtime": {
            "router_log": str(root / "meshd-router.jsonl"),
            "profile_log": str(root / "meshd-profile.jsonl"),
            "allowed_profiles": [],
        }
    }


def _load_config_via_dataconfy(path: Path) -> dict[str, Any] | None:
    if ConfigManager is None or path.suffix.lower() not in {".yaml", ".yml", ".json"}:
        return None

    cfg = default_values()
    mgr = ConfigManager(app_name="mesh", config_dir=path.parent, use_env_vars=True)
    loaded = mgr.load(dict, filename=path.name)
    if isinstance(loaded, dict):
        cfg.update(loaded)
    return cfg


def load_config(path: Path) -> dict[str, Any]:
    cfg = default_values()
    if not path.exists():
        loaded: dict[str, Any] = {}
    elif path.suffix.lower() in {".yaml", ".yml", ".json"}:
        loaded = _load_config_via_dataconfy(path) or {}
    else:
        loaded = tomllib.loads(path.read_text(encoding="utf-8"))

    section = loaded.get("runtime") if isinstance(loaded, dict) else None
    if isinstance(section, dict):
        cfg["runtime"].update(section)

    try:
        validated = MeshConfigModel.model_validate(cfg)
    except ValidationError as exc:
        raise SystemExit(f"invalid config: {exc}") from exc
    return validated.model_dump()


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _event_envelope(
    *,
    topic: str,
    payload: dict[str, Any],
    request_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    row = {
        "schema_name": "event.envelope",
        "schema_version": "v1",
        "event_id": f"evt-{uuid.uuid4().hex}",
        "request_id": request_id or f"req-{uuid.uuid4().hex[:12]}",
        "run_id": run_id or "mesh-runtime",
        "ts": _utc_now(),
        "topic": topic,
        "source": "mesh",
        "payload": payload,
    }
    validate_or_raise("event.envelope", row)
    return row


def write_default_config(path: Path) -> Path:
    cfg = default_values()["runtime"]
    lines = [
        "[runtime]",
        f'router_log = "{cfg["router_log"]}"',
        f'profile_log = "{cfg["profile_log"]}"',
        "allowed_profiles = []",
    ]
    _atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def daemon_run(config: Path, router_log: str = "") -> int:
    cfg = load_config(config)
    log_path = Path(router_log or cfg["runtime"]["router_log"]).expanduser()

    signal = {
        "kind": "mesh.daemon.start",
        "status": "scaffold",
        "message": "meshd daemon scaffold: router loop not implemented",
    }
    validate_or_raise("mesh.signal", signal)
    _write_jsonl(log_path, _event_envelope(topic="mesh.daemon.start", payload=signal))
    return 0


def handle_event(
    config: Path, event: str = "", stdin: bool = False, router_log: str = ""
) -> int:
    cfg = load_config(config)
    log_path = Path(router_log or cfg["runtime"]["router_log"]).expanduser()

    event_data: Any = {}
    if stdin:
        raw = os.sys.stdin.read().strip()
        if raw:
            try:
                event_data = json.loads(raw)
            except json.JSONDecodeError:
                event_data = {"raw": raw, "invalid_json": True}
    elif event:
        try:
            event_data = json.loads(event)
        except json.JSONDecodeError:
            event_data = {"raw": event, "invalid_json": True}

    topic = "mesh.event.ingested"
    payload: dict[str, Any]
    if isinstance(event_data, dict) and isinstance(event_data.get("payload"), dict):
        payload = event_data["payload"]
        maybe_topic = event_data.get("topic")
        if isinstance(maybe_topic, str) and maybe_topic.strip():
            topic = maybe_topic.strip()
    else:
        payload = {
            "kind": "mesh.event.ingested",
            "status": "ok",
            "data": event_data,
        }

    validate_or_raise("mesh.signal", payload)
    _write_jsonl(log_path, _event_envelope(topic=topic, payload=payload))
    return 0


def run_profile(config: Path, profile: str, profile_log: str = "") -> int:
    cfg = load_config(config)
    log_path = Path(profile_log or cfg["runtime"]["profile_log"]).expanduser()
    p = profile.strip()
    allowed_set = {
        str(item).strip()
        for item in cfg["runtime"].get("allowed_profiles", [])
        if str(item).strip()
    }
    allowed = not allowed_set or p in allowed_set

    payload = {
        "profile": p,
        "allowed": allowed,
        "status": "scaffold" if allowed else "blocked",
    }
    validate_or_raise("profile.run", payload)
    _write_jsonl(log_path, _event_envelope(topic="mesh.profile.run", payload=payload))
    return 0 if allowed else 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_daemon = sub.add_parser("daemon", help="Run mesh daemon loop")
    p_daemon.add_argument("--config", default=str(default_config_path()))
    p_daemon.add_argument("--router-log", default="")
    p_daemon.set_defaults(
        func=lambda a: daemon_run(Path(a.config).expanduser(), a.router_log)
    )

    p_event = sub.add_parser("handle-event", help="Handle one JSON event")
    p_event.add_argument("--config", default=str(default_config_path()))
    p_event.add_argument("--event", required=False, default="")
    p_event.add_argument("--stdin", action="store_true")
    p_event.add_argument("--router-log", default="")
    p_event.set_defaults(
        func=lambda a: handle_event(
            Path(a.config).expanduser(), a.event, a.stdin, a.router_log
        )
    )

    p_run = sub.add_parser("run-profile", help="Run named profile")
    p_run.add_argument("profile", nargs="?", default="")
    p_run.add_argument("--config", default=str(default_config_path()))
    p_run.add_argument("--profile-log", default="")
    p_run.set_defaults(
        func=lambda a: run_profile(
            Path(a.config).expanduser(), a.profile, a.profile_log
        )
    )

    p_write = sub.add_parser("write-config", help="Write default meshd config")
    p_write.add_argument("--config", default=str(default_config_path()))
    p_write.set_defaults(
        func=lambda a: (print(write_default_config(Path(a.config).expanduser())), 0)[1]
    )

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
