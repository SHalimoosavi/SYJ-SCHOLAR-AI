"""
scholar/ui/renderer.py
Terminal rendering of AI results using Rich.
Each action has a dedicated renderer for a polished output.
"""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.markdown import Markdown
from rich.rule import Rule

from scholar.ui.theme import SCHOLAR_THEME, SEP, SEP2

console = Console(theme=SCHOLAR_THEME)


# ── Main dispatcher ───────────────────────────────────────────────────────────

def render_result(result: dict[str, Any], action: str) -> None:
    """Route to the correct renderer based on *action*."""
    _render_header(action)

    if result.get("_error"):
        _render_error(result)
        return

    dispatch = {
        "summarize":  _render_summarize,
        "notes":      _render_notes,
        "flashcards": _render_flashcards,
        "quiz":       _render_quiz,
        "exam":       _render_exam,
        "study":      _render_study,
    }
    renderer = dispatch.get(action, _render_generic)
    renderer(result)
    _render_meta(result.get("_meta", {}))


# ── Shared helpers ────────────────────────────────────────────────────────────

def _render_header(action: str) -> None:
    label = {
        "summarize":  "📄  PDF SUMMARY",
        "notes":      "📝  STUDY NOTES",
        "flashcards": "🃏  FLASHCARDS",
        "quiz":       "❓  QUIZ",
        "exam":       "🎯  EXAM PREP",
        "study":      "📚  FULL STUDY PACKAGE",
    }.get(action, action.upper())

    console.print()
    console.print(Panel(
        f"[brand.title]{label}[/brand.title]",
        border_style="cyan",
        expand=True,
    ))


def _render_error(result: dict) -> None:
    console.print(Panel(
        f"[error]Error:[/error] {result.get('note', result.get('_error', 'Unknown error'))}",
        border_style="red",
        title="[error]Generation Failed[/error]",
    ))


def _render_meta(meta: dict) -> None:
    if not meta:
        return
    console.print(
        f"\n[footer]⚡ {meta.get('model','?')}  |  "
        f"⏱ {meta.get('duration_s','?')}s  |  "
        f"{'📦 cached' if meta.get('from_cache') else '🤖 generated'}[/footer]"
    )


# ── Summarize ─────────────────────────────────────────────────────────────────

def _render_summarize(r: dict) -> None:
    if title := r.get("title"):
        console.print(f"\n[heading]{title}[/heading]")

    if summary := r.get("summary"):
        console.print(
            Panel(
                summary,
                title="[subheading]Summary[/subheading]",
                border_style="blue",
            )
        )

    if points := r.get("key_points"):
        _render_bullet_list(
            "Key Points",
            points,
            "•",
        )

# ── Notes ─────────────────────────────────────────────────────────────────────

def _render_notes(r: dict) -> None:
    if title := r.get("title"):
        console.print(f"\n[heading]{title}[/heading]")

    if overview := r.get("overview"):
        console.print(
            Panel(
                overview,
                title="[subheading]Overview[/subheading]",
                border_style="green",
            )
        )

    if notes := r.get("notes"):
        _render_bullet_list(
            "Study Notes",
            notes,
            "•",
        )

# ── Flashcards ────────────────────────────────────────────────────────────────

def _render_flashcards(r: dict) -> None:
    cards = r.get("cards", [])
    topic = r.get("topic", "")
    if topic:
        console.print(f"\n[heading]Topic: {topic}[/heading]")
    console.print(f"[muted]{len(cards)} flashcards generated[/muted]\n")

    for card in cards:
        diff_color = {"easy": "green", "medium": "yellow", "hard": "red"}.get(
            card.get("difficulty", "medium"), "white"
        )
        tags = " ".join(f"[{t}]" for t in card.get("tags", []))
        q_panel = Panel(
            f"[question]{card.get('question', '')}[/question]\n\n"
            f"[answer]▶ {card.get('answer', '')}[/answer]\n\n"
            f"[{diff_color}]Difficulty: {card.get('difficulty','?')}[/{diff_color}]  "
            f"[muted]{tags}[/muted]",
            title=f"[muted]#{card.get('id','?')}[/muted]",
            border_style=diff_color,
        )
        console.print(q_panel)


# ── Quiz ──────────────────────────────────────────────────────────────────────

def _render_quiz(r: dict) -> None:
    if topic := r.get("topic"):
        console.print(f"\n[heading]Quiz: {topic}[/heading]")

    questions = r.get("questions", [])

    if not questions:
        console.print("[muted]No questions generated.[/muted]")
        return

    for i, q in enumerate(questions, 1):
        console.print(
            Panel(
                f"[question]{q.get('question','')}[/question]\n\n"
                f"[answer]{q.get('answer','')}[/answer]",
                title=f"Question {i}",
                border_style="yellow",
            )
        )

