"""Load the selected job's settings and start it."""
import json
import os
from pathlib import Path
import sys

job = os.environ.get("JOB_NAME")
required = {
    "hb-status": ("TG_USER_ID",),
    "mark-as-read": ("TG_BARCELONA_GROUP", "TG_MOON_CHANNEL"),
    "moon-clock": ("MOON_CHAT_ID",),
}
if job not in required:
    raise SystemExit("Unknown JOB_NAME")

with open("/run/secrets/settings", encoding="utf-8") as settings_file:
    settings = json.load(settings_file)
for key in required[job]:
    value = settings.get(key)
    if not isinstance(value, (str, int)) or not str(value):
        raise SystemExit("Missing setting: " + key)
    os.environ[key] = str(value)

if job in ("hb-status", "mark-as-read"):
    os.environ.update(TG_DATA_DIR="/data/tg", TG_CREDENTIALS_FILE="/run/secrets/telegram-api")
else:
    os.environ.update(MOON_DATA_DIR="/data/moon", MOON_EPHE_PATH="/data/moon", MOON_BOT_TOKEN_FILE="/run/secrets/moon-token")
script = Path("/app/jobs") / job / "main.py"
os.execv(sys.executable, [sys.executable, str(script)])
