"""meshctl entrypoint."""

from __future__ import annotations

import typer

from mesh.cli.commands.daemon import app as daemon_app
from mesh.cli.commands.event import app as event_app
from mesh.cli.commands.profile import app as profile_app
from mesh.cli.commands.ssot import app as ssot_app

app = typer.Typer(help="meshctl orchestration client")
app.add_typer(daemon_app, name="daemon")
app.add_typer(event_app, name="event")
app.add_typer(profile_app, name="profile")
app.add_typer(ssot_app, name="ssot")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
