# OctoPrint

The primary instance uses the official 1.11.8 image and the `octoprint-data`
Docker volume. From this directory, run `docker compose -f compose.primary.yaml
up -d` to apply the configuration. Docker restarts the container after boot.
This Compose project is not applied by the NixOS deployment script. See the
[operations handoff](../../docs/octopi-operations.md) for data, plugins,
recovery dependencies and outstanding tests.

Port 80 serves OctoPrint. The host `/dev` directory is visible read-only at
`/host-dev` so printer devices can appear after startup; Docker permits access
to USB ACM serial devices (major 166). In OctoPrint, the printer's additional
serial port is its stable `/host-dev/serial/by-id/` path. This mount exposes
host device names and the device rule permits ACM devices, not only one printer.

The Buster container no longer owns the printer or serves OctoPrint. Its old
HAProxy service is disabled; the official image serves HTTP on port 80.

## Migration notes

- Buster had a custom `OctoPrint-PiLink` / "Pi Music Link" plugin (version
  0.1.0), described as a navbar shortcut to a local multiroom coordinator.
  It was not installed in Docker. Investigate the multiroom services separately
  before deciding whether a shortcut is still useful. The previously identified
  dashboard address was `http://octoprint:32125`; it did not respond during the
  migration check on 2026-11-24. This does not establish why it was unavailable.
