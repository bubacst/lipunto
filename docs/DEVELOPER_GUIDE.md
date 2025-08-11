# Руководство разработчика lipunto

## Содержание

1. [Введение](#введение)
2. [Архитектура проекта](#архитектура-проекта)
3. [Настройка окружения разработки](#настройка-окружения-разработки)
4. [Структура кода](#структура-кода)
5. [Разработка новых функций](#разработка-новых-функций)
6. [Тестирование](#тестирование)
7. [Стиль кода и стандарты](#стиль-кода-и-стандарты)
8. [Система сборки и упаковки](#система-сборки-и-упаковки)
9. [Внесение вклада](#внесение-вклада)
10. [Отладка](#отладка)

## Введение

Это руководство предназначено для разработчиков, которые хотят:
- Вносить изменения в существующий код lipunto
- Добавлять новые функции
- Использовать lipunto как основу для других проектов
- Понимать внутреннюю архитектуру проекта

### Предварительные требования

- Python 3.13+
- Опыт работы с Python
- Знание основ Linux и KDE Plasma
- Опыт работы с Git
- Понимание принципов объектно-ориентированного программирования

## Архитектура проекта

### Обзор архитектуры

lipunto построен по модульной архитектуре с четким разделением ответственности:

```
lipunto/
├── switch_layout.py          # Основной модуль с бизнес-логикой
├── config_manager.py         # Управление конфигурацией
├── keyboard_layouts.py       # Словари преобразования
├── clipboard_utils.py        # Работа с буфером обмена
├── logger.py                 # Система логирования
├── sw_last.sh                # Shell-обертка для режима "last"
├── sw_selected.sh            # Shell-обертка для режима "selected"
├── lipunto.kksrc             # Конфигурация KDE
└── input-event-codes.h       # Коды клавиш Linux
```

### Ключевые компоненты

#### 1. LayoutSwitcher

**Файл**: [`switch_layout.py`](../switch_layout.py)

**Ответственность**: Основная бизнес-логика преобразования текста и управления процессом коррекции.

**Ключевые методы**:
- `switch_text_layout()`: Преобразование текста между раскладками
- `process_last_word()`: Обработка последнего слова перед курсором
- `process_selected_text()`: Обработка выделенного текста
- `convert_and_replace()`: Полный цикл преобразования и замены

**Пример использования**:
```python
from switch_layout import LayoutSwitcher
from config_manager import LipuntoSettings

# Создание экземпляра
settings = LipuntoSettings()
switcher = LayoutSwitcher(settings)

# Преобразование текста
result = switcher.switch_text_layout("ghbdtn")
print(result)  # "привет"

# Обработка последнего слова
switcher.process_last_word()
```

#### 2. ClipboardManager

**Файл**: [`clipboard_utils.py`](../clipboard_utils.py)

**Ответственность**: Управление буфером обмена через D-Bus и эмуляция операций копирования/вставки.

**Ключевые методы**:
- `get_selection()`: Получение выделенного текста
- `paste_text()`: Вставка текста
- `save_clipboard_history()`: Сохранение истории буфера
- `restore_clipboard_history()`: Восстановление истории буфера

**Пример использования**:
```python
from clipboard_utils import ClipboardManager

clipboard = ClipboardManager()

# Получение выделенного текста
text = clipboard.get_selection(delay=0.1)
print(text)  # "ghbdtn"

# Вставка преобразованного текста
clipboard.paste_text("привет", delay=0.1)
```

#### 3. ConfigManager

**Файл**: [`config_manager.py`](../config_manager.py)

**Ответственность**: Парсинг аргументов командной строки, работа с переменными окружением и валидация конфигурации.

**Ключевые модели**:
- `LipuntoSettings`: Основная модель конфигурации
- `DelaysConfig`: Настройки задержек
- `LoggingConfig`: Настройки логирования
- `UIConfig`: Настройки пользовательского интерфейса

**Пример использования**:
```python
from config_manager import create_arg_parser, LipuntoSettings

# Парсинг аргументов командной строки
parser = create_arg_parser()
args = parser.parse_args()

# Создание настроек
settings = LipuntoSettings(
    layout=args.layout,
    delays=args.delays,
    logging=args.logging,
    ui=args.ui
)
```

#### 4. KeyboardLayouts

**Файл**: [`keyboard_layouts.py`](../keyboard_layouts.py)

**Ответственность**: Хранение и предоставление словарей для преобразования символов между раскладками.

**Ключевые функции**:
- `get_layout_dict()`: Получение словарей преобразования
- `en_ru`, `ru_en`: Словари для английской и русской раскладок

**Пример использования**:
```python
from keyboard_layouts import get_layout_dict

# Получение словарей преобразования
forward_dict, reverse_dict = get_layout_dict("en_ru")

# Преобразование символа
char = "q"
converted_char = forward_dict.get(char, char)
print(converted_char)  # "й"
```

#### 5. Logger

**Файл**: [`logger.py`](../logger.py)

**Ответственность**: Многоуровневое логирование с поддержкой разных выводов.

**Ключевые методы**:
- `init_logger()`: Инициализация логгера
- `get_logger()`: Получение экземпляра логгера

**Пример использования**:
```python
from logger import init_logger

# Инициализация логгера
config = {
    "enabled": True,
    "level": "DEBUG",
    "console": True,
    "file": "/tmp/lipunto.log"
}
logger = init_logger(config)

# Логирование сообщений
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Настройка окружения разработки

### 1. Клонирование репозитория

```bash
# Клонируем репозиторий
git clone https://github.com/yourusername/lipunto.git
cd lipunto

# Создаем ветку для разработки
git checkout -b feature/my-new-feature
```

### 2. Создание виртуального окружения

```bash
# Создаем виртуальное окружение
python3 -m venv .venv

# Активируем окружение
source .venv/bin/activate

# Обновляем pip
pip install --upgrade pip
```

### 3. Установка зависимостей

```bash
# Устанавливаем зависимости для разработки
pip install -r requirements.txt

# Устанавливаем зависимости для тестирования
pip install pytest pytest-cov pytest-mock black flake8 mypy

# Устанавливаем зависимости для документации
pip install sphinx sphinx-rtd-theme
```

### 4. Настройка IDE

#### VS Code

Создайте файл `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true
    }
}
```

Создайте файл `.vscode/launch.json` для отладки:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Debug lipunto last",
            "type": "python",
            "request": "launch",
            "module": "switch_layout",
            "args": ["last", "--enable-logging", "--log-level", "DEBUG"],
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Debug lipunto selected",
            "type": "python",
            "request": "launch",
            "module": "switch_layout",
            "args": ["selected", "--enable-logging", "--log-level", "DEBUG"],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### 5. Настройка pre-commit хуков

Создайте файл `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Установите pre-commit:

```bash
pip install pre-commit
pre-commit install
```

## Структура кода

### 1. Основные модули

#### switch_layout.py
```python
#!/usr/bin/env python3
"""
Основной модуль lipunto с бизнес-логикой преобразования текста.
"""

import subprocess
import sys
import time
from typing import Optional

from clipboard_utils import ClipboardManager
from config_manager import LipuntoSettings
from keyboard_layouts import get_layout_dict
from logger import init_logger


class LayoutSwitcher:
    """Класс для переключения раскладки клавиатуры и преобразования текста."""

    def __init__(self, settings: LipuntoSettings):
        """
        Инициализация LayoutSwitcher.

        Args:
            settings: Экземпляр LipuntoSettings
        """
        self.settings = settings
        self.logger = init_logger(settings.logging.model_dump())
        self.clipboard_manager = ClipboardManager()

    def switch_text_layout(self, text: str) -> str:
        """
        Преобразование текста между раскладками клавиатуры.

        Args:
            text: Входной текст для преобразования

        Returns:
            Преобразованный текст
        """
        # Реализация преобразования
        pass
```

#### config_manager.py
```python
"""
Менеджер конфигурации lipunto на основе Pydantic.
"""

from typing import Optional
from pydantic import BaseSettings, Field
from argparse import ArgumentParser, Namespace


class DelaysConfig(BaseSettings):
    """Конфигурация задержек."""

    clipboard_set: float = Field(0.05, description="Задержка при установке буфера")
    clipboard_get: float = Field(0.1, description="Задержка при получении буфера")
    text_process: float = Field(0.2, description="Задержка при обработке текста")
    paste: float = Field(0.1, description="Задержка при вставке текста")


class LipuntoSettings(BaseSettings):
    """Основная конфигурация lipunto."""

    layout: str = Field("en_ru", description="Раскладка по умолчанию")
    delays: DelaysConfig = Field(default_factory=DelaysConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    class Config:
        env_prefix = "LIPUNTO_"
```

### 2. Вспомогательные модули

#### keyboard_layouts.py
```python
"""
Словари для преобразования символов между языковыми раскладками.
"""

from typing import Dict, Tuple


# Английская на русскую
en_ru = {
    "q": "й", "w": "ц", "e": "у", "r": "к", "t": "е", "y": "н",
    "u": "г", "i": "ш", "o": "щ", "p": "з", "[": "х", "]": "ъ",
    "a": "ф", "s": "ы", "d": "в", "f": "а", "g": "п", "h": "р",
    "j": "о", "k": "л", "l": "д", ";": "ж", "'": "э",
    "z": "я", "x": "ч", "c": "с", "v": "м", "b": "и", "n": "т",
    "m": "ь", ",": "б", ".": "ю", "/": ".",
    "Q": "Й", "W": "Ц", "E": "У", "R": "К", "T": "Е", "Y": "Н",
    "U": "Г", "I": "Ш", "O": "Щ", "P": "З", "{": "Х", "}": "Ъ",
    "A": "Ф", "S": "Ы", "D": "В", "F": "А", "G": "П", "H": "Р",
    "J": "О", "K": "Л", "L": "Д", ":": "Ж", "\"": "Э",
    "Z": "Я", "X": "Ч", "C": "С", "V": "М", "B": "И", "N": "Т",
    "M": "Ь", "<": "Б", ">": "Ю", "?": ",",
    " ": " ", "\n": "\n", "\t": "\t", "\r": "\r"
}

# Русская на английскую (инверсия)
ru_en = {v: k for k, v in en_ru.items()}


def get_layout_dict(layout_name: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Получение словарей преобразования для указанной раскладки.

    Args:
        layout_name: Название раскладки ("en_ru", "ru_en")

    Returns:
        Кортеж из двух словарей (прямой, обратный)

    Raises:
        ValueError: Если раскладка не найдена
    """
    layout_pairs = {
        "en_ru": (en_ru, ru_en),
        "ru_en": (ru_en, en_ru),
    }

    if layout_name not in layout_pairs:
        raise ValueError(f"Unknown layout: {layout_name}")

    return layout_pairs[layout_name]
```

#### clipboard_utils.py
```python
"""
Утилиты для работы с буфером обмена через D-Bus.
"""

import subprocess
import sys
import time
from typing import List, Optional


class ClipboardManager:
    """Класс для управления буфером обмена через D-Bus."""

    def __init__(self):
        """Инициализация ClipboardManager."""
        self.history: Optional[List[str]] = None

    def run_qbus_command(self, commands: List[str]) -> str:
        """
        Выполнение команды qbus.

        Args:
            commands: Команда для выполнения

        Returns:
            Результат выполнения команды
        """
        commands.insert(0, "qdbus")
        return self._run_command(commands)

    def run_ydotool_command(self, commands: List[str]) -> None:
        """
        Выполнение команды ydotool.

        Args:
            commands: Команда для выполнения
        """
        commands.insert(0, "ydotool")
        self._run_command(commands)

    def _run_command(self, commands: List[str]) -> str:
        """
        Выполнение команды с обработкой ошибок.

        Args:
            commands: Команда для выполнения

        Returns:
            Результат выполнения команды

        Raises:
            RuntimeError: Если команда завершилась с ошибкой
        """
        try:
            result = subprocess.check_output(
                commands, stderr=subprocess.STDOUT, timeout=10
            )
            return result.decode().strip()
        except subprocess.TimeoutExpired:
            raise RuntimeError("Команда выполнена с превышением времени ожидания")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка выполнения команды: {e.output.decode()}")
```

### 3. Тесты

#### tests/test_switch_layout.py
```python
"""
Тесты для модуля switch_layout.
"""

import pytest
from unittest.mock import Mock, patch
from switch_layout import LayoutSwitcher
from config_manager import LipuntoSettings


class TestLayoutSwitcher:
    """Тесты класса LayoutSwitcher."""

    @pytest.fixture
    def settings(self):
        """Фикстура с настройками."""
        return LipuntoSettings()

    @pytest.fixture
    def switcher(self, settings):
        """Фикстура с LayoutSwitcher."""
        return LayoutSwitcher(settings)

    def test_switch_text_layout_en_to_ru(self, switcher):
        """Тест преобразования английского текста в русский."""
        result = switcher.switch_text_layout("hello")
        assert result == "привет"

    def test_switch_text_layout_ru_to_en(self, switcher):
        """Тест преобразования русского текста в английский."""
        result = switcher.switch_text_layout("привет")
        assert result == "hello"

    def test_switch_text_layout_mixed(self, switcher):
        """Тест преобразования смешанного текста."""
        result = switcher.switch_text_layout("hello world")
        assert result == "привет мир"

    @patch('switch_layout.LayoutSwitcher.get_selection')
    @patch('switch_layout.LayoutSwitcher.paste_text')
    @patch('switch_layout.LayoutSwitcher.switch_kde_layout')
    def test_process_last_word(self, mock_switch, mock_paste, mock_get, switcher):
        """Тест обработки последнего слова."""
        mock_get.return_value = "ghbdtn"

        switcher.process_last_word()

        mock_get.assert_called_once()
        mock_paste.assert_called_once_with("привет")
        mock_switch.assert_called_once()
```

## Разработка новых функций

### 1. Добавление новой языковой пары

#### Шаг 1: Создание словарей преобразования

Добавьте словари в [`keyboard_layouts.py`](../keyboard_layouts.py):

```python
# Добавление украинской раскладки
en_ua = {
    "q": "й", "w": "ц", "e": "у", "r": "р", "t": "т", "y": "и",
    "u": "і", "i": "і", "o": "о", "p": "п", "[": "д", "]": "ж",
    "a": "а", "s": "с", "d": "д", "f": "ф", "g": "г", "h": "х",
    "j": "й", "k": "к", "l": "л", ";": "ї", "'": "є",
    "z": "з", "x": "ь", "c": "ц", "v": "в", "b": "б", "n": "н",
    "m": "м", ",": "ю", ".": ".", "/": "/",
    # ... остальные символы
}

ua_en = {v: k for k, v in en_ua.items()}
```

#### Шаг 2: Обновление функции get_layout_dict

```python
def get_layout_dict(layout_name: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Получение словарей преобразования."""
    layout_pairs = {
        "en_ru": (en_ru, ru_en),
        "ru_en": (ru_en, en_ru),
        "en_ua": (en_ua, ua_en),
        "ua_en": (ua_en, en_ua),
    }

    if layout_name not in layout_pairs:
        raise ValueError(f"Unknown layout: {layout_name}")

    return layout_pairs[layout_name]
```

#### Шаг 3: Обновление конфигурации

Добавьте новую раскладку в валидацию:

```python
class LipuntoSettings(BaseSettings):
    layout: str = Field("en_ru", description="Раскладка по умолчанию")

    @validator('layout')
    def validate_layout(cls, v):
        allowed_layouts = ['en_ru', 'ru_en', 'en_ua', 'ua_en']
        if v not in allowed_layouts:
            raise ValueError(f"Layout must be one of {allowed_layouts}")
        return v
```

#### Шаг 4: Тестирование

Добавьте тесты в [`tests/test_keyboard_layouts.py`](../tests/test_keyboard_layouts.py):

```python
def test_ukrainian_layout(self):
    """Тест украинской раскладки."""
    forward, reverse = get_layout_dict("en_ua")

    assert forward["q"] == "й"
    assert forward["w"] == "ц"
    assert reverse["й"] == "q"
    assert reverse["ц"] == "w"
```

### 2. Добавление нового режима работы

#### Шаг 1: Обновление аргументов командной строки

В [`config_manager.py`](../config_manager.py) добавьте новый режим:

```python
def create_arg_parser() -> ArgumentParser:
    """Создание парсера аргументов командной строки."""
    parser = ArgumentParser(description="lipunto - корректор раскладки клавиатуры")

    parser.add_argument(
        "mode",
        choices=["last", "selected", "current"],
        help="Режим работы: last (последнее слово), selected (выделенный текст), current (текущее слово)"
    )

    # ... остальные аргументы
```

#### Шаг 2: Реализация нового режима

В [`switch_layout.py`](../switch_layout.py) добавьте новый метод:

```python
def process_current_word(self) -> str:
    """
    Обработка текущего слова под курсором.

    Returns:
        Преобразованный текст
    """
    # 1. Получить текущее слово под курсором
    current_word = self.get_current_word()

    # 2. Преобразовать текст
    converted_text = self.switch_text_layout(current_word)

    # 3. Заменить текст
    self.replace_current_word(converted_text)

    # 4. Переключить раскладку
    self.switch_kde_layout()

    # 5. Показать уведомление
    self.show_popup_message(f"{current_word} → {converted_text}")

    return converted_text
```

#### Шаг 3: Обновление основной функции

```python
def main():
    """Основная функция."""
    # Парсинг аргументов
    args = create_arg_parser().parse_args()

    # Создание настроек
    settings = LipuntoSettings()

    # Создание экземпляра LayoutSwitcher
    switcher = LayoutSwitcher(settings)

    # Обработка в зависимости от режима
    if args.mode == "last":
        switcher.process_last_word()
    elif args.mode == "selected":
        switcher.process_selected_text()
    elif args.mode == "current":
        switcher.process_current_word()
```

#### Шаг 4: Создание shell-обертки

Создайте новый файл [`sw_current.sh`](../sw_current.sh):

```bash
#!/bin/bash
# Скрипт для коррекции текущего слова под курсором

# Установка прав сокета ydotool
sudo chmod go+rw /tmp/.ydotool_socket

# Вызов Python скрипта
python /usr/local/sbin/switch_layout.py current "$@"
```

#### Шаг 5: Обновление конфигурации KDE

Добавьте новую горячую клавишу в [`lipunto.kksrc`](../lipunto.kksrc):

```ini
[sw_current]
Comment=lipunto - коррекция текущего слова
Exec=/usr/local/sbin/sw_current.sh
Name[ru]=lipunto (текущее слово)
Name=lipunto (current word)
X-KDE-GlobalShortcut-shortcut=none
X-KDE-GlobalShortcut-component=kwin
```

### 3. Добавление нового типа уведомлений

#### Шаг 1: Обновление UIConfig

В [`config_manager.py`](../config_manager.py) добавьте новые опции:

```python
class UIConfig(BaseSettings):
    show_popup: bool = Field(False, description="Показывать уведомления")
    popup_timeout: int = Field(5, description="Время отображения уведомления")
    popup_type: str = Field("passive", description="Тип уведомления")
    popup_sound: bool = Field(False, description="Звуковое уведомление")
```

#### Шаг 2: Обновление функции show_popup_message

В [`switch_layout.py`](../switch_layout.py) обновите метод:

```python
def show_popup_message(self, text: str, error: bool = False) -> None:
    """Показ уведомления через kdialog."""
    if not self.show_popup:
        return

    # Определение типа уведомления
    if self.ui.popup_type == "passive":
        dialog_type = "--passivepopup"
    elif self.ui.popup_type == "error":
        dialog_type = "--error"
    else:
        dialog_type = "--msgbox"

    # Звуковое уведомление
    if self.ui.popup_sound:
        subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"])

    # Показ уведомления
    subprocess.run([
        "kdialog",
        "--title",
        "lipunto",
        dialog_type,
        text,
        str(self.ui.popup_timeout)
    ], check=True)
```

#### Шаг 3: Тестирование

Добавьте тесты в [`tests/test_ui.py`](../tests/test_ui.py):

```python
def test_popup_message_types(self, switcher):
    """Тест разных типов уведомлений."""
    with patch('subprocess.run') as mock_run:
        switcher.ui.popup_type = "error"
        switcher.show_popup_message("Test error", error=True)

        mock_run.assert_called_with([
            "kdialog", "--title", "lipunto", "--error",
            "Test error", "5"
        ], check=True)
```

## Тестирование

### 1. Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Общие фикстуры
├── test_switch_layout.py    # Тесты основного модуля
├── test_config_manager.py   # Тесты конфигурации
├── test_keyboard_layouts.py # Тесты словарей
├── test_clipboard_utils.py  # Тесты буфера обмена
├── test_logger.py           # Тесты логирования
└── test_integration.py      # Интеграционные тесты
```

### 2. Написание тестов

#### Пример unit теста

```python
import pytest
from unittest.mock import Mock, patch
from switch_layout import LayoutSwitcher
from config_manager import LipuntoSettings


class TestLayoutSwitcher:
    """Тесты для LayoutSwitcher."""

    @pytest.fixture
    def settings(self):
        """Фикстура с настройками."""
        return LipuntoSettings()

    @pytest.fixture
    def switcher(self, settings):
        """Фикстура с LayoutSwitcher."""
        return LayoutSwitcher(settings)

    def test_switch_text_layout_basic(self, switcher):
        """Базовый тест преобразования текста."""
        result = switcher.switch_text_layout("hello")
        assert result == "привет"

    def test_switch_text_layout_empty(self, switcher):
        """Тест с пустым текстом."""
        result = switcher.switch_text_layout("")
        assert result == ""

    def test_switch_text_layout_special_chars(self, switcher):
        """Тест со специальными символами."""
        result = switcher.switch_text_layout("hello!")
        assert result == "привет!"

    @patch('switch_layout.LayoutSwitcher.get_selection')
    @patch('switch_layout.LayoutSwitcher.paste_text')
    @patch('switch_layout.LayoutSwitcher.switch_kde_layout')
    def test_process_last_word_integration(self, mock_switch, mock_paste, mock_get, switcher):
        """Интеграционный тест обработки последнего слова."""
        mock_get.return_value = "ghbdtn"

        switcher.process_last_word()

        mock_get.assert_called_once()
        mock_paste.assert_called_once_with("привет")
        mock_switch.assert_called_once()
```

#### Пример интеграционного теста

```python
import pytest
from unittest.mock import patch
from switch_layout import LayoutSwitcher
from config_manager import LipuntoSettings


class TestIntegration:
    """Интеграционные тесты."""

    @pytest.fixture
    def switcher(self):
        """Фикстура с LayoutSwitcher."""
        settings = LipuntoSettings()
        return LayoutSwitcher(settings)

    @patch('switch_layout.LayoutSwitcher.get_selection')
    @patch('switch_layout.LayoutSwitcher.paste_text')
    @patch('switch_layout.LayoutSwitcher.switch_kde_layout')
    @patch('switch_layout.LayoutSwitcher.show_popup_message')
    def test_full_workflow(self, mock_popup, mock_switch, mock_paste, mock_get, switcher):
        """Тест полного рабочего процесса."""
        # Настройка моков
        mock_get.return_value = "ghbdtn"

        # Выполнение
        switcher.convert_and_replace("ghbdtn")

        # Проверки
        mock_get.assert_called_once()
        mock_paste.assert_called_once_with("привет")
        mock_switch.assert_called_once()
        mock_popup.assert_called_once_with("ghbdtn\nпривет")
```

### 3. Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=lipunto --cov-report=html

# Запуск конкретного теста
pytest tests/test_switch_layout.py::TestLayoutSwitcher::test_switch_text_layout_basic

# Запуск тестов с вербозным выводом
pytest -v

# Запуск тестов с отладкой
pytest --pdb
```

### 4. Тестирование производительности

```python
import timeit
import pytest
from switch_layout import LayoutSwitcher
from config_manager import LipuntoSettings


class TestPerformance:
    """Тесты производительности."""

    @pytest.fixture
    def switcher(self):
        """Фикстура с LayoutSwitcher."""
        settings = LipuntoSettings()
        return LayoutSwitcher(settings)

    def test_conversion_performance(self, switcher):
        """Тест производительности преобразования текста."""
        test_text = "hello world " * 100  # 1100 символов

        # Измерение времени
        time = timeit.timeit(
            lambda: switcher.switch_text_layout(test_text),
            number=1000
        )

        # Проверка, что время выполнения приемлемое
        assert time < 1.0, f"Преобразование заняло слишком много времени: {time:.3f}s"

        # Расчет средней скорости
        chars_per_second = (len(test_text) * 1000) / time
        assert chars_per_second > 10000, f"Слишком низкая скорость: {chars_per_second:.0f} chars/s"
```

## Стиль кода и стандарты

### 1. Стиль кода

#### Использование Black

Проект использует Black для форматирования кода:

```bash
# Форматирование кода
black lipunto/ tests/

# Проверка форматирования без изменений
black --check lipunto/ tests/
```

#### Использование Flake8

Проверка качества кода:

```bash
# Проверка кода
flake8 lipunto/ tests/

# Игнорирование определенных правил
flake8 --ignore=E203,W503 lipunto/
```

#### Использование MyPy

Статическая типизация:

```bash
# Проверка типов
mypy lipunto/

# Игнорирование определенных файлов
mypy --ignore-missing-imports lipunto/
```

### 2. Стандарты документации

#### Docstrings

Используется формат Google-style docstrings:

```python
def switch_text_layout(self, text: str) -> str:
    """
    Преобразование текста между раскладками клавиатуры.

    Args:
        text: Входной текст для преобразования

    Returns:
        Преобразованный текст

    Raises:
        ValueError: Если текст пустой или содержит недопустимые символы
    """
    if not text:
        raise ValueError("Text cannot be empty")

    # Реализация
    pass
```

#### Комментарии

```python
# Хорошие комментарии
# Используем словарь O(1) для быстрого поиска символов
forward_dict, reverse_dict = get_layout_dict(self.settings.layout)

result = []
for char in text:
    if char in forward_dict:
        result.append(forward_dict[char])  # Прямое преобразование
    elif char in reverse_dict:
        result.append(reverse_dict[char])  # Обратное преобразование
    else:
        result.append(char)  # Сохраняем неизменные символы
```

### 3. Обработка ошибок

```python
try:
    result = subprocess.check_output(
        ["which"] + self.commands, stderr=sys.stdout
    )
except FileNotFoundError:
    error_msg = "Команда 'which' не найдена"
    self.logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    exit(1)
except subprocess.CalledProcessError as e:
    error_msg = f"Не удалось найти команды: {self.commands}"
    self.logger.error(error_msg)
    print(error_msg, file=sys.stderr)
    exit(1)
```

### 4. Логирование

```python
# Использование уровней логирования
self.logger.debug("Debug information: %s", detailed_info)
self.logger.info("Operation started: %s", operation_name)
self.logger.warning("Potential issue detected: %s", issue_description)
self.logger.error("Error occurred: %s", error_message)
self.logger.critical("Critical error: %s", critical_error)
```

## Система сборки и упаковки

### 1. Сборка wheel пакета

```bash
# Создание wheel пакета
python setup.py bdist_wheel

# Создание sdist пакета
python setup.py sdist

# Установка локально
pip install dist/lipunto-1.0.0-py3-none-any.whl
```

### 2. Создание deb пакета

```bash
# Установка инструментов
sudo apt install build-essential devscripts debhelper

# Сборка пакета
debuild -us -uc

# Установка пакета
sudo dpkg -i ../lipunto_1.0.0_amd64.deb
```

### 3. Создание rpm пакета

```bash
# Установка инструментов
sudo dnf install rpm-build rpmdevtools

# Создание структуры
rpmdev-setuptree

# Сборка пакета
rpmbuild -ba lipunto.spec

# Установка пакета
sudo rpm -ivh ../rpms/x86_64/lipunto-1.0.0-1.x86_64.rpm
```

### 4. Docker контейнер

#### Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Копирование файлов
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY lipunto/ ./lipunto/

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя
RUN useradd -m -u 1000 lipunto
USER lipunto

# Точка входа
ENTRYPOINT ["python", "-m", "lipunto"]
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  lipunto:
    build: .
    container_name: lipunto
    environment:
      - DISPLAY=${DISPLAY}
      - XAUTHORITY=${XAUTHORITY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
      - /tmp/.ydotool_socket:/tmp/.ydotool_socket
    devices:
      - /dev/input/event0
    network_mode: host
```

## Внесение вклада

### 1. Процесс внесения вклада

1. **Форк репозитория**: Создайте форк основного репозитория
2. **Клонируйте**: `git clone https://github.com/yourusername/lipunto.git`
3. **Создайте ветку**: `git checkout -b feature/amazing-feature`
4. **Внесите изменения**: Сделайте ваши изменения
5. **Проверьте тесты**: `pytest`
6. **Проверьте стиль**: `black . && flake8 .`
7. **Сделайте коммит**: `git commit -m 'feat: add amazing feature'`
8. **Отправьте изменения**: `git push origin feature/amazing-feature`
9. **Создайте PR**: Откройте pull request в основной репозиторий

### 2. Требования к PR

- Все тесты должны проходить
- Код должен соответствовать стилю проекта
- Должны быть добавлены тесты для нового функционала
- Должна быть обновлена документация
- PR должен содержать описание изменений

### 3. Форматирование коммитов

Используется Conventional Commits:

```
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: update dependencies
```

### 4. Теги версий

Используется Semantic Versioning:

- `MAJOR.MINOR.PATCH`
- `1.0.0` - Первая стабильная версия
- `1.0.1` - Исправление ошибок
- `1.1.0` - Новые функции
- `2.0.0` - Крупные изменения

## Отладка

### 1. Отладка в VS Code

1. Установите точки останова в коде
2. Нажмите F5 для запуска отладки
3. Используйте отладчик для пошагового выполнения

### 2. Логирование

Для включения подробного логирования:

```bash
# Включение логирования
python /usr/local/sbin/switch_layout.py last --enable-logging --log-level DEBUG

# Логирование в файл
python /usr/local/sbin/switch_layout.py last --enable-logging --log-file /tmp/debug.log
```

### 3. Отладка с помощью pdb

```python
import pdb; pdb.set_trace()
```

### 4. Профилирование

```bash
# Профилирование
python -m cProfile -o profile.stats /usr/local/sbin/switch_layout.py last

# Анализ результатов
python -m pstats profile.stats
```

### 5. Отладка проблем с ydotool

```bash
# Проверка работы ydotool
ydotool key 29:1 29:0  # Нажатие и отпускание Ctrl

# Проверка сокета
ls -la /tmp/.ydotool_socket
sudo chmod go+rw /tmp/.ydotool_socket

# Проверка сервиса
systemctl status ydotool.service
journalctl -u ydotool.service -f
```

Это руководство должно помочь разработчикам эффективно работать с кодом lipunto, вносить изменения и добавлять новый функционал.