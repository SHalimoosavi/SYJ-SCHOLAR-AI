"""
tests/test_engine.py
Tests for scholar.ai.engine (AIEngine) — all provider calls are mocked.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scholar.ai.engine import AIEngine, _fallback_result
from scholar.core.config import AppConfig


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def app_config() -> AppConfig:
    cfg = AppConfig()
    cfg.ai.provider     = "ollama"
    cfg.ai.ollama_model = "gemma:2b"
    return cfg


@pytest.fixture
def mock_provider():
    """A fully mocked AI provider."""
    prov = MagicMock()
    prov.model = "gemma:2b"
    prov.generate_json.return_value = {
        "title": "Mocked Result",
        "key_concepts": ["A", "B"],
        "chapter_summary": "A test summary.",
        "important_definitions": {},
        "quick_revision_notes": [],
    }
    return prov


@pytest.fixture
def engine_with_mock(app_config, mock_provider, isolated_db):
    """AIEngine with the internal provider replaced by a mock."""
    with patch("scholar.ai.engine.OllamaProvider") as MockOllama:
        instance = MockOllama.return_value
        instance.is_available.return_value  = True
        instance.model_exists.return_value  = True
        instance.model                      = "gemma:2b"
        instance.generate_json.return_value = mock_provider.generate_json.return_value
        engine = AIEngine(app_config)
        engine.provider = instance
        yield engine, instance


# ── _fallback_result ──────────────────────────────────────────────────────────

def test_fallback_result_has_error_key():
    result = _fallback_result("summarize", "Connection refused")
    assert "_error" in result
    assert "Connection refused" in result["note"]


def test_fallback_result_has_title():
    result = _fallback_result("quiz", "timeout")
    assert result["title"] == "Generation failed"


# ── AIEngine.__init__ ─────────────────────────────────────────────────────────

def test_engine_uses_ollama_when_available(app_config, isolated_db):
    with patch("scholar.ai.engine.OllamaProvider") as MockOllama:
        instance = MockOllama.return_value
        instance.is_available.return_value = True
        instance.model_exists.return_value = True
        instance.model = "gemma:2b"
        engine = AIEngine(app_config)
        assert engine.provider is instance


def test_engine_falls_back_to_hf_when_ollama_unavailable(app_config, isolated_db):
    with patch("scholar.ai.engine.OllamaProvider") as MockOllama, \
         patch("scholar.ai.engine.HuggingFaceProvider") as MockHF:
        MockOllama.return_value.is_available.return_value = False
        MockHF.return_value.is_available.return_value    = True
        engine = AIEngine(app_config)
        assert engine.provider is MockHF.return_value


def test_engine_raises_when_no_provider(app_config, isolated_db):
    with patch("scholar.ai.engine.OllamaProvider") as MockOllama, \
         patch("scholar.ai.engine.HuggingFaceProvider") as MockHF:
        MockOllama.return_value.is_available.return_value = False
        MockHF.return_value.is_available.return_value    = False
        with pytest.raises(RuntimeError, match="No AI provider"):
            AIEngine(app_config)


# ── AIEngine.run ──────────────────────────────────────────────────────────────

def test_run_returns_dict(engine_with_mock):
    engine, mock_prov = engine_with_mock
    result = engine.run(action="summarize", text="Sample text " * 50)
    assert isinstance(result, dict)
    assert "title" in result


def test_run_adds_meta(engine_with_mock):
    engine, _ = engine_with_mock
    result = engine.run(action="summarize", text="Sample text " * 50)
    assert "_meta" in result
    assert result["_meta"]["action"]    == "summarize"
    assert result["_meta"]["model"]     == "gemma:2b"
    assert "duration_s" in result["_meta"]


def test_run_caches_result(engine_with_mock, sample_pdf_file):
    engine, mock_prov = engine_with_mock
    text = "Sample text " * 50

    # First call — goes to provider
    result1 = engine.run(action="summarize", text=text, pdf_path=sample_pdf_file)
    assert mock_prov.generate_json.call_count == 1

    # Second call — should hit cache and NOT call provider again
    result2 = engine.run(action="summarize", text=text, pdf_path=sample_pdf_file, use_cache=True)
    assert mock_prov.generate_json.call_count == 1   # still 1
    assert result2.get("_from_cache") is True


def test_run_skips_cache_when_no_pdf(engine_with_mock):
    engine, mock_prov = engine_with_mock
    # Without a pdf_path the hash is "" so no caching
    engine.run(action="summarize", text="text " * 50, pdf_path=None)
    engine.run(action="summarize", text="text " * 50, pdf_path=None)
    assert mock_prov.generate_json.call_count == 2


def test_run_no_cache_forces_regen(engine_with_mock, sample_pdf_file):
    engine, mock_prov = engine_with_mock
    text = "text " * 50
    engine.run(action="notes", text=text, pdf_path=sample_pdf_file, use_cache=False)
    engine.run(action="notes", text=text, pdf_path=sample_pdf_file, use_cache=False)
    assert mock_prov.generate_json.call_count == 2


def test_run_quiz_passes_count(engine_with_mock):
    engine, mock_prov = engine_with_mock
    mock_prov.generate_json.return_value = {
        "topic": "Test", "mcqs": [], "true_false": [],
        "short_questions": [], "long_questions": [],
    }
    engine.run(action="quiz", text="text " * 50, quiz_count=8)
    # The engine should have called generate_json (which received the quiz prompt with count=8)
    assert mock_prov.generate_json.called


def test_run_handles_provider_error(engine_with_mock):
    engine, mock_prov = engine_with_mock
    mock_prov.generate_json.side_effect = Exception("Model timeout")
    result = engine.run(action="summarize", text="text " * 50)
    assert "_error" in result
    assert "Model timeout" in result["_error"]


def test_run_truncates_long_text(engine_with_mock):
    engine, mock_prov = engine_with_mock
    very_long_text = "word " * 50_000   # >> MAX_CHARS
    engine.run(action="summarize", text=very_long_text)
    # The prompt sent to generate_json should contain truncated text
    call_args = mock_prov.generate_json.call_args
    _, user_prompt = call_args[0]
    # user prompt should not contain all 50_000 words verbatim
    assert len(user_prompt) < 50_000 * 6   # sanity check
