import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CLI = Path(__file__).resolve().parent.parent / "mac" / "card.py"


class AgentCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, DESKTOP_STICKY_CARD_HOME=self.tmp.name)
        self.content = Path(self.tmp.name) / "card-content.md"
        self.content.write_text("# Existing\n\nOriginal note", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, input=None):
        return subprocess.run([sys.executable, str(CLI), *args], env=self.env, input=input,
                              text=True, capture_output=True)

    def test_content_reads_full_markdown(self):
        result = self.run_cli("content")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "# Existing\n\nOriginal note")

    def test_append_stdin_preserves_existing_content_and_multiline_markdown(self):
        result = self.run_cli("append", "--stdin", input="## Notes\n- one\n- two\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.content.read_text(), "# Existing\n\nOriginal note\n## Notes\n- one\n- two\n")
        snapshot = next((Path(self.tmp.name) / "card-history").glob("*/card-content.md"))
        self.assertEqual(snapshot.read_text(), "# Existing\n\nOriginal note")

    def test_empty_append_and_missing_task_fail_without_changes(self):
        original = self.content.read_text()
        self.assertNotEqual(self.run_cli("append", "--stdin", input="").returncode, 0)
        self.assertNotEqual(self.run_cli("done", "99").returncode, 0)
        self.assertEqual(self.content.read_text(), original)

    def test_add_task_after_content_without_final_newline(self):
        result = self.run_cli("add", "Agent task")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Original note\n- [ ] Agent task", self.content.read_text())

    def test_help_and_incomplete_commands_do_not_create_tasks(self):
        original = self.content.read_text()
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("append --stdin", result.stdout)
        self.assertNotEqual(self.run_cli("done").returncode, 0)
        self.assertEqual(self.content.read_text(), original)

    def test_concurrent_appends_preserve_all_content(self):
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda n: self.run_cli("append", "--stdin", input=f"note-{n}\n"), range(10)))
        self.assertTrue(all(result.returncode == 0 for result in results))
        content = self.content.read_text()
        for n in range(10):
            self.assertIn(f"note-{n}\n", content)
