"""
Desktop Sticky Card
Medium style - file-driven - auto-refresh - resizable - editable
"""

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import tkinter as tk
import os
import sys
import re
import json
import queue
import threading
from ctypes import wintypes

import cardlib

# ── Config ────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONTENT_FILE = os.path.join(SCRIPT_DIR, "card-content.md")
STATE_FILE = os.path.join(SCRIPT_DIR, ".card-state.json")
TAGS_FILE = os.path.join(SCRIPT_DIR, "card-tags.json")
TAGS_EXAMPLE_FILE = os.path.join(SCRIPT_DIR, "card-tags.example.json")
HABITS_FILE = os.path.join(SCRIPT_DIR, "card-habits.md")
HISTORY_DIR = cardlib.HISTORY_DIR
POLL_INTERVAL_MS = 500
DEFAULT_WIDTH = 380
MIN_WIDTH = 260
MIN_HEIGHT = 140
RESIZE_EDGE = 6

SERIF = "Georgia"
SANS = "Segoe UI"

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

GLOBAL_HOTKEYS = {
    1001: {
        "label": "Ctrl+Alt+Space",
        "action": "toggle_visibility",
        "modifiers": MOD_CONTROL | MOD_ALT,
        "vk": 0x20,
    },
    1002: {
        "label": "Ctrl+Alt+N",
        "action": "quick_add",
        "modifiers": MOD_CONTROL | MOD_ALT,
        "vk": ord("N"),
    },
}

SHORTCUT_TIPS = [
    ("Ctrl+Alt+Space", "Show/Hide"),
    ("Ctrl+Alt+N", "Quick Add"),
    ("Ctrl+E", "Edit"),
    ("Ctrl+S", "Save"),
    ("Enter", "Save Quick Add"),
    ("Esc", "Cancel"),
    ("Ctrl+D", "All/Todo"),
    ("Ctrl+H", "Habits"),
    ("Ctrl+T", "Time"),
    ("Ctrl+Shift+T", "Tags"),
    ("Ctrl+P", "Pinned"),
    ("Ctrl+Shift+C", "Theme"),
    ("Ctrl+Shift+S", "Size"),
    ("Ctrl+Q", "Close"),
]

# Font size levels: (body, h1, h2, h3, small, topbar)
FONT_SIZES = {
    "XS": {"body": 9, "h1": 14, "h2": 11, "h3": 9, "small": 7, "top": 7},
    "S":  {"body": 10, "h1": 16, "h2": 12, "h3": 10, "small": 7, "top": 7},
    "M":  {"body": 11, "h1": 18, "h2": 14, "h3": 11, "small": 8, "top": 8},
    "L":  {"body": 13, "h1": 21, "h2": 16, "h3": 13, "small": 9, "top": 9},
    "XL": {"body": 15, "h1": 24, "h2": 18, "h3": 15, "small": 10, "top": 10},
}
FONT_SIZE_NAMES = list(FONT_SIZES.keys())

# ── Themes ────────────────────────────────────────────
# Keys: bg, fg, secondary, accent, title, done, hr, italic, border, topbar, pin_active, pin_inactive, edit_bg
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
        cardlib.ensure_daily_snapshot("state-save")
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def load_tags():
    """Load tag names from card-tags.json, fallback to example."""
    for path in (TAGS_FILE, TAGS_EXAMPLE_FILE):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            tags = data.get("tags", [])
            # Support both ["name", ...] and [{"name": ...}, ...] formats
            return [t if isinstance(t, str) else t["name"] for t in tags]
        except Exception:
            continue
    return []


def parse_tags(text):
    """Extract #TagName tokens from task text. Returns (clean_text, [tag_names])."""
    tags = re.findall(r'#([^\s#`]+)', text)
    clean = re.sub(r'\s*#[^\s#`]+', '', text).strip()
    return clean, tags


HWND_FILE = os.path.join(SCRIPT_DIR, ".card.hwnd")


def _activate_existing_window():
    """Read the running instance's HWND and bring it to the foreground."""
    try:
        with open(HWND_FILE, "r") as f:
            hwnd = int(f.read().strip())
    except (OSError, ValueError):
        return
    user32 = ctypes.windll.user32
    if not user32.IsWindow(hwnd):
        return
    SW_SHOW = 5
    user32.ShowWindow(hwnd, SW_SHOW)
    # AttachThreadInput trick to bypass SetForegroundWindow restrictions
    fg = user32.GetForegroundWindow()
    cur_tid = user32.GetWindowThreadProcessId(fg, None)
    own_tid = ctypes.windll.kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(own_tid, cur_tid, True)
    try:
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        user32.AttachThreadInput(own_tid, cur_tid, False)


