import ctypes
import ctypes.wintypes
import time

from . import save_data, script
from .display import clear_screen, print_divider, say
from .input_utils import arrow_menu, normalize_command

_CTRL_HANDLER_TYPE = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.DWORD)

_TURN_LABELS = (
    ("1. /attack", script.FIGHT_TURN1_RESPONSE),
    ("1. /attack", script.FIGHT_TURN2_RESPONSE),
    ("1. /attack", script.FIGHT_TURN3_RESPONSE),
)


def run_chapter_000(variant: int) -> None:
    for line in script.CHAPTER_000[variant]:
        say(line)


def run_save_corruption_notice() -> None:
    for line in script.SAVE_CORRUPTION_LINES:
        say(line)


def run_chapter_001(state: dict) -> None:
    choices_made = set(state["choices_made"])

    display_options = []
    for i, opt in enumerate(script.CHAPTER_001_OPTIONS, start=1):
        prefix = "*" if i in choices_made else ""
        display_options.append(f"{prefix}{i}. {opt}")

    idx = arrow_menu(display_options)
    choice_num = idx + 1
    was_repeat = choice_num in choices_made

    choices_made.add(choice_num)
    state["choices_made"] = sorted(choices_made)
    save_data.save(state)

    for line in script.CHAPTER_001_RESPONSES[choice_num]:
        say(line)

    if was_repeat:
        for line in script.CHAPTER_001_REPEAT:
            say(line)


def run_chapter_002(variant: int) -> None:
    for line in script.CHAPTER_002_COMMON:
        say(line)
    for line in script.CHAPTER_002_VARIANTS[variant]:
        say(line)


def run_all_clear() -> None:
    print_divider()
    for line in script.ALL_CLEAR_LINES:
        say(line)

    empty_count = 0
    eof_count = 0
    while True:
        print("Enter this.")
        print("1. /kill SasaharaKazuyuki")
        try:
            raw = input("> ")
        except EOFError:
            eof_count += 1
            for line in script.CHAPTER_XXX_KILL_EOF_RESPONSES[min(eof_count, 3)]:
                say(line)
            continue

        if normalize_command(raw) == "kill sasaharakazuyuki":
            return
        if raw.strip() == "":
            empty_count += 1
            for line in script.CHAPTER_XXX_KILL_EMPTY_RESPONSES[min(empty_count, 3)]:
                say(line)
        else:
            print("（そのコマンドは認識されませんでした）")


def run_chapter_xxx() -> None:
    print("【action rejected】")
    print_divider()
    for line in script.CHAPTER_XXX_PART1:
        say(line)

    time.sleep(3)

    for line in script.CHAPTER_XXX_PART2:
        say(line)
    say(script.CHAPTER_XXX_FINAL_LINE, delay=0.2)


def _restart_lines(restart_count: int) -> list:
    table = script.FIGHT_RESTART_RESPONSES
    if restart_count in table:
        return table[restart_count]
    if restart_count in (6, 7, 9, 10, 11):
        return table[5]
    return table[13]


def _fight_prompt(fs: dict, label_line: str, expected_cmd: str) -> str:
    """FIGHTシーン中の入力待ち。fsを直接更新する。

    結果は"normal"(想定コマンドが入力された)か"forced_end"
    (/mercyを5回以上入力した後にattackまたはkillが入力された)のいずれか。
    """
    while True:
        print(label_line)
        try:
            raw = input("> ")
        except EOFError:
            fs["eof_count"] += 1
            for line in script.FIGHT_EOF_RESPONSES[min(fs["eof_count"], 4)]:
                say(line)
            continue

        cmd = normalize_command(raw)

        if cmd in ("attack", "kill sasaharakazuyuki"):
            if fs["mercy_count"] >= 5:
                return "forced_end"
            if cmd != expected_cmd:
                print("（そのコマンドは認識されませんでした）")
                continue
            if fs["mercy_count"] >= 1 and cmd == "attack" and not fs["resume_line_shown"]:
                say(script.FIGHT_MERCY_RESUME_LINE)
                fs["resume_line_shown"] = True
            return "normal"

        if cmd == "mercy":
            if fs["mercy_locked"]:
                say(script.FIGHT_MERCY_LOCKED_LINE)
                continue
            if fs["resume_line_shown"]:
                say(script.FIGHT_MERCY_REJECTED_LINE)
                continue
            fs["mercy_count"] += 1
            for line in script.FIGHT_MERCY_RESPONSES[min(fs["mercy_count"], 7)]:
                say(line)
            continue

        if fs["mercy_count"] >= 5:
            fs["stall_count"] += 1
            for line in script.FIGHT_STALL_RESPONSES[min(fs["stall_count"], 3)]:
                say(line)
            continue

        if raw.strip() == "":
            fs["empty_count"] += 1
            for line in script.FIGHT_EMPTY_RESPONSES[min(fs["empty_count"], 4)]:
                say(line)
            continue

        print("（そのコマンドは認識されませんでした）")


