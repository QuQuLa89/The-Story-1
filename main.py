from game import save_data, story
from game.display import enable_windows_ansi


def main() -> None:
    enable_windows_ansi()
    state = save_data.load()
    corrupted = state.pop("_corrupted", False)

    if state.get("true_end"):
        story.run_true_end_replay(state)
        return

    if state.get("fight_state"):
        story.resume_fight(state)
        return

    state["launch_count"] += 1
    save_data.save(state)

    variant = min(state["launch_count"], 3)

    story.run_story(state, variant, corrupted)


if __name__ == "__main__":
    main()
