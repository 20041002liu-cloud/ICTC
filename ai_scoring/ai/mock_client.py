import json
from typing import Dict, List

from .base_client import BaseClient


class MockClient(BaseClient):
    def __init__(
        self,
        dimensions: Dict[str, dict],
        default_score: float = 60,
        confidence: float = 0.4,
        tags: List[str] | None = None,
    ) -> None:
        self.dimensions = list(dimensions.keys())
        self.default_score = float(default_score)
        self.confidence = float(confidence)
        self.tags = tags or ["pending"]

    def evaluate(self, prompt: str) -> str:
        scores = {dimension: self.default_score for dimension in self.dimensions}
        reasons = {
            dimension: "Mock evaluation for pipeline validation."
            for dimension in self.dimensions
        }
        payload = {
            "tech_id": "UNKNOWN",
            "score": scores,
            "total_score": self.default_score,
            "confidence": self.confidence,
            "reasons": reasons,
            "tags": self.tags,
        }
        return json.dumps(payload, ensure_ascii=False)
