#!/usr/bin/env python3
"""Тестовый скрипт для проверки работы новой конфигурации с pydantic settings"""

from config_manager import get_settings, get_delay, get_logging_config, get_ui_config, get_layout

# Создаем экземпляр настроек
settings = get_settings("~/.config/lipunto/config.json")

print(f"Layout from config: {get_layout()}")
print(f"UI config: {get_ui_config()}")
print(f"Logging config: {get_logging_config()}")
print(f"Delay for clipboard_set: {get_delay('clipboard_set')}")
print(f"Full settings: {settings.model_dump()}")