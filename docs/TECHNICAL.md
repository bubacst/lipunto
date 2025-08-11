# Техническая документация lipunto

## Содержание

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Системные зависимости](#системные-зависимости)
3. [Архитектурные компоненты](#архитектурные-компоненты)
4. [Технические детали реализации](#технические-детали-реализации)
5. [Производительность и оптимизация](#производительность-и-оптимизация)
6. [Безопасность](#безопасность)
7. [Тестирование](#тестирование)
8. [Развертывание](#развертывание)
9. [Мониторинг и логирование](#мониторинг-и-логирование)

## Обзор архитектуры

lipunto представляет собой модульную систему, состоящую из нескольких компонентов, работающих вместе для обеспечения автоматической коррекции раскладки клавиатуры.

### Архитектурные принципы

- **Модульность**: Каждый компонент имеет четкую ответственность
- **Расширяемость**: Легкое добавление новых языковых пар и функций
- **Надежность**: Обработка ошибок и восстановление после сбоев
- **Производительность**: Минимальные задержки при работе с текстом
- **Интеграция**: Бесшовная интеграция с экосистемой KDE Plasma

### Системная архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Приложение-клиент                        │
│  (Текстовый редактор, браузер, терминал и т.д.)             │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    lipunto ядро                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ LayoutSwitcher  │  │ ClipboardManager│  │ ConfigManager│ │
│  │                 │  │                 │  │             │ │
│  │ • switch_text_  │  │ • get_selection │  │ • ArgParser │ │
│  │   layout()      │  │ • paste_text()  │  │ • Pydantic  │ │
│  │ • process_last_ │  │ • save_history  │  │ • EnvVars   │ │
│  │   word()        │  │ • restore_hist  │  │             │ │
│  │ • process_sel_  │  │                 │  │             │ │
│  │   ected()       │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Системные утилиты                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    ydotool  │  │    qdbus    │  │   kdialog   │         │
│  │             │  │             │  │             │         │
│  │ • Эмуляция  │  │ • D-Bus     │  │ • Уведом-   │         │
│  │   ввода     │  │ • Буфер     │  │   ления     │         │
│  │ • Коды      │  │   обмена    │  │             │         │
│  │   клавиш    │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   KDE Plasma                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Global Keys │  │ Klipper     │  │ Keyboard    │         │
│  │             │  │             │  │ Layouts     │         │
│  │ • Горячие   │  │ • История   │  │ • Переключ- │         │
│  │   клавиши   │  │   буфера    │  │   ение      │         │
│  │             │  │             │  │   раскладок │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Системные зависимости

### Обязательные зависимости

#### Python 3.13+
- **Требуемая версия**: Python 3.13.5 или выше
- **Зависимости**:
  - `pydantic` >= 2.0 - Валидация конфигурации
  - `pydantic-settings` >= 2.0 - Работа с переменными окружения
  - `typing-extensions` - Расширения для типизации

#### Системные утилиты

**ydotool** - эмуляция ввода клавиш
- **Путь**: `/usr/bin/ydotool`
- **Сервис**: `ydotoold`
- **Сокет**: `/tmp/.ydotool_socket`
- **Права доступа**: `go+rw` (чтение и запись для группы и других)
- **Коды клавиш** (из `input-event-codes.h`):
  - `29`: KEY_LEFTCTRL (Ctrl)
  - `42`: KEY_LEFTSHIFT (Shift)
  - `46`: KEY_C (C)
  - `105`: KEY_LEFT (←)
  - `110`: KEY_INSERT (Insert)

**qdbus** - работа с D-Bus KDE
- **Путь**: `/usr/bin/qdbus`
- **Пакет**: `qt5-tools` или `qt6-tools`
- **Используемые интерфейсы**:
  - `org.kde.klipper` - работа с буфером обмена
  - `org.kde.keyboard` - переключение раскладки клавиатуры

**kdialog** - отображение уведомлений
- **Путь**: `/usr/bin/kdialog`
- **Пакет**: `qt5-tools` или `qt6-tools`
- **Используемые опции**:
  - `--passivepopup` - информационное уведомление
  - `--error` - уведомление об ошибке
  - `--title` - заголовок окна

### Опциональные зависимости

**systemd** - управление сервисом ydotool
- **Файл сервиса**: `/etc/systemd/system/ydotool.service`
- **Команды**:
  - `systemctl daemon-reload`
  - `systemctl enable ydotool.service`
  - `systemctl start ydotool.service`

## Архитектурные компоненты

### 1. LayoutSwitcher

**Файл**: [`switch_layout.py`](../switch_layout.py)

**Основные responsibilities**:
- Преобразование текста между раскладками
- Управление процессом коррекции
- Координация работы с буфером обмена
- Переключение раскладки клавиатуры

**Ключевые методы**:

```python
class LayoutSwitcher:
    def switch_text_layout(self, text: str) -> str:
        """Преобразование текста между раскладками"""
        # Использует словари из keyboard_layouts.py
        forward_dict, reverse_dict = get_layout_dict(self.settings.layout)
        # Преобразование каждого символа

    def process_last_word(self) -> str:
        """Обработка последнего слова перед курсором"""
        # Выделение слова через ydotool
        # Копирование в буфер обмена
        # Возврат текста

    def process_selected_text(self) -> str:
        """Обработка выделенного текста"""
        # Копирование выделенного текста
        # Возврат текста

    def convert_and_replace(self, text: str) -> None:
        """Преобразование и замена текста"""
        # Преобразование текста
        # Вставка через ydotool
        # Переключение раскладки
        # Показ уведомления
```

### 2. ClipboardManager

**Файл**: [`clipboard_utils.py`](../clipboard_utils.py)

**Основные responsibilities**:
- Управление буфером обмена через D-Bus
- Сохранение и восстановление истории буфера
- Эмуляция операций копирования/вставки

**Ключевые методы**:

```python
class ClipboardManager:
    def get_selection(self, delay: float = 0) -> str:
        """Получение выделенного текста"""
        # Сохранение текущей истории
        # Копирование через ydotool (Ctrl+C)
        # Получение текста из буфера
        # Восстановление истории

    def paste_text(self, new_text: str, delay: float = 0) -> None:
        """Вставка текста"""
        # Установка текста в буфер
        # Вставка через ydotool (Shift+Insert)
        # Восстановление истории

    def save_clipboard_history(self) -> list:
        """Сохранение истории буфера"""
        # Получение всех элементов истории
        # Сохранение в атрибут класса

    def restore_clipboard_history(self) -> None:
        """Восстановление истории буфера"""
        # Очистка текущей истории
        # Восстановление элементов в обратном порядке
```

### 3. ConfigManager

**Файл**: [`config_manager.py`](../config_manager.py)

**Основные responsibilities**:
- Парсинг аргументов командной строки
- Работа с переменными окружения
- Валидация конфигурации через Pydantic
- Управление настройками задержек

**Конфигурационные модели**:

```python
class DelaysConfig(BaseSettings):
    clipboard_set: float = 0.05
    clipboard_get: float = 0.1
    text_process: float = 0.2
    paste: float = 0.1

class LoggingConfig(BaseSettings):
    enabled: bool = False
    level: str = "WARNING"
    file: str = "/tmp/lipunto.log"
    console: bool = False
    syslog: bool = False

class UIConfig(BaseSettings):
    show_popup: bool = False
    popup_timeout: int = 5

class LipuntoSettings(BaseSettings):
    layout: str = "en_ru"
    delays: DelaysConfig
    logging: LoggingConfig
    ui: UIConfig
```

### 4. KeyboardLayouts

**Файл**: [`keyboard_layouts.py`](../keyboard_layouts.py)

**Основные responsibilities**:
- Хранение словарей преобразования символов
- Предоставление интерфейса для получения словарей
- Поддержка расширения для новых языковых пар

**Структура данных**:

```python
# Английская на русскую (en_ru)
en_ru = {
    "q": "й", "w": "ц", "e": "у", "r": "к", "t": "е", "y": "н",
    # ... остальные символы
}

# Русская на английскую (ru_en) - инверсия
ru_en = {v: k for k, v in en_ru.items()}

def get_layout_dict(layout_name: str) -> tuple:
    """Возвращает пару словарей (forward, reverse)"""
    layout_pairs = {
        "en_ru": (en_ru, ru_en),
        "ru_en": (ru_en, en_ru),
    }
    return layout_pairs[layout_name]
```

### 5. Logger

**Файл**: [`logger.py`](../logger.py)

**Основные responsibilities**:
- Многоуровневое логирование
- Поддержка разных выводов (консоль, файл, syslog)
- Контекстное логирование
- Управление состоянием логгера

**Особенности реализации**:

```python
class LipuntoLogger:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Проверка включенности логирования
        enabled = self.config.get("enabled", False)
        if not enabled:
            self.logger.setLevel(logging.CRITICAL + 1)
            return

        # Настройка обработчиков
        if self.config.get("console", False):
            # Консольный обработчик

        if self.config.get("file"):
            # Файловый обработчик

        if self.config.get("syslog", False):
            # Системный лог
```

## Технические детали реализации

### 1. Эмуляция ввода клавиш

**Принцип работы**:
- Использование `ydotool key` для эмуляции нажатий клавиш
- Передача кодов клавиш из `input-event-codes.h`
- Управление состоянием клавиш (нажатие/отпускание)

**Пример выделения последнего слова**:
```python
def select_last_word(self) -> None:
    """Выделение последнего слова (Ctrl+Shift+Left)"""
    self.run_ydotool_command([
        "key",
        "29:1",  # KEY_LEFTCTRL: нажать
        "42:1",  # KEY_LEFTSHIFT: нажать
        "105:1", # KEY_LEFT: нажать
        "105:0", # KEY_LEFT: отпустить
        "42:0",  # KEY_LEFTSHIFT: отпустить
        "29:0"   # KEY_LEFTCTRL: отпустить
    ])
```

### 2. Работа с буфером обмена

**Принцип работы**:
- Использование D-Bus интерфейса `org.kde.klipper`
- Сохранение и восстановление истории буфера
- Атомарные операции для предотвращения потери данных

**Получение выделенного текста**:
```python
def get_selection(self, delay: float = 0) -> str:
    """Получение выделенного текста"""
    # 1. Сохранение текущей истории
    last_item = self.get_clipboard_last_item()
    self.save_clipboard_history()

    # 2. Копирование (Ctrl+C)
    self.run_ydotool_command(["key", "29:1", "46:1", "46:0", "29:0"])

    # 3. Ожидание обновления буфера
    time.sleep(delay)

    # 4. Получение текста
    selection = self.get_clipboard_last_item()

    # 5. Восстановление истории
    self.restore_clipboard_history()
    if last_item:
        self.set_clipboard_last_item(last_item)

    return selection
```

### 3. Преобразование текста

**Принцип работы**:
- Использование словарей для прямого и обратного преобразования
- Обработка каждого символа индивидуально
- Сохранение неизменных символов (пробелы, знаки препинания)

**Оптимизация**:
```python
def switch_text_layout(self, text: str) -> str:
    """Оптимизированное преобразование текста"""
    forward_dict, reverse_dict = get_layout_dict(self.settings.layout)

    # Использование list comprehension для производительности
    result = []
    for char in text:
        if char in forward_dict:
            result.append(forward_dict[char])
        elif char in reverse_dict:
            result.append(reverse_dict[char])
        else:
            result.append(char)

    return "".join(result)
```

### 4. Управление задержками

**Принцип работы**:
- Настройка задержек для каждой операции
- Адаптация под разные системы
- Минимизация времени ожидания

**Типичные задержки**:
- `clipboard_set`: 0.05с - установка содержимого буфера
- `clipboard_get`: 0.1с - получение содержимого буфера
- `text_process`: 0.2с - обработка текста
- `paste`: 0.1с - вставка текста

### 5. Обработка ошибок

**Стратегии**:
- Проверка наличия зависимостей при старте
- Обработка исключений при выполнении операций
- Логирование ошибок для диагностики
- Пользовательские уведомления об ошибках

**Пример обработки ошибок**:
```python
def check_dependencies(self) -> None:
    """Проверка наличия необходимых утилит"""
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

## Производительность и оптимизация

### 1. Оптимизация преобразования текста

**Проблема**: Преобразование больших объемов текста может быть медленным.

**Решения**:
- Использование словарей O(1) для поиска символов
- Предварительная компиляция регулярных выражений (если используются)
- Кэширование часто используемых преобразований

**Бенчмарки**:
```python
# Тестирование производительности
import timeit

def benchmark_conversion():
    test_text = "hello world привет мир"
    setup = "from __main__ import switch_text_layout"

    time = timeit.timeit(
        f"switch_text_layout('{test_text}')",
        setup=setup,
        number=10000
    )

    print(f"Преобразование 10000 раз: {time:.3f}с")
    print(f"Среднее время: {time/10000*1000:.3f}мс")
```

### 2. Оптимизация работы с буфером обмена

**Проблема**: Частые операции с буфером обмена могут вызывать задержки.

**Решения**:
- Минимизация количества операций сохранения/восстановления
- Использование атомарных операций
- Оптимизация задержек под конкретную систему

### 3. Оптимизация логирования

**Проблема**: Логирование может влиять на производительность.

**Решения**:
- Отключение логирования по умолчанию
- Условное логирование только при включении
- Использование эффективных форматов логов

```python
class LipuntoLogger:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        enabled = self.config.get("enabled", False)
        if not enabled:
            # Полное отключение логирования
            self.logger.setLevel(logging.CRITICAL + 1)
            return
        # ... остальная инициализация
```

## Безопасность

### 1. Обработка пользовательского ввода

**Меры безопасности**:
- Валидация всех входных данных
- Ограничение длины текста для преобразования
- Обработка специальных символов

**Пример валидации**:
```python
def validate_text_input(self, text: str) -> bool:
    """Валидация текстового ввода"""
    if not text or not text.strip():
        return False

    # Проверка на слишком длинный текст
    if len(text) > 10000:  # 10KB limit
        return False

    # Проверка на контрольные символы
    if any(ord(char) < 32 or ord(char) > 126 for char in text):
        return False

    return True
```

### 2. Безопасность буфера обмена

**Меры безопасности**:
- Сохранение и восстановление истории буфера
- Атомарные операции для предотвращения потери данных
- Обработка ошибок при работе с буфером

### 3. Безопасность выполнения команд

**Меры безопасности**:
- Проверка всех внешних команд
- Ограничение прав доступа
- Обработка ошибок выполнения

```python
def _run_command(self, commands: list) -> str:
    """Безопасное выполнение команды"""
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

## Тестирование

### 1. Структура тестов

```
tests/
├── __init__.py
├── test_switch_layout.py
├── test_clipboard_utils.py
├── test_config_manager.py
├── test_keyboard_layouts.py
├── test_logger.py
└── conftest.py
```

### 2. Unit тесты

**Пример теста для преобразования текста**:
```python
def test_switch_text_layout():
    """Тест преобразования текста между раскладками"""
    switcher = LayoutSwitcher(settings)

    # Тест английский на русский
    result = switcher.switch_text_layout("hello")
    assert result == "привет"

    # Тест русский на английский
    result = switcher.switch_text_layout("привет")
    assert result == "hello"

    # Тест смешанного текста
    result = switcher.switch_text_layout("hello world")
    assert result == "привет мир"

    # Тест специальных символов
    result = switcher.switch_text_layout("hello!")
    assert result == "привет!"
```

**Пример теста для работы с буфером обмена**:
```python
def test_clipboard_operations():
    """Тест операций с буфером обмена"""
    clipboard = ClipboardManager()

    # Тест сохранения и восстановления истории
    original_text = "test text"
    clipboard.set_clipboard_last_item(original_text)

    history = clipboard.save_clipboard_history()
    assert len(history) > 0

    # Тест восстановления
    clipboard.clear_clipboard_contents()
    clipboard.restore_clipboard_history()

    restored_text = clipboard.get_clipboard_last_item()
    assert restored_text == original_text
```

### 3. Интеграционные тесты

**Пример интеграционного теста**:
```python
def test_full_workflow():
    """Тест полного рабочего процесса"""
    # Инициализация компонентов
    settings = LipuntoSettings()
    switcher = LayoutSwitcher(settings)

    # Тест полного цикла для последнего слова
    with patch.object(switcher, 'get_selection') as mock_get:
        with patch.object(switcher, 'paste_text') as mock_paste:
            with patch.object(switcher, 'switch_kde_layout') as mock_switch:
                mock_get.return_value = "ghbdtn"

                switcher.convert_and_replace("ghbdtn")

                # Проверка вызовов
                mock_paste.assert_called_once_with("привет")
                mock_switch.assert_called_once()
```

### 4. Производительность тесты

**Пример теста производительности**:
```python
def test_performance():
    """Тест производительности преобразования текста"""
    switcher = LayoutSwitcher(settings)
    test_text = "hello world " * 100  # 1100 символов

    start_time = time.time()
    for _ in range(1000):
        switcher.switch_text_layout(test_text)
    end_time = time.time()

    execution_time = end_time - start_time
    assert execution_time < 1.0  # Должно выполняться менее чем за 1 секунду
```

## Развертывание

### 1. Установка из исходного кода

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/lipunto.git
cd lipunto

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Установка системных файлов
sudo cp switch_layout.py /usr/local/sbin/
sudo cp sw_last.sh /usr/local/sbin/
sudo cp sw_selected.sh /usr/local/sbin/
sudo chmod +x /usr/local/sbin/*

# Настройка systemd сервиса
sudo cp ydotool.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ydotool.service
sudo systemctl start ydotool.service
```

### 2. Упаковка для распространения

**Создание deb пакета**:
```bash
# Установка инструментов сборки
sudo apt install build-essential devscripts debhelper

# Сборка пакета
debuild -us -uc

# Установка пакета
sudo dpkg -i ../lipunto_1.0.0_amd64.deb
```

**Создание rpm пакета**:
```bash
# Установка инструментов сборки
sudo dnf install rpm-build rpmdevtools

# Создание структуры
rpmdev-setuptree

# Сборка пакета
rpmbuild -ba lipunto.spec

# Установка пакета
sudo rpm -ivh ../rpms/x86_64/lipunto-1.0.0-1.x86_64.rpm
```

### 3. Docker контейнер

**Dockerfile**:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Копирование файлов
COPY requirements.txt .
COPY switch_layout.py .
COPY config_manager.py .
COPY keyboard_layouts.py .
COPY clipboard_utils.py .
COPY logger.py .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя
RUN useradd -m -u 1000 lipunto
USER lipunto

# Точка входа
ENTRYPOINT ["python", "switch_layout.py"]
```

**docker-compose.yml**:
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

## Мониторинг и логирование

### 1. Структура логов

**Уровни логирования**:
- `DEBUG`: Подробная информация для отладки
- `INFO`: Общая информация о работе системы
- `WARNING`: Предупреждения о потенциальных проблемах
- `ERROR`: Ошибки, требующие внимания
- `CRITICAL`: Критические ошибки, приводящие к остановке

**Формат логов**:
```
2025-08-11 10:05:00 - lipunto - INFO - Starting operation: Layout switch (last)
2025-08-11 10:05:00 - lipunto - DEBUG - Waiting 0.2s for text processing
2025-08-11 10:05:00 - lipunto - INFO - Converting text: 'ghbdtn'
2025-08-11 10:05:00 - lipunto - INFO - Converted text: 'привет'
2025-08-11 10:05:00 - lipunto - INFO - Operation 'Layout switch (last)' completed successfully in 0.234s
```

### 2. Сбор логов

**Сбор системных логов**:
```bash
# Просмотр логов systemd
journalctl -u ydotool.service -f

# Просмотр логов lipunto
tail -f /tmp/lipunto.log

# Сбор логов для отладки
python switch_layout.py last --enable-logging --log-level DEBUG --log-file /tmp/debug.log
```

### 3. Мониторинг производительности

**Метрики для мониторинга**:
- Время выполнения операций
- Частота использования
- Ошибки выполнения
- Использование памяти

**Пример скрипта мониторинга**:
```python
#!/usr/bin/env python3
import psutil
import time
from logger import get_logger

logger = get_logger({"enabled": True, "level": "INFO"})

def monitor_performance():
    """Мониторинг производительности lipunto"""
    process = psutil.Process()

    while True:
        # CPU использование
        cpu_percent = process.cpu_percent()

        # Память
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        # Диск ввод/вывод
        io_counters = process.io_counters()

        logger.info(f"CPU: {cpu_percent}%, Memory: {memory_mb:.1f}MB, "
                   f"Read: {io_counters.read_bytes}, Write: {io_counters.write_bytes}")

        time.sleep(60)  # Каждую минуту
```

### 4. Алерты и уведомления

**Настройка алертов**:
```bash
# Пример cron задания для проверки статуса
* * * * * /usr/local/sbin/switch_layout.py last --enable-logging >> /var/log/lipunto-cron.log 2>&1

# Проверка статуса сервиса
systemctl is-active ydotool.service

# Проверка сокета
ls -la /tmp/.ydotool_socket
```

Эта техническая документация предоставляет полное представление о внутренней работе lipunto, его архитектуре, принципах реализации и лучших практиках для разработки и развертывания.