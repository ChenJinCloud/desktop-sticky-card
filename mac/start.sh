#!/bin/bash
# Launch the menu bar card. Pass --chat to also open the chat terminal.
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ "${1:-}" = "--chat" ]; then
    "$DIR/python-with-tk.sh" "$DIR/sticky-card.py" &
    exec python3 "$DIR/chat.py"
fi
exec "$DIR/python-with-tk.sh" "$DIR/sticky-card.py"
