# lipunto - Технологии

## Используемые технологии

### Основные технологии

- **Python 3.13.5** - основной язык программирования
- **KDE Plasma** - среда рабочего стола для глобальных горячих клавиш
- **ydotool** - утилита для эмуляции ввода клавиш
- **qdbus** - утилита для взаимодействия с D-Bus KDE
- **kdialog** - утилита для отображения уведомлений в KDE

### Инструменты разработки

- **VS Code** - основная среда разработки
- **Debugpy** - отладчик для Python в VS Code
- **Virtual Environment** - изолированное окружение Python (.venv)

## Структура проекта

```
lipunto/
├── .kilocode/
│   └── rules/
│       └── memory-bank/
│           ├── brief.md
│           ├── product.md
│           ├── context.md
│           ├── architecture.md
│           └── tech.md
├── .venv/
│   ├── pyvenv.cfg
│   └── .gitignore
├── .vscode/
│   └── launch.json
├── switch_layout.py
├── sw_last.sh
├── sw_selected.sh
├── lipunto.kksrc
├── input-event-codes.h
└── README.md
```

## Конфигурация окружения

### Python окружение

- Версия Python: 3.13.5
- Тип окружения: Virtual Environment
- Расположение: `.venv/`
- Системные пакеты не включены

### VS Code конфигурация

- Конфигурация отладчика в `.vscode/launch.json`
- Две конфигурации для отладки:
  - "Switch last" - отладка коррекции последнего слова
  - "Switch selected" - отладка коррекции выделенного текста

## Системные зависимости

### Требуемые пакеты для Arch Linux

```bash
# ydotool и сервис
sudo pacman -S ydotool
# Создание systemd сервиса для ydotool
sudo systemctl daemon-reload
sudo systemctl enable ydotool.service
sudo systemctl start ydotool.service

# qdbus и kdialog
sudo pacman -S qt5-tools

# Настройка прав сокета
sudo chmod go+rw /tmp/.ydotool_socket
```

### Требуемые пакеты для других дистрибутивов

- **ydotool** - пакет для эмуляции ввода
- **qt5-tools** - содержит qdbus и kdialog
- Настройка systemd сервиса для ydotool

## Технические детали

### Коды клавиш Linux

Проект использует заголовочный файл [`input-event-codes.h`](input-event-codes.h) для получения кодов клавиш:

- KEY_LEFT (105) - стрелка влево
- KEY_INSERT (110) - Insert
- KEY_LEFTCTRL (29) - Ctrl
- KEY_LEFTSHIFT (42) - Shift
- KEY_C (46) - C

### D-Bus интерфейсы KDE

Используемые D-Bus интерфейсы:

- `org.kde.klipper` - работа с буфером обмена
- `org.kde.keyboard` - переключение раскладки клавиатуры

### Сокет ydotool

- Путь: `/tmp/.ydotool_socket`
- Права доступа: `go+rw` (чтение и запись для группы и других)
- Необходим для работы ydotool от имени пользователя

## Рекомендации по установке и настройке

1. Установить системные зависимости
2. Настроить systemd сервис для ydotool
3. Установить права на сокет ydotool
4. Скопировать скрипты в `/usr/local/sbin/`
5. Импортировать конфигурацию KDE через `kwriteconfig5`
6. Перезагрузить конфигурацию KDE
7. Проверить работу горячих клавиш

## Возможные проблемы и решения

1. **Проблема**: ydotool не работает
   **Решение**: Проверить работу сервиса ydotool и права на сокет

2. **Проблема**: qdbus не находит интерфейсы
   **Решение**: Убедиться, что установлены qt5-tools

3. **Проблема**: kdialog не показывает уведомления
   **Решение**: Проверить работу KDE и установку qt5-tools

4. **Проблема**: Глобальные клавиши не работают
   **Решение**: Проверить импорт конфигурации и перезапуск KDE

## Настройка отображения уведомлений

- Опциональное отображение уведомлений после конвертации текста
- Настройка через аргументы командной строки: `--no-popup` для отключения уведомлений
- Поддержка глобальных настроек через конфигурационный файл `~/.config/lipunto/config.json`
