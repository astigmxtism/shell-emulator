"""Тесты выполнения стартового скрипта."""
import unittest

from fs_helpers import make_temp_dir, write_file
from helpers import Collector
from shell_emulator.common import ERR, INPUT
from shell_emulator.script import ScriptError, read_script, run_script
from shell_emulator.shell import Shell


def run_text(test_case, text):
    """Выполнить скрипт из текста; вернуть собранный вывод и оболочку."""
    path = write_file(make_temp_dir(test_case), "s.emu", text)
    collector = Collector()
    shell = Shell()
    run_script(shell, path, collector)
    return collector, shell


class RunScriptTest(unittest.TestCase):
    """Проверки run_script."""

    def test_input_and_output_are_shown(self):
        collector, _ = run_text(self, "ls /etc\ncd /tmp\n")
        inputs = collector.texts(INPUT)
        self.assertTrue(inputs[0].endswith("$ ls /etc"))
        self.assertTrue(inputs[1].endswith("$ cd /tmp"))
        self.assertEqual(collector.texts("out"), ["motd"])

    def test_erroneous_lines_are_reported_and_skipped(self):
        collector, _ = run_text(self, "ls /etc\nbad\nexit 1\ncd /tmp\n")
        errors = collector.texts(ERR)
        self.assertIn("bad: command not found", errors)
        self.assertIn("[script] line 2: error, line skipped", errors)
        self.assertIn("[script] line 3: error, line skipped", errors)
        self.assertEqual(len(collector.texts(INPUT)), 4)

    def test_blank_lines_are_ignored(self):
        collector, _ = run_text(self, "\n   \nls\n")
        self.assertEqual(len(collector.texts(INPUT)), 1)

    def test_exit_stops_script(self):
        collector, shell = run_text(self, "ls\nexit\nls after\n")
        self.assertTrue(shell.session.finished)
        self.assertEqual(len(collector.texts(INPUT)), 2)

    def test_missing_script_reports_error(self):
        collector = Collector()
        run_script(Shell(), "no/such/script.emu", collector)
        self.assertIn("cannot read script", collector.texts(ERR)[0])

    def test_read_script_raises_for_missing_file(self):
        with self.assertRaises(ScriptError):
            read_script("no/such/script.emu")

    def test_read_script_raises_for_invalid_text(self):
        folder = make_temp_dir(self)
        path = folder + "/bin.emu"
        with open(path, "wb") as handle:
            handle.write(bytes([255, 254, 0]))
        with self.assertRaises(ScriptError):
            read_script(path)


if __name__ == "__main__":
    unittest.main()
