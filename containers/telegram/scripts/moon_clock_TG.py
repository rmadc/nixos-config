#!/usr/bin/env python3
# Sends the Moon sign + whole degrees, then cleans up older tracked posts.
# Requires: python-telegram-bot==20.3, pyswisseph

import asyncio
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from math import floor
from pathlib import Path

import swisseph as swe
from telegram import Bot

# ===== CONFIG =====
BOT_TOKEN = Path(os.environ["MOON_BOT_TOKEN_FILE"]).read_text(encoding="utf-8").strip()
EPHE_PATH = os.environ["MOON_EPHE_PATH"]
CHAT_ID = os.environ["MOON_CHAT_ID"]
TOPOCENTRIC = False
LAT, LON, ALT = 41.3879, 2.1699, 15.0   # used only if TOPOCENTRIC=True
STATE_PATH = Path(os.environ["MOON_DATA_DIR"]) / "moon_clock_TG_state.json"
# ==================

SIGNS = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']
EARLY_DEGREE_PRIORITY = (0, 1, 2)
MIDDLE_DEGREE_PRIORITY = (15, 14, 16)
DELETE_AFTER = timedelta(hours=36)
DELETE_LIMIT = timedelta(hours=48)

swe.set_ephe_path(EPHE_PATH)
if TOPOCENTRIC:
    swe.set_topo(LON, LAT, ALT)


def moon_now_position():
    y, m, d, hh, mm, ss = time.gmtime()[:6]  # UTC
    jd_ut = swe.julday(y, m, d, hh + mm / 60 + ss / 3600.0)
    flags = swe.FLG_SWIEPH | (swe.FLG_TOPOCTR if TOPOCENTRIC else 0)
    xx, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    lon = xx[0]
    sign_idx = int(lon // 30)
    deg_in_sign = lon - 30 * sign_idx
    deg = int(floor(deg_in_sign))
    mins = int(floor((deg_in_sign - deg) * 60))
    if mins == 60:  # rollover
        mins = 0
        deg += 1
    if deg == 30:
        deg = 0
        sign_idx = (sign_idx + 1) % 12
    return SIGNS[sign_idx], deg


def parse_utc(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_state():
    if not STATE_PATH.exists():
        return []
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("unsupported cleanup state format")
    records = data.get("messages")
    if not isinstance(records, list):
        raise ValueError("cleanup state has no messages list")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("invalid cleanup state record")
        record["message_id"] = int(record["message_id"])
        record["degree"] = int(record["degree"])
        if record["message_id"] <= 0:
            raise ValueError("invalid Telegram message ID")
        if record.get("sign") not in SIGNS or not 0 <= record["degree"] <= 29:
            raise ValueError("invalid sign or degree in cleanup state")
        if not isinstance(record.get("chat_id"), str) or not record["chat_id"]:
            raise ValueError("invalid chat ID in cleanup state")
        parse_utc(record["sent_at"])
    return records


def save_state(records):
    fd, temp_path = tempfile.mkstemp(
        prefix="." + STATE_PATH.name + ".", suffix=".tmp", dir=str(STATE_PATH.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump({"schema_version": 1, "messages": records}, output, separators=(",", ":"))
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, str(STATE_PATH))
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def preferred_record(records, priority):
    candidates = [record for record in records if record["degree"] in priority]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda record: (
            priority.index(record["degree"]),
            parse_utc(record["sent_at"]),
            record["message_id"],
        ),
    )


def retained_message_ids(records, now):
    groups = {}
    for record in records:
        age = now - parse_utc(record["sent_at"])
        if age < DELETE_LIMIT:
            groups.setdefault((record["chat_id"], record["sign"]), []).append(record)

    retained = set()
    for group in groups.values():
        for priority in (EARLY_DEGREE_PRIORITY, MIDDLE_DEGREE_PRIORITY):
            record = preferred_record(group, priority)
            if record is not None:
                retained.add(record["message_id"])
    return retained


async def clean_old_messages(bot, records, now):
    retained = retained_message_ids(records, now)
    remaining = []
    for record in records:
        age = now - parse_utc(record["sent_at"])
        if age >= DELETE_LIMIT:
            # Telegram no longer allows this bot to delete the message.
            continue
        if age > DELETE_AFTER and record["message_id"] not in retained:
            try:
                await bot.delete_message(
                    chat_id=record["chat_id"], message_id=record["message_id"]
                )
                print(
                    "Deleted old Moon update {} ({}{:02d})".format(
                        record["message_id"], record["sign"], record["degree"]
                    ),
                    file=sys.stderr,
                    flush=True,
                )
                continue
            except Exception as error:
                print(
                    "Delete error for message {}: {}".format(record["message_id"], error),
                    file=sys.stderr,
                    flush=True,
                )
        remaining.append(record)
    save_state(remaining)


async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        records = load_state()
    except Exception as error:
        records = None
        print("Cleanup disabled because state could not be read: {}".format(error), file=sys.stderr)

    try:
        sign, degree = moon_now_position()
        text = "{}{:02d}".format(sign, degree)
        sent = await bot.send_message(chat_id=CHAT_ID, text=text)
        if records is not None:
            records.append({
                "chat_id": CHAT_ID,
                "message_id": int(sent.message_id),
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "sign": sign,
                "degree": degree,
            })
            try:
                save_state(records)
            except Exception as error:
                records = None
                print("Cleanup disabled because state could not be saved: {}".format(error), file=sys.stderr)
    except Exception as error:
        print("Send error: {}".format(error), file=sys.stderr, flush=True)

    if records is not None:
        try:
            await clean_old_messages(bot, records, datetime.now(timezone.utc))
        except Exception as error:
            print("Cleanup error: {}".format(error), file=sys.stderr, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
