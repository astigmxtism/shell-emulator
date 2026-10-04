"""Тесты команд этапа 4: ls, cd, tac, cal."""
import datetime
import os
import unittest

from shell_emulator.commands import parse_cal_operands
from shell_emulator.common import CommandError
from shell_emulator.shell import Shell
from shell_emulator.vfs import load_directory

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP = os.path.join(REPO_ROOT, "examples", "vfs", "deep")
FILES = os.path.join(REPO_ROOT, "examples", "vfs", "files")

MARCH_2024 = """\
     March 2024
Su Mo Tu We Th Fr Sa
                1  2
 3  4  5  6  7  8  9
10 11 12 13 14 15 16
17 18 19 20 21 22 23
24 25 26 27 28 29 30
31"""


def deep_shell():
    """Оболочка с VFS из examples/vfs/deep."""
    return Shell(load_directory(DEEP))


def files_shell():
    """Оболочка с VFS из examples/vfs/files."""
    return Shell(load_directory(FILES))


class LsTest(unittest.TestCase):
    """Команда ls."""

    def test_lists_visible_entries(self):
        result = deep_shell().execute("ls")
        self.assertEqual(result.out, "docs  etc  home  var")

    def test_hidden_files_need_dash_a(self):
        shell = files_shell()
        self.assertNotIn(".hidden", shell.execute("ls").out)
        result = shell.execute("ls -a")
        self.assertEqual(result.out.split("  ")[:2], [".", ".."])
        self.assertIn(".hidden", result.out)

    def test_long_format(self):
        result = files_shell().execute("ls -l /notes.txt")
        self.assertEqual(
            result.out, "-rw-r--r-- user     user         39 /notes.txt"
        )

    def test_long_format_for_directory(self):
        result = deep_shell().execute("ls -l /etc")
        self.assertEqual(
            result.out, "drwxr-xr-x user     user       4096 app"
        )

    def test_combined_flags(self):
        result = deep_shell().execute("ls -la /etc")
        self.assertEqual(len(result.out.splitlines()), 3)

    def test_several_paths_get_headers(self):
        result = deep_shell().execute("ls /home/alice /etc")
        self.assertEqual(
            result.out, "/home/alice:\nmusic  projects\n\n/etc:\napp"
        )

    def test_file_and_directory_operands(self):
        result = deep_shell().execute("ls /docs/russian.txt /etc")
        self.assertEqual(result.out, "/docs/russian.txt\n\n/etc:\napp")

    def test_missing_path_is_error_but_others_listed(self):
        result = deep_shell().execute("ls /nope /etc")
        self.assertEqual(
            result.err, "ls: cannot access '/nope': No such file or directory"
        )
        self.assertIn("app", result.out)

    def test_invalid_option(self):
        result = deep_shell().execute("ls -q")
        self.assertEqual(result.err, "ls: invalid option -- 'q'")

    def test_long_option_is_unrecognized(self):
        result = deep_shell().execute("ls --color")
        self.assertEqual(result.err, "ls: unrecognized option '--color'")

    def test_empty_directory_prints_nothing(self):
        shell = Shell()
        self.assertEqual(shell.execute("ls /tmp").out, "")

    def test_relative_path_uses_current_directory(self):
        shell = deep_shell()
        shell.execute("cd /home")
        self.assertEqual(shell.execute("ls alice").out, "music  projects")


