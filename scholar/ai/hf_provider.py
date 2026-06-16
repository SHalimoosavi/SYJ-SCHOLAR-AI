"""
scholar/ai/hf_provider.py
HuggingFace Transformers fallback provider.

Used when Ollama is not available.
Downloads model to ~/.cache/huggingface on first use.
Recommended lightweight models for Termux:
  - microsoft/phi-2           (2.7B, CPU-feasible)
  - Qwen/Qwen1.5-0.5B-Chat   (0.5B — very fast)
  - TinyLlama/TinyLlama-1.1B-Chat-v1.0
"""

from __future__ import annotations

import json
import re
from typing import Any

from scholar.utils.logger import get_logger

logger = get_logger(__name__)


class HuggingFaceProvider:
    def __init__(
        self,
        model_id: str = "Qwen/Qwen1.5-0.5B-Chat",
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ):
        self.model_id    = model_id
        self.max_tokens  = max_tokens
        self.temperature = temperature
        self._pipe       = None     # lazy-loaded

    # ── Lazy pipeline ─────────────────────────────────────────────────────────

    def _get_pipeline(self):
        if self._pipe is not None:
            return self._pipe
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            import torch

            logger.info(f"Loading HuggingFace model: {self.model_id}")
            self._pipe = pipeline(
                "text-generation",
                model=self.model_id,
                torch_dtype=torch.float32,      # CPU-safe
                device_map="auto",
                max_new_tokens=self.max_tokens,
                do_sample=True,
                temperature=self.temperature,
                trust_remote_code=True,
            )
            return self._pipe
        except ImportError:
            raise RuntimeError(
                "transformers / torch not installed. "
                "Run: pip install transformers torch --break-system-packages"
            )

    def is_available(self) -> bool:
        try:
            import transformers   # noqa: F401
            return True
        except ImportError:
            return False

    # ── Core generation ───────────────────────────────────────────────────────

    def generate(self, system: str, user: str) -> str:
        pipe   = self._get_pipeline()
        prompt = f"<|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n"
        out    = pipe(prompt)
        text   = out[0]["generated_text"]
        # Strip the prompt prefix
        if "<|assistant|>" in text:
            text = text.split("<|assistant|>")[-1]
        return text.strip()

    def generate_json(self, system: str, user: str) -> dict[str, Any]:
        raw  = self.generate(system, user)
        text = raw.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$",           "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("HuggingFace model did not return valid JSON.")
