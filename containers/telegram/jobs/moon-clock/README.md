# moon-clock

- Schedule: minute 1 every three hours (`crontab`, Europe/Madrid).
- Dependencies: pyswisseph and python-telegram-bot (`requirements.txt`).
- Inputs: `/run/secrets/moon-token`, chat setting in the settings secret, and
  `/data/moon/semo_18.se1`.
- State: `/data/moon/moon_clock_TG_state.json`.
- Effects: sends moon-position messages and may delete old messages.
- Cron output: `/data/logs/moon_clock_TG.cron.log`.
