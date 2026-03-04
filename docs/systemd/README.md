# mesh systemd source units

These are starter user units for periodic source ingestion.

## Install

```bash
mkdir -p ~/.config/systemd/user
cp docs/systemd/mesh-source-*.service docs/systemd/mesh-source-*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now mesh-source-cloudflared.timer
systemctl --user enable --now mesh-source-pacman.timer
```

## Notes

- `mesh-source-cloudflared.service` defaults to user journal scope (`--scope user`).
- If cloudflared runs as a system unit, change to `--scope system`.
- `mesh-source-pacman.service` reads `/var/log/pacman.log` incrementally.
- Event rows are appended to `runtime.router_log` in `~/.config/mesh/meshd.toml`.
