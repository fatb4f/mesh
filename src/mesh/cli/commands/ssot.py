"""SSOT command group."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from mesh.cli.shared import console
from mesh.ssot import registry, validate

app = typer.Typer(help="SSOT schema tools")


@app.command("list")
def list_schemas() -> None:
    console.print_json(json.dumps({"schemas": registry.schema_names()}, sort_keys=True))


@app.command("validate-tree")
def validate_tree() -> None:
    count, schemas = validate.validate_tree()
    console.print_json(json.dumps({"checked": count, "schemas": schemas}, sort_keys=True))


@app.command("validate-file")
def validate_file(schema: str = typer.Argument(...), path: str = typer.Argument(...)) -> None:
    validate.validate_file(schema, Path(path).expanduser())
    console.print("ok")


@app.command("validate-json")
def validate_json(schema: str = typer.Argument(...), stdin: bool = typer.Option(True, "--stdin")) -> None:
    if not stdin:
        raise typer.BadParameter("only --stdin is currently supported")
    payload = json.loads(typer.get_text_stream("stdin").read())
    validate.validate_or_raise(schema, payload)
    console.print("ok")
