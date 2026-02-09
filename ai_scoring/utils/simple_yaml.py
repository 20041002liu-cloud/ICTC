from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class _Line:
    indent: int
    text: str


def load_yaml(path: str) -> Any:
    content = Path(path).read_text(encoding="utf-8")
    return loads(content)


def loads(text: str) -> Any:
    lines = _preprocess_lines(text)
    if not lines:
        return {}
    value, next_index = _parse_value(lines, 0, lines[0].indent)
    if next_index != len(lines):
        raise ValueError("Unexpected trailing YAML content.")
    return value


def _preprocess_lines(text: str) -> List[_Line]:
    out: List[_Line] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.lstrip(" ")
        if "#" in line:
            in_quote = False
            quote_char = ""
            cleaned_chars: List[str] = []
            for ch in line:
                if ch in {"'", '"'}:
                    if not in_quote:
                        in_quote = True
                        quote_char = ch
                    elif quote_char == ch:
                        in_quote = False
                        quote_char = ""
                if ch == "#" and not in_quote:
                    break
                cleaned_chars.append(ch)
            line = "".join(cleaned_chars).rstrip()
            if not line:
                continue
        out.append(_Line(indent=indent, text=line))
    return out


def _parse_value(lines: List[_Line], i: int, indent: int) -> Tuple[Any, int]:
    if i >= len(lines):
        return {}, i
    line = lines[i]
    if line.indent != indent:
        raise ValueError("Invalid indentation.")
    if line.text.startswith("- "):
        return _parse_sequence(lines, i, indent)
    return _parse_mapping(lines, i, indent)


def _parse_mapping(lines: List[_Line], i: int, indent: int) -> Tuple[Dict[str, Any], int]:
    obj: Dict[str, Any] = {}
    while i < len(lines):
        line = lines[i]
        if line.indent < indent:
            break
        if line.indent > indent:
            raise ValueError("Unexpected indentation inside mapping.")
        if line.text.startswith("- "):
            raise ValueError("Unexpected sequence item inside mapping.")

        if ":" not in line.text:
            raise ValueError(f"Invalid mapping line: {line.text}")

        key, rest = line.text.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        i += 1

        if rest:
            obj[key] = _parse_scalar(rest)
            continue

        if i >= len(lines) or lines[i].indent <= indent:
            obj[key] = {}
            continue

        child_indent = lines[i].indent
        child_value, i = _parse_value(lines, i, child_indent)
        obj[key] = child_value
    return obj, i


def _parse_sequence(lines: List[_Line], i: int, indent: int) -> Tuple[List[Any], int]:
    arr: List[Any] = []
    while i < len(lines):
        line = lines[i]
        if line.indent < indent:
            break
        if line.indent > indent:
            raise ValueError("Unexpected indentation inside sequence.")
        if not line.text.startswith("- "):
            break

        item_text = line.text[2:].strip()
        i += 1

        if item_text:
            arr.append(_parse_scalar(item_text))
            continue

        if i >= len(lines) or lines[i].indent <= indent:
            arr.append({})
            continue

        child_indent = lines[i].indent
        child_value, i = _parse_value(lines, i, child_indent)
        arr.append(child_value)
    return arr, i


def _parse_scalar(value: str) -> Any:
    v = value.strip()
    if not v:
        return ""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    low = v.lower()
    if low in {"null", "none", "~"}:
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        return v
