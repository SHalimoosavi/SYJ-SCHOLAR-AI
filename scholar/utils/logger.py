"""
scholar/utils/logger.py
Centralised logging configuration using Loguru.
"""

import sys
from pathlib import Path

from loguru import logger as _loguru_logger
from scholar.utils.paths import get_log_dir


def _configure_logger() -> None:
    """Set up sinks: rotating file + stderr (only WARNING+)."""
    _loguru_logger.remove()                    # clear default sink

    log_file = get_log_dir() / "scholar.log"

    # File sink – full detail, rotated daily, kept 7 days
    _loguru_logger.add(
        str(log_file),
        level="DEBUG",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
            "{name}:{function}:{line} — {message}"
        ),
        enqueue=True,           # thread-safe
    )

    # Stderr sink – warnings and above (keeps terminal clean)
    _loguru_logger.add(
        sys.stderr,
        level="WARNING",
        colorize=True,
        format="<yellow>{level}</yellow>: {message}",
    )


_configure_logger()


def get_logger(name: str):
    """Return a contextualised logger bound to *name*."""
    return _loguru_logger.bind(name=name)
