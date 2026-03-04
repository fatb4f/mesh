# SSOT Schema Registry

- Registry: `schema.index`
- Version: `v1`

## Schemas

| Name | Title | Description | File |
| --- | --- | --- | --- |
| `event.envelope` | EventEnvelope | Canonical envelope for persisted mesh events crossing systemd unit boundaries. | `event.envelope.schema.json` |
| `mesh.signal` | MeshSignal | Normalized mesh signal payload emitted by source adapters and runtime actions. | `mesh.signal.schema.json` |
| `profile.run` | ProfileRun | Profile execution decision payload for allow/block outcome tracking. | `profile.run.schema.json` |
