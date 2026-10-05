"""Реализации команд эмулятора: ls, cd, tac, cal, chown, exit."""
import calendar
import datetime
import re

from shell_emulator.common import CommandError, Result
from shell_emulator.vfs import (
    CURRENT, PARENT, ROOT_PATH, VFSError, normalize_path,
)

OPTION_PREFIX = "-"
LONG_PREFIX = "--"
HIDDEN_PREFIX = "."
NAME_WIDTH = 8
SIZE_WIDTH = 6
ALL_FLAG = "a"
LONG_FLAG = "l"
LS_OPTIONS = "al"
NO_OPTIONS = ""
MAX_CAL_OPERANDS = 2
MIN_MONTH, MAX_MONTH = 1, 12
MIN_YEAR, MAX_YEAR = 1, 9999
GROUP_SEPARATOR = ":"
RECURSIVE_FLAG = "R"
CHOWN_OPTIONS = "R"
NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


def is_option(token):
    """Проверить, что токен похож на опцию (-x), а не на операнд."""
    return token.startswith(OPTION_PREFIX) and token != OPTION_PREFIX


def check_flags(name, letters, allowed):
    """Проверить буквы короткой опции; вернуть их как множество."""
    for letter in letters:
        if letter not in allowed:
            raise CommandError(f"{name}: invalid option -- '{letter}'")
    return set(letters)


def split_options(name, args, allowed):
    """Отделить опции от операндов; вернуть (множество опций, операнды)."""
    flags, operands = set(), []
    for token in args:
        if not is_option(token):
            operands.append(token)
        elif token.startswith(LONG_PREFIX):
            raise CommandError(f"{name}: unrecognized option '{token}'")
        else:
            flags.update(check_flags(name, token[1:], allowed))
    return flags, operands


def find_node(session, operand):
    """Найти узел по операнду; вернуть (абсолютный путь, узел)."""
    path = normalize_path(session.cwd, operand)
    return path, session.vfs.lookup(path)


def sort_key(name):
    """Ключ сортировки имён: без учёта регистра, затем точный."""
    return (name.lower(), name)


def cmd_exit(session, args):
    """exit: завершить работу эмулятора."""
    if args:
        raise CommandError("exit: too many arguments")
    session.finished = True
    return Result()


def long_line(name, node):
    """Строка подробного списка (ls -l): права, владелец, размер, имя."""
    owner = f"{node.owner:<{NAME_WIDTH}}"
    group = f"{node.group:<{NAME_WIDTH}}"
    size = f"{node.size:>{SIZE_WIDTH}}"
    return f"{node.mode} {owner} {group} {size} {name}"


def render_entries(entries, flags):
    """Оформить список пар (имя, узел) в коротком или длинном виде."""
    if LONG_FLAG in flags:
        return "\n".join(long_line(name, node) for name, node in entries)
    return "  ".join(name for name, _ in entries)


def list_directory(session, path, node, flags):
    """Получить записи каталога; скрытые и . .. - только с опцией -a."""
    entries = []
    show_all = ALL_FLAG in flags
    if show_all:
        parent = session.vfs.lookup(normalize_path(path, PARENT))
        entries += [(CURRENT, node), (PARENT, parent)]
    for name in sorted(node.children, key=sort_key):
        if show_all or not name.startswith(HIDDEN_PREFIX):
            entries.append((name, node.children[name]))
    return entries


def collect_targets(session, operands):
    """Разделить операнды ls на файлы, каталоги и сообщения об ошибках."""
    files, directories, errors = [], [], []
    for operand in operands:
        try:
            path, node = find_node(session, operand)
        except VFSError as error:
            errors.append(f"ls: cannot access '{operand}': {error}")
            continue
        if node.is_dir:
            directories.append((operand, path, node))
        else:
            files.append((operand, node))
    return files, directories, errors


def cmd_ls(session, args):
    """ls [-a] [-l] [ПУТЬ...]: показать содержимое каталогов VFS."""
    flags, operands = split_options("ls", args, LS_OPTIONS)
    files, directories, errors = collect_targets(
        session, operands or [CURRENT]
    )
    blocks = []
    if files:
        blocks.append(render_entries(files, flags))
    titled = bool(operands[1:])
    for operand, path, node in directories:
        entries = list_directory(session, path, node, flags)
        body = render_entries(entries, flags)
        blocks.append(f"{operand}:\n{body}".rstrip() if titled else body)
    return Result(out="\n\n".join(blocks), err="\n".join(errors))


