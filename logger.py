#!/usr/bin/env python3
"""
Модуль логирования для lipunto
Предоставляет многоуровневое логирование с разными выводами
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class LipuntoLogger:
    """Класс для логирования lipunto"""

    # Уровни логирования
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация логгера

        Args:
            config: Конфигурация логирования
        """
        self.config = config or {}
        self.logger = logging.getLogger("lipunto")
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Проверяем, включено ли логирование
        enabled = self.config.get("enabled", False)
        if not enabled:
            # Устанавливаем уровень, чтобы ничего не логировать
            self.logger.setLevel(logging.CRITICAL + 1)
            return

        # Очищаем существующие обработчики
        self.logger.handlers.clear()

        # Устанавливаем уровень логирования
        self.logger.setLevel(self._get_log_level())

        # Обработчик для консоли
        if self.config.get("console", False):
            self.console_handler = logging.StreamHandler(sys.stderr)
            self.console_handler.setLevel(self._get_log_level())
            self.console_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.console_handler)

        # Обработчик для файла
        log_file = self.config.get("file")
        if log_file:
            try:
                # Создаем директорию если не существует
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setLevel(self._get_log_level())
                file_handler.setFormatter(self.formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                # Используем консольный обработчик для ошибки, если он существует
                if hasattr(self, 'console_handler'):
                    print(f"Failed to setup file handler: {e}", file=sys.stderr)
                else:
                    print(f"Failed to setup file handler: {e}")

        # Обработчик для системного лога
        if self.config.get("syslog", False):
            try:
                syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
                syslog_handler.setLevel(self._get_log_level())
                syslog_handler.setFormatter(self.formatter)
                self.logger.addHandler(syslog_handler)
            except Exception as e:
                # Используем консольный обработчик для ошибки, если он существует
                if hasattr(self, 'console_handler'):
                    print(f"Failed to setup syslog handler: {e}", file=sys.stderr)
                else:
                    print(f"Failed to setup syslog handler: {e}")

    def _get_log_level(self) -> int:
        """Получает уровень логирования из конфигурации"""
        # Если логирование отключено, возвращаем максимальный уровень
        if not self.config.get("enabled", False):
            return logging.CRITICAL + 1

        level = self.config.get("level", "WARNING").upper()
        return self.LEVELS.get(level, logging.WARNING)

    def debug(self, message: str, *args, **kwargs) -> None:
        """Логирование отладочной информации"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Логирование информационных сообщений"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Логирование предупреждений"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Логирование ошибок"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Логирование критических ошибок"""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Логирование исключений"""
        self.logger.exception(message, *args, **kwargs)


# Глобальный экземпляр логгера
_logger_instance = None


def get_logger(config: Optional[Dict[str, Any]] = None) -> LipuntoLogger:
    """Получает глобальный экземпляр логгера"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = LipuntoLogger(config)
    return _logger_instance


def init_logger(config: Optional[Dict[str, Any]] = None) -> LipuntoLogger:
    """Инициализирует глобальный экземпляр логгера"""
    global _logger_instance
    _logger_instance = LipuntoLogger(config)
    return _logger_instance


def debug(message: str, *args, **kwargs) -> None:
    """Удобная функция для отладочного логирования"""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs) -> None:
    """Удобная функция для информационного логирования"""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs) -> None:
    """Удобная функция для логирования предупреждений"""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs) -> None:
    """Удобная функция для логирования ошибок"""
    get_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs) -> None:
    """Удобная функция для логирования критических ошибок"""
    get_logger().critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs) -> None:
    """Удобная функция для логирования исключений"""
    get_logger().exception(message, *args, **kwargs)


class LogContext:
    """Контекстный менеджер для логирования"""

    def __init__(self, operation: str, logger: Optional[LipuntoLogger] = None):
        """
        Инициализация контекста

        Args:
            operation: Название операции
            logger: Экземпляр логгера
        """
        self.operation = operation
        self.logger = logger or get_logger()
        self.start_time = None

    def __enter__(self):
        """Вход в контекст"""
        self.start_time = datetime.now()
        self.logger.info(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста"""
        if self.start_time is not None:
            duration = datetime.now() - self.start_time
            if exc_type is None:
                self.logger.info(
                    f"Operation '{self.operation}' completed successfully in {duration.total_seconds():.3f}s"
                )
            else:
                self.logger.error(
                    f"Operation '{self.operation}' failed after {duration.total_seconds():.3f}s: {exc_val}"
                )
                return False  # Не подавляем исключение
