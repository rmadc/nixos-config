# Octopi operations and migration handoff

This records the observed setup on 2026-11-24. Runtime state can change; inspect
the host before acting. Never overwrite the original OctoPrint SD card, its
backup image, or the extracted root filesystem archive. The original archive
was identified as `D:\SD-images\octopi-rootfs_69eed6d7.tar.xz` on INTELi7;
verify that path and the backup image location before relying on either.

## Host and deployment

- Raspberry Pi 4 Model B rev 1.1, 2 GB RAM, hostname `octopi`, static Ethernet
  address `192.168.1.81`. The Windows SSH alias `octoprint` connects as `ra`.
- The NixOS flake checkout is `/etc/nixos`. The `octopi` flake entry imports
  `hosts/octopi/configuration.nix`, its hardware module, and
  `hosts/octopi/buster-container.nix`. Docker and Compose are enabled there.
- On the Pi, `sudo /etc/nixos/scripts/deploy.sh` checks for a clean checkout,
  fast-forward pulls, and switches NixOS using the short hostname. It does not
  build images or run Compose. See the root README for checkout and revision
  commands. Git edits should normally be made on INTELi7 and pushed first.
- `ra` is in the Docker group, which effectively grants root-level host access.
  SSH public keys are declared in the host configuration; private keys do not
  belong in Git. The SSH alias and its private key are Windows configuration,
  not supplied by this repository.

## Running services

| Component | Definition | Startup and operational state |
| --- | --- | --- |
| Buster | `hosts/octopi/buster-container.nix` | NixOS `octopi-buster.service`; rootfs at `/var/lib/machines/octopi-buster`. |
| OctoPrint | `containers/octoprint/compose.primary.yaml` | Official `octoprint/octoprint:1.11.8`, HTTP port 80, `octoprint-data` volume. |
| Telegram jobs | `containers/telegram/compose.yaml` | Three separately built services: `hb-status`, `mark-as-read`, `moon-clock`. |
| Portainer | `containers/portainer/compose.yaml` | `portainer/portainer-ce:lts`, HTTPS UI on port 9443 (LAN), `portainer-data` volume. Needs the NixOS firewall rule. Deployed and running; the admin user was created in the UI on 2026-11-24. |
| DockGraph | `containers/dockgraph/compose.yaml` | `dockgraph/dockgraph:0.5.0`, read-only topology viewer on Pi loopback port 7800 (SSH tunnel), no volume. |

Docker and Buster's systemd unit are enabled at boot. The six Docker
containers use `restart: unless-stopped`; Docker restarts existing containers,
but does not automatically create them from Git on a fresh host. A manually
stopped container can remain stopped. NixOS deploys do not apply Compose edits.

```sh
systemctl status octopi-buster docker
docker ps -a
docker volume ls
docker compose -f /etc/nixos/containers/octoprint/compose.primary.yaml ps
docker compose -f /etc/nixos/containers/telegram/compose.yaml ps
```

To apply reviewed Compose changes, use the relevant project directory and
`docker compose up -d`; use `docker compose up -d --build` for Telegram code or
Dockerfile changes. For OctoPrint specify `-f compose.primary.yaml`. These
commands may recreate containers: do not do that during a print. Never use
`down -v` as routine cleanup; it removes named volumes.

## OctoPrint

The official image tag is `1.11.8`; the inspected image used Python 3.10.18,
which is upstream end-of-life. An image tag can be republished, so a tag alone
does not guarantee an identical future image. The old experimental custom 2.x
image was not the deployed service. A successful Cura print and printer
power-off/power-on reconnect were observed; a full Pi reboot with the printer
off still needs testing. Webcam setup is deferred.

The original Buster settings and profiles were copied into
`octoprint-data` at `/octoprint/octoprint`; uploads, generated web assets and
old logs were excluded. OctoPrint regenerates web assets. Its web user `octo`,
settings, printer profiles, scripts, plugin data, new uploads, and generated
files now live in this volume. Installed Python plugins live in
`/octoprint/plugins` in the same volume, so recreating a container while
preserving the volume keeps them. Web-installed plugin versions are not
declared in Git. At the checkpoint: PrettyGCode 2.6.0, SmartPreheat 0.0.6,
Tempsgraph 0.3.7, and the local `convert_TF_SD.py` plugin were loaded. The
latter rewrites TF to SD in printer responses; whether this firmware still
needs it has not been established. UI Customizer was not reinstalled.

