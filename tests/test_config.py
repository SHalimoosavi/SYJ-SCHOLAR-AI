"""
tests/test_config.py
Tests for scholar.core.config
"""

import json
import pytest
from pathlib import Path
from scholar.core.config import AppConfig, AIConfig, ExportConfig, UIConfig, load_config, save_config


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    """Redirect CONFIG_FILE to a temp path."""
    cfg_path = tmp_path / "config.json"
    import scholar.core.config as cfg_module
    monkeypatch.setattr(cfg_module, "CONFIG_FILE", cfg_path)
    return cfg_path


def test_default_config():
    cfg = AppConfig()
    assert cfg.ai.provider         == "ollama"
    assert cfg.ai.ollama_model     == "gemma:2b"
    assert cfg.ai.temperature      == 0.3
    assert cfg.export.default_format == "markdown"
    assert cfg.ui.theme            == "dark"


def test_save_and_load(config_file):
    import scholar.core.config as cfg_module
    cfg                    = AppConfig()
    cfg.ai.ollama_model    = "phi:mini"
    cfg.export.default_format = "json"
    save_config(cfg)

    assert config_file.exists()
    loaded = load_config()
    assert loaded.ai.ollama_model      == "phi:mini"
    assert loaded.export.default_format == "json"


def test_load_missing_returns_defaults(config_file):
    # config_file does not exist yet
    loaded = load_config()
    assert loaded.ai.provider == "ollama"


def test_load_corrupt_returns_defaults(config_file):
    config_file.write_text("{ invalid json !!!", encoding="utf-8")
    loaded = load_config()
    assert loaded.ai.provider == "ollama"


def test_ai_config_fields():
    ai = AIConfig(
        provider="huggingface",
        hf_model_id="microsoft/phi-2",
        temperature=0.7,
        max_tokens=512,
    )
    assert ai.provider    == "huggingface"
    assert ai.temperature == 0.7
    assert ai.max_tokens  == 512


def test_config_model_copy():
    cfg     = AppConfig()
    new_ai  = cfg.ai.model_copy(update={"ollama_model": "tinyllama"})
    assert new_ai.ollama_model == "tinyllama"
    # Original unchanged
    assert cfg.ai.ollama_model == "gemma:2b"


def test_config_json_serializable():
    cfg  = AppConfig()
    data = json.loads(cfg.model_dump_json())
    assert "ai"     in data
    assert "export" in data
    assert "ui"     in data
