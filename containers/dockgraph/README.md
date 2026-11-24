# DockGraph

Live graph of the Pi's containers, networks, volumes and mounts. It only
observes; it does not start, stop or change containers. License: BSL-1.1.

- **Access:** `http://192.168.1.81:7800` on the LAN, behind a password. The
  UI is plain HTTP, so the password crosses the LAN unencrypted.
- **Firewall:** `hosts/octopi/configuration.nix` opens TCP 7800. Apply it
  with `sudo /etc/nixos/scripts/deploy.sh`.
- **Password:** read from `/var/lib/dockgraph/password` (a file-backed Compose
  secret, same pattern as the Telegram jobs). The file is not in Git. Create
  it once on the Pi:

  ```sh
  sudo install -d -m 700 /var/lib/dockgraph
  sudo sh -c 'umask 022; read -r -s -p "Password: " p; echo; printf %s "$p" > /var/lib/dockgraph/password'
  ```

  The file is world-readable (0644) inside a root-only directory so the
  container user can read it; only root can enter the directory.
- **Why a password:** the detail panels show container environment variables
  and labels.
- **Compose files:** `/etc/nixos/containers` is mounted read-only. DockGraph
  scans it for `.yml`/`.yaml` files and shows services that are defined but
  not running.
- **Docker socket:** mounted read-only, but the Docker API behind it is still
  sensitive. Keep the UI on the LAN.
- **Data:** none apart from the password file. There is no volume.
- **Start on boot:** `restart: unless-stopped`; not created from Git by NixOS.
- **Image:** pinned to `0.5.0` (multi-arch, includes arm64). The project is
  young (first commit 2026-03); review releases before bumping.

## Apply

```sh
docker compose -f /etc/nixos/containers/dockgraph/compose.yaml up -d
```
