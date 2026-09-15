"""Shared card operations for the macOS GUI, CLI, and chat entry points."""

import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from shared.cardstore import CardStore, ContentConflictError, split_multi_tasks


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DESKTOP_STICKY_CARD_HOME", SCRIPT_DIR)).expanduser().resolve()
_store = CardStore(DATA_DIR)

CONTENT_FILE = str(_store.content_file)
HABITS_FILE = str(_store.habits_file)
TAGS_FILE = str(_store.tags_file)
STATE_FILE = str(_store.state_file)
HISTORY_DIR = str(_store.history_dir)


def ensure_daily_snapshot(reason="auto"):
    return _store.ensure_daily_snapshot(reason)


def read_lines():
    return _store.read_lines()


def write_lines(lines):
    return _store.write_lines(lines)


def get_tasks(lines):
    return _store.get_tasks(lines)


def find_insert_position(lines):
    return _store.find_insert_position(lines)


def load_tag_names():
    return _store.load_tag_names()


def add_tasks(texts, tag=None):
    return _store.add_tasks(texts, tag=tag)


def toggle_task(num, to_done):
    return _store.toggle_task(num, to_done)


def remove_task(num):
    return _store.remove_task(num)


def clear_done():
    return _store.clear_done()


def set_title(title):
    return _store.set_title(title)


def overwrite(text):
    return _store.overwrite(text)


def read_json_file(path, default=None):
    return _store.read_json(path, default=default)


def update_json_file(path, updates, reason="state-save"):
    return _store.update_json(path, updates, reason=reason)


def write_text_file(path, text, reason, expected_text=None):
    return _store.write_text(path, text, reason=reason, expected_text=expected_text)


def toggle_task_at_line(path, line_idx, record_done=True):
    return _store.toggle_line(path, line_idx, record_done=record_done)


def reorder_line(path, source_idx, destination_idx):
    return _store.reorder_line(path, source_idx, destination_idx)


def reset_habits_if_needed(today):
    return _store.reset_habits_if_needed(today)
