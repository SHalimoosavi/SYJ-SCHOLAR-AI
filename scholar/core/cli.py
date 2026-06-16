"""
scholar/core/cli.py
Sub-command definitions for the `scholar` CLI.

Usage examples:
    scholar summarize lecture.pdf
    scholar notes   lecture.pdf --format json
    scholar flashcards lecture.pdf --output ./cards/
    scholar quiz    lecture.pdf --count 10
    scholar exam    lecture.pdf
    scholar study   lecture.pdf
    scholar update
    scholar settings
    scholar history
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from scholar.core.config import get_config, save_config
from scholar.core.updater import check_for_update, perform_update
from scholar.core.database import get_recent_sessions
from scholar.pdf.reader import PDFReader
from scholar.ai.engine import AIEngine
from scholar.ui.progress import with_progress
from scholar.ui.renderer import render_result
from scholar.exports.exporter import export_result
from scholar.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

# ── Export format enum ────────────────────────────────────────────────────────
from enum import Enum

class ExportFormat(str, Enum):
    markdown = "markdown"
    txt      = "txt"
    json     = "json"
    html     = "html"


# ── Helper ────────────────────────────────────────────────────────────────────

def _resolve_pdf(pdf_path: Path) -> Path:
    if not pdf_path.exists():
        console.print(f"[red]✗  File not found:[/red] {pdf_path}")
        raise typer.Exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        console.print(f"[yellow]⚠  Expected a .pdf file, got:[/yellow] {pdf_path.name}")
    return pdf_path.resolve()


def _run_action(
    pdf_path: Path,
    action: str,
    fmt: ExportFormat,
    output: Optional[Path],
    use_cache: bool = True,
    **engine_kwargs,
) -> None:
    """Common pipeline: read PDF → call AI → render → export."""
    cfg = get_config()
    pdf = _resolve_pdf(pdf_path)

    with with_progress(f"Reading {pdf.name} …") as progress:
        reader = PDFReader(pdf)
        text   = reader.extract_text()
        progress.update_text(f"Running AI ({cfg.ai.ollama_model}) …")
        engine = AIEngine(cfg)
        result = engine.run(
            action=action, text=text, pdf_path=pdf,
            use_cache=use_cache, **engine_kwargs,
        )

    render_result(result, action=action)

    out_fmt = fmt.value if fmt else cfg.export.default_format
    out_dir = output or None
    exported = export_result(result, action=action, stem=pdf.stem, fmt=out_fmt, out_dir=out_dir)
    if exported:
        console.print(f"\n[green]✓  Saved →[/green] {exported}")


# ── Sub-command builder (called from main.py) ─────────────────────────────────

def build_app(app: typer.Typer) -> None:

    # ── summarize ─────────────────────────────────────────────────────────────
    @app.command("summarize", help="Summarise a PDF into key concepts and revision notes.")
    def summarize_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        format: ExportFormat = typer.Option(ExportFormat.markdown, "--format", "-f"),
        output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
        no_cache: bool = typer.Option(False, "--no-cache", help="Skip cache lookup"),
    ):
        _run_action(pdf, "summarize", format, output, use_cache=not no_cache)

    # ── notes ─────────────────────────────────────────────────────────────────
    @app.command("notes", help="Generate structured study notes from a PDF.")
    def notes_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        format: ExportFormat = typer.Option(ExportFormat.markdown, "--format", "-f"),
        output: Optional[Path] = typer.Option(None, "--output", "-o"),
        no_cache: bool = typer.Option(False, "--no-cache"),
    ):
        _run_action(pdf, "notes", format, output, use_cache=not no_cache)

    # ── flashcards ────────────────────────────────────────────────────────────
    @app.command("flashcards", help="Create Q&A flashcards from a PDF.")
    def flashcards_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        format: ExportFormat = typer.Option(ExportFormat.markdown, "--format", "-f"),
        output: Optional[Path] = typer.Option(None, "--output", "-o"),
        no_cache: bool = typer.Option(False, "--no-cache"),
    ):
        _run_action(pdf, "flashcards", format, output, use_cache=not no_cache)

    # ── quiz ──────────────────────────────────────────────────────────────────
    @app.command("quiz", help="Generate MCQ, True/False and short-answer questions.")
    def quiz_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        count: int = typer.Option(5, "--count", "-n", help="Number of questions per type"),
        format: ExportFormat = typer.Option(ExportFormat.markdown, "--format", "-f"),
        output: Optional[Path] = typer.Option(None, "--output", "-o"),
        no_cache: bool = typer.Option(False, "--no-cache"),
    ):
        _run_action(pdf, "quiz", format, output, use_cache=not no_cache, quiz_count=count)

    # ── exam ──────────────────────────────────────────────────────────────────
    @app.command("exam", help="Generate exam preparation material and likely questions.")
    def exam_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        format: ExportFormat = typer.Option(ExportFormat.markdown, "--format", "-f"),
        output: Optional[Path] = typer.Option(None, "--output", "-o"),
        no_cache: bool = typer.Option(False, "--no-cache"),
    ):
        _run_action(pdf, "exam", format, output, use_cache=not no_cache)

    # ── study ─────────────────────────────────────────────────────────────────
    @app.command("study", help="Full study package: summary + notes + flashcards + quiz + exam.")
    def study_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        format: ExportFormat = typer.Option(ExportFormat.markdown, "--format", "-f"),
        output: Optional[Path] = typer.Option(None, "--output", "-o"),
        no_cache: bool = typer.Option(False, "--no-cache"),
    ):
        _run_action(pdf, "study", format, output, use_cache=not no_cache)

    # ── update ────────────────────────────────────────────────────────────────
    @app.command("update", help="Check for and install the latest SYJ Scholar AI release.")
    def update_cmd():
        console.print("[cyan]Checking for updates …[/cyan]")
        available, latest = check_for_update()
        if not available:
            from scholar import __version__
            console.print(f"[green]✓  You are on the latest version ({__version__}).[/green]")
            return
        console.print(f"[yellow]New version available: {latest}[/yellow]")
        if typer.confirm("Update now?", default=True):
            perform_update()

    # ── history ───────────────────────────────────────────────────────────────
    @app.command("history", help="Show recent study sessions.")
    def history_cmd(
        limit: int = typer.Option(10, "--limit", "-n"),
    ):
        from scholar.ui.renderer import render_history
        sessions = get_recent_sessions(limit=limit)
        render_history(sessions)

    # ── settings ──────────────────────────────────────────────────────────────
    @app.command("settings", help="View or change Scholar AI settings.")
    def settings_cmd(
        model:    Optional[str] = typer.Option(None, "--model",    help="Ollama model name"),
        provider: Optional[str] = typer.Option(None, "--provider", help="ai provider: ollama|huggingface"),
        format:   Optional[str] = typer.Option(None, "--format",   help="Default export format"),
        show:     bool          = typer.Option(False, "--show",     help="Print current settings"),
    ):
        from rich.table import Table
        cfg = get_config()

        if show or (not model and not provider and not format):
            tbl = Table(title="SYJ Scholar AI — Current Settings", show_header=True)
            tbl.add_column("Key",   style="cyan")
            tbl.add_column("Value", style="yellow")
            tbl.add_row("AI Provider",   cfg.ai.provider)
            tbl.add_row("Ollama Model",  cfg.ai.ollama_model)
            tbl.add_row("HF Model",      cfg.ai.hf_model_id)
            tbl.add_row("Temperature",   str(cfg.ai.temperature))
            tbl.add_row("Max Tokens",    str(cfg.ai.max_tokens))
            tbl.add_row("Export Format", cfg.export.default_format)
            tbl.add_row("Theme",         cfg.ui.theme)
            console.print(tbl)
            return

        ai_patch = {}
        if model:
            ai_patch["ollama_model"] = model
        if provider:
            ai_patch["provider"] = provider

        export_patch = {}
        if format:
            export_patch["default_format"] = format

        updated = get_config()
        if ai_patch:
            updated.ai = updated.ai.model_copy(update=ai_patch)
        if export_patch:
            updated.export = updated.export.model_copy(update=export_patch)

        save_config(updated)
        console.print("[green]✓  Settings saved.[/green]")

    # ── quiz-test (interactive self-test) ─────────────────────────────────────
    @app.command("quiz-test", help="Interactive self-test mode for a PDF quiz.")
    def quiz_test_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        count: int = typer.Option(5, "--count", "-n", help="Questions per type"),
        no_cache: bool = typer.Option(False, "--no-cache"),
    ):
        from scholar.quiz.runner import QuizRunner

        cfg = get_config()
        pdf = _resolve_pdf(pdf)

        with with_progress(f"Building quiz from {pdf.name} …") as prog:
            from scholar.pdf.reader import PDFReader
            text   = PDFReader(pdf).extract_text()
            prog.update_text(f"Running AI ({cfg.ai.ollama_model}) …")
            engine = AIEngine(cfg)
            result = engine.run(
                action="quiz", text=text, pdf_path=pdf,
                use_cache=not no_cache, quiz_count=count,
            )

        runner = QuizRunner(result)
        runner.run_interactive()

    # ── schedule ──────────────────────────────────────────────────────────────
    @app.command("schedule", help="Generate a day-by-day study schedule from exam prep.")
    def schedule_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        days: int = typer.Option(7, "--days", "-d", help="Days until exam"),
        no_cache: bool = typer.Option(False, "--no-cache"),
    ):
        from scholar.exam.prep import ExamPrepEngine
        from rich.table import Table

        cfg = get_config()
        pdf = _resolve_pdf(pdf)

        with with_progress(f"Generating exam prep for {pdf.name} …") as prog:
            from scholar.pdf.reader import PDFReader
            text   = PDFReader(pdf).extract_text()
            prog.update_text("Generating exam prep …")
            engine = AIEngine(cfg)
            result = engine.run(
                action="exam", text=text, pdf_path=pdf, use_cache=not no_cache,
            )

        ep       = ExamPrepEngine(result)
        schedule = ep.generate_schedule(days_until_exam=days)

        tbl = Table(title=f"Study Schedule — {days} days to exam",
                    show_header=True, header_style="bold cyan")
        tbl.add_column("Day",   style="cyan",   justify="center")
        tbl.add_column("Date",  style="white")
        tbl.add_column("Focus", style="yellow")
        tbl.add_column("Topic", style="white")

        focus_color = {
            "HIGH PRIORITY":   "red",
            "MEDIUM PRIORITY": "yellow",
            "LOW PRIORITY":    "green",
            "REVISION DAY":    "bright_cyan",
        }
        for s in schedule:
            focus = s["focus"]
            color = focus_color.get(focus, "white")
            tbl.add_row(
                str(s["day"]),
                s["date"],
                f"[{color}]{focus}[/{color}]",
                s["topic"],
            )
        console.print(tbl)

    # ── models ────────────────────────────────────────────────────────────────
    @app.command("models", help="List available Ollama models on this device.")
    def models_cmd(
        pull: Optional[str] = typer.Option(
            None, "--pull", "-p", help="Pull a model by name (e.g. gemma:2b)"
        ),
    ):
        from scholar.ai.ollama_provider import OllamaProvider, RECOMMENDED_MODELS
        from rich.table import Table
        import subprocess, sys

        cfg      = get_config()
        provider = OllamaProvider(host=cfg.ai.ollama_host)

        if pull:
            console.print(f"[cyan]Pulling model: {pull} …[/cyan]")
            try:
                subprocess.run(["ollama", "pull", pull], check=True)
                console.print(f"[green]✓  Model '{pull}' downloaded successfully.[/green]")
            except subprocess.CalledProcessError:
                console.print(f"[red]✗  Failed to pull '{pull}'. Is Ollama running?[/red]")
            return

        if not provider.is_available():
            console.print("[red]✗  Ollama is not running.[/red]")
            console.print("Start it with:  [cyan]ollama serve[/cyan]")
            return

        installed = provider.list_models()
        tbl = Table(title="Ollama Models", show_header=True, header_style="bold cyan")
        tbl.add_column("Model",      style="white")
        tbl.add_column("Status",     style="bold")
        tbl.add_column("Recommended for Termux")

        installed_names = {m.split(":")[0] for m in installed}
        for rec in RECOMMENDED_MODELS:
            base = rec.split(":")[0]
            is_installed = base in installed_names or rec in installed
            status = "[green]✓ Installed[/green]" if is_installed else "[dim]Not installed[/dim]"
            note   = "⚡ Fast, 2GB RAM" if "2b" in rec or "mini" in rec else \
                     "🪶 Lightest"    if "tiny" in rec else \
                     "⚖️  Balanced"
            tbl.add_row(rec, status, note)

        console.print(tbl)
        if installed:
            console.print(f"\n[dim]Other installed: {', '.join(installed)}[/dim]")
        console.print(
            f"\n[muted]Pull a model:[/muted] [cyan]scholar models --pull gemma:2b[/cyan]"
        )

