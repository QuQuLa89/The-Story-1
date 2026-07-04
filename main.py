from game import save_data, story
from game.display import clear_screen, enable_windows_ansi


def main() -> None:
    enable_windows_ansi()
    state = save_data.load()

    if state.get("true_end"):
        story.run_true_end_replay()
        return

    state["launch_count"] += 1
    save_data.save(state)

    variant = min(state["launch_count"], 3)

    story.run_chapter_000(variant)
    story.run_chapter_001(state)
    story.run_chapter_002(variant)

    if set(state["choices_made"]) == {1, 2, 3}:
        story.run_all_clear()
        story.run_chapter_xxx()
        clear_screen()
        story.run_fight(state)


if __name__ == "__main__":
    main()