def _run_fight_from(state: dict, fs: dict) -> None:
    killed = False

    def eligible_for_thanks() -> bool:
        return fs["empty_count"] >= 3 or fs["mercy_count"] >= 6

    def persist() -> None:
        state["fight_state"] = fs
        save_data.save(state)

    def on_console_close(_event) -> bool:
        # ウィンドウを閉じる等の異常終了でも、進行状況を保存して次回起動時にFIGHTシーンへ戻す。
        if not killed:
            persist()
            if eligible_for_thanks():
                save_data.write_thanks_note(script.SASAHARA_THANKS_NOTE)
        return False

    handler = _CTRL_HANDLER_TYPE(on_console_close)
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCtrlHandler(handler, True)

    try:
        forced_end = False

        while fs["turn"] < 3:
            label, responses = _TURN_LABELS[fs["turn"]]
            status = _fight_prompt(fs, label, "attack")
            if status == "forced_end":
                forced_end = True
                break
            fs["hp"] -= 100
            print("【笹原に100ダメージ！】")
            print(f"(残HP {fs['hp']}/400)")
            for line in responses:
                say(line)
            fs["turn"] += 1

        if not forced_end and fs["turn"] == 3:
            status = _fight_prompt(fs, "1. /kill SasaharaKazuyuki", "kill sasaharakazuyuki")
            forced_end = status == "forced_end"

        print("【2,147,483,647 damage!!!!!】")
        print("(残HP ■■/400)")

        if forced_end:
            for line in script.FIGHT_MERCY_FORCED_END_LINES:
                say(line, delay=0.1)
        else:
            for line in script.FIGHT_FINISH_LINES:
                say(line, delay=0.1)

        say(script.FIGHT_SORRY_LINE, delay=0.4)

        time.sleep(3)
        state["true_end"] = True
        state["fight_cleared"] = True
        state.pop("fight_state", None)
        save_data.save(state)
        killed = True

        say(script.FIGHT_END_LINE, delay=0.04)
    finally:
        kernel32.SetConsoleCtrlHandler(handler, False)
        if not killed:
            persist()
            if eligible_for_thanks():
                save_data.write_thanks_note(script.SASAHARA_THANKS_NOTE)


def run_fight(state: dict) -> None:
    print("【笹原 寿幸が戦闘をしかけてきた！】")
    print("笹原 寿幸")
    print("HP")
    print("400/400")

    for line in script.FIGHT_START_LINES:
        say(line)

    fs = {
        "turn": 0,
        "hp": 400,
        "mercy_count": 0,
        "empty_count": 0,
        "eof_count": 0,
        "stall_count": 0,
        "resume_line_shown": False,
        "restart_count": 0,
        "mercy_locked": False,
    }

    _run_fight_from(state, fs)


def resume_fight(state: dict) -> None:
    """FIGHTシーンを離脱後に再起動された場合、続きから再開する。"""
    fs = state["fight_state"]
    fs["restart_count"] += 1
    if fs["restart_count"] >= 3:
        fs["mercy_locked"] = True
    state["fight_state"] = fs
    save_data.save(state)

    for line in _restart_lines(fs["restart_count"]):
        say(line)

    _run_fight_from(state, fs)


def run_story(state: dict, variant: int, corrupted: bool) -> None:
    entered_fight = False
    handler_registered = False

    def on_console_close(_event) -> bool:
        # FIGHTシーン以外での異常終了を検知した場合の専用メモ。
        if not entered_fight:
            save_data.write_what_happened(script.WHAT_HAPPENED_NOTE)
        return False

    handler = _CTRL_HANDLER_TYPE(on_console_close)
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCtrlHandler(handler, True)
    handler_registered = True

    try:
        run_chapter_000(variant)
        if corrupted:
            run_save_corruption_notice()
        run_chapter_001(state)
        run_chapter_002(variant)

        if set(state["choices_made"]) == {1, 2, 3}:
            run_all_clear()
            run_chapter_xxx()
            clear_screen()
            entered_fight = True
            kernel32.SetConsoleCtrlHandler(handler, False)
            handler_registered = False
            run_fight(state)
    finally:
        if handler_registered:
            kernel32.SetConsoleCtrlHandler(handler, False)


def run_true_end_replay(state: dict) -> None:
    print_divider()
    if not state.get("fight_cleared"):
        for line in script.TRUE_END_TAMPER_LINES:
            say(line)
        time.sleep(3)
    say(script.FIGHT_END_LINE, delay=0.04)
