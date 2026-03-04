"""Daemon command group."""

from __future__ import annotations

from pathlib import Path

import typer

from mesh.cli.shared import console
from mesh.core import service

app = typer.Typer(help="Daemon operations")


@app.command("run")
def run(
    config: str = typer.Option(str(service.default_config_path()), "--config"),
    router_log: str = typer.Option("", "--router-log"),
) -> None:
    raise typer.Exit(service.daemon_run(Path(config).expanduser(), router_log))


@app.command("write-config")
def write_config(
    config: str = typer.Option(str(service.default_config_path()), "--config"),
) -> None:
    path = service.write_default_config(Path(config).expanduser())
    console.print(str(path))
