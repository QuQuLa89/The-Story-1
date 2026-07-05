import ctypes
import ctypes.wintypes
import time

from . import save_data, script
from .display import clear_screen, print_divider, say
from .input_utils import arrow_menu, normalize_command


def run_chapter_000(variant: int) -> None:
    for line in script.CHAPTER_000[variant]:
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
    while True:
        print("Enter this.")
        print("1. /kill SasaharaKazuyuki")
        raw = input("> ")
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


_CTRL_HANDLER_TYPE = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.DWORD)


def _fight_prompt(
    label_line: str,
    expected_cmd: str,
    empty_count: int,
    mercy_count: int,
    resume_line_shown: bool,
):
    """FIGHTシーン中の入力待ち。戻り値は(結果, empty_count, mercy_count, resume_line_shown)。

    結果は"normal"(想定コマンドが入力された)か"forced_end"
    (/mercyを5回以上入力した後にattackまたはkillが入力された)のいずれか。
    """
    while True:
        print(label_line)
        raw = input("> ")
        cmd = normalize_command(raw)

        if cmd in ("attack", "kill sasaharakazuyuki"):
            if mercy_count >= 5:
                return "forced_end", empty_count, mercy_count, resume_line_shown
            if cmd != expected_cmd:
                print("（そのコマンドは認識されませんでした）")
                continue
            if mercy_count >= 1 and cmd == "attack" and not resume_line_shown:
                say(script.FIGHT_MERCY_RESUME_LINE)
                resume_line_shown = True
            return "normal", empty_count, mercy_count, resume_line_shown

        if cmd == "mercy":
            if resume_line_shown:
                say(script.FIGHT_MERCY_REJECTED_LINE)
                continue
            mercy_count += 1
            for line in script.FIGHT_MERCY_RESPONSES[min(mercy_count, 7)]:
                say(line)
            continue

        if raw.strip() == "":
            empty_count += 1
            for line in script.FIGHT_EMPTY_RESPONSES[min(empty_count, 4)]:
                say(line)
            continue

        print("（そのコマンドは認識されませんでした）")


def run_fight(state: dict) -> None:
    print("【笹原 寿幸が戦闘をしかけてきた！】")
    print("笹原 寿幸")
    print("HP")
    hp = 400
    print(f"{hp}/400")

    for line in script.FIGHT_START_LINES:
        say(line)

    killed = False

    def on_console_close(_event) -> bool:
        # ウィンドウを閉じる等の異常終了でも、killせず閉じたことを検知して感謝メモを残す。
        if not killed:
            save_data.write_thanks_note(script.SASAHARA_THANKS_NOTE)
        return False

    handler = _CTRL_HANDLER_TYPE(on_console_close)
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCtrlHandler(handler, True)

    try:
        empty_count = 0
        mercy_count = 0
        resume_line_shown = False
        forced_end = False

        for label, responses in (
            ("1. /attack", script.FIGHT_TURN1_RESPONSE),
            ("1. /attack", script.FIGHT_TURN2_RESPONSE),
            ("1. /attack", script.FIGHT_TURN3_RESPONSE),
        ):
            status, empty_count, mercy_count, resume_line_shown = _fight_prompt(
                label, "attack", empty_count, mercy_count, resume_line_shown
            )
            if status == "forced_end":
                forced_end = True
                break
            hp -= 100
            print("【笹原に100ダメージ！】")
            print(f"(残HP {hp}/400)")
            for line in responses:
                say(line)

        if not forced_end:
            status, empty_count, mercy_count, resume_line_shown = _fight_prompt(
                "1. /kill SasaharaKazuyuki",
                "kill sasaharakazuyuki",
                empty_count,
                mercy_count,
                resume_line_shown,
            )
            forced_end = status == "forced_end"

        print("【2,147,483,647 damage!!!!!】")
        print("(残HP ■■/400)")

        if forced_end:
            for line in script.FIGHT_MERCY_FORCED_END_LINES:
                say(line, delay=0.2)
        else:
            for line in script.FIGHT_FINISH_LINES:
                say(line, delay=0.2)

        say(script.FIGHT_SORRY_LINE, delay=0.4)

        time.sleep(3)
        state["true_end"] = True
        save_data.save(state)
        killed = True

        say(script.FIGHT_END_LINE, delay=0.08)
    finally:
        kernel32.SetConsoleCtrlHandler(handler, False)
        if not killed:
            save_data.write_thanks_note(script.SASAHARA_THANKS_NOTE)


def run_true_end_replay() -> None:
    print_divider()
    say(script.FIGHT_END_LINE, delay=0.08)
