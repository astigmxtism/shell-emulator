"""Тесты команды chown этапа 5."""
import os
import unittest

from fs_helpers import make_temp_dir, write_file
from shell_emulator.commands import parse_owner_spec
from shell_emulator.common import CommandError
from shell_emulator.shell import Shell
from shell_emulator.vfs import load_directory


def owner_of(shell, path):
    """Вернуть строку владелец:группа для узла VFS."""
    node = shell.session.vfs.lookup(path)
    return f"{node.owner}:{node.group}"


class ParseOwnerSpecTest(unittest.TestCase):
    """Разбор аргумента ВЛАДЕЛЕЦ[:ГРУППА]."""

    def test_owner_only(self):
        self.assertEqual(parse_owner_spec("bob"), ("bob", None))

    def test_owner_and_group(self):
        self.assertEqual(parse_owner_spec("bob:dev"), ("bob", "dev"))

    def test_group_only(self):
        self.assertEqual(parse_owner_spec(":dev"), (None, "dev"))

    def test_trailing_colon_uses_owner_as_group(self):
        self.assertEqual(parse_owner_spec("bob:"), ("bob", "bob"))

    def test_invalid_specs(self):
        for spec in ("", ":", "1bad", "bob:9x", "a b"):
            with self.assertRaises(CommandError):
                parse_owner_spec(spec)


class ChownTest(unittest.TestCase):
    """Выполнение chown в оболочке."""

    def test_changes_owner(self):
        shell = Shell()
        shell.execute("chown root /home/user/notes.txt")
        self.assertEqual(owner_of(shell, "/home/user/notes.txt"), "root:user")

    def test_changes_group_only(self):
        shell = Shell()
        shell.execute("chown :staff /home/user/notes.txt")
        self.assertEqual(owner_of(shell, "/home/user/notes.txt"), "user:staff")

    def test_changes_owner_and_group(self):
        shell = Shell()
        shell.execute("chown bob:wheel /home/user/notes.txt")
        self.assertEqual(owner_of(shell, "/home/user/notes.txt"), "bob:wheel")

    def test_visible_in_long_listing(self):
        shell = Shell()
        shell.execute("chown bob:wheel /home/user/notes.txt")
        out = shell.execute("ls -l /home/user/notes.txt").out
        self.assertIn("bob      wheel", out)

    def test_relative_path_and_several_files(self):
        shell = Shell()
        shell.execute("chown bob /home/user/notes.txt /home/user/todo.txt")
        self.assertEqual(owner_of(shell, "/home/user/notes.txt"), "bob:user")
        self.assertEqual(owner_of(shell, "/home/user/todo.txt"), "bob:user")

    def test_directory_without_recursion(self):
        shell = Shell()
        shell.execute("chown bob /home/user/docs")
        self.assertEqual(owner_of(shell, "/home/user/docs"), "bob:user")
        self.assertEqual(
            owner_of(shell, "/home/user/docs/readme.txt"), "user:user"
        )

    def test_command_prints_nothing_on_success(self):
        result = Shell().execute("chown bob /home/user/notes.txt")
        self.assertEqual((result.out, result.err), ("", ""))

    def test_recursive(self):
        shell = Shell()
        shell.execute("chown -R bob /home/user/docs")
        self.assertEqual(owner_of(shell, "/home/user/docs"), "bob:user")
        self.assertEqual(
            owner_of(shell, "/home/user/docs/readme.txt"), "bob:user"
        )



class ChownErrorsTest(unittest.TestCase):
    """Ошибки chown."""

    def test_missing_operand(self):
        self.assertEqual(
            Shell().execute("chown").err, "chown: missing operand"
        )

    def test_missing_file_operand(self):
        self.assertEqual(
            Shell().execute("chown root").err,
            "chown: missing operand after 'root'",
        )

    def test_invalid_user(self):
        result = Shell().execute("chown 1bad /home/user/notes.txt")
        self.assertEqual(result.err, "chown: invalid user: '1bad'")

    def test_invalid_group(self):
        result = Shell().execute("chown root:9g /home/user/notes.txt")
        self.assertEqual(result.err, "chown: invalid group: 'root:9g'")

    def test_missing_file_does_not_stop_other_files(self):
        shell = Shell()
        result = shell.execute("chown bob missing.txt /home/user/notes.txt")
        self.assertEqual(
            result.err,
            "chown: cannot access 'missing.txt': No such file or directory",
        )
        self.assertEqual(owner_of(shell, "/home/user/notes.txt"), "bob:user")

    def test_invalid_option(self):
        result = Shell().execute("chown -x bob /home/user/notes.txt")
        self.assertEqual(result.err, "chown: invalid option -- 'x'")


class ChownInMemoryTest(unittest.TestCase):
    """Изменения VFS не затрагивают исходный каталог на диске."""

    def test_disk_is_not_modified(self):
        base = make_temp_dir(self)
        path = write_file(base, "f.txt", "data\n")
        before = os.stat(path)
        shell = Shell(load_directory(base))
        shell.execute("chown -R bob:dev /")
        self.assertEqual(owner_of(shell, "/f.txt"), "bob:dev")
        after = os.stat(path)
        self.assertEqual((before.st_uid, before.st_gid),
                         (after.st_uid, after.st_gid))
        self.assertEqual(os.listdir(base), ["f.txt"])


if __name__ == "__main__":
    unittest.main()
