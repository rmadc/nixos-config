"""Tests for the hb-status job. Telegram is faked: no network is used."""
import fcntl
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "jobs" / "hb-status" / "main.py"


@pytest.fixture
def job(tmp_path, monkeypatch):
    """Load main.py with temporary files and fake third-party modules."""
    credentials = tmp_path / "credentials.json"
    credentials.write_text(json.dumps({"api_id": 1, "api_hash": "fake"}))
    monkeypatch.setenv("TG_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("TG_CREDENTIALS_FILE", str(credentials))
    monkeypatch.setenv("TG_USER_ID", "1")

    fake_pytz = types.ModuleType("pytz")
    fake_pytz.timezone = lambda name: None
    fake_sync = types.ModuleType("telethon.sync")
    fake_sync.TelegramClient = None
    monkeypatch.setitem(sys.modules, "pytz", fake_pytz)
    monkeypatch.setitem(sys.modules, "telethon", types.ModuleType("telethon"))
    monkeypatch.setitem(sys.modules, "telethon.sync", fake_sync)

    spec = importlib.util.spec_from_file_location("hb_status", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ignored_status_has_no_signature(job):
    assert job.signature_for("UserStatusLastWeek()") is None


def test_offline_signature_includes_last_seen_time(job):
    text = "UserStatusOffline(was_online=2026-01-01 10:00:00)"
    assert job.signature_for(text) == ["UserStatusOffline", "2026-01-01 10:00:00"]


def test_second_run_exits_quietly_while_locked(job):
    with open(job.LOCK_FILE, "a") as other_run:
        fcntl.flock(other_run.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        job.main()

class FakeClient:
    """Stands in for TelegramClient. A status of None raises the alert."""

    def __init__(self, fail_send=False):
        self.fail_send = fail_send
        self.sent = []

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def get_entity(self, user_id):
        return types.SimpleNamespace(status=None)

    def send_message(self, *args, **kwargs):
        if self.fail_send:
            raise ConnectionError("send failed")
        self.sent.append(args)


def run_job(job, monkeypatch, client):
    monkeypatch.setattr(job, "TelegramClient", lambda *args: client)
    job.main()
    return client


def previous_run_saw_a_status(job):
    job.save_state({**job.load_state(), "alert_none": False})


def test_failed_alert_is_sent_on_the_next_run(job, monkeypatch):
    previous_run_saw_a_status(job)
    run_job(job, monkeypatch, FakeClient(fail_send=True))

    retry = run_job(job, monkeypatch, FakeClient())

    assert len(retry.sent) == 1


def test_sent_alert_is_not_repeated(job, monkeypatch):
    previous_run_saw_a_status(job)
    first = run_job(job, monkeypatch, FakeClient())

    second = run_job(job, monkeypatch, FakeClient())

    assert len(first.sent) == 1
    assert second.sent == []


def test_retry_does_not_duplicate_log_entries(job, monkeypatch):
    previous_run_saw_a_status(job)
    run_job(job, monkeypatch, FakeClient(fail_send=True))
    run_job(job, monkeypatch, FakeClient())

    assert len(Path(job.LOG_FILE).read_text().splitlines()) == 1