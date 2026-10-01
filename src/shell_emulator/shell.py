"""Ядро эмулятора: состояние сеанса и выполнение строк ввода."""
from shell_emulator.commands import COMMANDS
from shell_emulator.common import CommandError, Result, ERR, INPUT, OUT
from shell_emulator.parser import parse_line

USER_NAME = "user"
DEFAULT_LABEL = "default"
ROOT_PATH = "/"


class Session:
    """Состояние сеанса: пользователь, текущий каталог, признак выхода."""

    def __init__(self, label=DEFAULT_LABEL):
        self.user = USER_NAME
        self.label = label
        self.cwd = ROOT_PATH
        self.finished = False

    def prompt(self):
        """Вернуть строку приглашения вида user@vfs:/path$ ."""
        return f"{self.user}@{self.label}:{self.cwd}$ "


class Shell:
    """Интерпретатор: разбирает строку и вызывает нужную команду."""

    def __init__(self, session=None):
        self.session = session or Session()

    def execute(self, line):
        """Выполнить одну строку; вернуть Result с выводом и ошибками."""
        parsed = parse_line(line)
        if parsed is None:
            return Result()
        handler = COMMANDS.get(parsed.name)
        if handler is None:
            return Result(err=f"{parsed.name}: command not found")
        try:
            return handler(self.session, parsed.args)
        except CommandError as error:
            return Result(err=str(error))

    def run_and_emit(self, line, emit):
        """Выполнить строку, показав ввод и вывод через функцию emit."""
        emit(self.session.prompt() + line, INPUT)
        result = self.execute(line)
        if result.out:
            emit(result.out, OUT)
        if result.err:
            emit(result.err, ERR)
        return result
