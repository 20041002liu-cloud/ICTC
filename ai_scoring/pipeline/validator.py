import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.simple_yaml import load_yaml


class ValidationError(ValueError):
    def __init__(self, message: str, raw_text: Optional[str] = None) -> None:
        super().__init__(message)
        self.raw_text = raw_text


def load_scoring_config(path: str) -> Dict[str, Any]:
    config = load_yaml(path) or {}
    scale = config.get("score_scale", {})
    return {
        "min": scale.get("min", 0),
        "max": scale.get("max", 100),
        "precision": scale.get("precision", 2),
        "dimensions": config.get("dimensions", {}),
    }


def _extract_json_block(text: str) -> str:
    cleaned = text.strip()
    if "```" in cleaned:
        first = cleaned.find("```")
        last = cleaned.rfind("```")
        if last > first:
            block = cleaned[first + 3 : last].strip()
            if block.lower().startswith("json"):
                block = block[4:].strip()
            cleaned = block

    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]

    return cleaned


def parse_json(text: str) -> Dict[str, Any]:
    candidate = _extract_json_block(text)
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValidationError("Response is not valid JSON.", raw_text=text) from exc

    if not isinstance(data, dict):
        raise ValidationError("JSON root must be an object.", raw_text=text)
    return data


def compute_total_score(scores: Dict[str, float], dimensions: Dict[str, Any], precision: int) -> float:
    total = 0.0
    for key, meta in dimensions.items():
        weight = float(meta.get("weight", 0))
        total += float(scores[key]) * weight
    return round(total, precision)


def validate_and_normalize(
    raw_text: str,
    scoring_config: Dict[str, Any],
    expected_tech_id: Optional[str] = None,
) -> Dict[str, Any]:
    data = parse_json(raw_text)
    dimensions = scoring_config.get("dimensions", {})
    if not dimensions:
        raise ValidationError("No dimensions configured.", raw_text=raw_text)

    score = data.get("score")
    if not isinstance(score, dict):
        raise ValidationError("score must be an object.", raw_text=raw_text)

    reasons = data.get("reasons")
    if not isinstance(reasons, dict):
        raise ValidationError("reasons must be an object.", raw_text=raw_text)

    min_score = float(scoring_config.get("min", 0))
    max_score = float(scoring_config.get("max", 100))
    precision = int(scoring_config.get("precision", 2))

    normalized_scores: Dict[str, float] = {}
    normalized_reasons: Dict[str, str] = {}
    for dimension in dimensions.keys():
        value = score.get(dimension)
        if value is None or not isinstance(value, (int, float)):
            raise ValidationError(f"Missing or invalid score for {dimension}.", raw_text=raw_text)
        if value < min_score or value > max_score:
            raise ValidationError(f"Score {dimension} out of range.", raw_text=raw_text)
        normalized_scores[dimension] = round(float(value), precision)

        reason = reasons.get(dimension)
        if not isinstance(reason, str) or not reason.strip():
            raise ValidationError(f"Missing reason for {dimension}.", raw_text=raw_text)
        normalized_reasons[dimension] = reason.strip()

    confidence = data.get("confidence")
    if confidence is None or not isinstance(confidence, (int, float)):
        raise ValidationError("confidence must be numeric.", raw_text=raw_text)
    confidence = float(confidence)
    if not 0 <= confidence <= 1:
        raise ValidationError("confidence must be between 0 and 1.", raw_text=raw_text)

    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    if not isinstance(tags, list):
        raise ValidationError("tags must be a list.", raw_text=raw_text)
    tags = [str(tag).strip() for tag in tags if str(tag).strip()]

    tech_id = expected_tech_id if expected_tech_id is not None else data.get("tech_id")
    total_score = compute_total_score(normalized_scores, dimensions, precision)

    return {
        "tech_id": tech_id,
        "score": normalized_scores,
        "reasons": normalized_reasons,
        "confidence": round(confidence, 3),
        "tags": tags,
        "total_score": total_score,
    }