def cmd_cd(session, args):
    """cd [КАТАЛОГ]: сменить текущий каталог (без аргумента - корень)."""
    if args[1:]:
        raise CommandError("cd: too many arguments")
    target = args[0] if args else ROOT_PATH
    try:
        path, node = find_node(session, target)
    except VFSError as error:
        raise CommandError(f"cd: {target}: {error}") from error
    if not node.is_dir:
        raise CommandError(f"cd: {target}: Not a directory")
    session.cwd = path
    return Result()


def read_text(session, name, operand):
    """Прочитать файл VFS как текст UTF-8 (ошибки - CommandError)."""
    try:
        _, node = find_node(session, operand)
    except VFSError as error:
        raise CommandError(f"{name}: {operand}: {error}") from error
    if node.is_dir:
        raise CommandError(f"{name}: {operand}: Is a directory")
    return node.content.decode("utf-8", errors="replace")


def cmd_tac(session, args):
    """tac ФАЙЛ...: вывести строки файлов в обратном порядке."""
    _, operands = split_options("tac", args, NO_OPTIONS)
    if not operands:
        raise CommandError("tac: missing file operand")
    lines, errors = [], []
    for operand in operands:
        try:
            text = read_text(session, "tac", operand)
        except CommandError as error:
            errors.append(str(error))
            continue
        lines += reversed(text.splitlines())
    return Result(out="\n".join(lines), err="\n".join(errors))


def parse_number(label, text, low, high):
    """Разобрать целое из аргумента cal и проверить диапазон."""
    try:
        value = int(text)
    except ValueError as error:
        raise CommandError(f"cal: invalid {label} '{text}'") from error
    if not low <= value <= high:
        raise CommandError(f"cal: illegal {label} value: use {low}-{high}")
    return value


def parse_cal_operands(operands, today):
    """Вернуть (месяц, год, весь_год) по операндам cal."""
    if not operands:
        return today.month, today.year, False
    *month_part, year_text = operands
    year = parse_number("year", year_text, MIN_YEAR, MAX_YEAR)
    if not month_part:
        return today.month, year, True
    month = parse_number("month", month_part[0], MIN_MONTH, MAX_MONTH)
    return month, year, False


def cmd_cal(session, args):
    """cal [[МЕСЯЦ] ГОД]: показать календарь месяца или года."""
    _, operands = split_options("cal", args, NO_OPTIONS)
    if operands[MAX_CAL_OPERANDS:]:
        raise CommandError("cal: too many arguments")
    month, year, whole = parse_cal_operands(operands, datetime.date.today())
    text_calendar = calendar.TextCalendar(calendar.SUNDAY)
    if whole:
        text = text_calendar.formatyear(year)
    else:
        text = text_calendar.formatmonth(year, month)
    return Result(out="\n".join(line.rstrip() for line in text.splitlines()))


def check_name(kind, name, spec):
    """Проверить имя пользователя или группы из аргумента chown."""
    if name and not NAME_PATTERN.match(name):
        raise CommandError(f"chown: invalid {kind}: '{spec}'")


def parse_owner_spec(spec):
    """Разобрать ВЛАДЕЛЕЦ[:ГРУППА]; вернуть (владелец, группа) или None."""
    owner, separator, group = spec.partition(GROUP_SEPARATOR)
    check_name("user", owner, spec)
    check_name("group", group, spec)
    if not owner and not group:
        raise CommandError(f"chown: invalid user: '{spec}'")
    if separator and not group:
        group = owner
    return owner or None, group or None


def cmd_chown(session, args):
    """chown [-R] ВЛАДЕЛЕЦ[:ГРУППА] ФАЙЛ...: сменить владельца в памяти."""
    flags, operands = split_options("chown", args, CHOWN_OPTIONS)
    if not operands:
        raise CommandError("chown: missing operand")
    spec, *targets = operands
    if not targets:
        raise CommandError(f"chown: missing operand after '{spec}'")
    owner, group = parse_owner_spec(spec)
    errors = []
    for operand in targets:
        try:
            _, node = find_node(session, operand)
        except VFSError as error:
            errors.append(f"chown: cannot access '{operand}': {error}")
            continue
        nodes = node.walk() if RECURSIVE_FLAG in flags else [node]
        for item in nodes:
            item.set_owner(owner, group)
    return Result(err="\n".join(errors))


COMMANDS = {
    "cal": cmd_cal,
    "cd": cmd_cd,
    "chown": cmd_chown,
    "exit": cmd_exit,
    "ls": cmd_ls,
    "tac": cmd_tac,
}
