# DockGraph

Live graph of the Pi's containers, networks, volumes and mounts. It only
observes; it does not start, stop or change containers. License: BSL-1.1.

- **Access:** the port is published on the Pi's loopback only
  (`127.0.0.1:7800`), so the LAN cannot reach it and no NixOS firewall rule
  or password is needed. From Windows, open an SSH tunnel and browse to
  `http://localhost:7800`:

  ```sh
  ssh -L 7800:127.0.0.1:7800 octoprint
  ```

- **Why not the LAN:** the detail panels show container environment
  variables and labels. To publish on the LAN, change the port mapping to
  `"7800:7800"`, set `DG_PASSWORD_FILE` (see the upstream README), and open
  TCP 7800 in `hosts/octopi/configuration.nix`.
- **Compose files:** `/etc/nixos/containers` is mounted read-only. DockGraph
  scans it for `.yml`/`.yaml` files and shows services that are defined but
  not running.
- **Docker socket:** mounted read-only. The socket API is still sensitive;
  read-only on the mount does not restrict what the Docker API reports.
- **Data:** none. There is no volume.
- **Start on boot:** `restart: unless-stopped`; not created from Git by NixOS.
- **Image:** pinned to `0.5.0` (multi-arch, includes arm64). The project is
  young (first commit 2026-03); review releases before bumping.

## Apply

```sh
docker compose -f /etc/nixos/containers/dockgraph/compose.yaml up -d
```
