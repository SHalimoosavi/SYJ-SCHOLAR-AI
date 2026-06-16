"""scholar.core — configuration, CLI, DB, plugins, and updater."""
from .config import get_config, save_config, load_config, AppConfig
from .database import init_db, log_session, get_recent_sessions, get_cached_result, cache_result

__all__ = [
    "get_config", "save_config", "load_config", "AppConfig",
    "init_db", "log_session", "get_recent_sessions",
    "get_cached_result", "cache_result",
]
