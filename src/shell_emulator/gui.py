"""Графический интерфейс эмулятора на tkinter."""
import tkinter as tk
from tkinter import scrolledtext

from shell_emulator.common import DEBUG, ERR, INFO, INPUT, OUT

BG_COLOR = "#1e1e1e"
FG_COLOR = "#d4d4d4"
FONT = "TkFixedFont"
WINDOW_SIZE = "860x520"
START_DELAY_MS = 100
TAG_COLORS = {
    INPUT: "#ffffff",
    OUT: FG_COLOR,
    ERR: "#f48771",
    INFO: "#4fc1ff",
    DEBUG: "#9e9e9e",
}


class ShellWindow:
    """Окно эмулятора: область вывода и строка ввода с приглашением."""

    def __init__(self, shell, title):
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(WINDOW_SIZE)
        self.output = self._build_output()
        self.prompt_var = tk.StringVar()
        self.entry = self._build_input()
        self._refresh_prompt()

    def _build_output(self):
        """Создать прокручиваемую область вывода с цветными тегами."""
        output = scrolledtext.ScrolledText(
            self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT,
            state=tk.DISABLED, wrap=tk.WORD,
        )
        output.pack(fill=tk.BOTH, expand=True)
        for kind, color in TAG_COLORS.items():
            output.tag_configure(kind, foreground=color)
        return output

    def _build_input(self):
        """Создать строку ввода с меткой приглашения слева."""
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill=tk.X)
        label = tk.Label(
            frame, textvariable=self.prompt_var, bg=BG_COLOR,
            fg=TAG_COLORS[INFO], font=FONT,
        )
        label.pack(side=tk.LEFT)
        entry = tk.Entry(
            frame, bg=BG_COLOR, fg=FG_COLOR, font=FONT,
            insertbackground=FG_COLOR, relief=tk.FLAT,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self._on_submit)
        entry.focus_set()
        return entry

    def emit(self, text, kind=OUT):
        """Добавить строку в область вывода с цветом по её виду."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", kind)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)
        self.root.update_idletasks()

    def _refresh_prompt(self):
        """Обновить текст приглашения (он зависит от текущего каталога)."""
        self.prompt_var.set(self.shell.session.prompt())

    def _close_if_finished(self):
        """Закрыть окно, если команда exit завершила сеанс."""
        if self.shell.session.finished:
            self.root.destroy()

    def _on_submit(self, _event):
        """Обработать нажатие Enter: выполнить введённую строку."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.shell.run_and_emit(line, self.emit)
        self._refresh_prompt()
        self._close_if_finished()

    def _startup(self, startup):
        """Выполнить стартовые действия, затем обновить окно."""
        startup(self.emit)
        self._refresh_prompt()
        self._close_if_finished()

    def run(self, startup=None):
        """Запустить главный цикл; startup(emit) вызывается после показа."""
        if startup is not None:
            self.root.after(START_DELAY_MS, lambda: self._startup(startup))
        self.root.mainloop()
