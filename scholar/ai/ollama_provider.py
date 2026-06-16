from __future__ import annotations

import json
import re
from typing import Any

import httpx

from scholar.utils.logger import get_logger

logger = get_logger(__name__)

RECOMMENDED_MODELS = [
    "tinyllama:latest",
    "gemma:2b",
    "phi:mini",
    "qwen:1.8b",
    "phi3:mini",
    "gemma2:2b",
    "mistral:7b",
]


class OllamaProvider:
    """Thin wrapper around the Ollama REST API."""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "tinyllama:latest",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        timeout: int = 600,
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        try:
            resp = httpx.get(
                f"{self.host}/api/tags",
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        try:
            resp = httpx.get(
                f"{self.host}/api/tags",
                timeout=5,
            )
            resp.raise_for_status()

            data = resp.json()

            return [
                m["name"]
                for m in data.get("models", [])
            ]

        except Exception:
            return []

    def model_exists(self) -> bool:
        models = self.list_models()

        if self.model in models:
            return True

        base = self.model.split(":")[0]

        return any(
            m.startswith(base)
            for m in models
        )

    # ------------------------------------------------------------------
    # Text generation
    # ------------------------------------------------------------------

    def generate(
        self,
        system: str,
        user: str,
    ) -> str:

        payload = {
            "model": self.model,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
            "messages": [
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": user,
                },
            ],
        }

        try:
            resp = httpx.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout,
            )

            resp.raise_for_status()

            data = resp.json()

            if (
                isinstance(data, dict)
                and "message" in data
                and "content" in data["message"]
            ):
                return data["message"]["content"]

        except Exception as exc:
            logger.warning(f"Chat endpoint failed: {exc}")

        return self._generate_legacy(system, user)

    def _generate_legacy(
        self,
        system: str,
        user: str,
    ) -> str:

        prompt = (
            f"SYSTEM: {system}\n\n"
            f"USER: {user}\n\n"
            f"ASSISTANT:"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        resp = httpx.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=self.timeout,
        )

        resp.raise_for_status()

        data = resp.json()

        return data.get("response", "")

    # ------------------------------------------------------------------
    # JSON generation
    # ------------------------------------------------------------------

# ------------------------------------------------------------------
    # JSON generation
    # ------------------------------------------------------------------

    def generate_json(
        self,
        system: str,
        user: str,
    ) -> dict[str, Any]:

        raw = self.generate(system, user)

        text = _strip_fences(raw).strip()

        try:
            data = json.loads(text)

            if isinstance(data, dict):
                return data

            if (
                isinstance(data, list)
                and data
                and isinstance(data[0], dict)
            ):
                return data[0]

        except Exception:
            pass

        match = re.search(r"\{[\s\S]*\}", text)

        if match:
            try:
                data = json.loads(match.group())

                if isinstance(data, dict):
                    return data

            except Exception:
                pass

        match = re.search(r"\[[\s\S]*\]", text)

        if match:
            try:
                arr = json.loads(match.group())

                if (
                    isinstance(arr, list)
                    and arr
                    and isinstance(arr[0], dict)
                ):
                    return arr[0]

            except Exception:
                pass

        logger.warning("Model returned invalid JSON.")

        return {
            "_error": "Model returned invalid JSON",
            "title": "Generation Failed",
            "note": text[:1000],
        }


def _strip_fences(text: str) -> str:
    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return text.strip()
