"""
Desktop Sticky Card — macOS Edition
Medium style - file-driven - auto-refresh - resizable - editable
"""

import tkinter as tk
import os
import sys
import re
import json
import fcntl

# ── Config ────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONTENT_FILE = os.path.join(SCRIPT_DIR, "card-content.md")
STATE_FILE = os.path.join(SCRIPT_DIR, ".card-state.json")
POLL_INTERVAL_MS = 500
DEFAULT_WIDTH = 380
MIN_WIDTH = 260
MIN_HEIGHT = 140
RESIZE_EDGE = 8  # slightly larger for macOS trackpad

SERIF = "Georgia"
SANS = "Helvetica Neue"

# Font size levels: (body, h1, h2, h3, small, topbar)
FONT_SIZES = {
    "XS": {"body": 10, "h1": 15, "h2": 12, "h3": 10, "small": 8, "top": 8},
    "S":  {"body": 11, "h1": 17, "h2": 13, "h3": 11, "small": 8, "top": 8},
    "M":  {"body": 12, "h1": 19, "h2": 15, "h3": 12, "small": 9, "top": 9},
    "L":  {"body": 14, "h1": 22, "h2": 17, "h3": 14, "small": 10, "top": 10},
    "XL": {"body": 16, "h1": 25, "h2": 19, "h3": 16, "small": 11, "top": 11},
}
FONT_SIZE_NAMES = list(FONT_SIZES.keys())

# ── Themes ────────────────────────────────────────────
THEMES = {
    "Light": {
        "bg": "#FFFFFF", "fg": "#292929", "secondary": "#757575",
        "accent": "#1A8917", "title": "#292929", "done": "#B8B8B8",
        "hr": "#E6E6E6", "italic": "#757575", "border": "#E6E6E6",
        "topbar": "#FAFAFA", "pin_active": "#1A8917", "pin_inactive": "#B8B8B8",
        "edit_bg": "#FAFAFA",
    },
    "Dark": {
        "bg": "#1E1E2E", "fg": "#CDD6F4", "secondary": "#9399B2",
        "accent": "#89B4FA", "title": "#CDD6F4", "done": "#585B70",
        "hr": "#45475A", "italic": "#9399B2", "border": "#45475A",
        "topbar": "#181825", "pin_active": "#89B4FA", "pin_inactive": "#585B70",
        "edit_bg": "#181825",
    },
    "Macaron Rose": {
        "bg": "#FFF0F3", "fg": "#5C3D4E", "secondary": "#B08A9A",
        "accent": "#E8728A", "title": "#5C3D4E", "done": "#D4B8C4",
        "hr": "#F5D5DE", "italic": "#B08A9A", "border": "#F5D5DE",
        "topbar": "#FFE4EB", "pin_active": "#E8728A", "pin_inactive": "#D4B8C4",
        "edit_bg": "#FFE4EB",
    },
    "Macaron Mint": {
        "bg": "#F0FFF4", "fg": "#3D5C4E", "secondary": "#8AB0A0",
        "accent": "#5BAD8A", "title": "#3D5C4E", "done": "#B8D4C8",
        "hr": "#D5F5E3", "italic": "#8AB0A0", "border": "#D5F5E3",
        "topbar": "#E4FFEE", "pin_active": "#5BAD8A", "pin_inactive": "#B8D4C8",
        "edit_bg": "#E4FFEE",
    },
    "Macaron Lavender": {
        "bg": "#F5F0FF", "fg": "#4A3D5C", "secondary": "#9A8AB0",
        "accent": "#8B72E8", "title": "#4A3D5C", "done": "#C4B8D4",
        "hr": "#E0D5F5", "italic": "#9A8AB0", "border": "#E0D5F5",
        "topbar": "#EBE4FF", "pin_active": "#8B72E8", "pin_inactive": "#C4B8D4",
        "edit_bg": "#EBE4FF",
    },
    "Morandi Green": {
        "bg": "#E8E4D9", "fg": "#5B5E4B", "secondary": "#8B8E7A",
        "accent": "#7D8B6A", "title": "#5B5E4B", "done": "#B5B8A6",
        "hr": "#D1CDBE", "italic": "#8B8E7A", "border": "#D1CDBE",
        "topbar": "#DFDBCE", "pin_active": "#7D8B6A", "pin_inactive": "#B5B8A6",
        "edit_bg": "#DFDBCE",
    },
    "Morandi Blue": {
        "bg": "#E0E4E8", "fg": "#4B5560", "secondary": "#7A8694",
        "accent": "#6A7F8B", "title": "#4B5560", "done": "#A6B0B8",
        "hr": "#CDD3D9", "italic": "#7A8694", "border": "#CDD3D9",
        "topbar": "#D6DCE2", "pin_active": "#6A7F8B", "pin_inactive": "#A6B0B8",
        "edit_bg": "#D6DCE2",
    },
    "Morandi Rose": {
        "bg": "#EAE0E0", "fg": "#5E4B4F", "secondary": "#94787E",
        "accent": "#8B6A72", "title": "#5E4B4F", "done": "#B8A2A8",
        "hr": "#D9CCCE", "italic": "#94787E", "border": "#D9CCCE",
        "topbar": "#E2D4D6", "pin_active": "#8B6A72", "pin_inactive": "#B8A2A8",
        "edit_bg": "#E2D4D6",
    },
}
THEME_NAMES = list(THEMES.keys())


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def ensure_single_instance():
    """Prevent multiple card windows. Uses fcntl file lock on macOS."""
    lock_path = os.path.join(SCRIPT_DIR, ".card.lock")
    try:
        lock_file = open(lock_path, "w")
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Keep file handle alive for process lifetime
        ensure_single_instance._lock = lock_file
    except (OSError, IOError):
        sys.exit(0)


