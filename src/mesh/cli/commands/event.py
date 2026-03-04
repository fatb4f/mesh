"""Event command group."""

from __future__ import annotations

from pathlib import Path

import typer

from mesh.cli.shared import print_error
from mesh.core import service
from mesh.runtime.sources import cloudflared, pacman

app = typer.Typer(help="Event ingestion operations")


@app.command("handle")
def handle(
    config: str = typer.Option(str(service.default_config_path()), "--config"),
    event: str = typer.Option("", "--event"),
    stdin: bool = typer.Option(False, "--stdin"),
    router_log: str = typer.Option("", "--router-log"),
) -> None:
    raise typer.Exit(
        service.handle_event(
            Path(config).expanduser(), event=event, stdin=stdin, router_log=router_log
        )
    )


@app.command("ingest-cloudflared")
def ingest_cloudflared(
    config: str = typer.Option(str(service.default_config_path()), "--config"),
    unit: str = typer.Option("cloudflared.service", "--unit"),
    scope: str = typer.Option("user", "--scope", help="journal scope: user|system"),
    cursor_file: str = typer.Option("", "--cursor-file"),
    initial_tail: int = typer.Option(50, "--initial-tail"),
    router_log: str = typer.Option("", "--router-log"),
) -> None:
    cursor = (
        Path(cursor_file).expanduser()
        if cursor_file.strip()
        else cloudflared.default_cursor_file()
    )
    try:
        rc = cloudflared.ingest(
            config=Path(config).expanduser(),
            unit=unit,
            scope=scope,
            cursor_file=cursor,
            initial_tail=initial_tail,
            router_log=router_log,
        )
    except Exception as exc:
        print_error(f"ingest-cloudflared failed: {exc}")
        raise typer.Exit(2) from exc
    raise typer.Exit(rc)


@app.command("ingest-pacman")
def ingest_pacman(
    config: str = typer.Option(str(service.default_config_path()), "--config"),
    pacman_log: str = typer.Option("/var/log/pacman.log", "--pacman-log"),
    cursor_file: str = typer.Option("", "--cursor-file"),
    bootstrap_tail: int = typer.Option(100, "--bootstrap-tail"),
    router_log: str = typer.Option("", "--router-log"),
) -> None:
    cursor = (
        Path(cursor_file).expanduser()
        if cursor_file.strip()
        else pacman.default_cursor_file()
    )
    try:
        rc = pacman.ingest(
            config=Path(config).expanduser(),
            pacman_log=Path(pacman_log).expanduser(),
            cursor_file=cursor,
            bootstrap_tail=bootstrap_tail,
            router_log=router_log,
        )
    except Exception as exc:
        print_error(f"ingest-pacman failed: {exc}")
        raise typer.Exit(2) from exc
    raise typer.Exit(rc)
