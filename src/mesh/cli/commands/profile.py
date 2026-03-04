"""Profile command group."""

from __future__ import annotations

from pathlib import Path

import typer

from mesh.core import service

app = typer.Typer(help="Profile operations")


@app.command("run")
def run(
    profile: str = typer.Argument(""),
    config: str = typer.Option(str(service.default_config_path()), "--config"),
    profile_log: str = typer.Option("", "--profile-log"),
) -> None:
    raise typer.Exit(
        service.run_profile(
            Path(config).expanduser(), profile=profile, profile_log=profile_log
        )
    )
