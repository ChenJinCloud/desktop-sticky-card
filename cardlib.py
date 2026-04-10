"""
Shared library for card content operations.
Used by chat.py, card.py, and sticky-card.pyw.
"""

import os
import re
import json
from datetime import datetime

CONTENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "card-content.md")
TAGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "card-tags.json")


def read_lines():
    if not os.path.exists(CONTENT_FILE):
        return []
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        return f.readlines()


def write_lines(lines):
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def get_tasks(lines):
    """Return [(line_idx, is_done, task_text), ...]"""
    tasks = []
    for i, line in enumerate(lines):
        m = re.match(r'^[-*]\s*\[([ x])\]\s*(.*)', line.strip(), re.IGNORECASE)
        if m:
            tasks.append((i, m.group(1).lower() == 'x', m.group(2)))
    return tasks


def find_insert_position(lines):
    """Find where to insert new tasks: after last task, before separator."""
    last_task = -1
    separator = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if re.match(r'^[-*]\s*\[[ x]\]', s, re.IGNORECASE):
            last_task = i
        if re.match(r'^-{3,}$', s):
            separator = i
    if last_task >= 0:
        return last_task + 1
    if separator >= 0:
        return separator
    return len(lines)


def load_tag_names():
    """Return list of valid tag names from card-tags.json."""
    try:
        with open(TAGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        tags = data.get("tags", [])
        return [t if isinstance(t, str) else t["name"] for t in tags]
    except Exception:
        return []


def add_tasks(texts, tag=None):
    """Add one or more tasks with timestamp and optional tag. Returns list of added task names."""
    lines = read_lines()
    pos = find_insert_position(lines)
    now = datetime.now().strftime("%m/%d %H:%M")
    tag_suffix = f" #{tag}" if tag else ""
    for i, text in enumerate(texts):
        lines.insert(pos + i, f"- [ ] {text}{tag_suffix} `{now}`\n")
    write_lines(lines)
    return texts


def toggle_task(num, to_done):
    """Toggle task by 1-based number. Returns (success, task_text)."""
    lines = read_lines()
    tasks = get_tasks(lines)
    if num < 1 or num > len(tasks):
        return False, f"task {num} not found ({len(tasks)} total)"
    line_idx, _, text = tasks[num - 1]
    line = lines[line_idx]
    if to_done:
        now = datetime.now().strftime("%m/%d %H:%M")
        lines[line_idx] = re.sub(r'\[\s?\]', '[x]', line, count=1)
        lines[line_idx] = lines[line_idx].rstrip('\n') + f' done:`{now}`\n'
    else:
        lines[line_idx] = re.sub(r'\[x\]', '[ ]', line, count=1, flags=re.IGNORECASE)
        lines[line_idx] = re.sub(r'\s*done:`\d{2}/\d{2}\s+\d{2}:\d{2}`', '', lines[line_idx])
    write_lines(lines)
    return True, text


def remove_task(num):
    """Remove task by 1-based number. Returns (success, task_text)."""
    lines = read_lines()
    tasks = get_tasks(lines)
    if num < 1 or num > len(tasks):
        return False, f"task {num} not found ({len(tasks)} total)"
    line_idx, _, text = tasks[num - 1]
    del lines[line_idx]
    write_lines(lines)
    return True, text


def clear_done():
    """Remove all completed tasks. Returns count removed."""
    lines = read_lines()
    new_lines = [l for l in lines if not re.match(r'^[-*]\s*\[x\]', l.strip(), re.IGNORECASE)]
    removed = len(lines) - len(new_lines)
    write_lines(new_lines)
    return removed


def set_title(title):
    """Set or replace the first # heading."""
    lines = read_lines()
    for i, line in enumerate(lines):
        if re.match(r'^#\s+', line.strip()):
            lines[i] = f"# {title}\n"
            write_lines(lines)
            return
    lines.insert(0, f"# {title}\n\n")
    write_lines(lines)


def overwrite(text):
    """Replace entire card content."""
    text = text.replace("\\n", "\n")
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")


def split_multi_tasks(text):
    """Split '1.xxx；2.xxx' style input into individual task texts."""
    # Numbered items separated by semicolons
    parts = re.split(r'[;；]\s*(?=\d+[.、，,）)\s])', text)
    if len(parts) > 1:
        tasks = [re.sub(r'^\d+[.、，,）)\s]+\s*', '', p.strip()) for p in parts]
        tasks = [t for t in tasks if t]
        if tasks:
            return tasks

    # Plain semicolon-separated
    parts = re.split(r'[;；]', text)
    if len(parts) > 1:
        tasks = [p.strip() for p in parts if p.strip()]
        if len(tasks) > 1:
            return tasks

    # Inline numbered: 1.xxx 2.xxx
    items = re.findall(r'\d+[.、，,）)\s]+\s*([^0-9]+?)(?=\d+[.、，,）)\s]|$)', text)
    if len(items) > 1:
        return [i.strip().rstrip('；; ') for i in items if i.strip()]

    return [text]
