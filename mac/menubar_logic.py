def applescript_string(text):
    """Build an AppleScript string expression that keeps line breaks.

    osascript strings cannot span lines, so every line becomes its own literal
    joined with the ``return`` constant. Quotes and backslashes are escaped.
    """
    parts = [line.replace("\\", "\\\\").replace('"', '\\"') for line in text.split("\n")]
    return " & return & ".join(f'"{part}"' for part in parts)


def is_behind_notch(mid_x, gap_min, gap_max):
    """True when the status item centre falls inside the notch gap.

    On notched MacBooks the menu bar is split into a left and a right usable
    area. macOS clips status items that do not fit, so an item pushed into the
    gap is invisible and unclickable instead of failing loudly.
    """
    if mid_x is None or gap_min is None or gap_max is None:
        return False
    return gap_min < mid_x < gap_max


class HoverState:
    def __init__(self, grace=0.4):
        self.grace = grace
        self.visible = False
        self.left_at = None

    def update(self, now, over_icon, over_card, pinned=False):
        if pinned:
            self.left_at = None
            if not self.visible:
                self.visible = True
                return "show"
            return None
        if over_icon or (self.visible and over_card):
            self.left_at = None
            if over_icon and not self.visible:
                self.visible = True
                return "show"
        elif self.visible:
            if self.left_at is None:
                self.left_at = now
            elif now - self.left_at >= self.grace:
                self.visible = False
                self.left_at = None
                return "hide"
        return None
