"""Виртуальная файловая система, целиком хранящаяся в памяти."""
import os
from dataclasses import dataclass, field

ROOT_PATH = "/"
SEPARATOR = "/"
CURRENT = "."
PARENT = ".."
DEFAULT_LABEL = "default"
DEFAULT_OWNER = "user"
DEFAULT_GROUP = "user"
DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"
DIR_SIZE = 4096
REASON_NOT_FOUND = "No such file or directory"
REASON_NOT_DIR = "Not a directory"

DEFAULT_TREE = {
    "home": {
        "user": {
            "notes.txt": "first line\nsecond line\nthird line\n",
            "todo.txt": "buy milk\nwrite report\ncall mom\n",
            "docs": {"readme.txt": "Default in-memory VFS.\n"},
        },
    },
    "etc": {"motd": "Welcome to the shell emulator!\n"},
    "tmp": {},
}


class VFSError(Exception):
    """Ошибка VFS: загрузка источника или поиск узла."""


@dataclass
class Node:
    """Узел дерева: каталог или файл с владельцем и группой."""

    name: str
    is_dir: bool = False
    content: bytes = b""
    owner: str = DEFAULT_OWNER
    group: str = DEFAULT_GROUP
    children: dict = field(default_factory=dict)

    def set_owner(self, owner, group):
        """Изменить владельца и/или группу (None - не менять)."""
        if owner:
            self.owner = owner
        if group:
            self.group = group

    def walk(self):
        """Обойти узел и всех его потомков."""
        yield self
        for name in sorted(self.children):
            yield from self.children[name].walk()

    @property
    def size(self):
        """Размер в байтах (для каталога - условное значение)."""
        return DIR_SIZE if self.is_dir else len(self.content)

    @property
    def mode(self):
        """Строка прав доступа в стиле ls -l."""
        return DIR_MODE if self.is_dir else FILE_MODE


def split_parts(path):
    """Разбить путь на непустые компоненты."""
    return [part for part in path.split(SEPARATOR) if part]


def normalize_path(cwd, path):
    """Получить абсолютный путь с учётом . и .. относительно cwd."""
    parts = [] if path.startswith(SEPARATOR) else split_parts(cwd)
    for part in split_parts(path):
        if part == PARENT:
            if parts:
                parts.pop()
        elif part != CURRENT:
            parts.append(part)
    return SEPARATOR + SEPARATOR.join(parts)


def build_tree(spec, name=""):
    """Построить каталог из словаря: значение-словарь - подкаталог."""
    node = Node(name, is_dir=True)
    for child_name, value in spec.items():
        if isinstance(value, dict):
            node.children[child_name] = build_tree(value, child_name)
        else:
            data = value.encode("utf-8")
            node.children[child_name] = Node(child_name, content=data)
    return node


class VirtualFS:
    """Дерево узлов в памяти с поиском по абсолютному пути."""

    def __init__(self, root, label=DEFAULT_LABEL):
        self.root = root
        self.label = label

    def lookup(self, path):
        """Найти узел по пути; при неудаче бросить VFSError."""
        node = self.root
        for part in split_parts(path):
            if not node.is_dir:
                raise VFSError(REASON_NOT_DIR)
            if part not in node.children:
                raise VFSError(REASON_NOT_FOUND)
            node = node.children[part]
        return node


def default_vfs():
    """Создать VFS по умолчанию, полностью в памяти."""
    return VirtualFS(build_tree(DEFAULT_TREE), DEFAULT_LABEL)


def fill_node(node, disk_path):
    """Рекурсивно прочитать каталог с диска в память (только чтение)."""
    for entry in sorted(os.listdir(disk_path)):
        full = os.path.join(disk_path, entry)
        if os.path.islink(full):
            continue
        if os.path.isdir(full):
            child = Node(entry, is_dir=True)
            fill_node(child, full)
        else:
            with open(full, "rb") as handle:
                child = Node(entry, content=handle.read())
        node.children[entry] = child


def load_directory(path):
    """Загрузить VFS из каталога на диске; при ошибке бросить VFSError."""
    if not os.path.exists(path):
        raise VFSError(f"VFS source '{path}' not found")
    if not os.path.isdir(path):
        raise VFSError(f"invalid VFS format: '{path}' is not a directory")
    root = Node("", is_dir=True)
    try:
        fill_node(root, path)
    except OSError as error:
        raise VFSError(f"cannot read VFS '{path}': {error.strerror}") from error
    label = os.path.basename(os.path.abspath(path)) or path
    return VirtualFS(root, label)
