# Portainer

Web interface for inspecting and managing the Pi's Docker containers, images,
volumes and networks. Portainer CE runs as one Compose service, like the other
apps here.

- **UI:** `https://192.168.1.81:9443` (LAN only). The certificate is
  self-signed, so the browser warns once.
- **Data:** the `portainer-data` Docker volume (`/data`) holds the admin
  account, settings and stack records. Back it up if you care about them.
- **Start on boot:** `restart: unless-stopped`; Docker starts it after boot.
  NixOS does not create it from Git. Apply it by hand (below).
- **Firewall:** `hosts/octopi/configuration.nix` opens TCP 9443. That is the
  only NixOS change; run `sudo /etc/nixos/scripts/deploy.sh` to apply it.
- **Image tag:** `lts` is a floating tag. Pin an exact version once you have
  chosen one.

## Apply

```sh
docker compose -f /etc/nixos/containers/portainer/compose.yaml up -d
```

## First login

Open the UI and create the admin user within about 5 minutes of the first
start; Portainer locks itself after that. The form asks for a setup token,
which changes on every start:

```sh
docker logs portainer-portainer-1 2>&1 | grep setup_token
```

If the window locks, restart it (`docker restart portainer-portainer-1`),
fetch the new token and try again. Leave "Edge Compute" off; it is for
managing fleets of remote hosts.

## Compose and Portainer

Portainer sees every container through the Docker socket, including the
OctoPrint and Telegram projects. Stacks started from the command line show up
as "limited": you can view, start, stop, read logs and open a console, but
Portainer cannot edit or redeploy them. Git stays the source of truth.

## Security

Mounting `/var/run/docker.sock` gives Portainer root-level control of the
host, as does the `docker` group. Do not expose port 9443 beyond the LAN and
use a strong admin password.
