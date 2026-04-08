#!/bin/bash
# Launch Sticky Card + Chat Terminal
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$DIR/sticky-card.py" &
python3 "$DIR/chat.py"
