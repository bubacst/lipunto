#!/usr/bin/env python3
"""
Менеджер конфигурации для lipunto
Предоставляет гибкую систему конфигурации с поддержкой переменных окружения
и аргументов командной строки
"""

import argparse

from pydantic import Field
from pydantic_settings import BaseSettings


class DelaysConfig(BaseSettings):
    """Конфигурация задержек"""

    clipboard_set: float = Field(
        0.05, ge=0.0, le=10.0, description="Задержка при установке содержимого буфера"
    )
    clipboard_get: float = Field(
        0.1, ge=0.0, le=10.0, description="Задержка при получении содержимого буфера"
    )
    text_process: float = Field(
        0.2, ge=0.0, le=10.0, description="Задержка при обработке текста"
    )
    paste: float = Field(
        0.1, ge=0.0, le=10.0, description="Задержка при вставке текста"
    )

    class Config:
        populate_by_name = True
        validate_assignment = True
        env_prefix = "LIPUNTO_DELAY_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class LoggingConfig(BaseSettings):
    """Конфигурация логирования"""

    enabled: bool = Field(False, description="Включить логирование")
    level: str = Field(
        "WARNING",
        pattern="^(DEBUG|INFO|WARNING|ERROR)$",
        description="Уровень логирования",
    )
    file: str = Field("/tmp/lipunto.log", description="Файл для логирования")
    console: bool = Field(False, description="Выводить в консоль")
    syslog: bool = Field(False, description="Выводить в системный лог")

    class Config:
        populate_by_name = True
        validate_assignment = True
        env_prefix = "LIPUNTO_LOG_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class UIConfig(BaseSettings):
    """Конфигурация UI"""

    show_popup: bool = Field(False, description="Показывать уведомления")
    popup_timeout: int = Field(
        5, ge=1, le=60, description="Время отображения уведомления"
    )

    class Config:
        populate_by_name = True
        validate_assignment = True
        env_prefix = "LIPUNTO_UI_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class LipuntoSettings(BaseSettings):
    """Основная модель настроек lipunto"""

    layout: str = Field("en_ru", description="Пара раскладок для преобразования")
    delays: DelaysConfig
    logging: LoggingConfig
    ui: UIConfig

    def get_layout(self) -> str:
        """Получить текущую пару раскладок"""
        return self.layout

    def get_logging_config(self) -> LoggingConfig:
        """Получить конфигурацию логирования"""
        return self.logging

    class Config:
        populate_by_name = True
        validate_assignment = True
        env_prefix = "LIPUNTO_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def create_arg_parser() -> argparse.ArgumentParser:
    """Создает парсер аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Переключатель раскладки клавиатуры")

    # Группа аргументов для задержек
    delay_group = parser.add_argument_group("Задержки")
    delay_group.add_argument(
        "--delay-clipboard-set",
        type=float,
        help="Задержка при установке содержимого буфера (секунды)",
    )
    delay_group.add_argument(
        "--delay-clipboard-get",
        type=float,
        help="Задержка при получении содержимого буфера (секунды)",
    )
    delay_group.add_argument(
        "--delay-text-process",
        type=float,
        help="Задержка при обработке текста (секунды)",
    )
    delay_group.add_argument(
        "--delay-paste", type=float, help="Задержка при вставке текста (секунды)"
    )

    # Группа аргументов для логирования
    log_group = parser.add_argument_group("Логирование")
    log_group.add_argument(
        "--enable-logging",
        action="store_true",
        help="Включить логирование (отключено по умолчанию)"
    )
    log_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Уровень логирования (только при --enable-logging)"
    )
    log_group.add_argument("--log-file", help="Файл для логирования")
    log_group.add_argument(
        "--no-console-log",
        action="store_true",
        help="Отключить вывод логов в консоль (только при --enable-logging)"
    )
    log_group.add_argument(
        "--syslog", action="store_true", help="Включить вывод логов в системный лог (только при --enable-logging)"
    )

    # Группа аргументов для UI
    ui_group = parser.add_argument_group("Интерфейс")
    ui_group.add_argument(
        "--show-popup", action="store_true", help="Включить уведомления"
    )
    ui_group.add_argument(
        "--no-popup", action="store_true", help="Отключить уведомления"
    )
    ui_group.add_argument(
        "--popup-timeout", type=int, help="Время отображения уведомления (1-60 секунд)"
    )

    # Основные аргументы
    parser.add_argument(
        "--layout",
        default="en_ru",
        choices=["en_ru", "ru_en"],
        help="Пара раскладок для преобразования (по умолчанию: en_ru)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "action",
        default="last",
        nargs="?",
        choices=("last", "selected"),
        help='Действие: "last" для последнего слова, "selected" для выделенного текста (по умолчанию: last)',
    )

    return parser
