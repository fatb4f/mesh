"""Ingest pacman log events into mesh."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from mesh.core import service
from mesh.runtime_context import state_root

ALPM_RE = re.compile(
    r"^\[(?P<ts>[^\]]+)\]\s+\[ALPM\]\s+"
    r"(?P<action>installed|upgraded|reinstalled|removed|downgraded)\s+"
    r"(?P<pkg>\S+)\s+\((?P<ver>[^\)]+)\)"
)


def default_cursor_file() -> Path:
    return state_root() / "sources" / "pacman.cursor.json"


def _load_cursor(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def _write_cursor(path: Path, cursor: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cursor, sort_keys=True) + "\n", encoding="utf-8")


def _tail_lines(path: Path, max_lines: int) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if max_lines <= 0:
        return lines
    return lines[-max_lines:]


def _read_delta(
    path: Path, cursor: dict[str, Any], bootstrap_tail: int
) -> tuple[list[str], dict[str, Any]]:
    stat = path.stat()
    inode = int(stat.st_ino)
    size = int(stat.st_size)

    old_inode = int(cursor.get("inode", -1))
    old_offset = int(cursor.get("offset", 0))

    if old_inode != inode or old_offset < 0 or old_offset > size:
        lines = _tail_lines(path, bootstrap_tail)
        return lines, {"inode": inode, "offset": size}

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        handle.seek(old_offset)
        lines = handle.read().splitlines()
    return lines, {"inode": inode, "offset": size}


def _parse_alpm(line: str) -> dict[str, Any] | None:
    m = ALPM_RE.match(line.strip())
    if not m:
        return None
    return {
        "timestamp": m.group("ts"),
        "action": m.group("action"),
        "package": m.group("pkg"),
        "version": m.group("ver"),
        "raw": line,
    }


def ingest(
    *,
    config: Path,
    pacman_log: Path,
    cursor_file: Path,
    bootstrap_tail: int,
    router_log: str,
) -> int:
    if not pacman_log.exists():
        raise FileNotFoundError(f"pacman log not found: {pacman_log}")

    old_cursor = _load_cursor(cursor_file)
    lines, new_cursor = _read_delta(pacman_log, old_cursor, bootstrap_tail)

    for line in lines:
        event_data = _parse_alpm(line)
        if event_data is None:
            continue
        payload = {
            "kind": f"mesh.source.pacman.{event_data['action']}",
            "status": "ok",
            "message": f"{event_data['action']} {event_data['package']} ({event_data['version']})",
            "data": {
                **event_data,
                "log_path": str(pacman_log),
            },
        }
        event = {
            "topic": "mesh.source.pacman",
            "payload": payload,
        }
        service.handle_event(
            config=config, event=json.dumps(event), stdin=False, router_log=router_log
        )

    _write_cursor(cursor_file, new_cursor)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(service.default_config_path()))
    parser.add_argument("--pacman-log", default="/var/log/pacman.log")
    parser.add_argument("--cursor-file", default=str(default_cursor_file()))
    parser.add_argument("--bootstrap-tail", type=int, default=100)
    parser.add_argument("--router-log", default="")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    return ingest(
        config=Path(args.config).expanduser(),
        pacman_log=Path(args.pacman_log).expanduser(),
        cursor_file=Path(args.cursor_file).expanduser(),
        bootstrap_tail=max(1, int(args.bootstrap_tail)),
        router_log=str(args.router_log),
    )


if __name__ == "__main__":
    raise SystemExit(main())