def ensure_single_instance():
    """Prevent multiple card windows. Uses a lock file with exclusive access."""
    lock_path = os.path.join(SCRIPT_DIR, ".card.lock")
    try:
        import msvcrt
        lock_file = open(lock_path, "w")
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        # Keep file handle alive for process lifetime
        ensure_single_instance._lock = lock_file
    except (OSError, IOError):
        _activate_existing_window()
        sys.exit(0)


class GlobalHotkeys:
    """Register process-level Windows hotkeys without adding dependencies."""

    def __init__(self, action_queue):
        self.action_queue = action_queue
        self.thread = None
        self.thread_id = None
        self.registered_ids = []

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.thread_id:
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)

    def _run(self):
        user32 = ctypes.windll.user32
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        try:
            for hotkey_id, hotkey in GLOBAL_HOTKEYS.items():
                ok = user32.RegisterHotKey(
                    None, hotkey_id, hotkey["modifiers"], hotkey["vk"]
                )
                if ok:
                    self.registered_ids.append(hotkey_id)

            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == WM_HOTKEY:
                    hotkey = GLOBAL_HOTKEYS.get(int(msg.wParam))
                    if hotkey:
                        self.action_queue.put(hotkey["action"])
        finally:
            for hotkey_id in self.registered_ids:
                user32.UnregisterHotKey(None, hotkey_id)


