"""Тесты виртуальной файловой системы и сеанса."""
import os
import unittest

from fs_helpers import make_temp_dir, write_file
from shell_emulator.shell import Session
from shell_emulator.vfs import (
    VFSError, default_vfs, load_directory, normalize_path,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(REPO_ROOT, "examples", "vfs")


def make_disk_tree(test_case):
    """Создать на диске каталог с тремя уровнями вложенности."""
    base = make_temp_dir(test_case)
    os.makedirs(os.path.join(base, "a", "b"))
    write_file(base, "top.txt", "top\n")
    write_file(os.path.join(base, "a"), "mid.txt", "mid\n")
    write_file(os.path.join(base, "a", "b"), "low.txt", "low\n")
    return base


class NormalizePathTest(unittest.TestCase):
    """Нормализация путей."""

    def test_absolute_and_relative(self):
        self.assertEqual(normalize_path("/a", "/b/c"), "/b/c")
        self.assertEqual(normalize_path("/a", "b"), "/a/b")

    def test_dots(self):
        self.assertEqual(normalize_path("/a/b", ".."), "/a")
        self.assertEqual(normalize_path("/a/b", "./../c/."), "/a/c")

    def test_cannot_go_above_root(self):
        self.assertEqual(normalize_path("/", "../.."), "/")

    def test_extra_separators(self):
        self.assertEqual(normalize_path("/", "//a///b/"), "/a/b")


class DefaultVfsTest(unittest.TestCase):
    """VFS по умолчанию, создаваемая в памяти."""

    def test_has_directories_and_files(self):
        vfs = default_vfs()
        self.assertTrue(vfs.lookup("/home/user").is_dir)
        self.assertFalse(vfs.lookup("/home/user/notes.txt").is_dir)

    def test_missing_path_raises(self):
        with self.assertRaises(VFSError) as caught:
            default_vfs().lookup("/nope")
        self.assertEqual(str(caught.exception), "No such file or directory")

    def test_file_is_not_a_directory(self):
        with self.assertRaises(VFSError) as caught:
            default_vfs().lookup("/etc/motd/x")
        self.assertEqual(str(caught.exception), "Not a directory")


class LoadDirectoryTest(unittest.TestCase):
    """Загрузка VFS из каталога на диске."""

    def test_loads_nested_tree(self):
        vfs = load_directory(make_disk_tree(self))
        self.assertEqual(vfs.lookup("/a/b/low.txt").content, b"low\n")
        self.assertTrue(vfs.lookup("/a/b").is_dir)
        self.assertEqual(vfs.lookup("/top.txt").content, b"top\n")

    def test_label_is_directory_name(self):
        base = make_disk_tree(self)
        self.assertEqual(load_directory(base).label, os.path.basename(base))

    def test_missing_directory_raises(self):
        with self.assertRaises(VFSError) as caught:
            load_directory("no/such/dir")
        self.assertIn("not found", str(caught.exception))

    def test_file_instead_of_directory_raises(self):
        path = write_file(make_temp_dir(self), "f.txt", "x")
        with self.assertRaises(VFSError) as caught:
            load_directory(path)
        self.assertIn("invalid VFS format", str(caught.exception))

    def test_data_is_not_modified_on_disk(self):
        base = make_disk_tree(self)
        vfs = load_directory(base)
        vfs.lookup("/a").children.clear()
        self.assertTrue(os.path.isfile(os.path.join(base, "a", "mid.txt")))

    def test_binary_content_is_preserved(self):
        base = make_temp_dir(self)
        with open(os.path.join(base, "b.bin"), "wb") as handle:
            handle.write(bytes([0, 255, 10]))
        vfs = load_directory(base)
        self.assertEqual(vfs.lookup("/b.bin").content, bytes([0, 255, 10]))


class ExampleVfsTest(unittest.TestCase):
    """Примеры VFS из examples/vfs."""

    def test_minimal(self):
        vfs = load_directory(os.path.join(EXAMPLES, "minimal"))
        self.assertEqual(list(vfs.root.children), ["hello.txt"])

    def test_several_files(self):
        vfs = load_directory(os.path.join(EXAMPLES, "files"))
        self.assertEqual(len(vfs.root.children), 5)
        self.assertIn(".hidden", vfs.root.children)

    def test_three_or_more_levels(self):
        vfs = load_directory(os.path.join(EXAMPLES, "deep"))
        path = "/home/alice/projects/emulator/src/main.txt"
        self.assertFalse(vfs.lookup(path).is_dir)


class SessionTest(unittest.TestCase):
    """Состояние сеанса и приглашение."""

    def test_prompt_shows_vfs_name_and_directory(self):
        session = Session(default_vfs())
        self.assertEqual(session.prompt(), "user@default:/$ ")
        session.cwd = "/etc"
        self.assertEqual(session.prompt(), "user@default:/etc$ ")

    def test_label_comes_from_loaded_vfs(self):
        vfs = load_directory(os.path.join(EXAMPLES, "minimal"))
        self.assertEqual(Session(vfs).prompt(), "user@minimal:/$ ")


if __name__ == "__main__":
    unittest.main()
