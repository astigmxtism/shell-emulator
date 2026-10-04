"""Тесты ядра оболочки: команды-заглушки, ошибки, exit."""
import unittest

from helpers import Collector
from shell_emulator.common import ERR, INPUT, OUT
from shell_emulator.shell import Shell


class ShellStubTest(unittest.TestCase):
    """Проверки выполнения строк на этапе прототипа."""

    def test_ls_stub_prints_name_and_args(self):
        result = Shell().execute("ls -l /tmp")
        self.assertEqual(result.out, "ls: args = ['-l', '/tmp']")
        self.assertEqual(result.err, "")

    def test_cd_stub_prints_name_and_args(self):
        result = Shell().execute("cd /home")
        self.assertEqual(result.out, "cd: args = ['/home']")

    def test_unknown_command_reports_error(self):
        result = Shell().execute("foo bar")
        self.assertEqual(result.err, "foo: command not found")
        self.assertEqual(result.out, "")

    def test_exit_finishes_session(self):
        shell = Shell()
        shell.execute("exit")
        self.assertTrue(shell.session.finished)

    def test_exit_with_arguments_is_error(self):
        shell = Shell()
        result = shell.execute("exit now")
        self.assertEqual(result.err, "exit: too many arguments")
        self.assertFalse(shell.session.finished)

    def test_empty_line_does_nothing(self):
        result = Shell().execute("   ")
        self.assertEqual((result.out, result.err), ("", ""))

    def test_run_and_emit_shows_prompt_and_output(self):
        collector = Collector()
        Shell().run_and_emit("ls a", collector)
        self.assertEqual(collector.items[0][0], INPUT)
        self.assertTrue(collector.items[0][1].endswith("$ ls a"))
        self.assertEqual(collector.items[1][0], OUT)

    def test_run_and_emit_marks_errors(self):
        collector = Collector()
        Shell().run_and_emit("nope", collector)
        self.assertEqual(collector.items[-1][0], ERR)


if __name__ == "__main__":
    unittest.main()
