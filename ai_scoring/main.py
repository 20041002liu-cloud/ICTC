import argparse
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure local imports work in frozen environments
if getattr(sys, "frozen", False):
    sys.path.append(str(Path(__file__).parent))

from ai.client_factory import create_client, get_retry_config
from pipeline.scorer import Scorer
from pipeline.validator import load_scoring_config
from utils.excel_io import read_excel, write_excel
from utils.rule_parser import load_skill_rules
from utils.simple_yaml import load_yaml


BASE_DIR = Path(__file__).resolve().parent


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0].lower() == "ai_scoring":
        return Path.cwd() / path
    return BASE_DIR / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Skill scoring pipeline (Excel).")
    parser.add_argument("--input", default="input/tech_raw.xlsx")
    parser.add_argument("--output", default="output/tech_score.xlsx")
    parser.add_argument("--failed", default="output/tech_score_failed.xlsx")
    parser.add_argument("--skill", default="config/skill.md")
    parser.add_argument("--scoring", default="config/scoring.yaml")
    parser.add_argument("--providers", default="config/providers.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = resolve_path(args.input)
    output_path = resolve_path(args.output)
    failed_path = resolve_path(args.failed)
    skill_path = resolve_path(args.skill)
    scoring_path = resolve_path(args.scoring)
    providers_path = resolve_path(args.providers)

    rows = read_excel(str(input_path))
    if not rows:
        print("No input rows found.")
        return

    skill_rules = load_skill_rules(str(skill_path))
    scoring_config = load_scoring_config(str(scoring_path))
    provider_config = load_yaml(str(providers_path))

    client = create_client(provider_config, scoring_config)
    retry_config = get_retry_config(provider_config)

    scorer = Scorer(client, scoring_config, retry_config)
    results, failed = scorer.score_rows(rows, skill_rules)

    write_excel(str(output_path), results, columns=Scorer.OUTPUT_COLUMNS)

    if failed:
        write_excel(str(failed_path), failed, columns=Scorer.FAILED_COLUMNS)
        print(f"Completed with {len(failed)} failures.")
    else:
        print("Completed with 0 failures.")


if __name__ == "__main__":
    main()
