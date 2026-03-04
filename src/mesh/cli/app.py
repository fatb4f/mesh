"""meshctl entrypoint."""

from __future__ import annotations

import typer
from rich.traceback import install as install_rich_traceback

from mesh.cli.commands.daemon import app as daemon_app
from mesh.cli.commands.event import app as event_app
from mesh.cli.commands.profile import app as profile_app
from mesh.cli.commands.ssot import app as ssot_app
from mesh.logging_utils import setup_logging

app = typer.Typer(help="meshctl orchestration client")
app.add_typer(daemon_app, name="daemon")
app.add_typer(event_app, name="event")
app.add_typer(profile_app, name="profile")
app.add_typer(ssot_app, name="ssot")


def main() -> None:
    setup_logging()
    install_rich_traceback(show_locals=False)
    app()


if __name__ == "__main__":
    main()
