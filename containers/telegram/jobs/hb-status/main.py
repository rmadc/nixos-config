import fcntl
import json
import os
import re
from datetime import datetime

import pytz
from telethon.sync import TelegramClient

BASE_DIR = os.environ["TG_DATA_DIR"]
with open(os.environ["TG_CREDENTIALS_FILE"], "r") as f:
    creds = json.load(f)

USER_ID = int(os.environ["TG_USER_ID"])
SESSION_NAME = os.path.join(BASE_DIR, "session_name")
LOG_FILE = os.path.join(BASE_DIR, "hb_status.log")
STATE_FILE = os.path.join(BASE_DIR, "hb_status.state")
LOCK_FILE = os.path.join(BASE_DIR, "hb_status.lock")
LOCAL_TZ = pytz.timezone("Europe/Madrid")
IGNORED_STATES = {"UserStatusLastWeek", "UserStatusLastMonth"}
STATE_PATTERN = re.compile(r"^(UserStatus[A-Za-z0-9_]+)")
OFFLINE_TIME_PATTERN = re.compile(r"was_online=(.*)\)$")


def status_text(status):
    return "None" if status is None else str(status)


def signature_for(text):
    match = STATE_PATTERN.match(text)
    state = match.group(1) if match else text
    if state in IGNORED_STATES:
        return None
    if state == "UserStatusOffline":
        time_match = OFFLINE_TIME_PATTERN.search(text)
        return [state, time_match.group(1) if time_match else text]
    return [state]


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "signature": None,
            "alert_none": None,
            "date": None,
            "day_has_records": False,
            "day_has_trackable": False,
        }


def save_state(state):
    temp_file = STATE_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(state, f)
        f.write("\n")
    os.chmod(temp_file, 0o600)
    os.replace(temp_file, STATE_FILE)


def append_entry(kind, timestamp, status):
    with open(LOG_FILE, "a") as f:
        f.write("{} {} | {}\n".format(kind, timestamp, status))


def main():
    lock = open(LOCK_FILE, "a")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return

    state = load_state()
    with TelegramClient(SESSION_NAME, creds["api_id"], creds["api_hash"]) as client:
        try:
            user = client.get_entity(USER_ID)
            current_status = user.status
            current_text = status_text(current_status)
            current_signature = signature_for(current_text)
            now = datetime.now(LOCAL_TZ)
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            current_date = now.strftime("%Y-%m-%d")

            if state.get("date") and state["date"] != current_date:
                if state.get("day_has_records") and not state.get("day_has_trackable"):
                    append_entry(
                        "DAILY ", state["date"],
                        "no trackable status (LastWeek/LastMonth suppressed)",
                    )
                state["day_has_records"] = False
                state["day_has_trackable"] = False
            state["date"] = current_date
            state["day_has_records"] = True

            if current_signature is not None:
                previous_signature = state.get("signature")
                if not state.get("day_has_trackable"):
                    kind = (
                        "CHANGE"
                        if previous_signature is not None and current_signature != previous_signature
                        else "DAILY "
                    )
                    append_entry(kind, timestamp, current_text)
                    state["day_has_trackable"] = True
                elif current_signature != previous_signature:
                    append_entry("CHANGE", timestamp, current_text)
                state["signature"] = current_signature

            current_none = current_status is None
            previous_none = state.get("alert_none")
            alert = None
            if previous_none is not None and previous_none != current_none:
                if current_none:
                    alert = "<b>❌ Mel UNBLOCK:</b> {} ({})".format(current_text, timestamp)
                else:
                    alert = "<b>✅ Mel UNBLOCK:</b> {} ({})".format(current_text, timestamp)
            state["alert_none"] = current_none
            save_state(state)

            if alert:
                client.send_message("me", alert, parse_mode="html")

        except Exception as e:
            print("[{}] ERROR: {}".format(datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"), str(e)))


if __name__ == "__main__":
    main()
