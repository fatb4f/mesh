# mesh

Mesh fabric runtime repository.

## Scope
- `meshd`: daemon runtime substrate
- `meshctl`: thin orchestration/operator client
- contracts: SSOT schemas under `src/mesh/ssot/schemas/`

## Source Layout
- `src/mesh/cli/app.py`
- `src/mesh/core/service.py`
- `src/mesh/ssot/*`
- `docs/*`

## Run
```bash
cd ~/src/mesh
./bin/meshctl daemon run
```

Generate default daemon config (optional):
```bash
./bin/meshctl daemon write-config
```

## Install (packaged)
```bash
cd ~/src/mesh
uv pip install --system -e .
```

Installed console commands:
- `meshd`
- `meshctl`

Package source lives under `src/mesh/`.

## SSOT schema tools
- List schemas:
  - `meshctl ssot list`
- Validate schema registry + references:
  - `meshctl ssot validate-tree`
- Validate file:
  - `meshctl ssot validate-file event.envelope /path/to/event.json`
- Validate stdin JSON:
  - `cat payload.json | meshctl ssot validate-json event.envelope`

## Current command surface
- `meshctl daemon run`
- `meshctl event handle`
- `meshctl profile run`

## Optional dependencies
- `xdg-base-dirs` (`python-xdg-base-dirs`) for strict XDG path resolution.
- `pydantic` for typed config validation.
- `dataconfy` for YAML/JSON config loading with env support.

`meshd.toml` remains the default config format. Use `.yaml`/`.json` to activate
`dataconfy` loading.

## XDG links
Create local repo symlinks to runtime config/data:

```bash
cd ~/src/mesh
./scripts/link_xdg_paths.sh
```

## Engineering Rules
This repo follows `fabric-docs/docs/FABRIC_MUST_RULES.md` and `fabric-docs/docs/SYSTEMD_DIRECTIVE_GUIDELINES.md` as mandatory architecture constraints.

## Documentation
Shared standards and architecture live in `fabric-docs`.
