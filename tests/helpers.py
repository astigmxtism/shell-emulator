"""Вспомогательные средства для тестов."""


class Collector:
    """Собирает вывод эмулятора в список пар (вид, текст)."""

    def __init__(self):
        self.items = []

    def __call__(self, text, kind):
        """Запомнить строку вывода."""
        self.items.append((kind, text))

    def texts(self, kind=None):
        """Вернуть тексты всех строк или только заданного вида."""
        return [text for item, text in self.items if kind in (None, item)]
