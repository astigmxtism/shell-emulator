"""Общие типы: результат команды, ошибка команды, виды строк вывода."""
from dataclasses import dataclass

INPUT = "input"
OUT = "out"
ERR = "err"
INFO = "info"
DEBUG = "debug"


class CommandError(Exception):
    """Ошибка выполнения команды: неверные аргументы и подобное."""


@dataclass
class Result:
    """Результат выполнения команды: обычный вывод и сообщения об ошибках."""

    out: str = ""
    err: str = ""
