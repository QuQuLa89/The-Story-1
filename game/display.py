import ctypes
import os
import sys
import time

DEFAULT_DELAY = 0.04


def enable_windows_ansi() -> None:
    if os.name != "nt":
        return
    try:
        os.system("chcp 65001 >nul")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        kernel32.SetConsoleMode(handle, 7)
    except Exception:
        pass


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_divider() -> None:
    print("-" * 50)


def type_line(text: str, delay: float = DEFAULT_DELAY) -> None:
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def wait_for_enter() -> None:
    input("[Enterキーで続行]")
    clear_screen()


def say(text: str, delay: float = DEFAULT_DELAY) -> None:
    type_line(text, delay)
    wait_for_enter()


def say_lines(lines, delay: float = DEFAULT_DELAY) -> None:
    for line in lines:
        say(line, delay)
