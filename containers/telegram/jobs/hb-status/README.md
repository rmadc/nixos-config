# hb-status

- Schedule: every minute (`crontab`, Europe/Madrid).
- Dependencies: Telethon and pytz (`requirements.txt`).
- Inputs: `/run/secrets/telegram-api`, `TG_USER_ID` in the settings secret,
  and the existing `/data/tg/session_name.session` Telethon login.
- Data: `/data/tg/hb_status.state` and `/data/tg/hb_status.log` (status history).
- Effects: may send an alert to the account's saved messages.
- Operational output: stdout/stderr, collected by Docker.

A per-job lock prevents overlapping instances of this job.
