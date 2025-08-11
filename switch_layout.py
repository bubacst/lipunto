#!/usr/bin/env python3
import subprocess
import sys
import time

from clipboard_utils import ClipboardManager
from config_manager import (
    DelaysConfig,
    LipuntoSettings,
    LoggingConfig,
    UIConfig,
    create_arg_parser,
)
from keyboard_layouts import get_layout_dict
from logger import LogContext, init_logger


class LayoutSwitcher:
    """Класс для переключения раскладки клавиатуры и преобразования текста"""

    settings: LipuntoSettings

    def __init__(self, settings):
        """
        Инициализация LayoutSwitcher

        Args:
            settings: Экземпляр LipuntoSettings. Если None, используется глобальный.
        """
        # Инициализация конфигурации
        self.settings = settings
        # Инициализация логирования
        logging_config = self.settings.get_logging_config()
        self.logger = init_logger(logging_config.model_dump())

        # Получение настроек из Settings
        self.show_popup = self.settings.ui.show_popup
        self.layout = self.settings.get_layout()

        self.clipboard_manager = ClipboardManager()
        self.commands = ["qdbus", "kdialog", "ydotool"]

        self.logger.info(
            f"LayoutSwitcher initialized with layout: {self.layout}, popup: {self.show_popup}"
        )

    def switch_text_layout(self, text: str) -> str:
        """Преобразование текста между раскладками клавиатуры

        Args:
            text (str): Входной текст для преобразования

        Returns:
            str: Преобразованный текст
        """

        forward_dict, reverse_dict = get_layout_dict(self.settings.layout)
        result = []
        for char in text:
            if char in forward_dict:
                result.append(forward_dict[char])
            elif char in reverse_dict:
                result.append(reverse_dict[char])
            else:
                result.append(char)
        return "".join(result)

    def check_dependencies(self) -> None:
        """Проверка наличия необходимых утилит"""
        self.logger.info("Checking dependencies...")
        try:
            result = subprocess.check_output(
                ["which"] + self.commands, stderr=sys.stdout
            )
            self.logger.debug(f"Dependencies check result: {result.decode().strip()}")
        except FileNotFoundError:
            error_msg = "Команда 'which' не найдена. Убедитесь, что она установлена и доступна в вашем PATH."
            self.logger.error(error_msg)
            print(error_msg, file=sys.stderr)
            exit(1)
        except subprocess.CalledProcessError as e:
            error_msg = f"Не удалось найти команду.Убедитесь что утилиты {self.commands} установлены\n{e.output.decode().strip()}"
            self.logger.error(error_msg)
            print(error_msg, file=sys.stderr)
            exit(1)
        self.logger.info("All dependencies are available")

    def show_popup_message(self, text: str, error: bool = False) -> None:
        """Показ уведомления через kdialog

        Args:
            text (str): Текст сообщения
            error (bool): Показывать как ошибку
        """
        if not self.show_popup:
            self.logger.debug("Popup notifications are disabled")
            return

        self.logger.info(
            f"Showing {'error' if error else 'info'} popup: {text[:50]}..."
        )
        try:
            subprocess.run(
                [
                    "kdialog",
                    "--title",
                    "EnRu",
                    "--error" if error else "--passivepopup",
                    text,
                    str(self.settings.ui.popup_timeout),
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to show popup: {e}")

    def run_ydotool_command(self, commands: list) -> None:
        """Выполнение команды ydotool

        Args:
            commands (list): Команда для выполнения
        """
        self.clipboard_manager.run_ydotool_command(commands)

    def run_qbus_command(self, commands: list) -> str:
        """Выполнение команды qbus

        Args:
            commands (list): Команда для выполнения

        Returns:
            str: Результат выполнения команды
        """
        return self.clipboard_manager.run_qbus_command(commands)

    def select_last_word(self) -> None:
        """Выделение последнего слова с помощью ydotool (Ctrl+Shift+Left)
        Коды клавиш: 29=Ctrl, 42=Shift, 105=Left
        """
        self.logger.debug("Selecting last word with Ctrl+Shift+Left")
        self.run_ydotool_command(
            ["key", "29:1", "42:1", "105:1", "105:0", "42:0", "29:0"]
        )

    def get_last_word(self) -> str:
        """Выделение последнего слова и возврат его из буфера обмена"""
        self.logger.debug("Getting last word from clipboard")
        self.select_last_word()
        return self.clipboard_manager.get_selection()

    def switch_kde_layout(self) -> None:
        """Переключение на следующую раскладку клавиатуры в KDE Plasma через D-Bus"""
        self.logger.debug("Switching KDE keyboard layout")
        self.run_qbus_command(["org.kde.keyboard", "/Layouts", "switchToNextLayout"])

    def process_last_word(self) -> str:
        """Обработка последнего слова перед курсором

        Returns:
            str: Текст последнего слова или пустая строка
        """
        delay = self.settings.delays.text_process
        self.logger.debug(f"Waiting {delay}s for text processing")
        time.sleep(delay)
        return self.get_last_word()

    def process_selected_text(self) -> str:
        """Обработка выделенного текста

        Returns:
            str: Выделенный текст или пустая строка
        """
        delay = self.settings.delays.text_process
        self.logger.debug(f"Waiting {delay}s for text processing")
        time.sleep(delay)
        return self.clipboard_manager.get_selection()

    def convert_and_replace(self, text: str) -> None:
        """Преобразование текста и замена в приложении

        Args:
            text (str): Исходный текст для преобразования
        """
        self.logger.info(f"Converting text: '{text}'")
        converted_text = self.switch_text_layout(text)
        self.logger.info(f"Converted text: '{converted_text}'")

        self.logger.debug("Pasting converted text")
        self.clipboard_manager.paste_text(converted_text)

        self.logger.debug("Switching keyboard layout")
        self.switch_kde_layout()

        if self.show_popup:
            self.show_popup_message(f"{text}\n{converted_text}")

    def run(self, action: str) -> None:
        """Основной метод запуска переключения раскладки

        Args:
            action (str): Действие ('last' или 'selected')
        """
        with LogContext(f"Layout switch ({action})", self.logger):
            self.check_dependencies()

            selection_text = ""
            if action == "last":
                self.logger.info("Processing last word")
                selection_text = self.process_last_word()
            elif action == "selected":
                self.logger.info("Processing selected text")
                selection_text = self.process_selected_text()

            if selection_text:
                self.convert_and_replace(selection_text)
            else:
                self.logger.warning("No text selected or last word found")
                if self.show_popup:
                    self.show_popup_message(
                        "No text selected or last word found", error=True
                    )


def main():
    """Основная логика скрипта."""
    parser = create_arg_parser()
    args = parser.parse_args()

    # Инициализация конфигурации с аргументами командной строки
    delays_config = DelaysConfig(
        clipboard_set=args.delay_clipboard_set or 0.05,
        clipboard_get=args.delay_clipboard_get or 0.05,
        text_process=args.delay_text_process or 0.05,
        paste=args.delay_paste or 0.1,
    )

    # Определяем, включено ли логирование
    logging_enabled = args.enable_logging

    logging_config = LoggingConfig(
        enabled=logging_enabled,
        level=args.log_level if logging_enabled and args.log_level else "WARNING",
        file=args.log_file or "/tmp/lipunto.log",
        console=not args.no_console_log
        if logging_enabled and args.no_console_log is not None
        else False,
        syslog=args.syslog or False,
    )

    ui_config = UIConfig(
        show_popup=args.show_popup if args.show_popup else False,
        popup_timeout=args.popup_timeout or 5,
    )

    settings = LipuntoSettings(
        layout=args.layout, delays=delays_config, logging=logging_config, ui=ui_config
    )

    # Создаем LayoutSwitcher с передачей экземпляра Settings
    switcher = LayoutSwitcher(settings)
    switcher.run(args.action)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
