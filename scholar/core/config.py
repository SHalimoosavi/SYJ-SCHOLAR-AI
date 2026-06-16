"""
scholar/core/config.py

Persistent configuration backed by a JSON file in the user config dir.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from scholar.utils.paths import get_config_dir
from scholar.utils.logger import get_logger

logger = get_logger(__name__)

CONFIG_FILE = get_config_dir() / "config.json"


# ---------------------------------------------------------------------
# AI Configuration
# ---------------------------------------------------------------------

class AIConfig(BaseModel):
    provider: str = "ollama"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"

    hf_model_id: str = "microsoft/phi-2"

    temperature: float = 0.3
    max_tokens: int = 4096
    timeout_seconds: int = 120


# ---------------------------------------------------------------------
# Export Configuration
# ---------------------------------------------------------------------

class ExportConfig(BaseModel):
    default_format: str = "markdown"
    output_dir: str = ""
    open_after_export: bool = False


# ---------------------------------------------------------------------
# UI Configuration
# ---------------------------------------------------------------------

class UIConfig(BaseModel):
    theme: str = "dark"
    show_spinner: bool = True
    verbose: bool = False


# ---------------------------------------------------------------------
# Application Configuration
# ---------------------------------------------------------------------

class AppConfig(BaseModel):
    version: str = "1.0.0"

    ai: AIConfig = Field(default_factory=AIConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    last_used_model: str = ""
    plugins_enabled: bool = True


# ---------------------------------------------------------------------
# Load Configuration
# ---------------------------------------------------------------------

def load_config() -> AppConfig:
    """
    Load configuration from disk.
    Returns defaults if config does not exist or is invalid.
    """

    if not CONFIG_FILE.exists():
        return AppConfig()

    try:
        data = json.loads(
            CONFIG_FILE.read_text(encoding="utf-8")
        )

        cfg = AppConfig(**data)

        # Upgrade old configs automatically
        if cfg.ai.max_tokens < 2048:
            cfg.ai.max_tokens = 4096

        return cfg

    except Exception as exc:
        logger.warning(
            f"Config load error ({exc}), using defaults."
        )
        return AppConfig()


# ---------------------------------------------------------------------
# Save Configuration
# ---------------------------------------------------------------------

def save_config(cfg: AppConfig) -> None:
    """
    Persist configuration to disk.
    """

    CONFIG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CONFIG_FILE.write_text(
        cfg.model_dump_json(indent=2),
        encoding="utf-8",
    )

    logger.debug(
        f"Config saved -> {CONFIG_FILE}"
    )


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def get_config() -> AppConfig:
    """
    Return current configuration.
    """
    return load_config()


def update_config(**kwargs: Any) -> AppConfig:
    """
    Update configuration and save.

    Example:
        update_config(
            ai={"ollama_model": "phi3"}
        )
    """

    cfg = load_config()

    data = cfg.model_dump()
    data.update(kwargs)

    new_cfg = AppConfig(**data)

    save_config(new_cfg)

    return new_cfg
