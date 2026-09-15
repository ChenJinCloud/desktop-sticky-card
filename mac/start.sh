#!/bin/bash
# Launch Sticky Card + Chat Terminal
DIR="$(cd "$(dirname "$0")" && pwd)"
"$DIR/python-with-tk.sh" "$DIR/sticky-card.py" &
python3 "$DIR/chat.py"