# ── Exam ──────────────────────────────────────────────────────────────────────

def _render_exam(r: dict) -> None:
    if topic := r.get("topic"):
        console.print(f"\n[heading]Exam Prep: {topic}[/heading]")

    if topics := r.get("important_topics"):
        _render_bullet_list(
            "Important Topics",
            topics,
            "•",
        )

    if questions := r.get("possible_questions"):
        _render_bullet_list(
            "Possible Exam Questions",
            questions,
            "❓",
        )

# ── Study (all-in-one) ─────────────────────────────────────────────>

def _render_study(r: dict) -> None:

    summary = r.get("summary")
    if summary:
        console.print(
            Rule(
                "[subheading]📄 SUMMARY[/subheading]",
                style="blue",
            )
        )

        if isinstance(summary, dict):
            _render_summarize(summary)
        else:
            console.print(str(summary))

    notes = r.get("notes")
    if notes:
        console.print(
            Rule(
                "[subheading]📝 NOTES[/subheading]",
                style="green",
            )
        )

        if isinstance(notes, list):
            _render_bullet_list(
                "Study Notes",
                notes,
                "•",
            )
        elif isinstance(notes, dict):
            _render_notes(notes)
        else:
            console.print(str(notes))

    flashcards = r.get("flashcards")
    if flashcards:
        console.print(
            Rule(
                "[subheading]🃏 FLASHCARDS[/subheading]",
                style="yellow",
            )
        )

        if isinstance(flashcards, dict):
            _render_flashcards(flashcards)

        elif isinstance(flashcards, list):
            for i, card in enumerate(flashcards, 1):
                console.print(
                    Panel(
                        f"{card.get('question','')}\n\n{card.get('answer','')}",
                        title=f"Card {i}",
                    )
                )

    quiz = r.get("quiz")
    if quiz:
        console.print(
            Rule(
                "[subheading]❓ QUIZ[/subheading]",
                style="magenta",
            )
        )

        if isinstance(quiz, dict):
            _render_quiz(quiz)

        elif isinstance(quiz, list):
            for i, q in enumerate(quiz, 1):
                console.print(
                    Panel(
                        q.get("answer", ""),
                        title=f"Question {i}: {q.get('question','')}",
                    )
                )

    exam = r.get("exam")
    if exam:
        console.print(
            Rule(
                "[subheading]🎯 EXAM PREP[/subheading]",
                style="red",
            )
        )

        if isinstance(exam, dict):
            _render_exam(exam)

# ── Generic fallback ──────────────────────────────────────────────────────────

def _render_generic(r: dict) -> None:
    import json
    clean = {k: v for k, v in r.items() if not k.startswith("_")}
    console.print_json(json.dumps(clean, ensure_ascii=False))


# ── History ───────────────────────────────────────────────────────────────────

def render_history(sessions: list[dict]) -> None:
    if not sessions:
        console.print("[muted]No sessions found.[/muted]")
        return
    tbl = Table(title="Recent Sessions", show_header=True, header_style="bold cyan")
    tbl.add_column("ID",      justify="right", style="muted")
    tbl.add_column("Action",  style="bold cyan")
    tbl.add_column("PDF")
    tbl.add_column("Model",   style="yellow")
    tbl.add_column("Time",    style="green")
    tbl.add_column("Date",    style="muted")
    for s in sessions:
        tbl.add_row(
            str(s.get("id","")),
            s.get("action",""),
            s.get("pdf_path","").split("/")[-1],
            s.get("model",""),
            f"{s.get('duration_s','?')}s",
            s.get("created_at","")[:16],
        )
    console.print(tbl)


# ── Bullet list helper ────────────────────────────────────────────────────────

def _render_bullet_list(
    title: str,
    items: list,
    icon: str = "•",
    style: str = "bullet",
) -> None:
    console.print(f"\n[subheading]{title}[/subheading]")
    for item in items:
        if isinstance(item, dict):
            # Try common keys
            text = item.get("item") or item.get("topic") or item.get("concept") or str(item)
        else:
            text = str(item)
        console.print(f"  [{style}]{icon}[/{style}]  {text}")


def _render_definitions(defs: dict) -> None:
    if not defs:
        return
    tbl = Table(title="Definitions", show_header=True, header_style="bold cyan",
                show_lines=True)
    tbl.add_column("Term",       style="bold magenta")
    tbl.add_column("Definition", style="white")
    for term, defn in defs.items():
        tbl.add_row(term, defn)
    console.print(tbl)
