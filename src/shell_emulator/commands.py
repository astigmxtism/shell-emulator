"""Реализации команд эмулятора (на этапе 1 ls и cd - заглушки)."""
from shell_emulator.common import CommandError, Result


def stub_output(name, args):
    """Сформировать вывод заглушки: имя команды и её аргументы."""
    return Result(out=f"{name}: args = {args}")


def cmd_ls(session, args):
    """Заглушка ls: печатает своё имя и аргументы."""
    return stub_output("ls", args)


def cmd_cd(session, args):
    """Заглушка cd: печатает своё имя и аргументы."""
    return stub_output("cd", args)


def cmd_exit(session, args):
    """exit: завершить работу эмулятора."""
    if args:
        raise CommandError("exit: too many arguments")
    session.finished = True
    return Result()


COMMANDS = {
    "cd": cmd_cd,
    "exit": cmd_exit,
    "ls": cmd_ls,
}
