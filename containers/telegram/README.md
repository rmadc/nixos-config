# Telegram jobs: Docker Compose draft

This is an untested learning draft. Buster still runs the jobs. Do not start
the Compose service until the existing cron entries have been stopped and a
controlled migration of the data has been planned. Two schedulers can send
duplicate messages and compete for the same Telegram session.

## What each file does

- `compose.yaml` describes one service, three named volumes and three secrets.
- `Dockerfile` builds the image from Python 3.11 and the cron package.
- `requirements.txt` pins the four direct Python dependencies to the versions
  currently used in Buster; transitive dependencies and the base image digest
  are not yet pinned. The ARM64 build of `pyswisseph` is unverified.
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

Compose creates three Docker-managed named volumes: `telegram-data` for the
Telethon session and its state, `moon-data` for the moon state and ephemeris
file, and `job-logs` for cron output. Docker prefixes their names with the
Compose project name, here `octopi-telegram`. They persist if the container is
removed. **Do not use `docker compose down --volumes`** unless you intend to
delete that persisted data.

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

The volumes must be populated before startup. `telegram-data` needs
`session_name.session` and `hb_status.state`; `moon-data` needs
`moon_clock_TG_state.json` and `semo_18.se1`. Preserve the originals. Copy the
SQLite session only after the old jobs have stopped and no process has it open.
The entrypoint refuses to start if any of these files or secrets are missing or
unreadable. It changes only each volume root's ownership to UID/GID 1000, so
copied files must also be readable and writable by that user. `job-logs` needs
a log rotation and monitoring plan.

## Commands for later review

These are **not executed by this draft phase**. They assume this repository
and the Docker configuration have already been made available on the Pi.

```sh
cd /etc/nixos/containers/telegram
sudo docker compose config   # Inspect the resolved configuration; no start.
sudo docker compose build    # Build the ARM64 image; does not start jobs.
```

Do not run `docker compose up` until secrets and volumes are prepared, the
image has been validated, and the Buster jobs have been stopped as part of an
agreed cutover. The safe data-copy, validation, cutover and rollback commands
still need to be designed and reviewed. Restarting the Pi or the container has
not been tested. The Docker service itself also needs to be enabled through a
reviewed NixOS deployment before the Compose commands will work on the Pi.
