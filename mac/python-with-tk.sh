#!/bin/bash
set -euo pipefail

if [ -n "${PYTHON_WITH_TK:-}" ]; then
    candidates=("$PYTHON_WITH_TK")
else
    candidates=("python3" "/usr/bin/python3")
fi

for candidate in "${candidates[@]}"; do
    if ! command -v "$candidate" >/dev/null 2>&1; then
        continue
    fi
    if "$candidate" -c "import tkinter" >/dev/null 2>&1; then
        exec "$candidate" "$@"
    fi
done

printf '%s\n' \
    "Desktop Sticky Card needs Python with tkinter." \
    "Set PYTHON_WITH_TK to a compatible Python, or install python-tk with Homebrew."
exit 1
