"""Тесты запуска: объединение параметров и отладочный вывод."""
import os
import unittest

from fs_helpers import make_temp_dir, write_file
from helpers import Collector
from shell_emulator.app import prepare, run_startup, window_title
from shell_emulator.common import DEBUG, ERR

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_VFS = os.path.join(REPO_ROOT, "examples", "vfs", "files")
README = os.path.join(REPO_ROOT, "README.md")
EXAMPLES = os.path.join(REPO_ROOT, "examples")


class PrepareTest(unittest.TestCase):
    """Проверки prepare и run_startup."""

    def test_debug_output_contains_all_parameters(self):
        _, _, notices = prepare(["--vfs", "v", "--script", "s"])
        text = "\n".join(text for text, kind in notices if kind == DEBUG)
        self.assertIn("vfs_path = v (command line)", text)
        self.assertIn("script_path = s (command line)", text)
        self.assertIn("config_path = <not set>", text)

    def test_config_error_is_reported(self):
        _, _, notices = prepare(["--config", "no/such.json"])
        errors = [text for text, kind in notices if kind == ERR]
        self.assertIn("[config] error", errors[0])

    def test_cli_has_priority_over_config(self):
        folder = make_temp_dir(self)
        config = write_file(folder, "c.json", '{"vfs_path": "from_file"}')
        _, settings, _ = prepare(["--config", config, "--vfs", "from_cli"])
        self.assertEqual(settings.vfs_path, "from_cli")

    def test_values_come_from_config_file(self):
        folder = make_temp_dir(self)
        config = write_file(
            folder, "c.json", '{"vfs_path": "v", "script_path": "s"}'
        )
        _, settings, notices = prepare(["--config", config])
        self.assertEqual((settings.vfs_path, settings.script_path), ("v", "s"))
        self.assertIn("(config file)", "\n".join(t for t, _ in notices))

    def test_startup_runs_script(self):
        folder = make_temp_dir(self)
        script = write_file(folder, "s.emu", "ls one\n")
        shell, settings, notices = prepare(["--script", script])
        collector = Collector()
        run_startup(shell, settings, notices, collector)
        self.assertEqual(collector.texts("out"), ["ls: args = ['one']"])

    def test_example_scripts_run(self):
        path = os.path.join(REPO_ROOT, "examples", "scripts")
        shell, settings, notices = prepare(
            ["--script", os.path.join(path, "stage2_errors.emu")]
        )
        collector = Collector()
        run_startup(shell, settings, notices, collector)
        errors = collector.texts(ERR)
        self.assertIn("[script] line 2: error, line skipped", errors)
        self.assertIn("[script] line 3: error, line skipped", errors)

    def test_window_title_contains_vfs(self):
        shell, _, _ = prepare([])
        self.assertIn("VFS", window_title(shell))


class LoadVfsTest(unittest.TestCase):
    """Загрузка VFS при запуске."""

    def test_default_vfs_when_no_path(self):
        shell, _, notices = prepare([])
        self.assertEqual(shell.session.label, "default")
        self.assertFalse([n for n in notices if n[1] == ERR])

    def test_loads_vfs_from_directory(self):
        shell, _, _ = prepare(["--vfs", FILES_VFS])
        self.assertEqual(shell.session.label, "files")
        self.assertIn("VFS: files", window_title(shell))

    def test_vfs_path_from_config_file(self):
        config = os.path.join(EXAMPLES, "config", "vfs_deep.json")
        shell, _, _ = prepare(["--config", config])
        self.assertEqual(shell.session.label, "deep")

    def test_missing_vfs_is_reported_and_default_used(self):
        shell, _, notices = prepare(["--vfs", "no/such/dir"])
        errors = [text for text, kind in notices if kind == ERR]
        self.assertIn("[vfs] error", errors[0])
        self.assertIn("not found", errors[0])
        self.assertEqual(shell.session.label, "default")

    def test_file_as_vfs_is_reported(self):
        _, _, notices = prepare(["--vfs", README])
        errors = [text for text, kind in notices if kind == ERR]
        self.assertIn("invalid VFS format", errors[0])

    def test_stage3_script_covers_all_commands(self):
        script = os.path.join(EXAMPLES, "scripts", "stage3_all.emu")
        shell, settings, notices = prepare(
            ["--vfs", os.path.join(EXAMPLES, "vfs", "deep"),
             "--script", script]
        )
        collector = Collector()
        run_startup(shell, settings, notices, collector)
        self.assertTrue(shell.session.finished)
        self.assertIn("foo: command not found", collector.texts(ERR))


if __name__ == "__main__":
    unittest.main()
