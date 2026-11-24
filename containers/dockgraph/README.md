# DockGraph

Live graph of the Pi's containers, networks, volumes and mounts. It only
observes; it does not start, stop or change containers. License: BSL-1.1.

- **Access:** `http://192.168.1.81:7800` on the LAN. There is no password:
  anyone on the LAN can see container environment variables, labels, mounts
  and logs. This is a deliberate home-lab choice. Without a password,
  DockGraph answers only requests addressed by IP or `localhost`; to use a
  hostname, set `DG_ALLOWED_HOSTS`.
- **Firewall:** `hosts/octopi/configuration.nix` opens TCP 7800. Apply it
  with `sudo /etc/nixos/scripts/deploy.sh`.
- **Adding a password later:** set `DG_PASSWORD_FILE` to a Compose file
  secret (see the upstream README).
- **Compose files:** `/etc/nixos/containers` is mounted read-only. DockGraph
  scans it for `.yml`/`.yaml` files and shows services that are defined but
  not running.
- **Docker socket:** mounted read-only, but the Docker API behind it is still
  sensitive. Keep the UI on the LAN.
- **Data:** none. There is no volume.
- **Start on boot:** `restart: unless-stopped`; not created from Git by NixOS.
- **Image:** pinned to `0.5.0` (multi-arch, includes arm64). The project is
  young (first commit 2026-03); review releases before bumping.

## Apply

```sh
docker compose -f /etc/nixos/containers/dockgraph/compose.yaml up -d
```