OctoPrint's in-app restart command was corrected to
`s6-svc -r /var/run/s6/services/octoprint` and tested. The old Buster host
reboot and shutdown commands were removed from its settings; the web UI does
not provide NixOS host power control. These settings live in the volume, not
in the Compose file. Buster's OctoPrint and HAProxy services were disabled;
the old self-signed HTTPS endpoint is no longer provided.

The host `/dev` is mounted read-only at `/host-dev` and the container permits
character devices with USB ACM major 166. This makes changing devices visible
but exposes host device names and permits ACM devices generally, not solely
the printer. The selected additional serial path is
`/host-dev/serial/by-id/usb-marlinfw.org_Marlin_USB_Device_0F00300FAF4A10485D67AA23F50020C4-if00`.
The path is device-specific. Confirm the correct printer before changing it.

## Telegram data and recovery

The Telegram README describes job schedules, file-backed secrets and volumes.
The Compose definitions and job scripts are in Git; the files under
`/var/lib/telegram-jobs/secrets/` and volumes `TG-hb-status`,
`TG-mark-as-read` and `TG-moon-clock` are not. The two Telethon sessions are
separate authorizations for the same Telegram account. `TG-hb-status` includes
`hb_status.log`, which is application result history; operational logs go to
Docker. The old volumes `TG-data`, `TG-moon`, `TG-logs` and earlier
`octopi-telegram_*` volumes may contain historical copies: inspect and back up
before deleting any of them.

The moon job tracks messages in its state and deletes selected tracked messages
between 36 and 48 hours old, intentionally retaining some representatives.
Previously observed old messages were no longer tracked and had passed the
deletion window. Their desired cleanup policy remains undecided; do not assume
all old messages are unwanted or delete them automatically.

Rebuilding Telegram images uses a floating `python:3.11-slim-bookworm` base
and Debian package repositories even though job requirements are pinned.
Rebuilding later can therefore yield different image contents. Back up the
current image digests if exact deployments matter.

## Buster and remaining work

Buster shares the host network; it is not network-isolated. SSH to the guest
is available on host port 2222 (user `pi`; use the existing authorized key).
Its cron, `erika-watchdog` and `erika-telegram` services were running at the
checkpoint. The six obsolete FTX lending-rate cron entries were commented out
in Buster `/etc/crontab`; scripts and logs remain. A pre-change copy is at
`/etc/crontab.before-ftx-disabled-20261124` inside Buster. These are guest
filesystem changes, not declarations in the NixOS repository.
The Erika watchdog was previously configured to reach the Windows INTELi7
service at `192.168.1.37`; its remote allowlist was adjusted for both the
original Pi and the NixOS Pi. Verify the live Windows configuration rather
than assuming that local, uncommitted code changes were deployed.

The custom Pi Music Link OctoPrint plugin was a navbar shortcut to a multiroom
coordinator, not the coordinator itself. It was not reinstalled. The previously
identified dashboard `http://octoprint:32125` did not respond at the checkpoint;
the cause and both audio setups remain to be investigated separately. Keep the
audio services separate from the OctoPrint container.

A built-in OctoPrint backup made from Buster for migration comparison is at
`/home/pi/octoprint-comparison-20261124.zip` inside Buster, with uploads and
timelapses excluded. Comparison found all 29 backed-up files in the copied
Docker data, though some runtime files subsequently changed. Temporary
OctoPrint test containers, images or volumes may remain; inspect before cleanup.

## Backups and fresh-host recovery

Git alone cannot recover the system. Maintain separate protected, preferably
off-device backups of:

- The original SD image, original archive and Buster rootfs, including
  `/var/lib/machines/octopi-buster` and any changes made after extraction.
- `octoprint-data` and all required `TG-*` named volumes, including historical
  result data and Telethon session files. Container images are not backups.
- `/var/lib/telegram-jobs/secrets/`, SSH private keys and other credentials;
  store them securely outside Git. Session files are credentials too.

For consistent backups of live databases and session files, stop the relevant
jobs or use a verified application-consistent snapshot. Restore and test on a
separate target before relying on a backup; do not run duplicate active bots or
two OctoPrint instances connected to one printer. Preserve file ownership,
permissions and symlinks. OctoPrint's built-in Backup & Restore can exclude
uploads and reinstall repository plugins, but may install newer plugin versions
and can retain machine-specific settings that need review.

On a replacement host: restore host-specific NixOS hardware configuration and
network access; deploy NixOS and Docker; restore the required secrets and
volumes; check paths, permissions and device identity; then apply the Compose
projects and validate each service. Restore Buster separately if its remaining
services are still required. No automated full-host recovery procedure has yet
been tested.
