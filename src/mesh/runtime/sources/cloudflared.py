"""Ingest cloudflared journal events into mesh."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from mesh.core import service
from mesh.runtime_context import state_root


def default_cursor_file() -> Path:
    return state_root() / "sources" / "cloudflared.cursor.json"


def _load_cursor(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    cursor = raw.get("cursor") if isinstance(raw, dict) else ""
    return str(cursor).strip()


def _write_cursor(path: Path, cursor: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"cursor": cursor}, sort_keys=True) + "\n", encoding="utf-8"
    )


def _status_from_priority(priority: Any) -> str:
    try:
        p = int(str(priority))
    except (TypeError, ValueError):
        return "ok"
    if p <= 3:
        return "error"
    if p == 4:
        return "warn"
    return "ok"


def _journal_rows(
    *, unit: str, scope: str, cursor: str, initial_tail: int
) -> tuple[list[dict[str, Any]], str]:
    cmd = [
        "journalctl",
        f"--unit={unit}",
        "--output=json",
        "--no-pager",
    ]
    if scope == "system":
        cmd.insert(1, "--system")
    else:
        cmd.insert(1, "--user")
    if cursor:
        cmd.append(f"--after-cursor={cursor}")
    else:
        cmd.extend(["-n", str(initial_tail)])

    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "journalctl failed")

    rows: list[dict[str, Any]] = []
    last_cursor = cursor
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        rows.append(row)
        c = row.get("__CURSOR")
        if isinstance(c, str) and c.strip():
            last_cursor = c.strip()
    return rows, last_cursor


def ingest(
    *,
    config: Path,
    unit: str,
    scope: str,
    cursor_file: Path,
    initial_tail: int,
    router_log: str,
) -> int:
    previous_cursor = _load_cursor(cursor_file)
    rows, new_cursor = _journal_rows(
        unit=unit,
        scope=scope,
        cursor=previous_cursor,
        initial_tail=initial_tail,
    )

    for row in rows:
        payload = {
            "kind": "mesh.source.cloudflared.event",
            "status": _status_from_priority(row.get("PRIORITY")),
            "message": str(row.get("MESSAGE", "")).strip(),
            "data": {
                "unit": unit,
                "scope": scope,
                "cursor": row.get("__CURSOR"),
                "priority": row.get("PRIORITY"),
                "timestamp_usec": row.get("__REALTIME_TIMESTAMP"),
                "syslog_identifier": row.get("SYSLOG_IDENTIFIER"),
            },
        }
        event = {
            "topic": "mesh.source.cloudflared",
            "payload": payload,
        }
        service.handle_event(
            config=config, event=json.dumps(event), stdin=False, router_log=router_log
        )

    if new_cursor and new_cursor != previous_cursor:
        _write_cursor(cursor_file, new_cursor)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(service.default_config_path()))
    parser.add_argument("--unit", default="cloudflared.service")
    parser.add_argument("--scope", choices=("user", "system"), default="user")
    parser.add_argument("--cursor-file", default=str(default_cursor_file()))
    parser.add_argument("--initial-tail", type=int, default=50)
    parser.add_argument("--router-log", default="")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    return ingest(
        config=Path(args.config).expanduser(),
        unit=str(args.unit),
        scope=str(args.scope),
        cursor_file=Path(args.cursor_file).expanduser(),
        initial_tail=max(1, int(args.initial_tail)),
        router_log=str(args.router_log),
    )


if __name__ == "__main__":
    raise SystemExit(main())
