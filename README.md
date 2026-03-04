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
./scripts/install_xdg_bin.sh
```

Installed console commands (linked to XDG bin):
- `${XDG_BIN_HOME:-$HOME/.local/share/bin}/meshd`
- `${XDG_BIN_HOME:-$HOME/.local/share/bin}/meshctl`

Package source lives under `src/mesh/`.

If your shell PATH does not include `${XDG_BIN_HOME:-$HOME/.local/share/bin}`, add it.

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
- `meshctl event ingest-cloudflared`
- `meshctl event ingest-pacman`
- `meshctl profile run`

## Initial source adapters
- Cloudflared tunnel events from journald:
  - `meshctl event ingest-cloudflared --scope user --unit cloudflared.service`
- Pacman ALPM events from `/var/log/pacman.log`:
  - `meshctl event ingest-pacman --pacman-log /var/log/pacman.log`

Both adapters are incremental and store cursors under:
- `~/.local/state/mesh/sources/cloudflared.cursor.json`
- `~/.local/state/mesh/sources/pacman.cursor.json`

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

API specs + derived docs:
- OpenAPI 3.1 root: `api/openapi/openapi.yaml`
- Proto root: `api/proto/mesh/v1/mesh_control.proto`
- Redocly-derived docs: `docs/api/`
