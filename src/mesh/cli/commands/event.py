"""Event command group."""

from __future__ import annotations

from pathlib import Path

import typer

from mesh.core import service

app = typer.Typer(help="Event ingestion operations")


@app.command("handle")
def handle(
    config: str = typer.Option(str(service.default_config_path()), "--config"),
    event: str = typer.Option("", "--event"),
    stdin: bool = typer.Option(False, "--stdin"),
    router_log: str = typer.Option("", "--router-log"),
) -> None:
    raise typer.Exit(
        service.handle_event(Path(config).expanduser(), event=event, stdin=stdin, router_log=router_log)
    )
