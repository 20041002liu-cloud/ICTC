from typing import Any, Dict

from .base_client import BaseClient
from .mock_client import MockClient
from .openai_compatible_client import OpenAICompatibleClient


def create_client(provider_config: Dict[str, Any], scoring_config: Dict[str, Any]) -> BaseClient:
    provider = provider_config.get("provider", "mock")
    if provider == "mock":
        mock_config = provider_config.get("mock", {})
        return MockClient(
            dimensions=scoring_config["dimensions"],
            default_score=mock_config.get("default_score", 60),
            confidence=mock_config.get("confidence", 0.4),
            tags=mock_config.get("tags", ["pending"]),
        )
    if provider in {"openai_compatible", "qwen", "openai", "zhipu"}:
        cfg = provider_config.get(provider, {})
        api_key_env = cfg.get("api_key_env", "")
        # Allow override model via env var (useful for compiled app)
        import os
        model = os.environ.get("ZHIPU_MODEL") if provider == "zhipu" and os.environ.get("ZHIPU_MODEL") else cfg.get("model", "")
        base_url = cfg.get("base_url", "")
        if not api_key_env or not model or not base_url:
            raise ValueError(f"Missing {provider} config: api_key_env/model/base_url required.")
        return OpenAICompatibleClient(
            api_key_env=api_key_env,
            model=model,
            base_url=base_url,
            timeout_seconds=cfg.get("timeout_seconds", 60),
            temperature=cfg.get("temperature", 0),
            max_tokens=cfg.get("max_tokens"),
        )
    raise ValueError(f"Unsupported provider: {provider}")


def get_retry_config(provider_config: Dict[str, Any]) -> Dict[str, Any]:
    return provider_config.get("retry", {"attempts": 3, "backoff_seconds": 1.5})
