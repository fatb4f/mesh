# SYSTEMD_EVENT_MODEL (mesh)

Mesh follows a systemd-first runtime model:
- systemd owns activation/supervision boundaries.
- meshd owns contract validation and routing semantics.
- cross-unit persisted artifacts are schema-governed JSON.

Current scaffolded signals:
- `mesh.daemon.start`
- `mesh.event.ingested`
- `mesh.profile.run`
- `mesh.source.cloudflared`
- `mesh.source.pacman`

All emitted rows use `event.envelope`.

## Initial source strategy
- Cloudflared:
  - read journald (`cloudflared.service`) with cursor checkpointing.
  - emit `mesh.source.cloudflared` with payload kind `mesh.source.cloudflared.event`.
- Pacman:
  - read `/var/log/pacman.log` with inode+offset cursor checkpointing.
  - parse ALPM package actions and emit `mesh.source.pacman`.

## Systemd timer-first wiring
See `docs/systemd/` for ready-to-use user units:
- `mesh-source-cloudflared.service` + `.timer`
- `mesh-source-pacman.service` + `.timer`
