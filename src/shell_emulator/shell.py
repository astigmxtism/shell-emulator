"""Ядро эмулятора: состояние сеанса и выполнение строк ввода."""
from shell_emulator.commands import COMMANDS
from shell_emulator.common import CommandError, Result, ERR, INPUT, OUT
from shell_emulator.parser import parse_line
from shell_emulator.vfs import ROOT_PATH, default_vfs

USER_NAME = "user"


class Session:
    """Состояние сеанса: VFS, пользователь, текущий каталог, выход."""

    def __init__(self, vfs):
        self.vfs = vfs
        self.user = USER_NAME
        self.cwd = ROOT_PATH
        self.finished = False

    @property
    def label(self):
        """Имя VFS, показываемое в приглашении и заголовке окна."""
        return self.vfs.label

    def prompt(self):
        """Вернуть строку приглашения вида user@vfs:/path$ ."""
        return f"{self.user}@{self.label}:{self.cwd}$ "


class Shell:
    """Интерпретатор: разбирает строку и вызывает нужную команду."""

    def __init__(self, vfs=None):
        self.session = Session(vfs or default_vfs())

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
