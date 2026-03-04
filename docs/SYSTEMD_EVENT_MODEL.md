# SYSTEMD_EVENT_MODEL (mesh)

Mesh follows a systemd-first runtime model:
- systemd owns activation/supervision boundaries.
- meshd owns contract validation and routing semantics.
- cross-unit persisted artifacts are schema-governed JSON.

Current scaffolded signals:
- `mesh.daemon.start`
- `mesh.event.ingested`
- `mesh.profile.run`

All emitted rows use `event.envelope`.
