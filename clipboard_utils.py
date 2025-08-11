#!/usr/bin/env python3
import subprocess
import sys
import time

from logger import get_logger


class ClipboardManager:
    """Класс для управления буфером обмена в KDE Plasma"""

    # Атрибут класса для хранения истории буфера обмена
    history = []

    def __init__(self):
        self._cached_history = []
        self.logger = get_logger()

    def get_class_history(self) -> list:
        """Получает историю буфера обмена из атрибута класса"""
        return self.history

    def set_class_history(self, history: list) -> None:
        """Устанавливает историю буфера обмена в атрибут класса"""
        self.history = history

    def run_qbus_command(self, commands: list) -> str:
        """
        Run qbus command
        """
        commands.insert(0, "qdbus")
        return self._run_command(commands)

    def run_ydotool_command(self, commands: list) -> None:
        """
        Run ydotool command
        """
        commands.insert(0, "ydotool")
        self._run_command(commands)

    def _run_command(self, commands: list) -> str:
        """
        Run command
        """
        result = ""
        error_text = ""
        try:
            result = (
                subprocess.check_output(commands, stderr=sys.stdout).decode().strip()
            )
        except FileNotFoundError:
            # This error means the commands[0] command itself was not found.
            error_text = f"Команда {commands[0]} не найдена. Убедитесь, что она установлена и доступна в вашем PATH (например, через пакет 'qttools5-dev-tools')."
        except subprocess.CalledProcessError as e:
            # These errors mean commands[0] ran but failed to execute.
            error_text = f"Команда {commands[0]} завершилась с ошибкой:\n{e.output.decode().strip()}"

        if error_text:
            print(error_text, file=sys.stderr)
            raise RuntimeError(error_text)

        return result

    def get_clipboard_last_item(self) -> str:
        """
        Get last item from clipboard
        """
        return self.run_qbus_command(
            [
                "org.kde.klipper",
                "/klipper",
                "getClipboardContents",
            ]
        )

    def clear_clipboard_contents(self):
        """
        Clear clipboard contents
        """
        self.run_qbus_command(
            [
                "org.kde.klipper",
                "/klipper",
                "clearClipboardContents",
            ]
        )

    def set_clipboard_last_item(self, item: str, delay: float = 0):
        """
        Set clipboard last item
        """
        self.run_qbus_command(
            ["org.kde.klipper", "/klipper", "setClipboardContents", item]
        )
        self.logger.debug(f"Waiting {delay}s for clipboard set operation")
        time.sleep(delay)

    def save_clipboard_history(self) -> list:
        """Сохраняет текущую историю буфера обмена в список и атрибут класса"""
        history = []
        index = 0
        while True:
            item = self.run_qbus_command(
                ["org.kde.klipper", "/klipper", "getClipboardHistoryItem", str(index)]
            )
            if not item:  # Пустая строка означает конец истории
                break
            history.append(item)
            index += 1
        self.history = history
        return history

    def get_cached_clipboard_history(self) -> list:
        """Получает закэшированную историю или обновляет ее"""
        if not self.history:
            self.history = self.save_clipboard_history()
        return self.history

    def restore_clipboard_history(self) -> None:
        """Восстанавливает историю буфера обмена из списка и обновляет атрибут класса"""
        # Сначала очищаем текущую историю
        self.run_qbus_command(["org.kde.klipper", "/klipper", "clearClipboardHistory"])

        # Затем восстанавливаем элементы в обратном порядке
        for item in reversed(self.history):
            self.set_clipboard_last_item(item)

    def get_selection(self, delay: float = 0) -> str:
        """Get the last word using ydotool (Ctrl+C) and copy it to clipboard
        key codes: 29=Ctrl, 46=C
        """
        # Сохраняем текущую историю
        last_item = self.get_clipboard_last_item()
        self.save_clipboard_history()
        # Выполняем копирование
        self.run_ydotool_command(["key", "29:1", "46:1", "46:0", "29:0"])  # Ctrl+C
        # Ждем немного, чтобы история обновилась
        self.logger.debug(f"Waiting {delay}s for clipboard get operation")
        time.sleep(delay)
        # Получаем скопированный текст
        selection = self.get_clipboard_last_item()
        self.restore_clipboard_history()
        if last_item:
            self.set_clipboard_last_item(last_item)

        return selection

    def paste_text(self, new_text: str, delay: float = 0) -> None:
        """Pastes text using ydotool (Shift+Insert).
        key codes: 42=Shift, 110=Insert
        """
        last_item = self.get_clipboard_last_item()
        self.set_clipboard_last_item(new_text)
        self.run_ydotool_command(
            ["key", "42:1", "110:1", "110:0", "42:0"]
        )  # Shift+Insert
        self.logger.debug(f"Waiting {delay}s for clipboard paste operation")
        time.sleep(delay)
        self.restore_clipboard_history()
        if last_item:
            self.set_clipboard_last_item(last_item)
