"""SSOT command group."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from mesh.cli.shared import console, print_json
from mesh.ssot import registry, validate

app = typer.Typer(help="SSOT schema tools")


@app.command("list")
def list_schemas() -> None:
    print_json({"schemas": registry.schema_names()})


@app.command("validate-tree")
def validate_tree() -> None:
    count, schemas = validate.validate_tree()
    print_json({"checked": count, "schemas": schemas})


@app.command("validate-file")
def validate_file(
    schema: str = typer.Argument(...), path: str = typer.Argument(...)
) -> None:
    validate.validate_file(schema, Path(path).expanduser())
    console.print("ok")


@app.command("validate-json")
def validate_json(
    schema: str = typer.Argument(...), stdin: bool = typer.Option(True, "--stdin")
) -> None:
    if not stdin:
        raise typer.BadParameter("only --stdin is currently supported")
    payload = json.loads(typer.get_text_stream("stdin").read())
    validate.validate_or_raise(schema, payload)
    console.print("ok")
