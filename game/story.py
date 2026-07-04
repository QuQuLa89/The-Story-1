import time

from . import save_data, script
from .display import clear_screen, print_divider, say
from .input_utils import arrow_menu, prompt_command


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
    print("Enter this.")
    prompt_command("1. /kill SasaharaKazuyuki", ["kill sasaharakazuyuki"])


def run_chapter_xxx() -> None:
    print("【action rejected】")
    print_divider()
    for line in script.CHAPTER_XXX_PART1:
        say(line)

    time.sleep(3)

    for line in script.CHAPTER_XXX_PART2:
        say(line)
    say(script.CHAPTER_XXX_FINAL_LINE, delay=0.1)


def run_fight(state: dict) -> None:
    print("【笹原 寿幸が戦闘をしかけてきた！】")
    print("笹原 寿幸")
    print("HP")
    hp = 400
    print(f"{hp}/400")

    for line in script.FIGHT_START_LINES:
        say(line)

    prompt_command("1. /attack", ["attack"])
    hp -= 100
    print("【笹原に100ダメージ！】")
    print(f"(残HP {hp}/400)")
    for line in script.FIGHT_TURN1_RESPONSE:
        say(line)

    prompt_command("1. /attack", ["attack"])
    hp -= 100
    print("【笹原に100ダメージ！】")
    print(f"(残HP {hp}/400)")
    for line in script.FIGHT_TURN2_RESPONSE:
        say(line)

    prompt_command("1. /attack", ["attack"])
    hp -= 100
    print("【笹原に100ダメージ！】")
    print(f"(残HP {hp}/400)")
    for line in script.FIGHT_TURN3_RESPONSE:
        say(line)

    prompt_command("1. /kill SasaharaKazuyuki", ["kill sasaharakazuyuki"])
    print("【2,147,483,647 damage!!!!!】")
    print("(残HP ■■/400)")

    for line in script.FIGHT_FINISH_LINES:
        say(line, delay=0.1)

    say(script.FIGHT_SORRY_LINE, delay=0.2)

    time.sleep(3)
    state["true_end"] = True
    save_data.save(state)

    say(script.FIGHT_END_LINE, delay=0.04)


def run_true_end_replay() -> None:
    print_divider()
    say(script.FIGHT_END_LINE, delay=0.04)
