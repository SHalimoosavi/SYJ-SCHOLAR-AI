"""
scholar/core/plugins.py
Plugin discovery and loading system.

Plugins live in  ~/.local/share/SYJScholarAI/plugins/<name>/plugin.py
and must expose a `register(app)` function.

This keeps Scholar AI extensible for the community without touching core code.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import typer

from scholar.utils.paths import get_plugins_dir
from scholar.utils.logger import get_logger

logger = get_logger(__name__)


class PluginMeta:
    name: str
    version: str
    description: str
    author: str

    def __init__(self, **kwargs: Any):
        self.name        = kwargs.get("name", "unknown")
        self.version     = kwargs.get("version", "0.0.1")
        self.description = kwargs.get("description", "")
        self.author      = kwargs.get("author", "")


def discover_plugins() -> list[Path]:
    """Return plugin.py paths from the plugins directory."""
    plugins_dir = get_plugins_dir()
    return sorted(plugins_dir.glob("*/plugin.py"))


def load_plugin(plugin_path: Path) -> Any | None:
    """Dynamically load a plugin module."""
    spec = importlib.util.spec_from_file_location(
        f"scholar_plugin_{plugin_path.parent.name}",
        plugin_path,
    )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as exc:
        logger.warning(f"Plugin load error ({plugin_path.parent.name}): {exc}")
        return None


def register_plugins(app: typer.Typer) -> list[str]:
    """
    Discover and register all plugins.
    Returns list of successfully loaded plugin names.
    """
    loaded = []
    for plugin_path in discover_plugins():
        module = load_plugin(plugin_path)
        if module and hasattr(module, "register"):
            try:
                module.register(app)
                name = getattr(module, "PLUGIN_NAME", plugin_path.parent.name)
                loaded.append(name)
                logger.info(f"Plugin loaded: {name}")
            except Exception as exc:
                logger.warning(f"Plugin register error: {exc}")
    return loaded
