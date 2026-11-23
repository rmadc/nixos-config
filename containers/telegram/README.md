# Telegram jobs: Docker Compose

The three scheduled jobs run together in a Docker Compose service. Their
previous Buster cron entries were stopped during migration; never run both
schedulers at once, since they can duplicate messages and compete for the same
Telegram session. Check the live system before making changes.

## What each file does

- `compose.yaml` describes one service, three named volumes and three secrets.
- `Dockerfile` builds the image from Python 3.11 and the cron package.
- `requirements.txt` pins the four direct Python dependencies to the versions
  currently used in Buster; transitive dependencies and the base image digest
  are not yet pinned. The ARM64 image was built and its imports tested.
- `crontab` preserves the existing schedules in the Europe/Madrid timezone and
  locks the shared Telethon session to prevent the two jobs overlapping.
- `entrypoint.sh` checks required files, changes ownership of the three volume
  root directories, and starts cron; it does not recursively change ownership.
- `run_job.py` reads settings from a mounted secret and runs the selected job.
- `scripts/` contains copies of the three scripts with credentials, identifiers
  and writable paths supplied at runtime.

`hosts/octopi/configuration.nix` enables Docker and installs Compose for the
host. This does not start the Compose project. Docker's restart policy is
distinct from a NixOS service for managing the Compose project.

## Volumes and secrets

Compose project `telegram` uses three Docker-managed named volumes: `TG-data`
for the Telethon session and its state, `TG-moon` for the moon state and
ephemeris file, and `TG-logs` for cron output. Their explicit names are not
prefixed by the project name. They persist if the container is removed.
**Do not use `docker compose down --volumes`** unless you intend to delete that
persisted data.

The three Compose secrets originate from these host files:

```
/var/lib/telegram-jobs/secrets/settings.json
/var/lib/telegram-jobs/secrets/api_data.json
/var/lib/telegram-jobs/secrets/moon-token
```

`settings.json` needs keys `TG_USER_ID`, `TG_BARCELONA_GROUP`,
`TG_MOON_CHANNEL` and `MOON_CHAT_ID`, with values taken from the Buster scripts.
Use a string for `MOON_CHAT_ID`. `api_data.json` contains the existing Telethon
API credentials; `moon-token` contains the bot token. Do not place actual
values in this repository, the image, or the Nix store. Rotate the previously
exposed moon token.

With standalone Docker Compose, secrets backed by `file:` are bind-mounted from
the host. Their source files remain on disk; they are not Docker Swarm's
encrypted secrets. The jobs run as UID 1000, so that UID must be able to read
the mounted secret files. Set suitable host ownership and restrictive modes;
Compose cannot remap ownership or mode for file-backed secrets. Verify access
before enabling the jobs.

The volumes must be populated before startup. `TG-data` needs
`session_name.session` and `hb_status.state`; `TG-moon` needs
`moon_clock_TG_state.json` and `semo_18.se1`. Preserve the originals. Copy the
SQLite session only after the old jobs have stopped and no process has it open.
The entrypoint refuses to start if any of these files or secrets are missing or
unreadable. It changes only each volume root's ownership to UID/GID 1000, so
copied files must also be readable and writable by that user. `TG-logs` needs
a log rotation and monitoring plan.

## Inspect the service

```sh
cd /etc/nixos/containers/telegram
docker compose ps
docker compose logs --tail=30
```

Cron output is stored in `TG-logs`; application logs are also stored in
`TG-data`. Log rotation and monitoring need to be arranged. The moon bot's
scheduled Telegram send and recovery after a Pi reboot still need verification.
