# mark-as-read

- Schedule: minutes 2 and 32 of every hour (`crontab`, Europe/Madrid).
- Dependency: Telethon (`requirements.txt`).
- Inputs: `/run/secrets/telegram-api`, chat settings in the settings secret,
  and `/data/tg/mark-as-read.session`, a separately authorized Telegram login.
- Effects: marks the latest message in the configured chats as read.
- Operational output: stdout/stderr, collected by Docker.

A per-job lock prevents overlapping instances of this job. The session is for
the same account as hb-status, but uses a separate Telegram authorization.