class CdTest(unittest.TestCase):
    """Команда cd."""

    def test_absolute_and_relative(self):
        shell = deep_shell()
        shell.execute("cd /home/alice")
        shell.execute("cd projects/emulator")
        expected = "/home/alice/projects/emulator"
        self.assertEqual(shell.session.cwd, expected)

    def test_no_argument_goes_to_root(self):
        shell = Shell()
        shell.execute("cd /etc")
        shell.execute("cd")
        self.assertEqual(shell.session.cwd, "/")

    def test_parent_directory(self):
        shell = deep_shell()
        shell.execute("cd /home/alice/projects")
        shell.execute("cd ../..")
        self.assertEqual(shell.session.cwd, "/home")

    def test_missing_directory(self):
        result = deep_shell().execute("cd /nope")
        self.assertEqual(result.err, "cd: /nope: No such file or directory")

    def test_file_is_not_a_directory(self):
        result = deep_shell().execute("cd /docs/russian.txt")
        self.assertEqual(result.err, "cd: /docs/russian.txt: Not a directory")

    def test_too_many_arguments(self):
        result = deep_shell().execute("cd a b")
        self.assertEqual(result.err, "cd: too many arguments")

    def test_failed_cd_keeps_directory(self):
        shell = deep_shell()
        shell.execute("cd /nope")
        self.assertEqual(shell.session.cwd, "/")



class TacTest(unittest.TestCase):
    """Команда tac."""

    def test_reverses_lines(self):
        result = deep_shell().execute("tac /var/log/app.log")
        self.assertEqual(result.out, "stopped\nrunning\nstarted")

    def test_unicode_text(self):
        result = deep_shell().execute("tac /docs/russian.txt")
        self.assertEqual(
            result.out, "третья строка\nвторая строка\nпервая строка"
        )

    def test_several_files(self):
        result = deep_shell().execute("tac /etc/app/app.conf /var/log/app.log")
        self.assertEqual(
            result.out, "level=3\nmode=demo\nstopped\nrunning\nstarted"
        )

    def test_directory_and_missing_file_errors(self):
        result = deep_shell().execute("tac /docs /nope")
        self.assertIn("tac: /docs: Is a directory", result.err)
        self.assertIn("tac: /nope: No such file or directory", result.err)

    def test_missing_operand(self):
        self.assertEqual(
            deep_shell().execute("tac").err, "tac: missing file operand"
        )

    def test_options_are_rejected(self):
        result = deep_shell().execute("tac -x /var/log/app.log")
        self.assertEqual(result.err, "tac: invalid option -- 'x'")


class CalTest(unittest.TestCase):
    """Команда cal."""

    def test_month_and_year(self):
        self.assertEqual(Shell().execute("cal 3 2024").out, MARCH_2024)

    def test_single_argument_is_whole_year(self):
        out = Shell().execute("cal 2024").out
        self.assertIn("2024", out.splitlines()[0])
        for month in ("January", "June", "December"):
            self.assertIn(month, out)

    def test_current_month_without_arguments(self):
        today = datetime.date.today()
        out = Shell().execute("cal").out
        self.assertIn(str(today.year), out.splitlines()[0])

    def test_illegal_month(self):
        result = Shell().execute("cal 13 2024")
        self.assertEqual(result.err, "cal: illegal month value: use 1-12")

    def test_illegal_year(self):
        result = Shell().execute("cal 5 0")
        self.assertEqual(result.err, "cal: illegal year value: use 1-9999")

    def test_not_a_number(self):
        self.assertEqual(
            Shell().execute("cal abc").err, "cal: invalid year 'abc'"
        )

    def test_too_many_arguments(self):
        self.assertEqual(
            Shell().execute("cal 1 2 3").err, "cal: too many arguments"
        )

    def test_invalid_option(self):
        self.assertEqual(
            Shell().execute("cal -z").err, "cal: invalid option -- 'z'"
        )

    def test_parse_operands(self):
        today = datetime.date(2030, 7, 4)
        self.assertEqual(parse_cal_operands([], today), (7, 2030, False))
        self.assertEqual(parse_cal_operands(["1999"], today),
                         (7, 1999, True))
        self.assertEqual(parse_cal_operands(["2", "2000"], today),
                         (2, 2000, False))

    def test_parse_operands_reports_errors(self):
        today = datetime.date(2030, 7, 4)
        with self.assertRaises(CommandError):
            parse_cal_operands(["0", "2000"], today)


if __name__ == "__main__":
    unittest.main()
