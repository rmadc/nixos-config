#!/bin/sh
set -eu

for path in /data/tg /data/moon /data/logs; do
  [ -d "$path" ] || { echo "Missing required mount: $path" >&2; exit 1; }
  chown 1000:1000 "$path"
done

for path in /run/secrets/settings /run/secrets/telegram-api /run/secrets/moon-token \
            /data/tg/session_name.session /data/tg/hb_status.state \
            /data/moon/moon_clock_TG_state.json /data/moon/semo_18.se1; do
  runuser -u bot -- test -r "$path" || {
    echo "Required file is missing or unreadable by UID 1000: $path" >&2
    exit 1
  }
done

exec cron -f
