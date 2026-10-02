"""Создание временных файлов для тестов."""
import os
import tempfile


def make_temp_dir(test_case):
    """Создать временный каталог, удаляемый после теста."""
    holder = tempfile.TemporaryDirectory()
    test_case.addCleanup(holder.cleanup)
    return holder.name


def write_file(directory, name, text):
    """Записать текстовый файл и вернуть его полный путь."""
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path
