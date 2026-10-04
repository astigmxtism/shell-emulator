"""Тесты парсера строки ввода."""
import unittest

from shell_emulator.parser import parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки функции parse_line."""

    def test_splits_command_and_args(self):
        parsed = parse_line("ls -l /home")
        self.assertEqual(parsed.name, "ls")
        self.assertEqual(parsed.args, ["-l", "/home"])

    def test_command_without_args(self):
        parsed = parse_line("exit")
        self.assertEqual(parsed.name, "exit")
        self.assertEqual(parsed.args, [])

    def test_extra_spaces_are_ignored(self):
        parsed = parse_line("   cd    a    b  ")
        self.assertEqual(parsed.name, "cd")
        self.assertEqual(parsed.args, ["a", "b"])

    def test_empty_line_returns_none(self):
        self.assertIsNone(parse_line(""))
        self.assertIsNone(parse_line("    "))


if __name__ == "__main__":
    unittest.main()
