import re
import sys

import msvcrt

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

    while True:
        key = msvcrt.getch()
        if key in (b"\xe0", b"\x00"):
            key2 = msvcrt.getch()
            if key2 == UP:
                selected = (selected - 1) % len(options)
            elif key2 == DOWN:
                selected = (selected + 1) % len(options)
            else:
                continue
            sys.stdout.write(f"\x1b[{len(options)}A")
            for line in _render(options, selected):
                sys.stdout.write("\x1b[2K" + line + "\n")
            sys.stdout.flush()
        elif key == ENTER:
            print()
            return selected


def normalize_command(raw: str) -> str:
    raw = raw.strip().lstrip("/")
    raw = re.sub(r"\s+", " ", raw)
    return raw.lower()
