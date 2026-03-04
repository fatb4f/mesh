# TOOL_ARCHITECTURE_AND_DEPENDENCIES (mesh)

## Architecture
- `meshd` is the daemon substrate.
- `meshctl` is a thin CLI over core service functions.
- `ssot` validates persisted envelopes and payloads.

## Dependency policy
Core runtime dependencies mirror spawn patterns:
- `typer`, `rich` for CLI UX
- `pydantic` for typed config validation
- `jsonschema` for SSOT validation
- `xdg-base-dirs` for path resolution
- `dataconfy` optional for YAML/JSON config loading

## SSOT policy
- JSON Schema governs cross-unit persisted payloads.
- Required schemas are indexed in `src/mesh/ssot/schemas/schema.index.json`.
