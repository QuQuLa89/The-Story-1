import re
import sys

import msvcrt

from . import script

UP = b"H"
DOWN = b"P"
ENTER = b"\r"


def _render(options: list, selected: int) -> list:
    lines = []
    for i, opt in enumerate(options):
        cursor = "> " if i == selected else "  "
        lines.append(f"{cursor}{opt}")
    return lines


def arrow_menu(options: list) -> int:
    """矢印キーで選択、Enterで決定するメニュー。選択されたインデックス(0始まり)を返す。"""
    selected = 0
    for line in _render(options, selected):
        print(line)

    lines_printed = len(options)

    while True:
        key = msvcrt.getch()
        is_invalid = False

        if key in (b"\xe0", b"\x00"):
            key2 = msvcrt.getch()
            if key2 == UP:
                selected = (selected - 1) % len(options)
            elif key2 == DOWN:
                selected = (selected + 1) % len(options)
            else:
                is_invalid = True
        elif key == ENTER:
            if lines_printed > len(options):
                sys.stdout.write(f"\x1b[{lines_printed}A")
                for line in _render(options, selected):
                    sys.stdout.write("\x1b[2K" + line + "\n")
                sys.stdout.write("\x1b[2K")
                sys.stdout.flush()
            print()
            return selected
        else:
            is_invalid = True

        sys.stdout.write(f"\x1b[{lines_printed}A")
        for line in _render(options, selected):
            sys.stdout.write("\x1b[2K" + line + "\n")

        if is_invalid:
            sys.stdout.write("\x1b[2K" + script.INVALID_KEY_WARNING + "\n")
            lines_printed = len(options) + 1
        else:
            if lines_printed > len(options):
                sys.stdout.write("\x1b[2K")
            lines_printed = len(options)

        sys.stdout.flush()


def normalize_command(raw: str) -> str:
    raw = raw.strip().lstrip("/")
    raw = re.sub(r"\s+", " ", raw)
    return raw.lower()
