"""Reliable local storage for Desktop Sticky Card.

The GUI, CLI, and chat entry points all use this module so that every write is
serialized across processes, snapshotted, and atomically committed.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterable


TASK_RE = re.compile(r"^[-*]\s*\[([ x])\]\s*(.*)", re.IGNORECASE)
OPEN_TASK_RE = re.compile(r"^[-*]\s*\[\s?\]\s*", re.IGNORECASE)
DONE_TASK_RE = re.compile(r"^[-*]\s*\[x\]\s*", re.IGNORECASE)
DONE_TIMESTAMP_RE = re.compile(r"\s*done:`\d{2}/\d{2}\s+\d{2}:\d{2}`")


class ContentConflictError(RuntimeError):
    """Raised when an editor tries to overwrite content changed elsewhere."""


class CardStore:
    """File-backed task store with cross-process locking and atomic writes."""

    def __init__(self, data_dir: str | os.PathLike[str]):
        self.data_dir = Path(data_dir).expanduser().resolve()
        self.content_file = self.data_dir / "card-content.md"
        self.habits_file = self.data_dir / "card-habits.md"
        self.tags_file = self.data_dir / "card-tags.json"
        self.state_file = self.data_dir / ".card-state.json"
        self.history_dir = self.data_dir / "card-history"
        self.lock_file = self.data_dir / ".card-data.lock"

    @contextmanager
    def locked(self):
        """Hold one application-wide lock for a complete read-modify-write."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self.lock_file.open("a+b") as handle:
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)

            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)

                def unlock():
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)

                def unlock():
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

            try:
                yield
            finally:
                handle.seek(0)
                unlock()

    @staticmethod
    def _read_text_unlocked(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""

    @staticmethod
    def _atomic_write_text(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        original_mode = path.stat().st_mode if path.exists() else None
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            if original_mode is not None:
                os.chmod(temporary_path, original_mode)
            os.replace(temporary_path, path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

    def _snapshot_files(self) -> list[tuple[str, Path]]:
        return [
            ("card-content.md", self.content_file),
            ("card-habits.md", self.habits_file),
            ("card-tags.json", self.tags_file),
            (".card-state.json", self.state_file),
        ]

    def _ensure_daily_snapshot_unlocked(self, reason: str) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")
        snapshot_dir = self.history_dir / today
        manifest_path = snapshot_dir / "manifest.json"
        if manifest_path.exists():
            return snapshot_dir

        snapshot_dir.mkdir(parents=True, exist_ok=True)
        copied = []
        for filename, source in self._snapshot_files():
            if source.exists():
                shutil.copy2(source, snapshot_dir / filename)
                copied.append(filename)

        manifest = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "reason": reason,
            "source_dir": str(self.data_dir),
            "files": copied,
        }
        self._atomic_write_text(
            manifest_path,
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        )
        return snapshot_dir

    def ensure_daily_snapshot(self, reason: str = "auto") -> str:
        with self.locked():
            return str(self._ensure_daily_snapshot_unlocked(reason))

    def read_text(self, path: str | os.PathLike[str] | None = None) -> str:
        return self._read_text_unlocked(Path(path) if path else self.content_file)

    def read_lines(self) -> list[str]:
        return self.read_text().splitlines(keepends=True)

    def write_text(
        self,
        path: str | os.PathLike[str],
        text: str,
        *,
        reason: str,
        expected_text: str | None = None,
    ) -> None:
        target = Path(path)
        with self.locked():
            current = self._read_text_unlocked(target)
            if expected_text is not None and current != expected_text:
                raise ContentConflictError(
                    f"{target.name} changed outside the editor; reload before saving"
                )
            self._ensure_daily_snapshot_unlocked(reason)
            self._atomic_write_text(target, text)

    def read_json(self, path: str | os.PathLike[str], default=None):
        target = Path(path)
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {} if default is None else default

    def update_json(
        self, path: str | os.PathLike[str], updates: dict, *, reason: str
    ) -> dict:
        target = Path(path)
        with self.locked():
            try:
                current = json.loads(self._read_text_unlocked(target) or "{}")
            except json.JSONDecodeError:
                current = {}
            if not isinstance(current, dict):
                current = {}
            current.update(updates)
            self._ensure_daily_snapshot_unlocked(reason)
            self._atomic_write_text(
                target, json.dumps(current, ensure_ascii=False, indent=2) + "\n"
            )
            return current

    @staticmethod
    def get_tasks(lines: Iterable[str]):
        """Return ``[(line_idx, is_done, task_text), ...]``."""
        tasks = []
        for index, line in enumerate(lines):
            match = TASK_RE.match(line.strip())
            if match:
                tasks.append((index, match.group(1).lower() == "x", match.group(2)))
        return tasks

    @staticmethod
    def find_insert_position(lines: Iterable[str]) -> int:
        lines = list(lines)
        last_task = -1
        separator = -1
        for index, line in enumerate(lines):
            stripped = line.strip()
            if TASK_RE.match(stripped):
                last_task = index
            if re.match(r"^-{3,}$", stripped):
                separator = index
        if last_task >= 0:
            return last_task + 1
        if separator >= 0:
            return separator
        return len(lines)

    def _commit_lines_unlocked(self, lines: Iterable[str], reason: str) -> None:
        self._ensure_daily_snapshot_unlocked(reason)
        self._atomic_write_text(self.content_file, "".join(lines))

    def write_lines(self, lines: Iterable[str], reason: str = "before-write") -> None:
        with self.locked():
            self._commit_lines_unlocked(lines, reason)

    def add_tasks(self, texts: Iterable[str], tag: str | None = None) -> list[str]:
        texts = [text for text in texts if text.strip()]
        with self.locked():
            lines = self._read_text_unlocked(self.content_file).splitlines(keepends=True)
            position = self.find_insert_position(lines)
            now = datetime.now().strftime("%m/%d %H:%M")
            tag_suffix = f" #{tag}" if tag else ""
            for offset, text in enumerate(texts):
                lines.insert(position + offset, f"- [ ] {text}{tag_suffix} `{now}`\n")
            self._commit_lines_unlocked(lines, "add-task")
        return texts

    def toggle_task(self, number: int, to_done: bool):
        with self.locked():
            lines = self._read_text_unlocked(self.content_file).splitlines(keepends=True)
            tasks = self.get_tasks(lines)
            if number < 1 or number > len(tasks):
                return False, f"task {number} not found ({len(tasks)} total)"
            line_index, is_done, text = tasks[number - 1]
            if is_done == to_done:
                return True, text
            lines[line_index] = self._toggle_line_text(lines[line_index], record_done=True)
            self._commit_lines_unlocked(lines, "toggle-task")
            return True, text

    @staticmethod
    def _toggle_line_text(line: str, *, record_done: bool) -> str:
        if DONE_TASK_RE.match(line.strip()):
            updated = re.sub(r"\[x\]", "[ ]", line, count=1, flags=re.IGNORECASE)
            return DONE_TIMESTAMP_RE.sub("", updated)
        if OPEN_TASK_RE.match(line.strip()):
            updated = re.sub(r"\[\s?\]", "[x]", line, count=1)
            if record_done:
                now = datetime.now().strftime("%m/%d %H:%M")
                updated = updated.rstrip("\n") + f" done:`{now}`\n"
            return updated
        return line

    def toggle_line(
        self, path: str | os.PathLike[str], line_index: int, *, record_done: bool
    ) -> bool:
        target = Path(path)
        with self.locked():
            lines = self._read_text_unlocked(target).splitlines(keepends=True)
            if line_index < 0 or line_index >= len(lines):
                return False
            updated = self._toggle_line_text(lines[line_index], record_done=record_done)
            if updated == lines[line_index]:
                return False
            lines[line_index] = updated
            self._ensure_daily_snapshot_unlocked("task-toggle")
            self._atomic_write_text(target, "".join(lines))
            return True

    def reorder_line(
        self, path: str | os.PathLike[str], source_index: int, destination_index: int
    ) -> bool:
        target = Path(path)
        with self.locked():
            lines = self._read_text_unlocked(target).splitlines(keepends=True)
            if source_index < 0 or source_index >= len(lines):
                return False
            destination_index = max(0, min(destination_index, len(lines)))
            line = lines.pop(source_index)
            if source_index < destination_index:
                destination_index -= 1
            lines.insert(destination_index, line)
            self._ensure_daily_snapshot_unlocked("task-reorder")
            self._atomic_write_text(target, "".join(lines))
            return True

    def remove_task(self, number: int):
        with self.locked():
            lines = self._read_text_unlocked(self.content_file).splitlines(keepends=True)
            tasks = self.get_tasks(lines)
            if number < 1 or number > len(tasks):
                return False, f"task {number} not found ({len(tasks)} total)"
            line_index, _, text = tasks[number - 1]
            del lines[line_index]
            self._commit_lines_unlocked(lines, "remove-task")
            return True, text

    def clear_done(self) -> int:
        with self.locked():
            lines = self._read_text_unlocked(self.content_file).splitlines(keepends=True)
            new_lines = [line for line in lines if not DONE_TASK_RE.match(line.strip())]
            removed = len(lines) - len(new_lines)
            if removed:
                self._commit_lines_unlocked(new_lines, "clear-done")
            return removed

    def set_title(self, title: str) -> None:
        with self.locked():
            lines = self._read_text_unlocked(self.content_file).splitlines(keepends=True)
            for index, line in enumerate(lines):
                if re.match(r"^#\s+", line.strip()):
                    lines[index] = f"# {title}\n"
                    break
            else:
                lines.insert(0, f"# {title}\n\n")
            self._commit_lines_unlocked(lines, "set-title")

    def overwrite(self, text: str) -> None:
        text = text.replace("\\n", "\n")
        if not text.endswith("\n"):
            text += "\n"
        self.write_text(self.content_file, text, reason="overwrite")

    def load_tag_names(self) -> list[str]:
        data = self.read_json(self.tags_file, default={})
        tags = data.get("tags", []) if isinstance(data, dict) else []
        names = []
        for tag in tags:
            if isinstance(tag, str):
                names.append(tag)
            elif isinstance(tag, dict) and isinstance(tag.get("name"), str):
                names.append(tag["name"])
        return names

    def reset_habits_if_needed(self, today: str) -> bool:
        """Reset checked habits once per local date and persist that date."""
        with self.locked():
            try:
                state = json.loads(self._read_text_unlocked(self.state_file) or "{}")
            except json.JSONDecodeError:
                state = {}
            if state.get("habits_last_reset") == today:
                return False

            habits = self._read_text_unlocked(self.habits_file)
            reset = re.sub(r"\[x\]", "[ ]", habits, flags=re.IGNORECASE)
            self._ensure_daily_snapshot_unlocked("habits-reset")
            if reset != habits:
                self._atomic_write_text(self.habits_file, reset)
            state["habits_last_reset"] = today
            self._atomic_write_text(
                self.state_file, json.dumps(state, ensure_ascii=False, indent=2) + "\n"
            )
            return True


NUMBERED_MARKER_RE = re.compile(
    r"(?<![^\s;；])\d+[.、，,）)](?=\s*[^\d\s])\s*"
)


def split_multi_tasks(text: str) -> list[str]:
    """Split numbered or semicolon-delimited input without eating numeric text."""
    matches = list(NUMBERED_MARKER_RE.finditer(text))
    if len(matches) >= 2:
        tasks = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            item = text[match.end() : end].strip().strip(";；")
            if item:
                tasks.append(item)
        if tasks:
            return tasks

    parts = [part.strip() for part in re.split(r"[;；]", text) if part.strip()]
    if len(parts) > 1:
        tasks = [re.sub(r"^\d+[.、，,）)]\s*", "", part) for part in parts]
        return [task for task in tasks if task]

    return [text]
