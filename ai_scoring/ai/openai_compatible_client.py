import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from .base_client import BaseClient


class OpenAICompatibleClient(BaseClient):
    def __init__(
        self,
        api_key_env: str,
        model: str,
        base_url: str,
        timeout_seconds: float = 60,
        temperature: float = 0,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.api_key_env = api_key_env
        self.model = model
        self.base_url = base_url
        self.timeout_seconds = float(timeout_seconds)
        self.temperature = float(temperature)
        self.max_tokens = max_tokens

    def evaluate(self, prompt: str) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise ValueError(f"Missing API key env var: {self.api_key_env}")

        url = self._chat_completions_url(self.base_url)
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = int(self.max_tokens)

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise RuntimeError(f"HTTP {exc.code} calling model: {raw}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Network error calling model: {exc}") from exc

        data = json.loads(raw)
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"Empty model response content: {raw}")
        return content

    @staticmethod
    def _chat_completions_url(base_url: str) -> str:
        url = (base_url or "").strip().rstrip("/")
        if not url:
            raise ValueError("base_url is required")
        if url.endswith("/chat/completions"):
            return url
        if url.endswith("/v1"):
            return f"{url}/chat/completions"
        if "/paas/v4" in url or url.endswith("/v4"):
            return f"{url}/chat/completions"
        return f"{url}/v1/chat/completions"
