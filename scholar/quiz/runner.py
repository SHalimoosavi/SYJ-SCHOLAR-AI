"""
scholar/quiz/runner.py
QuizRunner — parses AI quiz output, provides interactive self-test mode,
and scoring utilities. Works entirely in the terminal via Rich.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.rule import Rule

from scholar.utils.logger import get_logger

logger   = get_logger(__name__)
console  = Console()


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class MCQ:
    id:          int
    question:    str
    options:     dict[str, str]   # {"A": "...", "B": "..."}
    correct:     str
    explanation: str = ""


@dataclass
class TrueFalse:
    id:        int
    statement: str
    answer:    bool
    explanation: str = ""


@dataclass
class ShortQuestion:
    id:           int
    question:     str
    model_answer: str


@dataclass
class LongQuestion:
    id:         int
    question:   str
    key_points: list[str] = field(default_factory=list)


@dataclass
class QuizResult:
    total:   int
    correct: int
    wrong:   int
    skipped: int
    score_pct: float

    def grade(self) -> str:
        p = self.score_pct
        if p >= 90: return "A+ 🏆"
        if p >= 80: return "A  🥇"
        if p >= 70: return "B  🥈"
        if p >= 60: return "C  🥉"
        if p >= 50: return "D  📚"
        return "F  💪 (Keep studying!)"


# ── Runner ────────────────────────────────────────────────────────────────────

class QuizRunner:
    """
    Wraps a raw AI quiz dict and provides:
      • .run_interactive()  — self-test in the terminal
      • .to_markdown()      — printable quiz sheet
      • .to_json()          — machine-readable
      • .to_txt()           — plain text version
    """

    def __init__(self, raw: dict[str, Any]):
        self.topic         = raw.get("topic", "Quiz")
        self.mcqs          = self._parse_mcqs(raw.get("mcqs", []))
        self.true_false    = self._parse_tf(raw.get("true_false", []))
        self.short_qs      = self._parse_short(raw.get("short_questions", []))
        self.long_qs       = self._parse_long(raw.get("long_questions", []))

    # ── Parsers ───────────────────────────────────────────────────────────────

    def _parse_mcqs(self, raw: list) -> list[MCQ]:
        out = []
        for i, q in enumerate(raw, 1):
            try:
                out.append(MCQ(
                    id          = int(q.get("id", i)),
                    question    = str(q.get("question", "")),
                    options     = dict(q.get("options", {})),
                    correct     = str(q.get("correct", "A")).upper(),
                    explanation = str(q.get("explanation", "")),
                ))
            except Exception as e:
                logger.warning(f"Bad MCQ #{i}: {e}")
        return out

    def _parse_tf(self, raw: list) -> list[TrueFalse]:
        out = []
        for i, q in enumerate(raw, 1):
            try:
                out.append(TrueFalse(
                    id          = int(q.get("id", i)),
                    statement   = str(q.get("statement", "")),
                    answer      = bool(q.get("answer", True)),
                    explanation = str(q.get("explanation", "")),
                ))
            except Exception as e:
                logger.warning(f"Bad T/F #{i}: {e}")
        return out

    def _parse_short(self, raw: list) -> list[ShortQuestion]:
        out = []
        for i, q in enumerate(raw, 1):
            try:
                out.append(ShortQuestion(
                    id           = int(q.get("id", i)),
                    question     = str(q.get("question", "")),
                    model_answer = str(q.get("model_answer", "")),
                ))
            except Exception as e:
                logger.warning(f"Bad short Q #{i}: {e}")
        return out

    def _parse_long(self, raw: list) -> list[LongQuestion]:
        out = []
        for i, q in enumerate(raw, 1):
            try:
                out.append(LongQuestion(
                    id         = int(q.get("id", i)),
                    question   = str(q.get("question", "")),
                    key_points = list(q.get("key_points", [])),
                ))
            except Exception as e:
                logger.warning(f"Bad long Q #{i}: {e}")
        return out

    # ── Interactive self-test ─────────────────────────────────────────────────

    def run_interactive(self) -> QuizResult:
        """
        Run an interactive MCQ + True/False quiz in the terminal.
        Returns a QuizResult with score.
        """
        console.print(Panel(
            f"[bold cyan]Interactive Quiz: {self.topic}[/bold cyan]\n"
            f"[dim]{len(self.mcqs)} MCQs + {len(self.true_false)} True/False[/dim]",
            border_style="cyan",
        ))

        total   = 0
        correct = 0
        wrong   = 0
        skipped = 0

        # ── MCQs ──────────────────────────────────────────────────────────────
        if self.mcqs:
            console.print(Rule("[cyan]Multiple Choice[/cyan]"))
            questions = self.mcqs[:]
            random.shuffle(questions)
            for q in questions:
                console.print(f"\n[bold white]Q{q.id}. {q.question}[/bold white]")
                for opt, text in q.options.items():
                    console.print(f"   [cyan]{opt})[/cyan] {text}")
                answer = Prompt.ask(
                    "   Your answer (A/B/C/D or S to skip)",
                    default="S",
                    console=console,
                ).strip().upper()
                total += 1
                if answer == "S":
                    skipped += 1
                    console.print(f"   [dim]Skipped. Correct: [green]{q.correct}[/green][/dim]")
                elif answer == q.correct:
                    correct += 1
                    console.print(f"   [green]✓ Correct![/green]")
                else:
                    wrong += 1
                    console.print(
                        f"   [red]✗ Wrong.[/red] Correct: [green]{q.correct}[/green]"
                        + (f"\n   [dim]{q.explanation}[/dim]" if q.explanation else "")
                    )

        # ── True/False ────────────────────────────────────────────────────────
        if self.true_false:
            console.print(Rule("[cyan]True / False[/cyan]"))
            for q in self.true_false:
                console.print(f"\n[bold white]{q.id}. {q.statement}[/bold white]")
                raw_ans = Prompt.ask(
                    "   True or False? (T/F or S to skip)",
                    default="S",
                    console=console,
                ).strip().upper()
                total += 1
                if raw_ans == "S":
                    skipped += 1
                    answer_str = "TRUE" if q.answer else "FALSE"
                    console.print(f"   [dim]Skipped. Correct: [green]{answer_str}[/green][/dim]")
                else:
                    user_bool = raw_ans == "T"
                    if user_bool == q.answer:
                        correct += 1
                        console.print("[green]   ✓ Correct![/green]")
                    else:
                        wrong += 1
                        answer_str = "TRUE" if q.answer else "FALSE"
                        console.print(
                            f"   [red]✗ Wrong.[/red] Answer: [green]{answer_str}[/green]"
                            + (f"\n   [dim]{q.explanation}[/dim]" if q.explanation else "")
                        )

        # ── Score ─────────────────────────────────────────────────────────────
        score_pct = round((correct / total * 100) if total else 0, 1)
        result    = QuizResult(
            total=total, correct=correct, wrong=wrong,
            skipped=skipped, score_pct=score_pct,
        )

        tbl = Table(title="Quiz Results", show_header=True, header_style="bold cyan")
        tbl.add_column("Metric",  style="cyan")
        tbl.add_column("Value",   style="bold white")
        tbl.add_row("Total",     str(total))
        tbl.add_row("Correct",   f"[green]{correct}[/green]")
        tbl.add_row("Wrong",     f"[red]{wrong}[/red]")
        tbl.add_row("Skipped",   str(skipped))
        tbl.add_row("Score",     f"[yellow]{score_pct}%[/yellow]")
        tbl.add_row("Grade",     f"[bold]{result.grade()}[/bold]")
        console.print(tbl)

        return result

    # ── Export ────────────────────────────────────────────────────────────────

    def to_markdown(self) -> str:
        lines = [f"# Quiz: {self.topic}", ""]

        if self.mcqs:
            lines += ["## Multiple Choice Questions", ""]
            for q in self.mcqs:
                lines.append(f"**Q{q.id}.** {q.question}")
                for opt, text in q.options.items():
                    marker = "✓" if opt == q.correct else " "
                    lines.append(f"- [{marker}] **{opt})** {text}")
                if q.explanation:
                    lines.append(f"  > 💡 {q.explanation}")
                lines.append("")

        if self.true_false:
            lines += ["## True / False", ""]
            for q in self.true_false:
                ans = "**TRUE**" if q.answer else "**FALSE**"
                lines.append(f"**{q.id}.** {q.statement}")
                lines.append(f"→ Answer: {ans}")
                if q.explanation:
                    lines.append(f"> 💡 {q.explanation}")
                lines.append("")

        if self.short_qs:
            lines += ["## Short Answer Questions", ""]
            for q in self.short_qs:
                lines.append(f"**Q{q.id}.** {q.question}")
                lines.append(f"**Model Answer:** {q.model_answer}")
                lines.append("")

        if self.long_qs:
            lines += ["## Long / Essay Questions", ""]
            for q in self.long_qs:
                lines.append(f"**Q{q.id}.** {q.question}")
                lines.append("**Key points to cover:**")
                for kp in q.key_points:
                    lines.append(f"- {kp}")
                lines.append("")

        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "topic":            self.topic,
                "mcqs":             [{"id": q.id, "question": q.question,
                                      "options": q.options, "correct": q.correct,
                                      "explanation": q.explanation} for q in self.mcqs],
                "true_false":       [{"id": q.id, "statement": q.statement,
                                      "answer": q.answer, "explanation": q.explanation}
                                     for q in self.true_false],
                "short_questions":  [{"id": q.id, "question": q.question,
                                      "model_answer": q.model_answer} for q in self.short_qs],
                "long_questions":   [{"id": q.id, "question": q.question,
                                      "key_points": q.key_points} for q in self.long_qs],
            },
            indent=2,
            ensure_ascii=False,
        )

    def to_txt(self) -> str:
        lines = [f"QUIZ: {self.topic}", "=" * 60, ""]
        if self.mcqs:
            lines += ["MULTIPLE CHOICE", "-" * 40, ""]
            for q in self.mcqs:
                lines.append(f"Q{q.id}. {q.question}")
                for opt, text in q.options.items():
                    lines.append(f"   {opt}) {text}")
                lines.append(f"   [Answer: {q.correct}]")
                lines.append("")
        if self.true_false:
            lines += ["TRUE / FALSE", "-" * 40, ""]
            for q in self.true_false:
                ans = "TRUE" if q.answer else "FALSE"
                lines.append(f"{q.id}. {q.statement}")
                lines.append(f"   [Answer: {ans}]")
                lines.append("")
        if self.short_qs:
            lines += ["SHORT ANSWER", "-" * 40, ""]
            for q in self.short_qs:
                lines.append(f"Q{q.id}. {q.question}")
                lines.append(f"   Model Answer: {q.model_answer}")
                lines.append("")
        if self.long_qs:
            lines += ["LONG QUESTIONS", "-" * 40, ""]
            for q in self.long_qs:
                lines.append(f"Q{q.id}. {q.question}")
                for kp in q.key_points:
                    lines.append(f"   • {kp}")
                lines.append("")
        return "\n".join(lines)

    def save(self, path: Path, fmt: str = "markdown") -> Path:
        writers = {
            "markdown": (self.to_markdown, ".md"),
            "json":     (self.to_json,     ".json"),
            "txt":      (self.to_txt,      ".txt"),
        }
        fn, default_ext = writers.get(fmt, writers["markdown"])
        if not path.suffix:
            path = path.with_suffix(default_ext)
        path.write_text(fn(), encoding="utf-8")
        logger.info(f"Quiz saved → {path}")
        return path

    def stats(self) -> dict[str, int]:
        return {
            "mcqs":           len(self.mcqs),
            "true_false":     len(self.true_false),
            "short_questions": len(self.short_qs),
            "long_questions":  len(self.long_qs),
            "total":          len(self.mcqs) + len(self.true_false) +
                              len(self.short_qs) + len(self.long_qs),
        }
