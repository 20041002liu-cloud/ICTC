from __future__ import annotations

import json
from typing import Any, Dict


def _normalize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and value != value:
        return None
    return value


def build_prompt(skill_rules: str, row: Dict[str, Any]) -> str:
    payload = {
        "tech_id": row.get("tech_id"),
        "name": row.get("name"),
        "repo_url": row.get("repo_url"),
        "summary": row.get("summary"),
        "readme": row.get("readme"),
        "stars": row.get("stars"),
        "forks": row.get("forks"),
        "last_update": row.get("last_update"),
        "issues_open": row.get("issues_open"),
        "language": row.get("language"),
        "keywords": row.get("keywords"),
    }

    cleaned: Dict[str, Any] = {}
    for key, value in payload.items():
        normalized = _normalize_value(value)
        if normalized is None:
            continue
        if isinstance(normalized, str) and not normalized.strip():
            continue
        cleaned[key] = normalized

    input_json = json.dumps(cleaned, ensure_ascii=False, indent=2)
    return (
        f"{skill_rules}\n\n"
        "TASK:\n"
        "Follow the rules above. Evaluate the technology and return JSON only."
        "\n\nINPUT:\n"
        f"{input_json}"
    )
