#!/usr/bin/env python3
import argparse
import subprocess

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
    subprocess.run(["ydotool", "key", "29:1", "42:1", "105:1", "105:0", "42:0", "29:0"])


def paste_text():
    subprocess.run(["ydotool", "key", "42:1", "110:1", "110:0", "42:0"])


def get_last_word():
    select_last_word()
    return (
        subprocess.check_output(["wl-paste", "--primary", "--no-newline"])
        .decode()
        .strip()
    )


def get_clipboard_text():
    return (
        subprocess.check_output(["wl-paste", "--primary", "--no-newline"])
        .decode()
        .strip()
    )


def get_selection():
    return (
        subprocess.check_output(["wl-paste", "--primary", "--no-newline"])
        .decode()
        .strip()
    )


parser = argparse.ArgumentParser(description="Keyboard layout switcher")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "last",
    nargs="?",
    choices=("last", "selected"),
    help="Switch last word",
)

text = ""
args = parser.parse_args()
if args.last:
    text = get_last_word()
elif args.selected:
    text = get_selection()

if text:
    converted_text = switch_text_layout(text)
    subprocess.run(["wl-copy", converted_text])
    paste_text()
    # subprocess.run(["xkb-switch", "-n"])
    subprocess.run(
        [
            "kdialog",
            "--title",
            "EnRu",
            "--passivepopup",
            f"In: {text}\nOut:{converted_text}",
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
