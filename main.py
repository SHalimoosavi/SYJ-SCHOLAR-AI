#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════╗
║           SYJ SCHOLAR AI  v1.0.0                  ║
║       Your Offline AI Study Companion             ║
║  https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI  ║
╚═══════════════════════════════════════════════════╝

Entry point — handles both:
  • `scholar`                  → interactive dashboard
  • `scholar <command> <file>` → direct CLI commands
"""

import sys
from pathlib import Path

import typer
from rich.console import Console

# Make package importable when run directly (e.g. python main.py)
sys.path.insert(0, str(Path(__file__).parent))

from scholar.core.cli import build_app
from scholar.ui.dashboard import launch_dashboard
from scholar.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)

# ── Typer root app ────────────────────────────────────────────────────────────
app = typer.Typer(
    name="scholar",
    help="[bold cyan]SYJ Scholar AI[/bold cyan] — Your Offline AI Study Companion",
    rich_markup_mode="rich",
    no_args_is_help=False,         # We want to show dashboard on bare `scholar`
    add_completion=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# Register all sub-commands (summarize, notes, flashcards, quiz, exam, study …)
build_app(app)


@app.callback(invoke_without_command=True)
def root_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit.", is_eager=True
    ),
):
    """
    Launch the interactive dashboard when called with no sub-command,
    or execute a sub-command directly.
    """
    if version:
        console.print("[bold cyan]SYJ Scholar AI[/bold cyan] [yellow]v1.0.0[/yellow]")
        console.print("MIT License | https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/")
        raise typer.Exit()

    # No sub-command → open interactive dashboard
    if ctx.invoked_subcommand is None:
        launch_dashboard()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app()
