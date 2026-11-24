# OctoPrint

The primary instance uses the official 1.11.8 image and the `octoprint-data`
Docker volume. From this directory, run `docker compose -f compose.primary.yaml
up -d` to apply the configuration. Docker restarts the container after boot.

Port 80 serves OctoPrint. The host `/dev` directory is visible read-only at
`/host-dev` so printer devices can appear after startup; Docker permits access
to USB ACM serial devices (major 166). In OctoPrint, the printer's additional
serial port is its stable `/host-dev/serial/by-id/` path. This mount exposes
host device names and the device rule permits ACM devices, not only one printer.

The Buster container no longer owns the printer. Its HAProxy still serves HTTPS
on port 443 and forwards OctoPrint requests to port 80; the old webcam routes
remain in place.
