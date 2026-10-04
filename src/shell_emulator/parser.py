"""Простой парсер: разделяет строку ввода на команду и аргументы."""
from dataclasses import dataclass


@dataclass
class ParsedLine:
    """Разобранная строка: имя команды и список аргументов."""

    name: str
    args: list


def parse_line(line):
    """Разделить строку по пробелам; для пустой строки вернуть None."""
    parts = line.split()
    if not parts:
        return None
    return ParsedLine(parts[0], parts[1:])
