#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys

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


def switch_text_layout(text):
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


def select_last_word():
    """Selects the last word using ydotool (Ctrl+Shift+Left)."""
    # key codes: 29=Ctrl, 42=Shift, 105=Left
    subprocess.run(["ydotool", "key", "29:1", "42:1", "105:1", "105:0", "42:0", "29:0"])


def paste_text():
    """Pastes text using ydotool (Shift+Insert)."""
    # key codes: 42=Shift, 110=Insert
    subprocess.run(["ydotool", "key", "42:1", "110:1", "110:0", "42:0"])


def get_selection():
    """Gets the current primary selection using wl-paste."""
    try:
        return (
            subprocess.check_output(["wl-paste", "--primary", "--no-newline"])
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Return empty string if wl-paste fails or nothing is selected
        return ""


def get_last_word():
    """Selects the last word and returns it from the primary selection."""
    select_last_word()
    return get_selection()


def switch_kde_layout():
    """
    Switches to the next keyboard layout in KDE Plasma using D-Bus.
    Prints an error to stderr if it fails, but does not crash the script.
    """
    try:
        # Get the current layout index (0-based)
        layouts_list_str = (
            subprocess.check_output(
                [
                    "qdbus",
                    "org.kde.keyboard",
                    "/Layouts",
                    "getLayout",
                ]
            )
            .decode()
            .strip()
        )
        current_index = int(layouts_list_str)

        # Calculate the next layout index
        next_index = (current_index + 1) % 2

        # Set the new layout
        subprocess.run(
            [
                "qdbus",
                "org.kde.keyboard",
                "/Layouts",
                "setLayout",
                str(next_index),
            ],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        # This error means the qdbus command itself was not found.
        error_message = "Команда 'qdbus' не найдена. Убедитесь, что она установлена и доступна в вашем PATH (например, через пакет 'qttools5-dev-tools')."
        return f"Warning: {error_message}"
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as e:
        # These errors mean qdbus ran but failed to communicate with the KDE service.
        error_message = "Не удалось переключить раскладку через D-Bus. Убедитесь, что вы используете KDE Plasma и служба клавиатуры активна."
        return f"Warning: {error_message}\nDetails: {e}"

    return None


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
    text = ""
    if args.action == "last":
        text = get_last_word()
    elif args.action == "selected":
        text = get_selection()

    if text:
        converted_text = switch_text_layout(text)
        subprocess.run(["wl-copy", converted_text])
        paste_text()

        # Switch layout using KDE D-Bus

        message_text = switch_kde_layout()
        if not message_text:
            message_text = f"In: {text}\nOut:{converted_text}"
        subprocess.run(
            [
                "kdialog",
                "--title",
                "EnRu",
                "--passivepopup",
                f"Было: {text}\nСтало:{converted_text}",
                "5",
            ]
        )
    else:
        subprocess.run(
            [
                "kdialog",
                "--title",
                "EnRu",
                "--passivepopup",
                "Ничего не выделено!",
                "5",
            ]
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        # Try to show an error notification if kdialog is available
        subprocess.run(
            [
                "kdialog",
                "--title",
                "EnRu Error",
                "--passivepopup",
                f"Произошла критическая ошибка:\n{e}",
                "5",
            ]
        )
        sys.exit(1)
