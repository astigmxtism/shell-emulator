"""Выполнение стартового скрипта с имитацией диалога с пользователем."""
from shell_emulator.common import ERR


class ScriptError(Exception):
    """Ошибка чтения файла стартового скрипта."""


def read_script(path):
    """Прочитать строки скрипта; при ошибке бросить ScriptError."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().splitlines()
    except OSError as error:
        message = f"cannot read script '{path}': {error.strerror}"
        raise ScriptError(message) from error
    except ValueError as error:
        message = f"script '{path}' is not a valid UTF-8 text file"
        raise ScriptError(message) from error


def run_script(shell, path, emit):
    """Выполнить команды по порядку; ошибочные строки пропускать."""
    try:
        lines = read_script(path)
    except ScriptError as error:
        emit(f"[script] error: {error}", ERR)
        return
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        result = shell.run_and_emit(line.strip(), emit)
        if result.err:
            emit(f"[script] line {number}: error, line skipped", ERR)
        if shell.session.finished:
            break
