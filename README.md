# lipunto

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![KDE Plasma](https://img.shields.io/badge/DE-KDE%20Plasma-blue.svg)](https://kde.org/plasma-desktop/)

**lipunto** — утилита для автоматической коррекции опечаток, вызванных переключением раскладки клавиатуры между английской и русской языками.

## 🎯 Основная цель

lipunto решает распространенную проблему пользователей, работающих с двумя языковыми раскладками клавиатуры. При переключении раскладки пользователи часто продолжают печатать на неправильной раскладке, что приводит к опечаткам. Например, вместо "привет" получается "ghbdtn".

lipunto предоставляет автоматическое решение для коррекции таких опечаток с помощью глобальных горячих клавиш.

## ✨ Ключевые особенности

- 🔄 **Автоматическое преобразование текста** между английской и русской раскладками
- ⌨️ **Интеграция с KDE Plasma** через глобальные горячие клавиши
- 🎯 **Два режима работы**: коррекция последнего слова перед курсором и коррекция выделенного текста
- 🖱️ **Использование ydotool** для эмуляции ввода клавиш
- 📋 **Интеграция с системным буфером обмена** через qdbus
- 🔔 **Опциональное отображение уведомлений** после конвертации
- ⚙️ **Гибкая система конфигурации** через аргументы командной строки и переменные окружения
- 📊 **Многоуровневое логирование** с возможностью отключения для производительности

## 📋 Системные требования

- **Python 3.13+**
- **KDE Plasma** (для глобальных горячих клавиш)
- **ydotool** (для эмуляции ввода)
- **qdbus** (для работы с буфером обмена KDE)
- **kdialog** (для отображения уведомлений)

## 🚀 Установка

### 1. Установка системных зависимостей

#### Arch Linux

```bash
# ydotool и сервис
sudo pacman -S ydotool

# Создание systemd сервиса для ydotool
sudo systemctl daemon-reload
sudo systemctl enable ydotool.service
sudo systemctl start ydotool.service

# qdbus и kdialog
sudo pacman -S qt5-tools
```

#### Другие дистрибутивы Linux

```bash
# Установка ydotool (пример для Ubuntu/Debian)
sudo apt install ydotool

# Установка qt5-tools (пример для Ubuntu/Debian)
sudo apt install qt5-tools qtbase5-dev-tools

# Настройка systemd сервиса для ydotool
sudo systemctl daemon-reload
sudo systemctl enable ydotool.service
sudo systemctl start ydotool.service
```

### 2. Настройка прав доступа

Убедитесь в наличии сокета и установите ему права:

```bash
# Проверка наличия сокета
ls -la /tmp/.ydotool_socket

# Установка прав (если сокет существует)
sudo chmod go+rw /tmp/.ydotool_socket
```

### 3. Установка скриптов

Скопируйте скрипты в системные директории:

```bash
# Копирование Python скрипта
sudo cp switch_layout.py /usr/local/sbin/
sudo chmod +x /usr/local/sbin/switch_layout.py

# Копирование shell скриптов
sudo cp sw_last.sh /usr/local/sbin/
sudo cp sw_selected.sh /usr/local/sbin/
sudo chmod +x /usr/local/sbin/sw_last.sh
sudo chmod +x /usr/local/sbin/sw_selected.sh
```

### 4. Установка Python зависимостей

```bash
# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 5. Настройка глобальных горячих клавиш

Импортируйте конфигурацию KDE:

```bash
# Импорт конфигурации
kwriteconfig5 --file kglobalshortcutsrc < lipunto.kksrc
kbuildsycoca5
```

Или добавьте горячие клавиши вручную через:

- `System Settings` → `Shortcuts` → `Custom Shortcuts`

## 🎮 Использование

### Глобальные горячие клавиши

- **Pause** — коррекция последнего слова перед курсором
- **Shift + Pause** — коррекция выделенного текста

### Примеры использования

1. **Коррекция последнего слова**:
   - Напечатайте текст на неправильной раскладке: `ghbdtn`
   - Нажмите `Pause`
   - Текст автоматически преобразуется: `привет`

2. **Коррекция выделенного текста**:
   - Выделите текст на неправильной раскладке: `rfhf`
   - Нажмите `Shift + Pause`
   - Текст автоматически преобразуется: `дом`

### Командная строка

Скрипт также можно использовать напрямую из командной строки:

```bash
# Коррекция последнего слова
python switch_layout.py last

# Коррекция выделенного текста
python switch_layout.py selected

# С включенным логированием
python switch_layout.py last --enable-logging --log-level DEBUG

# С отключенными уведомлениями
python switch_layout.py last --no-popup

# С указанием времени отображения уведомления
python switch_layout.py last --popup-timeout 3
```

## ⚙️ Конфигурация

### Аргументы командной строки

| Аргумент | Описание | По умолчанию |
|----------|----------|-------------|
| `--layout` | Пара раскладок для преобразования (`en_ru`, `ru_en`) | `en_ru` |
| `--delay-clipboard-set` | Задержка при установке содержимого буфера (секунды) | `0.05` |
| `--delay-clipboard-get` | Задержка при получении содержимого буфера (секунды) | `0.1` |
| `--delay-text-process` | Задержка при обработке текста (секунды) | `0.2` |
| `--delay-paste` | Задержка при вставке текста (секунды) | `0.1` |
| `--enable-logging` | Включить логирование | `False` |
| `--log-level` | Уровень логирования (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `WARNING` |
| `--log-file` | Файл для логирования | `/tmp/lipunto.log` |
| `--no-console-log` | Отключить вывод логов в консоль | `False` |
| `--syslog` | Включить вывод логов в системный лог | `False` |
| `--show-popup` | Включить уведомления | `False` |
| `--no-popup` | Отключить уведомления | `False` |
| `--popup-timeout` | Время отображения уведомления (1-60 секунд) | `5` |

### Переменные окружения

Вы также можете настроить lipunto через переменные окружения:

```bash
export LIPUNTO_LAYOUT=ru_en
export LIPUNTO_DELAY_TEXT_PROCESS=0.3
export LIPUNTO_LOG_ENABLED=true
export LIPUNTO_LOG_LEVEL=INFO
export LIPUNTO_UI_SHOW_POPUP=true
export LIPUNTO_UI_POPUP_TIMEOUT=3
```

### Конфигурационный файл

Создайте файл `~/.config/lipunto/config.json`:

```json
{
  "layout": "en_ru",
  "delays": {
    "clipboard_set": 0.05,
    "clipboard_get": 0.1,
    "text_process": 0.2,
    "paste": 0.1
  },
  "logging": {
    "enabled": false,
    "level": "WARNING",
    "file": "/tmp/lipunto.log",
    "console": false,
    "syslog": false
  },
  "ui": {
    "show_popup": false,
    "popup_timeout": 5
  }
}
```

## 🏗️ Архитектура проекта

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Глобальные    │    │   Shell скрипты  │    │   Python скрипт │
│   Горячие клави │    │   (обертки)      │    │   (ядро)        │
│  ши (KDE)       │    │                 │    │                 │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │  Pause      │ │    │ │ sw_last.sh  │ │    │ │switch_layout│ │
│ │  Shift+Pause│ │    │ │ sw_selected.sh│ │    │ │.py          │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Системные     │
                    │   утилиты       │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │   ydotool   │ │
                    │ │   qdbus     │ │
                    │ │   kdialog   │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

### Основные компоненты

1. **[`switch_layout.py`](switch_layout.py)** - Основной Python скрипт
   - Содержит словари для преобразования символов
   - Реализует функции для работы с буфером обмена и эмуляции ввода
   - Обрабатывает два режима работы: "last" и "selected"

2. **[`sw_last.sh`](sw_last.sh)** - Скрипт для коррекции последнего слова
   - Устанавливает права сокета ydotool
   - Вызывает switch_layout.py с параметром "last"

3. **[`sw_selected.sh`](sw_selected.sh)** - Скрипт для коррекции выделенного текста
   - Устанавливает права сокета ydotool
   - Вызывает switch_layout.py с параметром "selected"

4. **[`lipunto.kksrc`](lipunto.kksrc)** - Конфигурация KDE
   - Определяет глобальные горячие клавиши
   - Привязывает Pause к sw_last.sh
   - Привязывает Shift+Pause к sw_selected.sh

5. **[`input-event-codes.h`](input-event-codes.h)** - Заголовочный файл
   - Содержит коды клавиш Linux
   - Используется для эмуляции ввода через ydotool

### Ключевые функции

- **[`switch_text_layout()`](switch_layout.py:47)** - Основная функция преобразования текста
- **[`get_selection()`](clipboard_utils.py:128)** - Получение выделенного текста
- **[`paste_text()`](clipboard_utils.py:148)** - Вставка текста
- **[`select_last_word()`](switch_layout.py:136)** - Выделение последнего слова
- **[`show_popup_message()`](switch_layout.py:88)** - Показ уведомлений

## 🔧 Критические пути выполнения

### Путь 1: Коррекция последнего слова

1. Нажатие Pause
2. Вызов [`sw_last.sh`](sw_last.sh)
3. Вызов [`switch_layout.py`](switch_layout.py) с параметром "last"
4. Выделение последнего слова (Ctrl+Shift+Left)
5. Копирование в буфер (Ctrl+C)
6. Преобразование текста
7. Вставка преобразованного текста (Shift+Insert)
8. Переключение раскладки
9. Показ уведомления

### Путь 2: Коррекция выделенного текста

1. Нажатие Shift+Pause
2. Вызов [`sw_selected.sh`](sw_selected.sh)
3. Вызов [`switch_layout.py`](switch_layout.py) с параметром "selected"
4. Копирование выделенного текста (Ctrl+C)
5. Преобразование текста
6. Вставка преобразованного текста (Shift+Insert)
7. Переключение раскладки
8. Показ уведомления

## 🐛 Отладка и логирование

По умолчанию логирование отключено для улучшения производительности. Для включения логирования используйте:

```bash
# Включение логирования с уровнем DEBUG
python switch_layout.py last --enable-logging --log-level DEBUG

# Логирование в файл
python switch_layout.py last --enable-logging --log-file /var/log/lipunto.log

# Логирование в консоль и системный лог
python switch_layout.py last --enable-logging --console-log --syslog
```

Логи будут содержать информацию о:

- Проверке зависимостей
- Операциях с буфером обмена
- Преобразовании текста
- Ошибках выполнения

## 🛠️ Разработка

### Структура проекта

```
lipunto/
├── .kilocode/
│   └── rules/
│       └── memory-bank/          # Внутренняя документация
├── .venv/                       # Виртуальное окружение
├── .vscode/
│   └── launch.json              # Конфигурация отладчика
├── switch_layout.py             # Основной скрипт
├── config_manager.py            # Менеджер конфигурации
├── keyboard_layouts.py          # Словари преобразования
├── clipboard_utils.py           # Утилиты буфера обмена
├── logger.py                    # Система логирования
├── sw_last.sh                   # Скрипт для последнего слова
├── sw_selected.sh               # Скрипт для выделенного текста
├── lipunto.kksrc                # Конфигурация KDE
├── input-event-codes.h          # Коды клавиш Linux
├── requirements.txt             # Python зависимости
└── README.md                    # Эта документация
```

### Запуск тестов

```bash
# Активация виртуального окружения
source .venv/bin/activate

# Запуск тестов
python -m pytest tests/

# Запуск тестов с покрытием
python -m pytest tests/ --cov=lipunto
```

### Добавление новых раскладок

Для добавления поддержки новых языковых раскладок:

1. Добавьте словарь в [`keyboard_layouts.py`](keyboard_layouts.py)
2. Обновьте функцию [`get_layout_dict()`](keyboard_layouts.py:87)
3. Добавьте тесты для новой раскладки

Пример добавления украинской раскладки:

```python
# В keyboard_layouts.py
en_ua = {
    "q": "й", "w": "ц", "e": "у", "r": "к", "t": "е", "y": "н",
    # ... остальные символы
}

ua_en = {v: k for k, v in en_ua.items()}

# В get_layout_dict()
layout_pairs = {
    "en_ru": (en_ru, ru_en),
    "ru_en": (ru_en, en_ru),
    "en_ua": (en_ua, ua_en),
    "ua_en": (ua_en, en_ua),
}
```

## 📄 Лицензия

Этот проект распространяется под лицензией GNU General Public License v3.0. См. файл [LICENSE](LICENSE) для получения дополнительной информации.

## 🤝 Вклад

Вклады приветствуются! Пожалуйста, не стесняйтесь создавать pull request или открывать issue для обсуждения.

### Развитие проекта

Проект активно развивается и планируется добавить:

- Поддержку большего количества языковых пар
- Умное определение языка текста
- Интеграцию с другими desktop средами
- Графический интерфейс настройки

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте [Issues](https://github.com/yourusername/lipunto/issues)
2. Создайте новый issue с подробным описанием проблемы
3. Для вопросов по установке проверьте раздел [Установка](#установка)

## 📝 История изменений

### v1.0.0 (2025-08-10)

- Первая стабильная версия
- Поддержка английского и русского языков
- Д режима работы: коррекция последнего слова и выделенного текста
- Интеграция с KDE Plasma через глобальные горячие клавиши
- Гибкая система конфигурации
- Многоуровневое логирование

---

**lipunto** — сделает вашу работу с двумя языками комфортной и продуктивной! 🚀

## 📚 Документация проекта

| Тип документации | Описание |
|------------------|----------|
| [📖 Руководство пользователя](docs/USER_GUIDE.md) | Полное руководство по использованию, настройке и устранению неполадок |
| [🔧 Руководство разработчика](docs/DEVELOPER_GUIDE.md) | Для разработчиков: архитектура, тестирование, внесение вклада |
| [🛠️ Техническая документация](docs/TECHNICAL.md) | Подробные технические аспекты и API |
| [📋 Оглавление документации](docs/README.md) | Навигация по всей документации проекта |

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие lipunto!

### Как внести вклад

1. **Форкните репозиторий**
2. **Создайте ветку для вашей функции**:

   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Внесите изменения** и добавьте тесты
4. **Проверьте стиль кода**:

   ```bash
   black . && flake8 .
   ```

5. **Сделайте коммит**:

   ```bash
   git commit -m 'feat: add amazing feature'
   ```

6. **Отправьте изменения**:

   ```bash
   git push origin feature/amazing-feature
   ```

7. **Создайте Pull Request**

### Требования к PR

- Все тесты должны проходить
- Код должен соответствовать стилю проекта
- Должны быть добавлены тесты для нового функционала
- Должна быть обновлена документация
- PR должен содержать описание изменений

## 🆘 Поддержка

Если у вас возникли проблемы:

1. 📖 Воспользуйтесь [руководством пользователя](docs/USER_GUIDE.md)
2. 🔍 Проверьте [раздел устранения неполадок](docs/USER_GUIDE.md#устранение-неполадок)
3. 🐛 Создайте [issue на GitHub](https://github.com/yourusername/lipunto/issues)
4. 💬 Участвуйте в [обсуждениях](https://github.com/yourusername/lipunto/discussions)

## 📄 Лицензия

Этот проект распространяется под лицензией GPL v3. Подробности смотрите в файле [LICENSE](LICENSE).

## 🙏 Благодарности

- [ydotool](https://github.com/iamtalhaasghar/ydotool) - эмуляция ввода
- [KDE Plasma](https://kde.org/plasma-desktop/) - среда рабочего стола
- [Pydantic](https://pydantic-docs.helpmanual.io/) - валидация данных

---

**[📚 Полная документация](docs/README.md)** | **[🔧 Руководство разработчика](docs/DEVELOPER_GUIDE.md)** | **[📖 Руководство пользователя](docs/USER_GUIDE.md)**
