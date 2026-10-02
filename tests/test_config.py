"""Тесты чтения параметров: командная строка, JSON, приоритеты."""
import unittest

from fs_helpers import make_temp_dir, write_file
from shell_emulator.config import (
    ConfigError, SOURCE_CLI, SOURCE_FILE, SOURCE_NONE,
    load_config_file, parse_args, resolve_settings,
)


class ParseArgsTest(unittest.TestCase):
    """Параметры командной строки."""

    def test_all_parameters(self):
        args = parse_args(["--vfs", "a", "--script", "b", "--config", "c"])
        self.assertEqual(args.vfs_path, "a")
        self.assertEqual(args.script_path, "b")
        self.assertEqual(args.config_path, "c")

    def test_defaults_are_empty(self):
        args = parse_args([])
        self.assertIsNone(args.vfs_path)
        self.assertIsNone(args.script_path)
        self.assertIsNone(args.config_path)


class LoadConfigTest(unittest.TestCase):
    """Чтение JSON-файла конфигурации."""

    def test_reads_both_values(self):
        folder = make_temp_dir(self)
        path = write_file(
            folder, "c.json", '{"vfs_path": "v", "script_path": "s"}'
        )
        values = load_config_file(path)
        self.assertEqual(values, {"vfs_path": "v", "script_path": "s"})

    def test_missing_keys_are_none(self):
        path = write_file(make_temp_dir(self), "c.json", "{}")
        values = load_config_file(path)
        self.assertEqual(values, {"vfs_path": None, "script_path": None})

    def test_missing_file_raises(self):
        with self.assertRaises(ConfigError):
            load_config_file("no/such/config.json")

    def test_invalid_json_raises(self):
        path = write_file(make_temp_dir(self), "c.json", "{ not json")
        with self.assertRaises(ConfigError):
            load_config_file(path)

    def test_non_object_raises(self):
        path = write_file(make_temp_dir(self), "c.json", "[1, 2]")
        with self.assertRaises(ConfigError):
            load_config_file(path)

    def test_wrong_type_raises(self):
        path = write_file(make_temp_dir(self), "c.json", '{"vfs_path": 5}')
        with self.assertRaises(ConfigError):
            load_config_file(path)


class ResolveSettingsTest(unittest.TestCase):
    """Приоритет: командная строка главнее файла."""

    def test_cli_overrides_file(self):
        args = parse_args(["--vfs", "cli_vfs"])
        file_values = {"vfs_path": "file_vfs", "script_path": "file_script"}
        settings = resolve_settings(args, file_values)
        self.assertEqual(settings.vfs_path, "cli_vfs")
        self.assertEqual(settings.script_path, "file_script")
        self.assertEqual(settings.sources["vfs_path"], SOURCE_CLI)
        self.assertEqual(settings.sources["script_path"], SOURCE_FILE)

    def test_unset_values(self):
        settings = resolve_settings(parse_args([]), {})
        self.assertIsNone(settings.vfs_path)
        self.assertEqual(settings.sources["vfs_path"], SOURCE_NONE)

    def test_debug_lines_list_all_parameters(self):
        args = parse_args(["--config", "c.json", "--script", "s.emu"])
        lines = resolve_settings(args, {}).debug_lines()
        text = "\n".join(lines)
        for name in ("config_path", "vfs_path", "script_path"):
            self.assertIn(name, text)
        self.assertIn("s.emu (command line)", text)


if __name__ == "__main__":
    unittest.main()
