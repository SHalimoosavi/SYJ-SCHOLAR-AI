"""
scholar/ai/engine.py

Central AI Engine
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from scholar.core.config import AppConfig
from scholar.core.database import (
    get_cached_result,
    cache_result,
    log_session,
)

from scholar.ai.prompts import get_prompt
from scholar.ai.ollama_provider import OllamaProvider
from scholar.ai.hf_provider import HuggingFaceProvider

from scholar.utils.helpers import file_hash
from scholar.utils.logger import get_logger

logger = get_logger(__name__)

MAX_CHARS = 3000


class AIEngine:
    """
    Main AI engine.
    """

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.provider = self._resolve_provider()

    # ------------------------------------------------------------------
    # Provider selection
    # ------------------------------------------------------------------

    def _resolve_provider(self):
        ai = self.cfg.ai

        if ai.provider == "ollama":

            provider = OllamaProvider(
                host=ai.ollama_host,
                model=ai.ollama_model,
                temperature=ai.temperature,
                max_tokens=ai.max_tokens,
            )

            if provider.is_available():

                if not provider.model_exists():
                    logger.warning(
                        f"Ollama model '{ai.ollama_model}' not found."
                    )

                return provider

            logger.warning(
                "Ollama unavailable. Falling back to HuggingFace."
            )

        hf = HuggingFaceProvider(
            model_id=ai.hf_model_id,
            max_tokens=ai.max_tokens,
            temperature=ai.temperature,
        )

        if not hf.is_available():
            raise RuntimeError(
                "No AI provider available.\n"
                "Start Ollama:\n"
                "ollama serve"
            )

        return hf

    # ------------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        text: str,
        pdf_path: Path | None = None,
        use_cache: bool = True,
        quiz_count: int = 5,
        **kwargs,
    ) -> dict[str, Any]:

        model = getattr(
            self.provider,
            "model",
            self.cfg.ai.hf_model_id,
        )

        pdf_hash = (
            file_hash(pdf_path)
            if pdf_path
            else ""
        )

        cache_action = (
            f"{action}_{quiz_count}"
            if action == "quiz"
            else action
        )

        # --------------------------------------------------------------
        # Cache
        # --------------------------------------------------------------

        if use_cache and pdf_hash:

            cached = get_cached_result(
                pdf_hash,
                cache_action,
                model,
            )

            if cached:
                cached["_from_cache"] = True
                return cached

        # --------------------------------------------------------------
        # Text limit
        # --------------------------------------------------------------

        truncated = text[:MAX_CHARS]

        prompt_kwargs = {}

        if action == "quiz":
            prompt_kwargs["count"] = quiz_count

        system, user = get_prompt(
            action,
            truncated,
            **prompt_kwargs,
        )

        # --------------------------------------------------------------
        # Generation
        # --------------------------------------------------------------

        start = time.time()

        try:
            result = self.provider.generate_json(
                system,
                user,
            )

        except Exception as exc:

            logger.error(
                f"AI generation failed ({action}): {exc}"
            )

            result = _fallback_result(
                action,
                str(exc),
            )

        elapsed = round(
            time.time() - start,
            2,
        )

        result["_meta"] = {
            "action": action,
            "model": model,
            "duration_s": elapsed,
            "from_cache": False,
        }

        # --------------------------------------------------------------
        # Cache save
        # --------------------------------------------------------------

        if pdf_hash and not result.get("_error"):

            cache_result(
                pdf_hash,
                cache_action,
                model,
                result,
            )

        # --------------------------------------------------------------
        # Session log
        # --------------------------------------------------------------

        if pdf_path:

            log_session(
                pdf_path=str(pdf_path),
                pdf_hash=pdf_hash,
                action=action,
                model=model,
                duration_s=elapsed,
            )

        return result


def _fallback_result(
    action: str,
    error_msg: str,
) -> dict[str, Any]:

    return {
        "_error": error_msg,
        "title": "Generation failed",
        "note": (
            "The AI model could not produce a result.\n"
            f"Error: {error_msg}"
        ),
    }
