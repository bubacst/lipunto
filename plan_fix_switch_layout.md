# План инициализации классов config переменными из args

## Цель
Инициализировать классы config в строке 229 файла `switch_layout.py` переменными из `args` для поддержки аргументов командной строки.

## Текущая ситуация
В строке 229 сейчас:
```python
delays_config = DelaysConfig()
logging_config = LoggingConfig()
ui_config = UIConfig()
```

Все классы инициализируются без параметров, используются значения по умолчанию.

## Анализ доступных аргументов

### UIConfig
- `--show-popup`: включить уведомления
- `--no-popup`: отключить уведомления
- Взаимоисключающие аргументы (mutually exclusive group)

### DelaysConfig
- `--delay-clipboard-set`: задержка при установке буфера
- `--delay-clipboard-get`: задержка при получении буфера
- `--delay-text-process`: задержка при обработке текста
- `--delay-paste`: задержка при вставке

### LoggingConfig
- `--log-level`: уровень логирования
- `--log-file`: файл логирования
- `--no-console-log`: отключить консольный вывод
- `--syslog`: включить системный лог

### LipuntoSettings
- `--layout`: пара раскладок для преобразования

## План реализации

### Шаг 1: UIConfig
```python
# Вместо:
ui_config = UIConfig()

# Будет:
ui_config = UIConfig(
    show_popup=args.show_popup if args.show_popup else not args.no_popup
)
```

### Шаг 2: DelaysConfig
```python
# Вместо:
delays_config = DelaysConfig()

# Будет:
delays_config = DelaysConfig(
    clipboard_set=args.delay_clipboard_set,
    clipboard_get=args.delay_clipboard_get,
    text_process=args.delay_text_process,
    paste=args.delay_paste
)
```

### Шаг 3: LoggingConfig
```python
# Вместо:
logging_config = LoggingConfig()

# Будет:
logging_config = LoggingConfig(
    level=args.log_level,
    file=args.log_file,
    console=not args.no_console_log,
    syslog=args.syslog
)
```

### Шаг 4: LipuntoSettings
```python
# Вместо:
settings = LipuntoSettings(
    delays=delays_config, logging=logging_config, ui=ui_config
)

# Будет:
settings = LipuntoSettings(
    layout=args.layout,
    delays=delays_config,
    logging=logging_config,
    ui=ui_config
)
```

## Обработка обратной совместимости
- Если аргумент не передан, использовать `None` в конструкторе
- Классы BaseSettings автоматически используют значения по умолчанию для `None`
- Это обеспечит полную обратную совместимость

## Пример полной реализации
```python
def main():
    """Основная логика скрипта."""
    parser = create_arg_parser()
    args = parser.parse_args()

    # Инициализация конфигурации с аргументами командной строки
    delays_config = DelaysConfig(
        clipboard_set=args.delay_clipboard_set,
        clipboard_get=args.delay_clipboard_get,
        text_process=args.delay_text_process,
        paste=args.delay_paste
    )

    logging_config = LoggingConfig(
        level=args.log_level,
        file=args.log_file,
        console=not args.no_console_log,
        syslog=args.syslog
    )

    ui_config = UIConfig(
        show_popup=args.show_popup if args.show_popup else not args.no_popup
    )

    settings = LipuntoSettings(
        layout=args.layout,
        delays=delays_config,
        logging=logging_config,
        ui=ui_config
    )

    # Создаем LayoutSwitcher с передачей экземпляра Settings
    switcher = LayoutSwitcher(settings)
    switcher.run(args.action)
```

## Тестирование
1. Проверить работу без аргументов (должно работать как раньше)
2. Проверить работу с аргументами (--show-popup, --layout и т.д.)
3. Проверить взаимоисключающие аргументы (--show-popup и --no-popup)
4. Проверить числовые аргументы (--delay-text-process и т.д.)

## Преимущества
- Полная поддержка аргументов командной строки
- Обратная совместимость
- Гибкая конфигурация через CLI
- Читаемый и поддерживаемый код