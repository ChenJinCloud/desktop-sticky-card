import importlib.util
import json
import os
import queue
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


@unittest.skipUnless(sys.platform == "darwin", "Requires macOS Tk")
class MacGuiTests(unittest.TestCase):
    def test_edit_view_controls_and_task_persistence(self):
        import tkinter as tk

        project = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"DESKTOP_STICKY_CARD_HOME": directory}
        ), patch.object(tk.Tk, "mainloop"):
            Path(directory, "card-content.md").write_text("# Original\n", encoding="utf-8")
            sys.path.insert(0, str(project / "mac"))
            try:
                spec = importlib.util.spec_from_file_location("mac_sticky_card", project / "mac/sticky-card.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                card = module.StickyCard()
                try:
                    card._enter_edit()
                    card.editor.insert("end", "unsaved task")
                    expected = card.editor.get("1.0", "end-1c")
                    for change in (card._next_theme, card._next_font_size):
                        change()
                        self.assertTrue(card.is_editing)
                        self.assertTrue(card.editor_frame.winfo_manager())
                        self.assertEqual(card.editor.get("1.0", "end-1c"), expected)
                    card._save_edit()
                    self.assertIn("unsaved task", Path(directory, "card-content.md").read_text())
                    card.root.update()
                    original_pin = card.is_pinned
                    card.pin_label.event_generate("<Button-1>", x=10, y=5)
                    card.root.update()
                    self.assertNotEqual(card.is_pinned, original_pin)
                    cardlib = module.cardlib
                    cardlib.add_tasks(["GUI toggle check"])
                    card._load_content()
                    lines = cardlib.read_lines()
                    index = next(i for i, line in enumerate(lines) if "GUI toggle check" in line)
                    card._toggle_task(index)
                    self.assertIn("- [x] GUI toggle check", Path(directory, "card-content.md").read_text())
                    card._toggle_fold()
                    self.assertFalse(card.show_done)
                    card._toggle_time()
                    self.assertFalse(card.show_time)
                    result = subprocess.run(
                        [str(project / "mac/card.sh"), "append", "--stdin"],
                        input="## Agent note\nHello from CLI\n", text=True,
                        capture_output=True, env=os.environ.copy(),
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    card._load_content()
                    labels = [widget.cget("text") for widget in card.content_frame.winfo_children()
                              if isinstance(widget, tk.Label)]
                    self.assertIn("Agent note", labels)
                    self.assertIn("Hello from CLI", labels)
                    card.menu_bar = True
                    card.menu_bridge = SimpleNamespace(events=queue.Queue())
                    card.hover.visible = True
                    card._toggle_pin()
                    card.root.update_idletasks()
                    self.assertTrue(card.is_pinned)
                    self.assertEqual(card.root.winfo_x(), card.root.winfo_screenwidth() - card.card_width - 20)
                    self.assertTrue(json.loads(Path(directory, ".card-state.json").read_text())["is_pinned"])
                    with patch.object(card.root, "winfo_pointerxy", return_value=(0, 500)), \
                         patch.object(card.root, "after"), \
                         patch.object(module.time, "monotonic", side_effect=[10, 11, 12]):
                        card._poll_menu()
                        self.assertEqual(card.root.state(), "normal")
                        card._toggle_pin()
                        card._poll_menu()
                        card._poll_menu()
                        self.assertEqual(card.root.state(), "withdrawn")
                    card._toggle_pin()
                finally:
                    card.root.destroy()
                with patch.object(module, "MenuBridge", return_value=SimpleNamespace(events=queue.Queue())):
                    restored = module.StickyCard(menu_bar=True)
                    try:
                        restored.root.update()
                        self.assertTrue(restored.is_pinned)
                        self.assertEqual(restored.root.state(), "normal")
                        self.assertEqual(restored.root.winfo_x(), restored.root.winfo_screenwidth() - restored.card_width - 20)
                    finally:
                        restored.root.destroy()
            finally:
                sys.path.remove(str(project / "mac"))
