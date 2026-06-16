"""
scholar/ui/progress.py
Reusable Rich progress / spinner context manager.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, TextColumn,
    BarColumn, TimeElapsedColumn, TaskID,
)
from scholar.ui.theme import SCHOLAR_THEME

console = Console(theme=SCHOLAR_THEME)


class _ProgressHandle:
    """Thin wrapper to allow mid-operation status text updates."""

    def __init__(self, progress: Progress, task_id: TaskID):
        self._progress = progress
        self._task_id  = task_id

    def update_text(self, text: str) -> None:
        self._progress.update(self._task_id, description=f"[cyan]{text}[/cyan]")

    def advance(self, amount: float = 1) -> None:
        self._progress.advance(self._task_id, amount)


@contextmanager
def with_progress(description: str = "Working …") -> Generator[_ProgressHandle, None, None]:
    """
    Usage:
        with with_progress("Reading PDF …") as p:
            do_stuff()
            p.update_text("Running AI …")
            do_more_stuff()
    """
    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[cyan]{task.description}[/cyan]"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description, total=None)
        yield _ProgressHandle(progress, task)
