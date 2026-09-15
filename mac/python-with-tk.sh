#!/bin/bash
set -euo pipefail

if [ -n "${PYTHON_WITH_TK:-}" ]; then
    candidates=("$PYTHON_WITH_TK")
else
    candidates=(
        "python3"
        "/opt/homebrew/opt/python@3.14/bin/python3.14"
        "/opt/homebrew/opt/python@3.13/bin/python3.13"
        "/usr/local/bin/python3"
        "/usr/bin/python3"
    )
fi

for candidate in "${candidates[@]}"; do
    if ! command -v "$candidate" >/dev/null 2>&1; then
        continue
    fi
    # The Tk 8.5 bundled with macOS can create a window whose entire client
    # area is blank on recent macOS versions.  Treat that runtime as
    # incompatible instead of silently launching a broken-looking app.
    if "$candidate" -c \
        'import tkinter as tk; raise SystemExit(0 if tk.TkVersion >= 8.6 else 1)' \
        >/dev/null 2>&1; then
        exec "$candidate" "$@"
    fi
done

printf '%s\n' \
    "Desktop Sticky Card needs Python with Tk 8.6 or newer." \
    "Install it with: brew install python-tk@3.14" \
    "Or set PYTHON_WITH_TK to another compatible Python executable."
exit 1
