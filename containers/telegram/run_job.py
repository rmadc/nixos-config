"""Load private runtime settings and execute one scheduled script."""
import json
import os
import sys
from pathlib import Path

allowed = {"hb_status.py", "mark_as_read.py", "moon_clock_TG.py"}
if len(sys.argv) != 2 or sys.argv[1] not in allowed:
    raise SystemExit("unknown job")

with open("/run/secrets/settings", encoding="utf-8") as settings_file:
    settings = json.load(settings_file)

required = ("TG_USER_ID", "TG_BARCELONA_GROUP", "TG_MOON_CHANNEL", "MOON_CHAT_ID")
for key in required:
    value = settings.get(key)
    if not isinstance(value, (str, int)) or not str(value):
        raise SystemExit("missing setting: " + key)
    os.environ[key] = str(value)

os.environ.update({
    "TG_DATA_DIR": "/data/tg",
    "TG_CREDENTIALS_FILE": "/run/secrets/telegram-api",
    "MOON_DATA_DIR": "/data/moon",
    "MOON_EPHE_PATH": "/data/moon",
    "MOON_BOT_TOKEN_FILE": "/run/secrets/moon-token",
})
script = Path("/app/scripts") / sys.argv[1]
os.execv(sys.executable, [sys.executable, str(script)])
