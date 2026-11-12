import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "mac" / "menubar_logic.py"
spec = importlib.util.spec_from_file_location("menubar_logic", path)
logic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logic)


class HoverTests(unittest.TestCase):
    def test_hover_opens_and_leaving_both_closes_after_grace_period(self):
        state = logic.HoverState(grace=0.4)
        self.assertEqual(state.update(0, True, False), "show")
        self.assertIsNone(state.update(0.1, False, False))
        self.assertIsNone(state.update(0.3, False, True))
        self.assertIsNone(state.update(1, False, False))
        self.assertEqual(state.update(1.5, False, False), "hide")

    def test_reentry_cancels_pending_hide(self):
        state = logic.HoverState(grace=0.4)
        state.update(0, True, False)
        state.update(1, False, False)
        self.assertIsNone(state.update(1.3, True, False))
        self.assertIsNone(state.update(1.7, True, False))

    def test_pinned_stays_visible_and_unpin_restarts_hide_delay(self):
        state = logic.HoverState(grace=0.4)
        self.assertEqual(state.update(0, False, False, pinned=True), "show")
        self.assertIsNone(state.update(10, False, False, pinned=True))
        self.assertIsNone(state.update(11, False, False, pinned=False))
        self.assertEqual(state.update(11.5, False, False, pinned=False), "hide")

    def test_pin_cancels_pending_hide(self):
        state = logic.HoverState(grace=0.4)
        state.update(0, True, False)
        state.update(1, False, False)
        self.assertIsNone(state.update(2, False, False, pinned=True))
        self.assertIsNone(state.update(3, False, False, pinned=False))


class NotchTests(unittest.TestCase):
    def test_icon_inside_gap_is_behind_notch(self):
        # Measured on a 16-inch MacBook Pro: the gap runs from 771 to 956 points.
        self.assertTrue(logic.is_behind_notch(944, 771, 956))

    def test_icon_outside_gap_is_visible(self):
        self.assertFalse(logic.is_behind_notch(700, 771, 956))
        self.assertFalse(logic.is_behind_notch(1000, 771, 956))

    def test_unknown_geometry_means_no_warning(self):
        self.assertFalse(logic.is_behind_notch(None, 771, 956))
        self.assertFalse(logic.is_behind_notch(944, None, None))


class AppleScriptTests(unittest.TestCase):
    def test_line_breaks_survive_as_return(self):
        self.assertEqual(logic.applescript_string("a\nb"), '"a" & return & "b"')

    def test_quotes_and_backslashes_are_escaped(self):
        self.assertEqual(logic.applescript_string('say "hi"'), '"say \\"hi\\""')
        self.assertEqual(logic.applescript_string("c:\\path"), '"c:\\\\path"')
