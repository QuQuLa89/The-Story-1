import json
import os

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save")
SAVE_PATH = os.path.join(SAVE_DIR, "save.json")

DEFAULT_SAVE = {
    "launch_count": 0,
    "choices_made": [],
    "true_end": False,
}


def load() -> dict:
    if not os.path.exists(SAVE_PATH):
        return dict(DEFAULT_SAVE)
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = dict(DEFAULT_SAVE)
    merged.update(data)
    return merged


def save(data: dict) -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_thanks_note(text: str) -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, "for_you.txt")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
