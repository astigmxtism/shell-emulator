"""Запуск эмулятора: параметры, конфигурация, стартовый скрипт."""
from functools import partial

from shell_emulator.common import DEBUG, ERR
from shell_emulator.config import (
    ConfigError, load_config_file, parse_args, resolve_settings,
)
from shell_emulator.script import run_script
from shell_emulator.shell import Shell

WINDOW_TITLE = "Shell Emulator"


def window_title(shell):
    """Сформировать заголовок окна, содержащий имя VFS."""
    return f"{WINDOW_TITLE} - VFS: {shell.session.label}"


def read_file_values(args, problems):
    """Прочитать файл конфигурации; ошибку добавить в problems."""
    if args.config_path is None:
        return {}
    try:
        return load_config_file(args.config_path)
    except ConfigError as error:
        problems.append((f"[config] error: {error}", ERR))
        return {}


def prepare(argv=None):
    """Собрать настройки, оболочку и сообщения, показываемые при запуске."""
    args = parse_args(argv)
    problems = []
    file_values = read_file_values(args, problems)
    settings = resolve_settings(args, file_values)
    notices = [(line, DEBUG) for line in settings.debug_lines()]
    return Shell(), settings, notices + problems


def run_startup(shell, settings, notices, emit):
    """Показать отладочный вывод и выполнить стартовый скрипт."""
    for text, kind in notices:
        emit(text, kind)
    if settings.script_path is not None:
        run_script(shell, settings.script_path, emit)


def main(argv=None):
    """Точка входа: разобрать параметры и показать графическое окно."""
    from shell_emulator.gui import ShellWindow
    shell, settings, notices = prepare(argv)
    startup = partial(run_startup, shell, settings, notices)
    ShellWindow(shell, window_title(shell)).run(startup)
