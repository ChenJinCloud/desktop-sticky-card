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
