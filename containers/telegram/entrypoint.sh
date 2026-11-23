#!/bin/sh
set -eu


case "$JOB_NAME" in
  hb-status)
    data=/data/tg
    required="/run/secrets/settings /run/secrets/telegram-api /data/tg/session_name.session /data/tg/hb_status.state"
    ;;
  mark-as-read)
    data=/data/tg
    required="/run/secrets/settings /run/secrets/telegram-api /data/tg/mark-as-read.session"
    ;;
  moon-clock)
    data=/data/moon
    required="/run/secrets/settings /run/secrets/moon-token /data/moon/moon_clock_TG_state.json /data/moon/semo_18.se1"
    ;;
  *) echo "Unknown JOB_NAME" >&2; exit 1 ;;
esac
[ -d "$data" ] || { echo "Missing required mount: $data" >&2; exit 1; }
chown 1000:1000 "$data"
for path in $required; do
  runuser -u bot -- test -r "$path" || {
    echo "Required file is missing or unreadable by UID 1000: $path" >&2
    exit 1
  }
done
# Cron jobs run as bot, so use writable FIFOs to forward their output to
# Docker's stdout/stderr without giving the bot access to PID 1's file handles.
mkdir -p /run/telegram-logs
rm -f /run/telegram-logs/stdout /run/telegram-logs/stderr
mkfifo -m 0622 /run/telegram-logs/stdout /run/telegram-logs/stderr
exec 3<>/run/telegram-logs/stdout
exec 4<>/run/telegram-logs/stderr
cat <&3 >&1 &
cat <&4 >&2 &
exec cron -f
