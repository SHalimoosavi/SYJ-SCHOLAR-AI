"""
scholar/utils/paths.py
Cross-platform path helpers.
Works on standard Linux AND Termux ($PREFIX/home).
"""

from pathlib import Path
import os

import platformdirs


APP_NAME = "SYJScholarAI"
APP_AUTHOR = "SHalimoosavi"


def _termux_home() -> Path | None:
    """Return Termux home if we are running inside Termux."""
    prefix = os.environ.get("PREFIX", "")
    if prefix and "termux" in prefix.lower():
        return Path.home()
    return None


def get_data_dir() -> Path:
    """~/.local/share/SYJScholarAI  (or Termux equivalent)"""
    p = Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_config_dir() -> Path:
    """~/.config/SYJScholarAI"""
    p = Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_cache_dir() -> Path:
    """~/.cache/SYJScholarAI"""
    p = Path(platformdirs.user_cache_dir(APP_NAME, APP_AUTHOR))
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_log_dir() -> Path:
    """~/.local/share/SYJScholarAI/logs"""
    p = get_data_dir() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_output_dir() -> Path:
    """~/SYJScholarAI-output  (visible to the student)"""
    p = Path.home() / "SYJScholarAI-output"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_models_dir() -> Path:
    """~/.local/share/SYJScholarAI/models"""
    p = get_data_dir() / "models"
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_db_path() -> Path:
    """SQLite database file path."""
    return get_data_dir() / "scholar.db"


def get_plugins_dir() -> Path:
    """~/.local/share/SYJScholarAI/plugins"""
    p = get_data_dir() / "plugins"
    p.mkdir(parents=True, exist_ok=True)
    return p