class StickyCard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sticky Card")
        self.root.attributes("-alpha", 0.97)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

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
        self.task_widgets = []
        self.drag_task = None
        self.drop_line = None
        self.tag_names = load_tags()
        self.active_tag = None  # None = show all
        self.show_tags = True
        self.collapsed_sections = set()  # h2 titles that are collapsed
        self.habits_mode = False
        self.quick_add_mode = False
        self.quick_add_line = None
        self.saving_edit = False
        self.hotkey_queue = queue.Queue()
        self.hotkeys = GlobalHotkeys(self.hotkey_queue)

        # Restore state
        state = load_state()
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
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
        self.user_height = state.get("height", None)
        self.show_tags = state.get("show_tags", True)
        self.collapsed_sections = set(state.get("collapsed_sections", []))
        saved_tag = state.get("active_tag", None)
        if saved_tag and saved_tag in self.tag_names:
            self.active_tag = saved_tag
        cardlib.ensure_daily_snapshot("startup")
        self._check_habits_reset(state)
        self.root.configure(bg=self.t("border"))
        init_h = self.user_height if self.user_height else MIN_HEIGHT
        # Clamp position to keep window visible on current screen
        x = max(0, min(x, sx - min(self.card_width, sx)))
        y = max(0, min(y, sy - min(init_h, sy)))
        self.root.geometry(f"{self.card_width}x{init_h}+{x}+{y}")

        self._build_ui()
        self._load_content()
        self._poll_file()
        self._auto_save_state()
        self.hotkeys.start()
        self._poll_hotkey_actions()
        # Publish HWND so a second launch can bring this window to front
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
            with open(HWND_FILE, "w") as f:
                f.write(str(hwnd))
        except Exception:
            pass
        self.root.after(100, self._fix_focus_hack)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def t(self, key):
        """Get color from current theme."""
        return THEMES[self.theme_name][key]

    def fs(self, key):
        """Get font size from current level."""
        return FONT_SIZES[self.font_size][key]

    @staticmethod
    def _blend_color(color1, color2, alpha):
        """Blend color1 into color2 by alpha (0=all color2, 1=all color1)."""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 * alpha + r2 * (1 - alpha))
        g = int(g1 * alpha + g2 * (1 - alpha))
        b = int(b1 * alpha + b2 * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _check_habits_reset(self, state):
        """Reset habits checkboxes if a new day has started."""
        from datetime import date
        today = date.today().isoformat()
        last_reset = state.get("habits_last_reset", "")
        if today != last_reset and os.path.exists(HABITS_FILE):
            try:
                with open(HABITS_FILE, "r", encoding="utf-8") as f:
                    text = f.read()
                new_text = re.sub(r'\[x\]', '[ ]', text, flags=re.IGNORECASE)
                if new_text != text:
                    cardlib.ensure_daily_snapshot("habits-reset")
                    with open(HABITS_FILE, "w", encoding="utf-8") as f:
                        f.write(new_text)
            except Exception:
                pass
            # Save reset date immediately
            state["habits_last_reset"] = today
            save_state(state)

    def _fix_focus_hack(self):
        self.root.withdraw()
        self.root.after(50, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _toggle_visibility(self, event=None):
        if self.root.state() == "withdrawn":
            self._show_window()
        else:
            if self.quick_add_mode and self.is_editing:
                self._save_edit()
            self.root.withdraw()
        return "break"

    def _poll_hotkey_actions(self):
        while True:
            try:
                action = self.hotkey_queue.get_nowait()
            except queue.Empty:
                break
            if action == "toggle_visibility":
                self._toggle_visibility()
            elif action == "quick_add":
                self._quick_add()
        self.root.after(50, self._poll_hotkey_actions)

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
                "font_size": self.font_size,
                "height": self.user_height,
                "active_tag": self.active_tag,
                "show_tags": self.show_tags,
                "collapsed_sections": list(self.collapsed_sections)
            })

    def _on_close(self):
        self._save_geometry()
        self.hotkeys.stop()
        self.root.destroy()

    # ── UI ────────────────────────────────────────────

    def _build_ui(self):
        self.drop_line = None
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
            topbar_inner, text="\u25cf", font=(SANS, 9),
            bg=self.t("topbar"), fg=self.t("pin_active") if self.is_pinned else self.t("pin_inactive"),
            cursor="hand2"
        )
        self.pin_btn.pack(side="left")
        self.pin_btn.bind("<Button-1>", self._toggle_pin)

        self.pin_label = tk.Label(
            topbar_inner, text=" Pinned" if self.is_pinned else " Unpinned",
            font=(SANS, 8), bg=self.t("topbar"), fg=self.t("secondary")
        )
        self.pin_label.pack(side="left")
        self.pin_label.bind("<Button-1>", self._toggle_pin)

        close_btn = tk.Label(
            topbar_inner, text="\u2715", font=(SANS, 10),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2"
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self._on_close())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg=self.t("fg")))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg=self.t("secondary")))

        # Edit button
        self.edit_btn = tk.Label(
            topbar_inner, text="Edit", font=(SANS, 8),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2"
        )
        self.edit_btn.pack(side="right", padx=(0, 10))
        self.edit_btn.bind("<Button-1>", self._toggle_edit)
        self.edit_btn.bind("<Enter>", lambda e: self.edit_btn.configure(fg=self.t("fg")))
        self.edit_btn.bind("<Leave>", lambda e: self.edit_btn.configure(
            fg=self.t("accent") if self.is_editing else self.t("secondary")))

        # Tag toggle
        self.tag_btn = tk.Label(
            topbar_inner, text="Tag", font=(SANS, 8), bg=self.t("topbar"),
            fg=self.t("accent") if self.show_tags else self.t("pin_inactive"),
            cursor="hand2"
        )
        self.tag_btn.pack(side="right", padx=(0, 6))
        self.tag_btn.bind("<Button-1>", self._toggle_show_tags)
        self.tag_btn.bind("<Enter>", lambda e: self.tag_btn.configure(fg=self.t("fg")))
        self.tag_btn.bind("<Leave>", lambda e: self.tag_btn.configure(
            fg=self.t("accent") if self.show_tags else self.t("pin_inactive")))

        # Time toggle
        self.time_btn = tk.Label(
            topbar_inner, text="T", font=(SANS, 8), bg=self.t("topbar"),
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
            font=(SANS, 8), bg=self.t("topbar"),
            fg=self.t("accent") if not self.show_done else self.t("secondary"),
            cursor="hand2"
        )
        self.fold_btn.pack(side="right", padx=(0, 6))
        self.fold_btn.bind("<Button-1>", self._toggle_fold)
        self.fold_btn.bind("<Enter>", lambda e: self.fold_btn.configure(fg=self.t("fg")))
        self.fold_btn.bind("<Leave>", lambda e: self.fold_btn.configure(
            fg=self.t("accent") if not self.show_done else self.t("secondary")))

        # Habits toggle
        if os.path.exists(HABITS_FILE):
            self.habits_btn = tk.Label(
                topbar_inner, text="Habits",
                font=(SANS, 8, "bold" if self.habits_mode else ""),
                bg=self.t("topbar"),
                fg=self.t("accent") if self.habits_mode else self.t("secondary"),
                cursor="hand2"
            )
            self.habits_btn.pack(side="right", padx=(0, 6))
            self.habits_btn.bind("<Button-1>", self._toggle_habits)
            self.habits_btn.bind("<Enter>", lambda e: self.habits_btn.configure(fg=self.t("fg")))
            self.habits_btn.bind("<Leave>", lambda e: self.habits_btn.configure(
                fg=self.t("accent") if self.habits_mode else self.t("secondary")))

        # Theme toggle
        self.theme_btn = tk.Label(
            topbar_inner, text=self.theme_name, font=(SANS, 8),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2"
        )
        self.theme_btn.pack(side="right", padx=(0, 6))
        self.theme_btn.bind("<Button-1>", self._next_theme)
        self.theme_btn.bind("<Enter>", lambda e: self.theme_btn.configure(fg=self.t("fg")))
        self.theme_btn.bind("<Leave>", lambda e: self.theme_btn.configure(fg=self.t("secondary")))

        # Font size toggle
        self.size_btn = tk.Label(
            topbar_inner, text=self.font_size, font=(SANS, 8),
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

        # ── Tag filter bar ──
        if self.tag_names:
            self.tag_bar = tk.Frame(self.card, bg=self.t("topbar"))
            self.tag_bar.pack(fill="x")
            tag_inner = tk.Frame(self.tag_bar, bg=self.t("topbar"))
            tag_inner.pack(fill="x", padx=14, pady=(5, 4))

            accent = self.t("accent")
            inactive_bg = self._blend_color(accent, self.t("bg"), 0.12)

            # "All" pill
            all_active = self.active_tag is None
            all_btn = tk.Label(
                tag_inner, text=" All ",
                font=(SANS, self.fs("top"), "bold" if all_active else ""),
                bg=accent if all_active else inactive_bg,
                fg="#FFFFFF" if all_active else self.t("secondary"),
                cursor="hand2", padx=8, pady=2, relief="flat", borderwidth=0
            )
            all_btn.pack(side="left")
            all_btn.bind("<Button-1>", lambda e: self._filter_tag(None))

            for tname in self.tag_names:
                is_active = self.active_tag == tname
                btn = tk.Label(
                    tag_inner, text=f" {tname} ",
                    font=(SANS, self.fs("top"), "bold" if is_active else ""),
                    bg=accent if is_active else inactive_bg,
                    fg="#FFFFFF" if is_active else self.t("secondary"),
                    cursor="hand2", padx=8, pady=2, relief="flat", borderwidth=0
                )
                btn.pack(side="left", padx=(4, 0))
                btn.bind("<Button-1>", lambda e, n=tname: self._filter_tag(n))

            tk.Frame(self.card, bg=self.t("hr"), height=1).pack(fill="x")

        # ── Shortcut tips ──
        self._build_shortcut_tips()

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
            ebar, text="Save", font=(SANS, 9, "bold"),
            bg=self.t("topbar"), fg=self.t("accent"), cursor="hand2", padx=10, pady=4
        )
        save_btn.pack(side="right", padx=8, pady=4)
        save_btn.bind("<Button-1>", lambda e: self._save_edit())
        cancel_btn = tk.Label(
            ebar, text="Cancel", font=(SANS, 9),
            bg=self.t("topbar"), fg=self.t("secondary"), cursor="hand2", padx=10, pady=4
        )
        cancel_btn.pack(side="right", pady=4)
        cancel_btn.bind("<Button-1>", lambda e: self._cancel_edit())

        self.editor.bind("<Control-s>", lambda e: self._save_edit())
        self.editor.bind("<Control-Return>", lambda e: self._save_edit())
        self.editor.bind("<Return>", self._quick_add_return)
        self.editor.bind("<Escape>", lambda e: self._cancel_edit())
        self.editor.bind("<FocusOut>", self._editor_focus_out)

        # ── Resize edges ──
        self.root.bind("<Motion>", self._resize_cursor)
        self.root.bind("<Button-1>", self._resize_start, add="+")
        self.root.bind("<B1-Motion>", self._resize_move, add="+")
        self.root.bind("<ButtonRelease-1>", self._resize_end, add="+")
        self._bind_keyboard_shortcuts()

    def _build_shortcut_tips(self):
        tip_frame = tk.Frame(self.card, bg=self.t("topbar"))
        tip_frame.pack(side="bottom", fill="x")
        tk.Frame(tip_frame, bg=self.t("hr"), height=1).pack(fill="x")
        tip_text = "Keys: " + "  |  ".join(f"{keys} {label}" for keys, label in SHORTCUT_TIPS)
        tk.Label(
            tip_frame,
            text=tip_text,
            font=(SANS, self.fs("small")),
            bg=self.t("topbar"),
            fg=self.t("secondary"),
            anchor="w",
            justify="left",
            wraplength=max(220, self.card_width - 28),
        ).pack(fill="x", padx=14, pady=(5, 6))
        history_label = tk.Label(
            tip_frame,
            text=f"Local history: {HISTORY_DIR}",
            font=(SANS, self.fs("small")),
            bg=self.t("topbar"),
            fg=self.t("secondary"),
            anchor="w",
            justify="left",
            wraplength=max(220, self.card_width - 28),
            cursor="hand2",
        )
        history_label.pack(fill="x", padx=14, pady=(0, 6))
        history_label.bind("<Button-1>", lambda e: self._open_history_dir())

    def _open_history_dir(self):
        os.makedirs(HISTORY_DIR, exist_ok=True)
        try:
            os.startfile(HISTORY_DIR)
        except Exception:
            pass

    def _bind_keyboard_shortcuts(self):
        def bind(sequence, handler, allow_editing=False):
            def run(event=None):
                if self.is_editing and not allow_editing:
                    return None
                return handler(event)
            self.root.bind_all(sequence, run)

        bind("<Control-e>", self._toggle_edit, allow_editing=True)
        bind("<Control-n>", self._quick_add)
        bind("<Control-d>", self._toggle_fold)
        bind("<Control-h>", self._toggle_habits_if_available)
        bind("<Control-t>", self._toggle_time)
        bind("<Control-Shift-T>", self._toggle_show_tags)
        bind("<Control-Shift-t>", self._toggle_show_tags)
        bind("<Control-p>", self._toggle_pin)
        bind("<Control-Shift-C>", self._next_theme)
        bind("<Control-Shift-c>", self._next_theme)
        bind("<Control-Shift-S>", self._next_font_size)
        bind("<Control-Shift-s>", self._next_font_size)
        bind("<Control-q>", lambda e: self._on_close())

    # ── Edit mode ─────────────────────────────────────

    def _toggle_edit(self, event=None):
        if self.is_editing:
            self._save_edit()
        else:
            self._enter_edit()
        return "break"

    @staticmethod
    def _find_insert_position(lines):
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

    def _prepare_quick_add_text(self, text):
        lines = text.splitlines()
        pos = self._find_insert_position(lines)
        lines.insert(pos, "- [ ] ")
        return "\n".join(lines), pos + 1, len("- [ ] ")

    def _enter_edit(self, quick_add=False):
        self.is_editing = True
        self.quick_add_mode = quick_add
        self.quick_add_line = None
        self.edit_btn.configure(text="Editing", fg=self.t("accent"))
        self.content_frame.pack_forget()
        self.editor_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        try:
            with open(self._active_file, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            text = ""
        if quick_add:
            text, line_no, col_no = self._prepare_quick_add_text(text)
            self.quick_add_line = line_no
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        if quick_add and self.quick_add_line:
            self.editor.mark_set("insert", f"{line_no}.{col_no}")
            self.editor.see("insert")
        self.editor.focus_set()

    def _cleanup_quick_add_placeholder(self, text):
        if not self.quick_add_line:
            return text
        lines = text.split("\n")
        idx = self.quick_add_line - 1
        if 0 <= idx < len(lines) and re.match(r'^[-*]\s*\[\s?\]\s*$', lines[idx]):
            del lines[idx]
        return "\n".join(lines)

    def _save_edit(self):
        if not self.is_editing or self.saving_edit:
            return "break"
        from datetime import datetime
        self.saving_edit = True
        try:
            text = self.editor.get("1.0", "end-1c")
            if self.quick_add_mode:
                text = self._cleanup_quick_add_placeholder(text)
            if not self.habits_mode:
                now = datetime.now().strftime("%m/%d %H:%M")
                # Auto-add timestamp to new unchecked tasks that don't have one
                lines = text.split("\n")
                for i, line in enumerate(lines):
                    if re.match(r'^[-*]\s*\[\s?\]\s*\S', line) and not re.search(r'`\d{2}/\d{2}\s+\d{2}:\d{2}`', line):
                        lines[i] = line.rstrip() + f" `{now}`"
                text = "\n".join(lines)
            cardlib.ensure_daily_snapshot("edit-save")
            with open(self._active_file, "w", encoding="utf-8") as f:
                f.write(text)
                if not text.endswith("\n"):
                    f.write("\n")
            self.last_mtime = 0  # force refresh
            self._exit_edit()
        finally:
            self.saving_edit = False
        return "break"

    def _cancel_edit(self):
        self._exit_edit()
        return "break"

    def _exit_edit(self):
        self.is_editing = False
        self.quick_add_mode = False
        self.quick_add_line = None
        self.edit_btn.configure(text="Edit", fg=self.t("secondary"))
        self.editor_frame.pack_forget()
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(12, 16))
        self._load_content()

    def _quick_add_return(self, event=None):
        if self.quick_add_mode:
            return self._save_edit()
        return None

    def _editor_focus_out(self, event=None):
        if self.quick_add_mode:
            self.root.after(80, self._save_quick_add_if_unfocused)

    def _save_quick_add_if_unfocused(self):
        if not self.quick_add_mode or not self.is_editing:
            return
        focused = self.root.focus_get()
        if focused is None or not self._is_descendant(focused, self.editor_frame):
            self._save_edit()

    @staticmethod
    def _is_descendant(widget, parent):
        while widget is not None:
            if widget == parent:
                return True
            widget = widget.master
        return False

    def _quick_add(self, event=None):
        self._show_window()
        if self.habits_mode:
            self.habits_mode = False
            self._apply_theme()
        if self.is_editing:
            self.editor.focus_set()
            return "break"
        self._enter_edit(quick_add=True)
        return "break"

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
        cursors = {
            "e": "sb_h_double_arrow", "w": "sb_h_double_arrow",
            "s": "sb_v_double_arrow",
            "se": "size_nw_se", "sw": "size_ne_sw",
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
            edge = self.resize_data.get("edge", "")
            self.resize_data["active"] = False
            if "s" in edge:
                # User manually set height via bottom edge
                geo = self.root.geometry()
                m = re.match(r'(\d+)x(\d+)', geo)
                if m:
                    self.user_height = int(m.group(2))
            self._save_geometry()
            if not self.is_editing:
                self.last_mtime = 0  # re-render with new width
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
        self.tag_names = load_tags()
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
            target = self._active_file
            lines = list(open(target, "r", encoding="utf-8"))
            if line_idx < 0 or line_idx >= len(lines):
                return
            line = lines[line_idx]
            if re.search(r'\[x\]', line, re.IGNORECASE):
                lines[line_idx] = re.sub(r'\[x\]', '[ ]', line, count=1, flags=re.IGNORECASE)
                if not self.habits_mode:
                    lines[line_idx] = re.sub(r'\s*done:`\d{2}/\d{2}\s+\d{2}:\d{2}`', '', lines[line_idx])
            elif re.search(r'\[\s?\]', line):
                lines[line_idx] = re.sub(r'\[\s?\]', '[x]', line, count=1)
                if not self.habits_mode:
                    now = datetime.now().strftime("%m/%d %H:%M")
                    lines[line_idx] = lines[line_idx].rstrip('\n') + f' done:`{now}`\n'
            cardlib.ensure_daily_snapshot("task-toggle")
            with open(target, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            pass

    def _make_clickable(self, widget, line_idx):
        def bind_task(w):
            w.bind("<Button-1>", lambda e, idx=line_idx: self._task_press(e, idx))
            w.bind("<B1-Motion>", lambda e, idx=line_idx: self._task_drag(e, idx))
            w.bind("<ButtonRelease-1>", lambda e, idx=line_idx: self._task_release(e, idx))
            w.configure(cursor="hand2")
        bind_task(widget)
        for child in widget.winfo_children():
            bind_task(child)

    # ── Task drag reorder ─────────────────────────────

    def _task_press(self, event, line_idx):
        self.drag_task = {
            "line_idx": line_idx,
            "start_y": event.y_root,
            "dragging": False
        }

    def _task_drag(self, event, line_idx):
        if self.drag_task is None or self.is_editing:
            return
        dy = abs(event.y_root - self.drag_task["start_y"])
        if dy > 5:
            self.drag_task["dragging"] = True
            # Highlight dragged task
            for w, idx in self.task_widgets:
                if idx == self.drag_task["line_idx"]:
                    w.configure(bg=self.t("hr"))
                    for child in w.winfo_children():
                        child.configure(bg=self.t("hr"))
            self._update_drop_indicator(event.y_root)

    def _task_release(self, event, line_idx):
        if self.drag_task is None:
            return
        if self.drag_task["dragging"]:
            # Reset highlight
            bg = self.t("bg")
            for w, idx in self.task_widgets:
                if idx == self.drag_task["line_idx"]:
                    w.configure(bg=bg)
                    for child in w.winfo_children():
                        child.configure(bg=bg)
            self._complete_reorder(event.y_root)
        else:
            self._toggle_task(line_idx)
        self.drag_task = None
        self._hide_drop_indicator()

    def _find_drop_index(self, y_root):
        """Find drop position index among task_widgets."""
        for i, (widget, _) in enumerate(self.task_widgets):
            wy = widget.winfo_rooty()
            wh = widget.winfo_height()
            if y_root < wy + wh // 2:
                return i
        return len(self.task_widgets)

    def _update_drop_indicator(self, y_root):
        drop_idx = self._find_drop_index(y_root)
        if not self.task_widgets:
            return
        if drop_idx < len(self.task_widgets):
            target = self.task_widgets[drop_idx][0]
            y = target.winfo_y() - 1
        else:
            last = self.task_widgets[-1][0]
            y = last.winfo_y() + last.winfo_height() + 1
        self._show_drop_indicator(y)

    def _show_drop_indicator(self, y):
        if self.drop_line is None:
            self.drop_line = tk.Frame(self.content_frame, bg=self.t("accent"), height=2)
        self.drop_line.place(x=0, relwidth=1.0, y=y)

    def _hide_drop_indicator(self):
        if self.drop_line is not None:
            self.drop_line.place_forget()
            self.drop_line = None

    def _complete_reorder(self, y_root):
        """Move task to new position in file."""
        if self.drag_task is None:
            return
        src_line_idx = self.drag_task["line_idx"]
        drop_idx = self._find_drop_index(y_root)

        # Find source position in task_widgets
        src_task_idx = None
        for i, (_, idx) in enumerate(self.task_widgets):
            if idx == src_line_idx:
                src_task_idx = i
                break
        if src_task_idx is None:
            return
        # No move needed if same position
        if drop_idx == src_task_idx or drop_idx == src_task_idx + 1:
            return

        # Determine target line index in file
        if drop_idx < len(self.task_widgets):
            dst_line_idx = self.task_widgets[drop_idx][1]
        else:
            dst_line_idx = self.task_widgets[-1][1] + 1

        try:
            target = self._active_file
            with open(target, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if src_line_idx < 0 or src_line_idx >= len(lines):
                return
            line = lines.pop(src_line_idx)
            if src_line_idx < dst_line_idx:
                dst_line_idx -= 1
            lines.insert(dst_line_idx, line)
            cardlib.ensure_daily_snapshot("task-reorder")
            with open(target, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            pass

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

    def _toggle_habits(self, event=None):
        self.habits_mode = not self.habits_mode
        self._save_geometry()
        self._apply_theme()
        return "break"

    def _toggle_habits_if_available(self, event=None):
        if os.path.exists(HABITS_FILE):
            return self._toggle_habits(event)
        return "break"

    def _toggle_section(self, title):
        if title in self.collapsed_sections:
            self.collapsed_sections.discard(title)
        else:
            self.collapsed_sections.add(title)
        self._save_geometry()
        self.last_mtime = 0
        self._load_content()

    def _toggle_show_tags(self, event=None):
        self.show_tags = not self.show_tags
        self.tag_btn.configure(fg=self.t("accent") if self.show_tags else self.t("pin_inactive"))
        self._save_geometry()
        self.last_mtime = 0
        self._load_content()
        return "break"

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

    def _filter_tag(self, tag_name):
        if self.active_tag == tag_name:
            self.active_tag = None  # toggle off
        else:
            self.active_tag = tag_name
        self._save_geometry()
        self._apply_theme()  # rebuild UI to update tag bar highlight
        return "break"

    def _render_content(self, text):
        for w in self.content_frame.winfo_children():
            w.destroy()
        self.task_widgets = []
        self._hide_drop_indicator()

        bg = self.t("bg")
        raw_lines = text.split("\n")
        wrap_w = self.card_width - 60
        current_h2 = None  # track which h2 section we're in

        for line_idx, line in enumerate(raw_lines):
            stripped = line.strip()

            if not stripped:
                if current_h2 and current_h2 in self.collapsed_sections:
                    continue
                tk.Frame(self.content_frame, bg=bg, height=6).pack(fill="x")
                continue

            if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
                current_h2 = None  # separator ends h2 section
                tk.Frame(self.content_frame, bg=bg, height=8).pack(fill="x")
                tk.Frame(self.content_frame, bg=self.t("hr"), height=1).pack(fill="x", padx=4)
                tk.Frame(self.content_frame, bg=bg, height=8).pack(fill="x")
                continue

            m = re.match(r'^#\s+(.*)', stripped)
            if m:
                current_h2 = None  # h1 ends h2 section
                tk.Label(
                    self.content_frame, text=m.group(1),
                    font=(SERIF, self.fs("h1"), "bold"),
                    bg=bg, fg=self.t("title"), anchor="w",
                    wraplength=wrap_w, justify="left"
                ).pack(fill="x", pady=(4, 6))
                continue

            m = re.match(r'^##\s+(.*)', stripped)
            if m:
                h2_title = m.group(1)
                current_h2 = h2_title
                is_collapsed = h2_title in self.collapsed_sections
                arrow = "\u25b6" if is_collapsed else "\u25bc"
                h2_label = tk.Label(
                    self.content_frame, text=f"{arrow}  {h2_title}",
                    font=(SERIF, self.fs("h2"), "bold"),
                    bg=bg, fg=self.t("title"), anchor="w",
                    wraplength=wrap_w, justify="left", cursor="hand2"
                )
                h2_label.pack(fill="x", pady=(6, 4))
                h2_label.bind("<Button-1>", lambda e, t=h2_title: self._toggle_section(t))
                continue

            # Skip content if inside a collapsed h2 section
            if current_h2 and current_h2 in self.collapsed_sections:
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
                clean_text, task_tags = parse_tags(task_text)
                if self.active_tag and self.active_tag not in task_tags:
                    continue
                f = tk.Frame(self.content_frame, bg=bg)
                f.pack(fill="x", pady=2)
                tk.Label(f, text="  \u2611 ", font=(SANS, self.fs("body") - 1), bg=bg, fg=self.t("done")).pack(side="left", anchor="n")
                tk.Label(
                    f, text=clean_text, font=(SERIF, self.fs("body"), "overstrike"),
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
                if self.show_tags:
                    for tname in task_tags:
                        tk.Label(f, text=f" {tname} ", font=(SANS, self.fs("small")),
                                 bg=self.t("accent"), fg="#FFFFFF", padx=4, pady=0
                                 ).pack(side="right", padx=(2, 0))
                self._make_clickable(f, line_idx)
                self.task_widgets.append((f, line_idx))
                continue

            # Pending task
            m = re.match(r'^[-*]\s*\[\s?\]\s*(.*)', stripped)
            if m:
                task_text, create_ts, _ = self._split_timestamp(m.group(1))
                clean_text, task_tags = parse_tags(task_text)
                if self.active_tag and self.active_tag not in task_tags:
                    continue
                f = tk.Frame(self.content_frame, bg=bg)
                f.pack(fill="x", pady=2)
                tk.Label(f, text="  \u2610 ", font=(SANS, self.fs("body") - 1), bg=bg, fg=self.t("accent")).pack(side="left", anchor="n")
                tk.Label(
                    f, text=clean_text, font=(SERIF, self.fs("body")),
                    bg=bg, fg=self.t("fg"), anchor="w",
                    wraplength=wrap_w - 70, justify="left"
                ).pack(side="left", fill="x")
                if create_ts and self.show_time:
                    tk.Label(f, text=create_ts, font=(SANS, self.fs("small")), bg=bg, fg=self.t("secondary")
                    ).pack(side="right", padx=(4, 0))
                if self.show_tags:
                    for tname in task_tags:
                        tk.Label(f, text=f" {tname} ", font=(SANS, self.fs("small")),
                                 bg=self.t("accent"), fg="#FFFFFF", padx=4, pady=0
                                 ).pack(side="right", padx=(2, 0))
                self._make_clickable(f, line_idx)
                self.task_widgets.append((f, line_idx))
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

        # Auto height (skip if user has manually set height via bottom-edge resize)
        self.root.update_idletasks()
        if self.user_height is None:
            need_h = self.card.winfo_reqheight() + 4
            h = max(MIN_HEIGHT, need_h)
            geo = self.root.geometry()
            parts = geo.split("+")
            self.root.geometry(f"{self.card_width}x{h}+{parts[1]}+{parts[2]}")

    # ── File polling ──────────────────────────────────

    @property
    def _active_file(self):
        return HABITS_FILE if self.habits_mode else CONTENT_FILE

    def _load_content(self):
        if self.is_editing:
            return
        try:
            target = self._active_file
            mtime = os.path.getmtime(target)
            if mtime != self.last_mtime:
                self.last_mtime = mtime
                with open(target, "r", encoding="utf-8") as f:
                    text = f.read()
                self._render_content(text)
        except FileNotFoundError:
            name = "card-habits.md" if self.habits_mode else "card-content.md"
            self._render_content(f"{name} not found")

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
