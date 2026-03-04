# TOOL_ARCHITECTURE_AND_DEPENDENCIES (mesh)

## Architecture
- `meshd` is the daemon substrate.
- `meshctl` is a thin CLI over core service functions.
- `ssot` validates persisted envelopes and payloads.
- `runtime.sources` contains incremental source adapters (cloudflared, pacman).

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
- OpenAPI 3.1 is derived from exported schemas (`api/openapi/openapi.yaml`).
- API docs are derived by Redocly bundle + docs render (`docs/api/*`).
