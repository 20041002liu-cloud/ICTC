import json
from datetime import datetime
from typing import Any, Dict, List, Tuple
import time

from prompts.prompt_builder import build_prompt
from pipeline.retry import run_with_retry
from pipeline.validator import ValidationError, validate_and_normalize


class Scorer:
    OUTPUT_COLUMNS = [
        "tech_id",
        "name",
        "repo_url",
        "summary",
        "Efficiency",
        "Frequency",
        "Security",
        "Auditability",
        "Connectivity",
        "Accessibility",
        "total_score",
        "confidence",
        "reasons_json",
        "tags",
        "evaluated_at",
    ]

    FAILED_COLUMNS = ["tech_id", "name", "error", "raw_response"]

    def __init__(
        self,
        client: Any,
        scoring_config: Dict[str, Any],
        retry_config: Dict[str, Any],
    ) -> None:
        self.client = client
        self.scoring_config = scoring_config
        self.retry_attempts = int(retry_config.get("attempts", 3))
        self.retry_backoff = float(retry_config.get("backoff_seconds", 1.5))

    def score_rows(
        self,
        rows: List[Dict[str, Any]],
        skill_rules: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        results: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []
        
        total = len(rows)
        print(f"Found {total} items to score.", flush=True)

        for i, row in enumerate(rows, 1):
            tech_id = row.get("tech_id")
            name = row.get("name", "Unknown")
            print(f"[{i}/{total}] Scoring: {name}...", flush=True)
            
            try:
                prompt = build_prompt(skill_rules, row)
                response = run_with_retry(
                    lambda: self.client.evaluate(prompt),
                    attempts=self.retry_attempts,
                    backoff_seconds=self.retry_backoff,
                )
                normalized = validate_and_normalize(
                    response, self.scoring_config, expected_tech_id=tech_id
                )
                results.append(self._build_output_row(row, normalized))
                print(f"  > Success: {name} (Score: {normalized['total_score']})", flush=True)
                
                # 增加请求间隔，避免 429 错误
                time.sleep(2) 
                
            except ValidationError as exc:
                print(f"  > Failed: {name} - Validation Error", flush=True)
                failed.append(
                    self._build_failed_row(row, str(exc), getattr(exc, "raw_text", None))
                )
            except Exception as exc:
                print(f"  > Failed: {name} - {str(exc)}", flush=True)
                failed.append(self._build_failed_row(row, str(exc), None))

        return results, failed

    def _build_output_row(
        self,
        row: Dict[str, Any],
        normalized: Dict[str, Any],
    ) -> Dict[str, Any]:
        scores = normalized["score"]
        reasons = normalized["reasons"]
        return {
            "tech_id": normalized.get("tech_id") or row.get("tech_id"),
            "name": row.get("name"),
            "repo_url": row.get("repo_url", ""),
            "summary": row.get("summary", ""),
            **scores,
            "total_score": normalized["total_score"],
            "confidence": normalized["confidence"],
            "reasons_json": json.dumps(reasons, ensure_ascii=False),
            "tags": ", ".join(normalized.get("tags", [])),
            "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        }

    def _build_failed_row(
        self,
        row: Dict[str, Any],
        error: str,
        raw_response: Any,
    ) -> Dict[str, Any]:
        return {
            "tech_id": row.get("tech_id"),
            "name": row.get("name"),
            "error": error,
            "raw_response": raw_response,
        }
