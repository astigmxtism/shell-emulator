"""Запуск эмулятора: создание оболочки и окна."""
from shell_emulator.common import INFO
from shell_emulator.gui import ShellWindow
from shell_emulator.shell import Shell

WINDOW_TITLE = "Shell Emulator"
WELCOME = "Shell emulator prototype: ls, cd, exit."


def window_title(shell):
    """Сформировать заголовок окна, содержащий имя VFS."""
    return f"{WINDOW_TITLE} - VFS: {shell.session.label}"


def show_welcome(emit):
    """Вывести приветствие при запуске."""
    emit(WELCOME, INFO)


def main():
    """Создать оболочку и показать графическое окно."""
    shell = Shell()
    ShellWindow(shell, window_title(shell)).run(show_welcome)
