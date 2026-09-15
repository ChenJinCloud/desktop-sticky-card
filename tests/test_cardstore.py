import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from shared.cardstore import CardStore, ContentConflictError, split_multi_tasks


PROJECT_DIR = Path(__file__).resolve().parent.parent


class CardStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temporary.name)
        self.store = CardStore(self.data_dir)
        self.store.content_file.write_text(
            "# Test\n- [ ] alpha `04/15 10:00`\n", encoding="utf-8"
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_done_is_idempotent(self):
        self.assertTrue(self.store.toggle_task(1, True)[0])
        first = self.store.content_file.read_text(encoding="utf-8")
        self.assertTrue(self.store.toggle_task(1, True)[0])
        second = self.store.content_file.read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertEqual(second.count("done:`"), 1)

    def test_editor_detects_external_change(self):
        original = self.store.content_file.read_text(encoding="utf-8")
        self.store.add_tasks(["external"])
        with self.assertRaises(ContentConflictError):
            self.store.write_text(
                self.store.content_file,
                "# overwritten\n",
                reason="edit-save",
                expected_text=original,
            )

    def test_daily_snapshot_keeps_pre_write_content(self):
        original = self.store.content_file.read_text(encoding="utf-8")
        snapshot_dir = Path(self.store.ensure_daily_snapshot("test"))
        self.store.add_tasks(["new task"])
        self.assertEqual(
            (snapshot_dir / "card-content.md").read_text(encoding="utf-8"),
            original,
        )
        manifest = json.loads((snapshot_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("card-content.md", manifest["files"])

    def test_habits_reset_only_once_and_state_updates_are_merged(self):
        self.store.habits_file.write_text("- [x] walk\n", encoding="utf-8")
        self.assertTrue(self.store.reset_habits_if_needed("2026-09-15"))
        self.assertFalse(self.store.reset_habits_if_needed("2026-09-15"))
        self.store.update_json(self.store.state_file, {"theme": "Dark"}, reason="state-save")
        state = self.store.read_json(self.store.state_file)
        self.assertEqual(state["habits_last_reset"], "2026-09-15")
        self.assertEqual(state["theme"], "Dark")
        self.assertEqual(self.store.habits_file.read_text(encoding="utf-8"), "- [ ] walk\n")

    def test_concurrent_cli_adds_do_not_lose_tasks(self):
        env = os.environ.copy()
        env["DESKTOP_STICKY_CARD_HOME"] = str(self.data_dir)

        def add(number):
            return subprocess.run(
                [sys.executable, str(PROJECT_DIR / "card.py"), "add", f"task-{number}"],
                cwd=PROJECT_DIR,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(add, range(20)))
        self.assertTrue(all(result.returncode == 0 for result in results), results)
        tasks = self.store.get_tasks(self.store.read_lines())
        task_text = "\n".join(text for _, _, text in tasks)
        self.assertEqual(len(tasks), 21)
        for number in range(20):
            self.assertIn(f"task-{number}", task_text)


class ParsingTests(unittest.TestCase):
    def test_inline_numbered_tasks_keep_decimal_version(self):
        self.assertEqual(
            split_multi_tasks("1.Fix Python 3.12 2.Write docs"),
            ["Fix Python 3.12", "Write docs"],
        )

    def test_chinese_numbered_tasks(self):
        self.assertEqual(split_multi_tasks("1.买菜；2.做饭"), ["买菜", "做饭"])

    def test_plain_semicolon_tasks(self):
        self.assertEqual(
            split_multi_tasks("Budget 2026; Review Q4"),
            ["Budget 2026", "Review Q4"],
        )

    def test_single_year_prefix_is_preserved(self):
        self.assertEqual(split_multi_tasks("2026.Plan"), ["2026.Plan"])


if __name__ == "__main__":
    unittest.main()
