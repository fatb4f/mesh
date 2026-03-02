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

## XDG links
Create local repo symlinks to runtime config/data:

```bash
cd ~/src/mesh
./scripts/link_xdg_paths.sh
```

## Documentation
Shared standards and architecture live in `fabric-docs`.
