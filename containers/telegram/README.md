# Scheduled Telegram jobs

This Compose project contains three independent services, images, schedules and
job directories. Docker is enabled by the host NixOS configuration. Python
dependencies are pinned separately for each job; consult their requirements
files for the current versions.

| Service | Schedule (Europe/Madrid) | Purpose |
| --- | --- | --- |
| [hb-status](jobs/hb-status/README.md) | Every minute | Record a Telegram user's status history. |
| [mark-as-read](jobs/mark-as-read/README.md) | Minutes 2 and 32 hourly | Mark configured chats read. |
| [moon-clock](jobs/moon-clock/README.md) | Minute 1 every 3 hours | Send moon-position messages and manage old ones. |

`Dockerfile`, `entrypoint.sh` and `run_job.py` are shared build/runtime tools.
Each `jobs/<name>/` directory owns its code, requirements, cron schedule and
input/output documentation. Each service is built separately with its own
`JOB` argument and receives only its required volumes and secrets.

## Data and secrets

- `TG-hb-status`: the hb-status Telegram session, state and `hb_status.log`
  result history.
- `TG-mark-as-read`: its separate Telethon session for the same account.
- `TG-moon-clock`: moon state and ephemeris data.
- `/var/lib/telegram-jobs/secrets/`: file-backed Compose secrets, stored on the
  host rather than in the repository or image. The bot runs as UID 1000.

Each job mounts only its own data volume. Session files are credentials. Compose
file-backed secrets are bind mounts, not Swarm's encrypted secret store. The
images and container filesystems are replaceable; the named volumes and host
secret files hold persistent data. Never remove volumes during a normal Compose
shutdown. The previous TG-data, TG-moon and TG-logs volumes contain historical
copies and should be retained until the migration is verified and backed up.

## Operational logs

The scheduler forwards each job's stdout and stderr to its container's Docker
logs. Compose uses the Docker `local` logging driver with a 10 MB limit per
file and three rotated files per container. `hb_status.log` is application
result data and remains in `TG-hb-status`; historical pre-migration logs
remain in the old volumes. Docker-managed logs are not application backups.

## Inspect

```sh
cd /etc/nixos/containers/telegram
docker compose ps -a
docker compose logs --tail=30
```

Use `docker compose logs -f <service>` to follow a job's output. The moon bot's
message cleanup limitations and reboot verification are tracked in the
[operations handoff](../../docs/octopi-operations.md).
