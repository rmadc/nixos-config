#!/usr/bin/env python3
"""Mark the latest messages read in the Barcelona and Moon chats."""

import json
import logging
import os
from pathlib import Path

from telethon.sync import TelegramClient

BASE_DIR = Path(os.environ["TG_DATA_DIR"])
CREDENTIALS_FILE = Path(os.environ["TG_CREDENTIALS_FILE"])
SESSION_PATH = str(BASE_DIR / "mark-as-read")
BARCELONA_GROUP = os.environ["TG_BARCELONA_GROUP"]
MOON_CHANNEL = os.environ["TG_MOON_CHANNEL"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def archived_group_entity(client):
    matches = [
        dialog.entity
        for dialog in client.iter_dialogs(folder=1)
        if dialog.name == BARCELONA_GROUP
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "Expected one archived group named {!r}; found {}".format(
                BARCELONA_GROUP, len(matches)
            )
        )
    return matches[0]


def mark_latest_read(client, entity, label):
    latest = client.get_messages(entity, limit=1)
    if not latest:
        logging.info("No messages to mark read in %s", label)
        return
    client.send_read_acknowledge(entity, latest[0])
    logging.info(
        "Marked %s (id=%s) read through message %s",
        label,
        entity.id,
        latest[0].id,
    )


def main():
    with CREDENTIALS_FILE.open(encoding="utf-8") as f:
        credentials = json.load(f)

    failures = []
    with TelegramClient(
        SESSION_PATH, credentials["api_id"], credentials["api_hash"]
    ) as client:
        targets = [
            (BARCELONA_GROUP, lambda: archived_group_entity(client)),
            (MOON_CHANNEL, lambda: client.get_entity(MOON_CHANNEL)),
        ]
        for label, resolve_entity in targets:
            try:
                entity = resolve_entity()
                mark_latest_read(client, entity, label)
            except Exception:
                logging.exception("Failed to mark %s read", label)
                failures.append(label)

    if failures:
        raise RuntimeError("Mark-as-read failed for: {}".format(", ".join(failures)))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Mark-as-read run failed")
        raise
