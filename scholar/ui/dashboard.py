"""
scholar/ui/dashboard.py
Interactive terminal dashboard for SYJ Scholar AI.

Launched when `scholar` is run with no arguments.
Built with Rich — works beautifully in Termux and standard Linux terminals.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.align import Align
from rich.columns import Columns
from rich.live import Live
from rich import box

from scholar import __version__
from scholar.ui.theme import SCHOLAR_THEME, SEP
from scholar.core.config import get_config, save_config
from scholar.core.updater import check_for_update
from scholar.core.database import get_recent_sessions
from scholar.utils.logger import get_logger

logger   = get_logger(__name__)
console  = Console(theme=SCHOLAR_THEME)

LOGO = r"""
 ███████╗██╗   ██╗     ██╗
 ██╔════╝╚██╗ ██╔╝     ██║
 ███████╗ ╚████╔╝      ██║
 ╚════██║  ╚██╔╝  ██   ██║
 ███████║   ██║   ╚█████╔╝
 ╚══════╝   ╚═╝    ╚════╝
"""

TAGLINE = "Your Offline AI Study Companion"


# ── Menu items ────────────────────────────────────────────────────────────────

MENU = [
    ("1", "📚  Study PDF",           "Full study package: summary + notes + flashcards + quiz + exam"),
    ("2", "📄  Summarize PDF",        "Chapter summary, key concepts, definitions, revision notes"),
    ("3", "📝  Generate Notes",       "Structured study notes with formulas and key concepts"),
    ("4", "🃏  Generate Flashcards",  "Q&A cards — export to Markdown or JSON"),
    ("5", "❓  Generate Quiz",        "MCQs, True/False, short & long questions"),
    ("6", "🎯  Exam Mode",            "Likely questions, priority topics, revision checklist"),
    ("7", "🧠  Interactive Quiz",     "Self-test mode with instant scoring"),
    ("8", "📅  Study Schedule",       "AI-generated day-by-day study plan"),
    ("9", "📜  View History",         "Recent study sessions"),
    ("s", "⚙️   Settings",            "AI model, export format, theme"),
    ("m", "🤖  AI Models",            "List/download Ollama models"),
    ("u", "🔄  Check for Update",     "Pull the latest Scholar AI version"),
    ("0", "👋  Exit",                ""),
]


# ── Entry point ───────────────────────────────────────────────────────────────

def launch_dashboard() -> None:
    """Main event loop for the interactive dashboard."""
    _print_banner()

    while True:
        _print_menu()
        choice = Prompt.ask(
            "[bold cyan]scholar[/bold cyan]",
            default="0",
            console=console,
        ).strip()

        if choice == "0":
            console.print("\n[brand]Goodbye! Keep studying! 🚀[/brand]\n")
            sys.exit(0)
        elif choice == "1":
            _handle_action("study")
        elif choice == "2":
            _handle_action("summarize")
        elif choice == "3":
            _handle_action("notes")
        elif choice == "4":
            _handle_action("flashcards")
        elif choice == "5":
            _handle_action("quiz")
        elif choice == "6":
            _handle_action("exam")
        elif choice == "7":
            _handle_quiz_test()
        elif choice == "8":
            _handle_schedule()
        elif choice == "9":
            _handle_history()
        elif choice in ("s", "S"):
            _handle_settings()
        elif choice in ("m", "M"):
            _handle_models()
        elif choice in ("u", "U"):
            _handle_update()
        else:
            console.print("[warning]Unknown choice. Enter a number or letter from the menu.[/warning]")


# ── Banner ────────────────────────────────────────────────────────────────────

def _print_banner() -> None:
    console.clear()
    logo_text = Text(LOGO, style="bold cyan")
    console.print(Align.center(logo_text))
    console.print(Align.center(Text(f"  SCHOLAR AI  v{__version__}", style="bold white")))
    console.print(Align.center(Text(f"  {TAGLINE}", style="dim cyan")))
    console.print(Align.center(Text(
        "  MIT License | github.com/SHalimoosavi/SYJ-SCHOLAR-AI", style="dim"
    )))
    console.print()


# ── Menu ──────────────────────────────────────────────────────────────────────

def _print_menu() -> None:
    tbl = Table(
        box=box.ROUNDED,
        border_style="cyan",
        show_header=False,
        expand=False,
        padding=(0, 1),
    )
    tbl.add_column("key",  style="bold cyan",  width=4)
    tbl.add_column("name", style="bold white",  min_width=28)
    tbl.add_column("desc", style="dim",         min_width=40)

    for key, name, desc in MENU:
        tbl.add_row(f"[{key}]", name, desc)

    console.print(Align.center(tbl))
    console.print()


# ── Action handler ────────────────────────────────────────────────────────────

def _handle_action(action: str) -> None:
    """Prompt for a PDF path and run the chosen action."""
    console.print(f"\n[subheading]Enter path to your PDF file:[/subheading]")
    console.print("[muted](drag & drop the file here or type the path)[/muted]")

    raw = Prompt.ask("[cyan]PDF path[/cyan]", console=console).strip().strip("'\"")
    if not raw:
        console.print("[warning]No path entered.[/warning]")
        return

    pdf_path = Path(raw).expanduser().resolve()
    if not pdf_path.exists():
        console.print(f"[error]File not found:[/error] {pdf_path}")
        return
    if not pdf_path.suffix.lower() == ".pdf":
        if not Confirm.ask(f"[warning]File does not have .pdf extension. Continue?[/warning]",
                           default=False, console=console):
            return

    fmt = _ask_format()

    # Import lazily to keep startup fast
    from scholar.pdf.reader import PDFReader
    from scholar.ai.engine import AIEngine
    from scholar.ui.progress import with_progress
    from scholar.ui.renderer import render_result
    from scholar.exports.exporter import export_result
    from scholar.core.config import get_config

    cfg = get_config()

    try:
        with with_progress(f"Reading {pdf_path.name} …") as prog:
            reader = PDFReader(pdf_path)
            text   = reader.extract_text()
            prog.update_text(f"Running AI ({cfg.ai.ollama_model}) …")
            engine = AIEngine(cfg)
            result = engine.run(action=action, text=text, pdf_path=pdf_path)

        render_result(result, action=action)
        exported = export_result(result, action=action, stem=pdf_path.stem, fmt=fmt)
        if exported:
            console.print(f"\n[success]✓  Saved →[/success] [underline]{exported}[/underline]")

    except Exception as exc:
        console.print(f"\n[error]Error:[/error] {exc}")
        logger.error(f"Dashboard action error: {exc}", exc_info=True)

    Prompt.ask("\n[muted]Press Enter to return to menu …[/muted]", console=console)


def _ask_format() -> str:
    formats = ["markdown", "txt", "json", "html"]
    console.print("\n[subheading]Export format:[/subheading]")
    for i, f in enumerate(formats, 1):
        console.print(f"  [{i}] {f}")
    choice = Prompt.ask("[cyan]Format (default: markdown)[/cyan]",
                        default="1", console=console).strip()
    try:
        return formats[int(choice) - 1]
    except (ValueError, IndexError):
        return "markdown"


# ── History ───────────────────────────────────────────────────────────────────

def _handle_history() -> None:
    from scholar.ui.renderer import render_history
    sessions = get_recent_sessions(limit=15)
    render_history(sessions)
    Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)


# ── Settings ──────────────────────────────────────────────────────────────────

def _handle_settings() -> None:
    cfg = get_config()
    console.print()
    console.print(Rule("[subheading]Settings[/subheading]", style="cyan"))

    tbl = Table(box=box.SIMPLE, show_header=False)
    tbl.add_column("Key",   style="cyan",   min_width=20)
    tbl.add_column("Value", style="yellow")
    tbl.add_row("AI Provider",     cfg.ai.provider)
    tbl.add_row("Ollama Model",    cfg.ai.ollama_model)
    tbl.add_row("HF Model",        cfg.ai.hf_model_id)
    tbl.add_row("Temperature",     str(cfg.ai.temperature))
    tbl.add_row("Max Tokens",      str(cfg.ai.max_tokens))
    tbl.add_row("Export Format",   cfg.export.default_format)
    console.print(tbl)

    if not Confirm.ask("[cyan]Edit settings?[/cyan]", default=False, console=console):
        return

    new_model = Prompt.ask(
        f"[cyan]Ollama model[/cyan] (current: {cfg.ai.ollama_model})",
        default=cfg.ai.ollama_model,
        console=console,
    )
    new_fmt = Prompt.ask(
        f"[cyan]Default export format[/cyan] (current: {cfg.export.default_format})",
        default=cfg.export.default_format,
        console=console,
    )

    cfg.ai.ollama_model = new_model
    cfg.export.default_format = new_fmt
    save_config(cfg)
    console.print("[success]✓  Settings saved.[/success]")
    Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)


# ── Update ────────────────────────────────────────────────────────────────────

def _handle_update() -> None:
    from scholar.core.updater import check_for_update, perform_update

    console.print("[cyan]Checking for updates …[/cyan]")
    available, latest = check_for_update()
    if not available:
        console.print(f"[success]✓  You are on the latest version (v{__version__}).[/success]")
    else:
        console.print(f"[warning]New version available: v{latest}[/warning]")
        if Confirm.ask("Update now?", default=True, console=console):
            perform_update()

    Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)


# ── Interactive quiz ───────────────────────────────────────────────────────────

def _handle_quiz_test() -> None:
    """Generate a quiz and run interactive self-test mode."""
    from scholar.quiz.runner import QuizRunner
    from scholar.pdf.reader import PDFReader
    from scholar.ai.engine import AIEngine
    from scholar.core.config import get_config

    console.print("\n[subheading]Interactive Quiz Mode[/subheading]")
    raw = Prompt.ask("[cyan]PDF path[/cyan]", console=console).strip().strip("'\"")
    if not raw:
        return
    pdf_path = Path(raw).expanduser().resolve()
    if not pdf_path.exists():
        console.print(f"[error]File not found:[/error] {pdf_path}")
        Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)
        return

    count_str = Prompt.ask("[cyan]Questions per type[/cyan]", default="5", console=console)
    try:
        count = max(1, int(count_str))
    except ValueError:
        count = 5

    cfg = get_config()
    try:
        with with_progress(f"Building quiz from {pdf_path.name} …") as prog:
            text   = PDFReader(pdf_path).extract_text()
            prog.update_text(f"Running AI ({cfg.ai.ollama_model}) …")
            engine = AIEngine(cfg)
            result = engine.run(
                action="quiz", text=text, pdf_path=pdf_path,
                use_cache=True, quiz_count=count,
            )
        runner = QuizRunner(result)
        runner.run_interactive()
    except Exception as exc:
        console.print(f"[error]Error:[/error] {exc}")

    Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)


# ── Study schedule ─────────────────────────────────────────────────────────────

def _handle_schedule() -> None:
    """Generate an AI-powered study schedule."""
    from scholar.exam.prep import ExamPrepEngine
    from scholar.pdf.reader import PDFReader
    from scholar.ai.engine import AIEngine
    from scholar.core.config import get_config
    from rich.table import Table

    console.print("\n[subheading]Study Schedule Generator[/subheading]")
    raw = Prompt.ask("[cyan]PDF path[/cyan]", console=console).strip().strip("'\"")
    if not raw:
        return
    pdf_path = Path(raw).expanduser().resolve()
    if not pdf_path.exists():
        console.print(f"[error]File not found:[/error] {pdf_path}")
        Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)
        return

    days_str = Prompt.ask("[cyan]Days until exam[/cyan]", default="7", console=console)
    try:
        days = max(1, int(days_str))
    except ValueError:
        days = 7

    cfg = get_config()
    try:
        with with_progress(f"Generating exam prep for {pdf_path.name} …") as prog:
            text   = PDFReader(pdf_path).extract_text()
            prog.update_text("Analysing topics …")
            engine = AIEngine(cfg)
            result = engine.run(
                action="exam", text=text, pdf_path=pdf_path, use_cache=True,
            )

        ep       = ExamPrepEngine(result)
        schedule = ep.generate_schedule(days_until_exam=days)

        tbl = Table(
            title=f"Study Schedule — {days} day(s) to exam",
            show_header=True, header_style="bold cyan",
        )
        tbl.add_column("Day",   justify="center", style="cyan")
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
                str(s["day"]), s["date"],
                f"[{color}]{focus}[/{color}]", s["topic"],
            )
        console.print(tbl)

    except Exception as exc:
        console.print(f"[error]Error:[/error] {exc}")

    Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)


# ── Models ─────────────────────────────────────────────────────────────────────

def _handle_models() -> None:
    """List installed Ollama models and optionally pull new ones."""
    from scholar.ai.ollama_provider import OllamaProvider, RECOMMENDED_MODELS
    from scholar.core.config import get_config
    from rich.table import Table
    import subprocess

    cfg      = get_config()
    provider = OllamaProvider(host=cfg.ai.ollama_host)

    console.print("\n[subheading]AI Models (Ollama)[/subheading]")

    if not provider.is_available():
        console.print("[warning]⚠  Ollama is not running.[/warning]")
        console.print("Start it with: [cyan]ollama serve[/cyan]")
        Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)
        return

    installed      = provider.list_models()
    installed_bases = {m.split(":")[0] for m in installed}

    tbl = Table(show_header=True, header_style="bold cyan")
    tbl.add_column("Model",  style="white", min_width=18)
    tbl.add_column("Status", style="bold")
    tbl.add_column("RAM",    style="dim")
    tbl.add_column("Notes",  style="dim")

    model_info = {
        "gemma:2b":   ("2 GB",   "⚡ Fast, great quality"),
        "phi:mini":   ("1.3 GB", "⚡ Very fast"),
        "tinyllama":  ("0.6 GB", "🪶 Lightest option"),
        "qwen:1.8b":  ("1 GB",   "⚡ Fast multilingual"),
        "phi3:mini":  ("2.3 GB", "⭐ High quality"),
        "mistral:7b": ("4 GB",   "🏆 Best quality"),
    }
    for rec in RECOMMENDED_MODELS:
        base       = rec.split(":")[0]
        installed_ = base in installed_bases or rec in installed
        status     = "[green]✓ Installed[/green]" if installed_ else "[dim]Available[/dim]"
        ram, note  = model_info.get(rec, ("?", ""))
        tbl.add_row(rec, status, ram, note)
    console.print(tbl)
    console.print(f"\nCurrent model: [cyan]{cfg.ai.ollama_model}[/cyan]")

    pull = Prompt.ask(
        "\n[cyan]Pull a model (e.g. gemma:2b) or press Enter to skip[/cyan]",
        default="",
        console=console,
    ).strip()
    if pull:
        console.print(f"[cyan]Pulling {pull} …[/cyan]")
        try:
            subprocess.run(["ollama", "pull", pull], check=True)
            console.print(f"[success]✓  Model '{pull}' downloaded.[/success]")
            if Confirm.ask(
                f"Switch to '{pull}' as default model?", default=True, console=console
            ):
                cfg.ai.ollama_model = pull
                save_config(cfg)
                console.print("[success]✓  Default model updated.[/success]")
        except Exception as exc:
            console.print(f"[error]Failed:[/error] {exc}")

    Prompt.ask("\n[muted]Press Enter to return …[/muted]", console=console)