class StickyCard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sticky Card")
        self.root.attributes("-alpha", 0.97)
        self.root.attributes("-topmost", True)

        # macOS: use overrideredirect but handle focus carefully
        self.root.overrideredirect(True)

        self.is_pinned = True
        self.is_editing = False
        self.show_time = True
        self.show_done = True
        self.theme_name = "Light"
        self.font_size = "M"
        self.last_mtime = 0
        self.drag_data = {"x": 0, "y": 0}
        self.resize_data = {"active": False, "edge": None}
        self.card_width = DEFAULT_WIDTH

        # Restore state
        state = load_state()
        sx = self.root.winfo_screenwidth()
        x = state.get("x", sx - DEFAULT_WIDTH - 50)
        y = state.get("y", 50)
        self.card_width = state.get("width", DEFAULT_WIDTH)
        self.show_time = state.get("show_time", True)
        self.show_done = state.get("show_done", True)
        self.theme_name = state.get("theme", "Light")
        if self.theme_name not in THEMES:
            self.theme_name = "Light"
        self.font_size = state.get("font_size", "M")
        if self.font_size not in FONT_SIZES:
            self.font_size = "M"
        self.root.configure(bg=self.t("border"))
        self.root.geometry(f"{self.card_width}x{MIN_HEIGHT}+{x}+{y}")

        self._build_ui()
        self._load_content()
        self._poll_file()
        self._auto_save_state()
        # macOS focus workaround: brief withdraw/deiconify cycle
        self.root.after(100, self._fix_focus_mac)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def t(self, key):
        """Get color from current theme."""
        return THEMES[self.theme_name][key]

    def fs(self, key):
        """Get font size from current level."""
        return FONT_SIZES[self.font_size][key]

    def _fix_focus_mac(self):
        """macOS focus fix: withdraw and re-show to ensure window is interactive."""
        self.root.withdraw()
        self.root.after(50, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _save_geometry(self):
        geo = self.root.geometry()
        m = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geo)
        if m:
            save_state({
                "width": int(m.group(1)),
                "x": int(m.group(3)),
                "y": int(m.group(4)),
                "show_time": self.show_time,
                "show_done": self.show_done,
                "theme": self.theme_name,
                "font_size": self.font_size
            })

    def _on_close(self):
        self._save_geometry()
        self.root.destroy()

    # ── UI ────────────────────────────────────────────

    def _build_ui(self):
        self.outer_border = tk.Frame(self.root, bg=self.t("border"), padx=1, pady=1)
        self.outer_border.pack(fill="both", expand=True)

        self.card = tk.Frame(self.outer_border, bg=self.t("bg"))
        self.card.pack(fill="both", expand=True)

        # ── Topbar ──
        topbar = tk.Frame(self.card, bg=self.t("topbar"))
        topbar.pack(fill="x")

        topbar_inner = tk.Frame(topbar, bg=self.t("topbar"))
        topbar_inner.pack(fill="x", padx=14, pady=(8, 7))

        self.pin_btn = tk.Label(
            topbar_inner, text="\u25cf", font=(SANS, 10),
            bg=self.t("topbar"), fg=self.t("pin_active") if self.is_pinned else self.t("pin_inactive"),
            cursor="hand2"
        )
        self.pin_btn.pack(side="left")
        self.pin_btn.bind("<Button-1>", self._toggle_pin)

        self.pin_label = tk.Label(
            topbar_inner, text=" Pinned" if self.is_pinned else " Unpinned",
            font=(SANS, 9), bg=self.t("topbar"), fg=self.t("secondary")
        )
        self.pin_label.pack(side="left")
        self.pin_label.bind("<Button-1>", self._toggle_pin)

        close_btn = tk.Label(
            topbar_inner, text="\u2715", font=(SANS, 11),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2"
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self._on_close())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg=self.t("fg")))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg=self.t("secondary")))

        # Edit button
        self.edit_btn = tk.Label(
            topbar_inner, text="Edit", font=(SANS, 9),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2"
        )
        self.edit_btn.pack(side="right", padx=(0, 10))
        self.edit_btn.bind("<Button-1>", self._toggle_edit)
        self.edit_btn.bind("<Enter>", lambda e: self.edit_btn.configure(fg=self.t("fg")))
        self.edit_btn.bind("<Leave>", lambda e: self.edit_btn.configure(
            fg=self.t("accent") if self.is_editing else self.t("secondary")))

        # Time toggle
        self.time_btn = tk.Label(
            topbar_inner, text="T", font=(SANS, 9), bg=self.t("topbar"),
            fg=self.t("accent") if self.show_time else self.t("pin_inactive"),
            cursor="hand2"
        )
        self.time_btn.pack(side="right", padx=(0, 6))
        self.time_btn.bind("<Button-1>", self._toggle_time)
        self.time_btn.bind("<Enter>", lambda e: self.time_btn.configure(fg=self.t("fg")))
        self.time_btn.bind("<Leave>", lambda e: self.time_btn.configure(
            fg=self.t("accent") if self.show_time else self.t("pin_inactive")))

        # Fold toggle
        self.fold_btn = tk.Label(
            topbar_inner, text="All" if self.show_done else "Todo",
            font=(SANS, 9), bg=self.t("topbar"),
            fg=self.t("accent") if not self.show_done else self.t("secondary"),
            cursor="hand2"
        )
        self.fold_btn.pack(side="right", padx=(0, 6))
        self.fold_btn.bind("<Button-1>", self._toggle_fold)
        self.fold_btn.bind("<Enter>", lambda e: self.fold_btn.configure(fg=self.t("fg")))
        self.fold_btn.bind("<Leave>", lambda e: self.fold_btn.configure(
            fg=self.t("accent") if not self.show_done else self.t("secondary")))

        # Theme toggle
        self.theme_btn = tk.Label(
            topbar_inner, text=self.theme_name, font=(SANS, 9),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2"
        )
        self.theme_btn.pack(side="right", padx=(0, 6))
        self.theme_btn.bind("<Button-1>", self._next_theme)
        self.theme_btn.bind("<Enter>", lambda e: self.theme_btn.configure(fg=self.t("fg")))
        self.theme_btn.bind("<Leave>", lambda e: self.theme_btn.configure(fg=self.t("secondary")))

        # Font size toggle
        self.size_btn = tk.Label(
            topbar_inner, text=self.font_size, font=(SANS, 9),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2"
        )
        self.size_btn.pack(side="right", padx=(0, 6))
        self.size_btn.bind("<Button-1>", self._next_font_size)
        self.size_btn.bind("<Enter>", lambda e: self.size_btn.configure(fg=self.t("fg")))
        self.size_btn.bind("<Leave>", lambda e: self.size_btn.configure(fg=self.t("secondary")))

        # Drag bindings
        for w in (topbar, topbar_inner, self.pin_label):
            w.configure(cursor="fleur")
            w.bind("<Button-1>", self._drag_start)
            w.bind("<B1-Motion>", self._drag_move)
            w.bind("<ButtonRelease-1>", self._drag_end)

        tk.Frame(self.card, bg=self.t("hr"), height=1).pack(fill="x")

        # ── Content area ──
        self.content_frame = tk.Frame(self.card, bg=self.t("bg"))
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(12, 16))

        # ── Text editor (hidden initially) ──
        self.editor_frame = tk.Frame(self.card, bg=self.t("bg"))
        self.editor = tk.Text(
            self.editor_frame, font=(SERIF, self.fs("body")), bg=self.t("edit_bg"), fg=self.t("fg"),
            wrap="word", relief="flat", borderwidth=0,
            insertbackground=self.t("fg"), selectbackground=self.t("hr"),
            padx=12, pady=8, undo=True
        )
        self.editor.pack(fill="both", expand=True)

        ebar = tk.Frame(self.editor_frame, bg=self.t("topbar"))
        ebar.pack(fill="x")
        save_btn = tk.Label(
            ebar, text="Save", font=(SANS, 10, "bold"),
            bg=self.t("topbar"), fg=self.t("accent"), cursor="hand2", padx=10, pady=4
        )
        save_btn.pack(side="right", padx=8, pady=4)
        save_btn.bind("<Button-1>", lambda e: self._save_edit())
        cancel_btn = tk.Label(
            ebar, text="Cancel", font=(SANS, 10),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2", padx=10, pady=4
        )
        cancel_btn.pack(side="right", pady=4)
        cancel_btn.bind("<Button-1>", lambda e: self._cancel_edit())

        # macOS: Cmd+S to save, Escape to cancel
        self.editor.bind("<Command-s>", lambda e: self._save_edit())
        self.editor.bind("<Escape>", lambda e: self._cancel_edit())

        # ── Resize edges ──
        self.root.bind("<Motion>", self._resize_cursor)
        self.root.bind("<Button-1>", self._resize_start, add="+")
        self.root.bind("<B1-Motion>", self._resize_move, add="+")
        self.root.bind("<ButtonRelease-1>", self._resize_end, add="+")

    # ── Edit mode ─────────────────────────────────────

    def _toggle_edit(self, event=None):
        if self.is_editing:
            self._save_edit()
        else:
            self._enter_edit()
        return "break"

    def _enter_edit(self):
        self.is_editing = True
        self.edit_btn.configure(text="Editing", fg=self.t("accent"))
        self.content_frame.pack_forget()
        self.editor_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        try:
            with open(CONTENT_FILE, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            text = ""
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        self.editor.focus_set()

    def _save_edit(self):
        text = self.editor.get("1.0", "end-1c")
        with open(CONTENT_FILE, "w", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")
        self.last_mtime = 0  # force refresh
        self._exit_edit()

    def _cancel_edit(self):
        self._exit_edit()

    def _exit_edit(self):
        self.is_editing = False
        self.edit_btn.configure(text="Edit", fg=self.t("secondary"))
        self.editor_frame.pack_forget()
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(12, 16))
        self._load_content()

    # ── Resize ────────────────────────────────────────

    def _get_resize_edge(self, event):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x, y = event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y()
        edges = []
        if x >= w - RESIZE_EDGE:
            edges.append("e")
        elif x <= RESIZE_EDGE:
            edges.append("w")
        if y >= h - RESIZE_EDGE:
            edges.append("s")
        return "".join(edges) if edges else None

    def _resize_cursor(self, event):
        if self.resize_data["active"]:
            return
        edge = self._get_resize_edge(event)
        # macOS tkinter cursor names
        cursors = {
            "e": "sb_h_double_arrow", "w": "sb_h_double_arrow",
            "s": "sb_v_double_arrow",
            "se": "bottom_right_corner", "sw": "bottom_left_corner",
        }
        if edge and edge in cursors:
            self.root.configure(cursor=cursors[edge])
        else:
            self.root.configure(cursor="")

    def _resize_start(self, event):
        edge = self._get_resize_edge(event)
        if edge:
            self.resize_data = {
                "active": True, "edge": edge,
                "x": event.x_root, "y": event.y_root,
                "w": self.root.winfo_width(), "h": self.root.winfo_height(),
                "rx": self.root.winfo_x(), "ry": self.root.winfo_y()
            }

    def _resize_move(self, event):
        if not self.resize_data["active"]:
            return
        d = self.resize_data
        dx = event.x_root - d["x"]
        dy = event.y_root - d["y"]
        edge = d["edge"]

        new_w, new_x = d["w"], d["rx"]
        new_h = d["h"]

        if "e" in edge:
            new_w = max(MIN_WIDTH, d["w"] + dx)
        if "w" in edge:
            new_w = max(MIN_WIDTH, d["w"] - dx)
            new_x = d["rx"] + d["w"] - new_w
        if "s" in edge:
            new_h = max(MIN_HEIGHT, d["h"] + dy)

        self.card_width = new_w
        self.root.geometry(f"{new_w}x{new_h}+{new_x}+{d['ry']}")

    def _resize_end(self, event):
        if self.resize_data["active"]:
            self.resize_data["active"] = False
            self._save_geometry()
            if not self.is_editing:
                self.last_mtime = 0
                self._load_content()

    # ── Theme ─────────────────────────────────────────

    def _next_theme(self, event=None):
        idx = THEME_NAMES.index(self.theme_name)
        self.theme_name = THEME_NAMES[(idx + 1) % len(THEME_NAMES)]
        self._apply_theme()
        return "break"

    def _next_font_size(self, event=None):
        idx = FONT_SIZE_NAMES.index(self.font_size)
        self.font_size = FONT_SIZE_NAMES[(idx + 1) % len(FONT_SIZE_NAMES)]
        self._apply_theme()
        return "break"

    def _apply_theme(self):
        """Rebuild entire UI with new theme/font."""
        self.root.configure(bg=self.t("border"))
        self.outer_border.destroy()
        self._build_ui()
        self._save_geometry()
        self.last_mtime = 0
        self._load_content()

    # ── Task toggle ───────────────────────────────────

    def _toggle_task(self, line_idx):
        if self.is_editing:
            return
        try:
            from datetime import datetime
            lines = list(open(CONTENT_FILE, "r", encoding="utf-8"))
            if line_idx < 0 or line_idx >= len(lines):
                return
            line = lines[line_idx]
            if re.search(r'\[x\]', line, re.IGNORECASE):
                lines[line_idx] = re.sub(r'\[x\]', '[ ]', line, count=1, flags=re.IGNORECASE)
                lines[line_idx] = re.sub(r'\s*done:`\d{2}/\d{2}\s+\d{2}:\d{2}`', '', lines[line_idx])
            elif re.search(r'\[\s?\]', line):
                now = datetime.now().strftime("%m/%d %H:%M")
                lines[line_idx] = re.sub(r'\[\s?\]', '[x]', line, count=1)
                lines[line_idx] = lines[line_idx].rstrip('\n') + f' done:`{now}`\n'
            with open(CONTENT_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            pass

    def _make_clickable(self, widget, line_idx):
        widget.bind("<Button-1>", lambda e, idx=line_idx: self._toggle_task(idx))
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            child.bind("<Button-1>", lambda e, idx=line_idx: self._toggle_task(idx))
            child.configure(cursor="hand2")

    # ── Render ────────────────────────────────────────

    @staticmethod
    def _split_timestamp(text):
        """Parse task text, created time, and done time."""
        done_ts = None
        dm = re.search(r'\s*done:`(\d{2}/\d{2}\s+\d{2}:\d{2})`', text)
        if dm:
            done_ts = dm.group(1)
            text = text[:dm.start()] + text[dm.end():]
        create_ts = None
        cm = re.match(r'^(.*?)\s*`(\d{2}/\d{2}\s+\d{2}:\d{2})`\s*$', text)
        if cm:
            text = cm.group(1)
            create_ts = cm.group(2)
        return text, create_ts, done_ts

    def _toggle_time(self, event=None):
        self.show_time = not self.show_time
        self.time_btn.configure(fg=self.t("accent") if self.show_time else self.t("pin_inactive"))
        self._save_geometry()
        self.last_mtime = 0
        self._load_content()
        return "break"

    def _toggle_fold(self, event=None):
        self.show_done = not self.show_done
        self.fold_btn.configure(
            text="All" if self.show_done else "Todo",
            fg=self.t("accent") if not self.show_done else self.t("secondary")
        )
        self._save_geometry()
        self.last_mtime = 0
        self._load_content()
        return "break"

    def _render_content(self, text):
        for w in self.content_frame.winfo_children():
            w.destroy()

        bg = self.t("bg")
        raw_lines = text.split("\n")
        wrap_w = self.card_width - 60

        for line_idx, line in enumerate(raw_lines):
            stripped = line.strip()

            if not stripped:
                tk.Frame(self.content_frame, bg=bg, height=6).pack(fill="x")
                continue

            if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
                tk.Frame(self.content_frame, bg=bg, height=8).pack(fill="x")
                tk.Frame(self.content_frame, bg=self.t("hr"), height=1).pack(fill="x", padx=4)
                tk.Frame(self.content_frame, bg=bg, height=8).pack(fill="x")
                continue

            m = re.match(r'^#\s+(.*)', stripped)
            if m:
                tk.Label(
                    self.content_frame, text=m.group(1),
                    font=(SERIF, self.fs("h1"), "bold"),
                    bg=bg, fg=self.t("title"), anchor="w",
                    wraplength=wrap_w, justify="left"
                ).pack(fill="x", pady=(4, 6))
                continue

            m = re.match(r'^##\s+(.*)', stripped)
            if m:
                tk.Label(
                    self.content_frame, text=m.group(1),
                    font=(SERIF, self.fs("h2"), "bold"),
                    bg=bg, fg=self.t("title"), anchor="w",
                    wraplength=wrap_w, justify="left"
                ).pack(fill="x", pady=(6, 4))
                continue

            m = re.match(r'^###\s+(.*)', stripped)
            if m:
                tk.Label(
                    self.content_frame, text=m.group(1),
                    font=(SANS, self.fs("h3"), "bold"),
                    bg=bg, fg=self.t("fg"), anchor="w",
                    wraplength=wrap_w, justify="left"
                ).pack(fill="x", pady=(4, 2))
                continue

            # Done task
            m = re.match(r'^[-*]\s*\[x\]\s*(.*)', stripped, re.IGNORECASE)
            if m:
                if not self.show_done:
                    continue
                task_text, create_ts, done_ts = self._split_timestamp(m.group(1))
                f = tk.Frame(self.content_frame, bg=bg)
                f.pack(fill="x", pady=2)
                tk.Label(f, text="  \u2611 ", font=(SANS, self.fs("body") - 1), bg=bg, fg=self.t("done")).pack(side="left", anchor="n")
                tk.Label(
                    f, text=task_text, font=(SERIF, self.fs("body"), "overstrike"),
                    bg=bg, fg=self.t("done"), anchor="w",
                    wraplength=wrap_w - 70, justify="left"
                ).pack(side="left", fill="x")
                if self.show_time:
                    ts_parts = []
                    if create_ts:
                        ts_parts.append(create_ts)
                    if done_ts:
                        ts_parts.append("\u2713 " + done_ts)
                    if ts_parts:
                        tk.Label(f, text=" | ".join(ts_parts), font=(SANS, self.fs("small")),
                                 bg=bg, fg=self.t("done")).pack(side="right", padx=(4, 0))
                self._make_clickable(f, line_idx)
                continue

            # Pending task
            m = re.match(r'^[-*]\s*\[\s?\]\s*(.*)', stripped)
            if m:
                task_text, create_ts, _ = self._split_timestamp(m.group(1))
                f = tk.Frame(self.content_frame, bg=bg)
                f.pack(fill="x", pady=2)
                tk.Label(f, text="  \u2610 ", font=(SANS, self.fs("body") - 1), bg=bg, fg=self.t("accent")).pack(side="left", anchor="n")
                tk.Label(
                    f, text=task_text, font=(SERIF, self.fs("body")),
                    bg=bg, fg=self.t("fg"), anchor="w",
                    wraplength=wrap_w - 70, justify="left"
                ).pack(side="left", fill="x")
                if create_ts and self.show_time:
                    tk.Label(f, text=create_ts, font=(SANS, self.fs("small")), bg=bg, fg=self.t("secondary")
                    ).pack(side="right", padx=(4, 0))
                self._make_clickable(f, line_idx)
                continue

            # List item
            m = re.match(r'^[-*]\s+(.*)', stripped)
            if m:
                f = tk.Frame(self.content_frame, bg=bg)
                f.pack(fill="x", pady=2)
                tk.Label(f, text="  \u00b7  ", font=(SERIF, self.fs("body")), bg=bg, fg=self.t("secondary")).pack(side="left", anchor="n")
                tk.Label(
                    f, text=m.group(1), font=(SERIF, self.fs("body")),
                    bg=bg, fg=self.t("fg"), anchor="w",
                    wraplength=wrap_w - 40, justify="left"
                ).pack(side="left", fill="x")
                continue

            # Italic
            if re.match(r'^\*[^*]+\*$', stripped):
                tk.Label(
                    self.content_frame, text=stripped.strip("*"),
                    font=(SERIF, self.fs("body") - 1, "italic"),
                    bg=bg, fg=self.t("italic"), anchor="w",
                    wraplength=wrap_w, justify="left"
                ).pack(fill="x", pady=1)
                continue

            # Plain text
            tk.Label(
                self.content_frame, text=stripped,
                font=(SERIF, self.fs("body")),
                bg=bg, fg=self.t("fg"), anchor="w",
                wraplength=wrap_w, justify="left"
            ).pack(fill="x", pady=2)

        # Auto height
        self.root.update_idletasks()
        need_h = self.card.winfo_reqheight() + 4
        h = max(MIN_HEIGHT, need_h)
        geo = self.root.geometry()
        parts = geo.split("+")
        self.root.geometry(f"{self.card_width}x{h}+{parts[1]}+{parts[2]}")

    # ── File polling ──────────────────────────────────

    def _load_content(self):
        if self.is_editing:
            return
        try:
            mtime = os.path.getmtime(CONTENT_FILE)
            if mtime != self.last_mtime:
                self.last_mtime = mtime
                with open(CONTENT_FILE, "r", encoding="utf-8") as f:
                    text = f.read()
                self._render_content(text)
        except FileNotFoundError:
            self._render_content("card-content.md not found")

    def _poll_file(self):
        self._load_content()
        self.root.after(POLL_INTERVAL_MS, self._poll_file)

    def _auto_save_state(self):
        """Periodically save state as a safety net."""
        self._save_geometry()
        self.root.after(5000, self._auto_save_state)

    # ── Pin / Drag ────────────────────────────────────

    def _toggle_pin(self, event=None):
        self.is_pinned = not self.is_pinned
        self.root.attributes("-topmost", self.is_pinned)
        self.pin_btn.configure(fg=self.t("pin_active") if self.is_pinned else self.t("pin_inactive"))
        self.pin_label.configure(text=" Pinned" if self.is_pinned else " Unpinned")
        return "break"

    def _drag_start(self, event):
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()

    def _drag_move(self, event):
        if self.resize_data["active"]:
            return
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _drag_end(self, event):
        self._save_geometry()


if __name__ == "__main__":
    ensure_single_instance()
    StickyCard()
