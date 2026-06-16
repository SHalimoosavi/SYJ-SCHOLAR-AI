"""
tests/test_ollama_provider.py
Tests for scholar.ai.ollama_provider (all HTTP calls are mocked).
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from scholar.ai.ollama_provider import OllamaProvider, _strip_fences, RECOMMENDED_MODELS


# ── _strip_fences ─────────────────────────────────────────────────────────────

def test_strip_fences_plain():
    assert _strip_fences('{"key": "value"}') == '{"key": "value"}'


def test_strip_fences_json_code_block():
    text = '```json\n{"key": "value"}\n```'
    assert _strip_fences(text) == '{"key": "value"}'


def test_strip_fences_bare_code_block():
    text = '```\n{"key": "value"}\n```'
    assert _strip_fences(text) == '{"key": "value"}'


def test_strip_fences_whitespace():
    text = '  \n```json\n{"a":1}\n```\n  '
    assert _strip_fences(text) == '{"a":1}'


# ── OllamaProvider.is_available ───────────────────────────────────────────────

def test_is_available_success():
    with patch("scholar.ai.ollama_provider.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        p = OllamaProvider()
        assert p.is_available() is True


def test_is_available_failure():
    with patch("scholar.ai.ollama_provider.httpx.get", side_effect=Exception("refused")):
        p = OllamaProvider()
        assert p.is_available() is False


# ── OllamaProvider.list_models ────────────────────────────────────────────────

def test_list_models_returns_names():
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {
        "models": [{"name": "gemma:2b"}, {"name": "phi:mini"}]
    }
    with patch("scholar.ai.ollama_provider.httpx.get", return_value=mock_resp):
        p = OllamaProvider()
        models = p.list_models()
        assert "gemma:2b" in models
        assert "phi:mini" in models


def test_list_models_on_error_returns_empty():
    with patch("scholar.ai.ollama_provider.httpx.get", side_effect=Exception("fail")):
        p = OllamaProvider()
        assert p.list_models() == []


# ── OllamaProvider.model_exists ──────────────────────────────────────────────

def test_model_exists_true():
    with patch.object(OllamaProvider, "list_models", return_value=["gemma:2b", "phi:mini"]):
        p = OllamaProvider(model="gemma:2b")
        assert p.model_exists() is True


def test_model_exists_false():
    with patch.object(OllamaProvider, "list_models", return_value=["phi:mini"]):
        p = OllamaProvider(model="mistral:7b")
        assert p.model_exists() is False


# ── OllamaProvider.generate ───────────────────────────────────────────────────

def test_generate_chat_endpoint():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"message": {"content": "Hello!"}}
    mock_resp.raise_for_status = MagicMock()
    with patch("scholar.ai.ollama_provider.httpx.post", return_value=mock_resp):
        p      = OllamaProvider()
        result = p.generate("system prompt", "user prompt")
        assert result == "Hello!"


def test_generate_json_valid():
    payload = '{"title": "Test", "concepts": ["A", "B"]}'
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"message": {"content": payload}}
    mock_resp.raise_for_status = MagicMock()
    with patch("scholar.ai.ollama_provider.httpx.post", return_value=mock_resp):
        p      = OllamaProvider()
        result = p.generate_json("sys", "user")
        assert result["title"] == "Test"
        assert result["concepts"] == ["A", "B"]


def test_generate_json_with_fences():
    payload = '```json\n{"title": "Fenced"}\n```'
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"message": {"content": payload}}
    mock_resp.raise_for_status = MagicMock()
    with patch("scholar.ai.ollama_provider.httpx.post", return_value=mock_resp):
        p      = OllamaProvider()
        result = p.generate_json("sys", "user")
        assert result["title"] == "Fenced"


def test_generate_json_invalid_raises():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"message": {"content": "not json at all !!!"}}
    mock_resp.raise_for_status = MagicMock()
    with patch("scholar.ai.ollama_provider.httpx.post", return_value=mock_resp):
        p = OllamaProvider()
        with pytest.raises(ValueError, match="valid JSON"):
            p.generate_json("sys", "user")


# ── RECOMMENDED_MODELS ────────────────────────────────────────────────────────

def test_recommended_models_not_empty():
    assert len(RECOMMENDED_MODELS) >= 4


def test_recommended_models_are_strings():
    for m in RECOMMENDED_MODELS:
        assert isinstance(m, str)
        assert len(m) >= 3   # minimum sensible model name length
