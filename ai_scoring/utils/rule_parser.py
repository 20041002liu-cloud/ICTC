from pathlib import Path


def load_skill_rules(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()
