import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(sys.platform == "darwin", "macOS installer")
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "user with spaces"
        self.home.mkdir()
        self.repo = self.root / "fixture"
        self.repo.mkdir()
        for folder in ("mac", "shared", "skills"):
            source = ROOT / folder
            if source.exists():
                shutil.copytree(source, self.repo / folder, ignore=shutil.ignore_patterns(
                    "__pycache__", "card-content.md", "card-history", ".card*"))
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit", "-qm", "fixture"], check=True)
        self.env = dict(os.environ, STICKY_CARD_INSTALL_HOME=str(self.home),
                        STICKY_CARD_REPOSITORY=str(self.repo))
        for name in (".agents", ".claude", ".codex", ".workbuddy"):
            (self.home / name / "skills").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def install(self):
        return subprocess.run(["bash", str(ROOT / "install-macos.sh")], env=self.env,
                              text=True, capture_output=True)

    def test_install_and_repeat_preserve_data_and_enable_cli_and_skills(self):
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        cli = self.home / ".local/bin/sticky-card"
        env = dict(self.env, DESKTOP_STICKY_CARD_HOME=str(self.home / "data"))
        add = subprocess.run([str(cli), "add", "install test"], env=env, capture_output=True, text=True)
        self.assertEqual(add.returncode, 0, add.stderr)
        content = (self.home / "data/card-content.md").read_text()
        self.assertIn("install test", content)
        for name in (".agents", ".claude", ".codex", ".workbuddy"):
            self.assertTrue((self.home / name / "skills/desktop-sticky-card/SKILL.md").is_file())
        start = subprocess.Popen([str(self.home / ".local/bin/sticky-card-start")], env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            time.sleep(2)
            self.assertIsNone(start.poll(), "card exited during startup")
        finally:
            start.terminate()
            start.communicate(timeout=10)
        second = self.install()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual((self.home / "data/card-content.md").read_text(), content)

    def test_existing_unmanaged_command_is_not_overwritten(self):
        path = self.home / ".local/bin/sticky-card"
        path.parent.mkdir(parents=True)
        path.write_text("existing", encoding="utf-8")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_text(), "existing")
        self.assertFalse((self.home / ".local/share/desktop-sticky-card").exists())

    def test_existing_unmanaged_skill_is_not_overwritten(self):
        folder = self.home / ".claude/skills/desktop-sticky-card"
        folder.mkdir()
        (folder / "SKILL.md").write_text("existing skill")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((folder / "SKILL.md").read_text(), "existing skill")
        self.assertFalse((self.home / ".local/share/desktop-sticky-card").exists())

    def test_existing_marker_with_wrong_launcher_is_not_accepted(self):
        path = self.home / ".local/bin/sticky-card"
        path.parent.mkdir(parents=True)
        path.write_text("#!/bin/bash\n# desktop-sticky-card managed launcher\nexec /wrong/path\n")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("/wrong/path", path.read_text())

    def test_install_creates_missing_skill_roots(self):
        for name in (".agents", ".claude", ".codex", ".workbuddy"):
            shutil.rmtree(self.home / name)
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.home / ".agents/skills/desktop-sticky-card/SKILL.md").is_file())
