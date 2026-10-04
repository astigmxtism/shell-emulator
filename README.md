# Shell Emulator

Эмулятор оболочки UNIX-подобной ОС с графическим интерфейсом (GUI) на
Python. Практическая работа, вариант №2.

## 1. Общее описание

- язык: Python 3.9+, только стандартная библиотека;
- GUI: `tkinter` (входит в стандартную поставку Python; в некоторых
  дистрибутивах Linux ставится отдельно: `sudo apt install python3-tk`);
- заголовок окна содержит имя VFS: `Shell Emulator - VFS: <имя>`;
- приглашение как в UNIX-оболочке: `user@<имя VFS>:<каталог>$`;
- ввод разбирается простым парсером: команда и аргументы разделяются
  пробелами; об ошибках (неизвестная команда, неверные аргументы)
  сообщается в окне красным цветом.
- эмулятор настраивается параметрами командной строки и JSON-файлом, а
  также умеет выполнять стартовый скрипт, имитируя диалог с пользователем.

## 2. Описание всех функций и настроек

### 2.1. Интерфейс

Окно состоит из области вывода (ввод пользователя, результаты и ошибки
разного цвета) и строки ввода с приглашением. Команда выполняется по
Enter. Команда `exit` закрывает окно.

### 2.2. Параметры командной строки

| Параметр        | Описание                                           |
|-----------------|----------------------------------------------------|
| `--vfs PATH`    | путь к физическому расположению VFS                |
| `--script PATH` | путь к стартовому скрипту                          |
| `--config PATH` | путь к конфигурационному файлу                     |

При запуске в окно выводится отладочная информация: значение каждого
параметра и его источник (`command line`, `config file`, `not set`).

### 2.3. Конфигурационный файл

JSON-объект с двумя необязательными ключами:

```json
{
  "vfs_path": "examples/vfs/files",
  "script_path": "examples/scripts/stage2_demo.emu"
}
```

**Приоритет:** значение из командной строки главнее значения из файла.
Ошибка чтения конфигурации (нет файла, неверный JSON, значение не
строка) показывается в окне как `[config] error: ...`; запуск при этом
продолжается. Относительные пути считаются от текущего каталога.

### 2.4. Стартовый скрипт

Текстовый файл: одна команда эмулятора в строке. Строки выполняются
последовательно, в окне видны и ввод (с приглашением), и вывод - как
диалог с пользователем. Пустые строки пропускаются.

- строка с ошибкой пропускается: печатается сообщение команды и
  `[script] line N: error, line skipped`, выполнение продолжается;
- ошибка чтения самого скрипта: `[script] error: ...`;
- `exit` в скрипте завершает скрипт и закрывает эмулятор.

### 2.6. Команды

| Команда | Описание |
|---------|----------|
| `ls`    | заглушка: печатает своё имя и аргументы |
| `cd`    | заглушка: печатает своё имя и аргументы |
| `exit`  | завершение работы эмулятора |

## 3. Сборка, запуск и тесты

Сборка не требуется. Нужен Python 3.9+ (и tkinter для GUI).

```sh
make run                    # или: ./run.sh   (Linux/macOS), run.bat (Windows)
make test                   # запуск модульных тестов
```

Без `make` (PowerShell):

```sh
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Параметры запуска:

```sh
./run.sh --vfs examples/vfs/deep --script examples/scripts/stage2_demo.emu
./run.sh --config examples/config/full.json
```

Скрипты реальной ОС (`scripts/*.sh` для Linux/macOS и `scripts/*.bat` для
Windows) вызывают эмулятор; каждый вызов открывает окно, которое нужно
закрыть, чтобы перейти к следующему:

```sh
scripts/stage2_cli.sh       # каждый параметр отдельно и все вместе
scripts/stage2_config.sh    # конфигурация и приоритет командной строки
scripts/stage2_errors.sh    # ошибки конфигурации и стартового скрипта
```

## 4. Примеры использования

Интерактивный сеанс:

```text
[debug] config_path = <not set>
[debug] vfs_path = <not set> (not set)
[debug] script_path = <not set> (not set)
user@default:/$ ls -l /home
ls: args = ['-l', '/home']
user@default:/$ cd docs
cd: args = ['docs']
user@default:/$ foo bar
foo: command not found
user@default:/$ exit now
exit: too many arguments
user@default:/$ exit
```

Параметры из файла и приоритет командной строки (значение `--vfs`
переопределяет `vfs_path` из файла):

```text
[debug] config_path = examples/config/full.json
[debug] vfs_path = examples/vfs/minimal (command line)
[debug] script_path = examples/scripts/stage2_demo.emu (config file)
user@default:/$ ls
ls: args = []
user@default:/$ cd /etc
cd: args = ['/etc']
user@default:/$ ls -l /etc
ls: args = ['-l', '/etc']
```

Ошибка в конфигурации - значение не строка (запуск продолжается):

```text
[debug] config_path = examples/config/wrong_type.json
[debug] vfs_path = <not set> (not set)
[debug] script_path = <not set> (not set)
[config] error: 'examples/config/wrong_type.json': 'vfs_path' must be a string
```

Стартовый скрипт с ошибочными строками (строки пропускаются):

```text
[debug] config_path = <not set>
[debug] vfs_path = <not set> (not set)
[debug] script_path = examples/scripts/stage2_errors.emu (command line)
user@default:/$ ls /etc
ls: args = ['/etc']
user@default:/$ no_such_command arg
no_such_command: command not found
[script] line 2: error, line skipped
user@default:/$ exit now
exit: too many arguments
[script] line 3: error, line skipped
user@default:/$ cd /etc
cd: args = ['/etc']
user@default:/$ ls /
ls: args = ['/']
```
