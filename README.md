# mesh

Mesh fabric runtime repository.

## Scope
- `meshd`: event-router/runtime daemon
- `meshctl`: thin operator/orchestration client

## Status
Current `meshd` is an explicit scaffold with command surface only:
- `daemon`
- `handle-event`
- `run-profile`

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
