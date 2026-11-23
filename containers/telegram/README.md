# Scheduled Telegram jobs

This Compose project contains three independent services, images, schedules and
job directories. Docker is enabled by the host NixOS configuration. The jobs
continue to use the same pinned package versions as the previous single image.

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

- `TG-data`: existing status history, state, logs and both Telethon sessions.
  `session_name.session` is for hb-status; `mark-as-read.session` is a separate
  login to the same Telegram account. Both session files are credentials.
- `TG-moon`: moon state and ephemeris data.
- `TG-logs`: scheduled-job output. Rotation and monitoring are not yet set up.
- `/var/lib/telegram-jobs/secrets/`: file-backed Compose secrets, stored on the
  host rather than in the repository or image. File-backed Compose secrets are
  bind mounts, not Swarm's encrypted secret store. The bot runs as UID 1000.

The images and container filesystems are replaceable; these named volumes and
host secret files hold persistent data. Do not remove volumes during a normal
Compose shutdown. Avoid running old and new schedulers at the same time.

## Inspect

```sh
cd /etc/nixos/containers/telegram
docker compose ps -a
docker compose logs --tail=30
```

Cron output currently goes to files in `TG-logs`; application history and logs
also exist in `TG-data`. Moving operational output to stdout/stderr with
rotation is separate follow-up work. The moon bot's scheduled Telegram send and
Pi reboot recovery still need verification.
