import json
import os

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save")
SAVE_PATH = os.path.join(SAVE_DIR, "save.json")
THANKS_NOTE_FILENAME = "for_you.txt"
WHAT_HAPPENED_FILENAME = "what_happend.txt"

DEFAULT_SAVE = {
    "launch_count": 0,
    "choices_made": [],
    "true_end": False,
}

_FIGHT_STATE_INT_FIELDS = ("turn", "hp", "mercy_count", "empty_count", "eof_count", "stall_count", "restart_count")
_FIGHT_STATE_BOOL_FIELDS = ("resume_line_shown", "mercy_locked")


def _sanitize_fight_state(fight_state):
    if not isinstance(fight_state, dict):
        return None, True

    corrupted = False
    fixed = dict(fight_state)

    for key in _FIGHT_STATE_INT_FIELDS:
        value = fixed.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            fixed[key] = 0
            corrupted = True

    for key in _FIGHT_STATE_BOOL_FIELDS:
        if not isinstance(fixed.get(key), bool):
            fixed[key] = False
            corrupted = True

    if not (0 <= fixed["turn"] <= 3):
        fixed["turn"] = 0
        corrupted = True

    return fixed, corrupted


def load() -> dict:
    corrupted = False
    data = {}

    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
                corrupted = True
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            data = {}
            corrupted = True

    merged = dict(DEFAULT_SAVE)
    merged.update(data)

    launch_count = merged.get("launch_count")
    if not isinstance(launch_count, int) or isinstance(launch_count, bool) or launch_count < 0:
        merged["launch_count"] = DEFAULT_SAVE["launch_count"]
        corrupted = True

    choices = merged.get("choices_made")
    if isinstance(choices, list) and all(isinstance(c, int) and c in (1, 2, 3) for c in choices):
        merged["choices_made"] = choices
    else:
        merged["choices_made"] = (
            [c for c in choices if isinstance(c, int) and c in (1, 2, 3)] if isinstance(choices, list) else []
        )
        corrupted = True

    if not isinstance(merged.get("true_end"), bool):
        merged["true_end"] = DEFAULT_SAVE["true_end"]
        corrupted = True

    if not isinstance(merged.get("fight_cleared"), bool):
        merged.pop("fight_cleared", None)

    if "fight_state" in merged:
        fixed_fight_state, fight_state_corrupted = _sanitize_fight_state(merged["fight_state"])
        if fixed_fight_state is None:
            merged.pop("fight_state", None)
        else:
            merged["fight_state"] = fixed_fight_state
        corrupted = corrupted or fight_state_corrupted

    merged["_corrupted"] = corrupted
    return merged


def save(data: dict) -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)
    to_write = {k: v for k, v in data.items() if not k.startswith("_")}
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(to_write, f, ensure_ascii=False, indent=2)


def _write_note_if_absent(filename: str, text: str) -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def write_thanks_note(text: str) -> None:
    _write_note_if_absent(THANKS_NOTE_FILENAME, text)


def write_what_happened(text: str) -> None:
    _write_note_if_absent(WHAT_HAPPENED_FILENAME, text)
