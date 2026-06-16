"""scholar.ui — terminal UI components (dashboard, renderer, progress, theme)."""
from .dashboard import launch_dashboard
from .renderer import render_result, render_history
from .progress import with_progress
from .theme import SCHOLAR_THEME

__all__ = [
    "launch_dashboard", "render_result", "render_history",
    "with_progress", "SCHOLAR_THEME",
]
