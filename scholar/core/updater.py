"""
scholar/core/updater.py
Self-update via GitHub releases API + pip install.
Runs entirely offline if no network is available (fails gracefully).
"""

from __future__ import annotations

import subprocess
import sys

import requests
from packaging.version import Version
from rich.console import Console

from scholar import __version__
from scholar.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

GITHUB_REPO = "SHalimoosavi/SYJ-SCHOLAR-AI"
GITHUB_API  = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
INSTALL_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/install.sh"
RAW_BASE    = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"


def _fetch_latest_version() -> str | None:
    """Query GitHub API for the latest release tag.  Returns None on error."""
    try:
        resp = requests.get(GITHUB_API, timeout=8)
        resp.raise_for_status()
        tag = resp.json().get("tag_name", "")
        return tag.lstrip("v")
    except Exception as exc:
        logger.warning(f"Update check failed: {exc}")
        return None


def check_for_update() -> tuple[bool, str]:
    """
    Returns (update_available, latest_version_str).
    update_available is False when offline or already latest.
    """
    latest = _fetch_latest_version()
    if latest is None:
        return False, __version__
    try:
        is_newer = Version(latest) > Version(__version__)
        return is_newer, latest
    except Exception:
        return False, __version__


def perform_update() -> bool:
    """
    Pull the latest version via pip (works on Termux with pip inside $PREFIX).
    Returns True on success.
    """
    pip_target = f"git+https://github.com/{GITHUB_REPO}.git"
    console.print(f"[cyan]⬇  Updating SYJ Scholar AI …[/cyan]")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", pip_target],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            console.print("[green]✓  Update complete! Please restart scholar.[/green]")
            return True
        else:
            console.print(f"[red]Update failed:[/red] {result.stderr.strip()}")
            return False
    except Exception as exc:
        console.print(f"[red]Update error:[/red] {exc}")
        return False
