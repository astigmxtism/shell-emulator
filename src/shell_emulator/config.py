"""Параметры запуска: командная строка и JSON-файл конфигурации."""
import argparse
import json
from dataclasses import dataclass, field
from typing import Optional

PARAM_NAMES = ("vfs_path", "script_path")
SOURCE_CLI = "command line"
SOURCE_FILE = "config file"
SOURCE_NONE = "not set"
NOT_SET = "<not set>"


class ConfigError(Exception):
    """Ошибка чтения или проверки конфигурационного файла."""


@dataclass
class Settings:
    """Итоговые параметры запуска и источник каждого значения."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None
    config_path: Optional[str] = None
    sources: dict = field(default_factory=dict)

    def debug_lines(self):
        """Сформировать отладочный вывод всех параметров запуска."""
        config = NOT_SET if self.config_path is None else self.config_path
        lines = [f"[debug] config_path = {config}"]
        for name in PARAM_NAMES:
            value = getattr(self, name)
            shown = NOT_SET if value is None else value
            lines.append(f"[debug] {name} = {shown} ({self.sources[name]})")
        return lines


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Shell emulator with a virtual file system.",
    )
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="path to the directory used as the VFS source",
    )
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="path to the startup script with emulator commands",
    )
    parser.add_argument(
        "--config", dest="config_path", metavar="PATH",
        help="path to the JSON configuration file",
    )
    return parser


def parse_args(argv=None):
    """Разобрать параметры командной строки."""
    return build_parser().parse_args(argv)


def validate_config(data, path):
    """Проверить содержимое конфигурации; вернуть словарь параметров."""
    if not isinstance(data, dict):
        raise ConfigError(f"'{path}': top-level JSON value must be an object")
    values = {}
    for name in PARAM_NAMES:
        value = data.get(name)
        if value is not None and not isinstance(value, str):
            raise ConfigError(f"'{path}': '{name}' must be a string")
        values[name] = value
    return values


def load_config_file(path):
    """Прочитать JSON-конфигурацию; при ошибке бросить ConfigError."""
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as error:
        raise ConfigError(f"cannot read '{path}': {error.strerror}") from error
    except ValueError as error:
        raise ConfigError(f"invalid JSON in '{path}': {error}") from error
    return validate_config(data, path)


def resolve_settings(args, file_values):
    """Объединить параметры: командная строка главнее файла."""
    settings = Settings(config_path=args.config_path)
    for name in PARAM_NAMES:
        cli_value = getattr(args, name)
        file_value = file_values.get(name)
        if cli_value is not None:
            value, source = cli_value, SOURCE_CLI
        elif file_value is not None:
            value, source = file_value, SOURCE_FILE
        else:
            value, source = None, SOURCE_NONE
        setattr(settings, name, value)
        settings.sources[name] = source
    return settings
