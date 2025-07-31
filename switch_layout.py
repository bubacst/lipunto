#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time


class Result:
    error: int
    text: str
    clipboard: str

    def __init__(self, error: int = 0, text: str = "", clipboard: str = ""):
        self.error = error
        self.text = text
        self.clipboard = clipboard


# Словари для замены символов
en_ru = {
    "q": "й",
    "w": "ц",
    "e": "у",
    "r": "к",
    "t": "е",
    "y": "н",
    "u": "г",
    "i": "ш",
    "o": "щ",
    "p": "з",
    "[": "х",
    "]": "ъ",
    "a": "ф",
    "s": "ы",
    "d": "в",
    "f": "а",
    "g": "п",
    "h": "р",
    "j": "о",
    "k": "л",
    "l": "д",
    ";": "ж",
    "'": "э",
    "z": "я",
    "x": "ч",
    "c": "с",
    "v": "м",
    "b": "и",
    "n": "т",
    "m": "ь",
    ",": "б",
    ".": "ю",
    "/": ".",
    "Q": "Й",
    "W": "Ц",
    "E": "У",
    "R": "К",
    "T": "Е",
    "Y": "Н",
    "U": "Г",
    "I": "Ш",
    "O": "Щ",
    "P": "З",
    "{": "Х",
    "}": "Ъ",
    "A": "Ф",
    "S": "Ы",
    "D": "В",
    "F": "А",
    "G": "П",
    "H": "Р",
    "J": "О",
    "K": "Л",
    "L": "Д",
    ":": "Ж",
    '"': "Э",
    "Z": "Я",
    "X": "Ч",
    "C": "С",
    "V": "М",
    "B": "И",
    "N": "Т",
    "M": "Ь",
    "<": "Б",
    ">": "Ю",
    "?": ",",
}

ru_en = {v: k for k, v in en_ru.items()}
commands = ["qdbus", "kdialog", "ydotool"]


def switch_text_layout(text: str) -> str:
    """Function to switch text layout between English and Russian and vice versa"""
    result = []
    for char in text:
        if char in en_ru:
            result.append(en_ru[char])
        elif char in ru_en:
            result.append(ru_en[char])
        else:
            result.append(char)
    return "".join(result)


def which():
    """
    Check qbus, kdialog, ydotool
    """
    try:
        subprocess.check_output(["which"] + commands, stderr=sys.stdout)
    except FileNotFoundError:
        print(
            "Команда 'which' не найдена. Убедитесь, что она установлена и доступна в вашем PATH."
        )
        exit(1)
    except subprocess.CalledProcessError as e:
        print(
            f"Не удалось найти команду.Убедитесь что утилиты {commands} установлены\n{e.output.decode().strip()}"
        )
        exit(1)


def popup_message(text: str, error=False) -> None:
    subprocess.run(
        [
            "kdialog",
            "--title",
            "EnRu",
            "--error" if error else "--passivepopup",
            text,
            "5",
        ]
    )


def run_command(commands: list) -> str:
    """
    Run command
    """
    result = ""
    error_text = ""
    try:
        result = subprocess.check_output(commands, stderr=sys.stdout).decode().strip()
    except FileNotFoundError:
        # This error means the commands[0] command itself was not found.
        error_text = f"Команда {commands[0]} не найдена. Убедитесь, что она установлена и доступна в вашем PATH (например, через пакет 'qttools5-dev-tools')."
    except subprocess.CalledProcessError as e:
        # These errors mean commands[0] ran but failed to execute.
        error_text = (
            f"Команда {commands[0]} завершилась с ошибкой:\n{e.output.decode().strip()}"
        )

    if error_text:
        popup_message(error_text, True)
        exit(1)

    return result


def run_ydotool_command(commands: list) -> None:
    """
    Run ydotool command
    """
    commands.insert(0, "ydotool")
    run_command(commands)


def run_qbus_command(commands: list) -> str:
    """
    Run qbus command
    """
    commands.insert(0, "qdbus")
    return run_command(commands)


def select_last_word() -> None:
    """Selects the last word using ydotool (Ctrl+Shift+Left).
    key codes: 29=Ctrl, 42=Shift, 105=Left
    """
    run_ydotool_command(["key", "29:1", "42:1", "105:1", "105:0", "42:0", "29:0"])


def paste_text(text: str) -> None:
    """Pastes text using ydotool (Shift+Insert)."""
    # Set the new clipboard text
    run_qbus_command(["org.kde.klipper", "/klipper", "setClipboardContents", text])
    # Paste text key codes: 42=Shift, 110=Insert
    run_ydotool_command(["key", "42:1", "110:1", "110:0", "42:0"])


def get_selection() -> str:
    """Get the last word using ydotool (Ctrl+C) and copy it to clipboard
    key codes: 29=Ctrl, 46=C
    """
    run_ydotool_command(["key", "29:1", "46:1", "46:0", "29:0"])
    return run_qbus_command(
        [
            "org.kde.klipper",
            "/klipper",
            "getClipboardContents",
        ]
    )


def get_last_word() -> str:
    """Selects the last word and returns it from the primary selection."""
    select_last_word()
    return get_selection()


def save_clipboard_last_item() -> str:
    """
    Save clipboard last item
    """
    return run_qbus_command(
        [
            "org.kde.klipper",
            "/klipper",
            "getClipboardContents",
        ]
    )


def switch_kde_layout() -> None:
    """
    Switches to the next keyboard layout in KDE Plasma using D-Bus.
    """
    run_qbus_command(["org.kde.keyboard", "/Layouts", "switchToNextLayout"])


def main():
    """Main script logic."""
    parser = argparse.ArgumentParser(description="Keyboard layout switcher")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "action",
        nargs="?",
        choices=("last", "selected"),
        help="Action: 'last' for last word, 'selected' for current selection",
    )

    args = parser.parse_args()
    which()
    # clipboard_last_item = run_qbus_command(["org.kde.klipper", "/klipper", "getClipboardContents"])
    selection_text = ""
    if args.action == "last":
        time.sleep(0.2)
        selection_text = get_last_word()
    elif args.action == "selected":
        time.sleep(0.2)
        selection_text = get_selection()

    if selection_text:
        converted_text = switch_text_layout(selection_text)
        paste_text(converted_text)
        switch_kde_layout()
        popup_message(f"{selection_text}\n{converted_text}")
    else:
        popup_message("No text selected or last word found", error=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
