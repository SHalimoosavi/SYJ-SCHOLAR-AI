"""
scholar/notes/formatter.py
NotesFormatter — post-processes raw AI notes output into clean,
structured documents with multiple export formats.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scholar.utils.logger import get_logger

logger = get_logger(__name__)


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class NoteSection:
    heading:    str
    content:    str
    key_points: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "heading":    self.heading,
            "content":   self.content,
            "key_points": self.key_points,
        }


@dataclass
class StudyNotes:
    title:             str
    overview:          str
    sections:          list[NoteSection] = field(default_factory=list)
    formulas:          list[str]         = field(default_factory=list)
    definitions:       dict[str, str]    = field(default_factory=dict)
    important_concepts: list[str]        = field(default_factory=list)


# ── Formatter ─────────────────────────────────────────────────────────────────

class NotesFormatter:
    """
    Wraps raw AI-generated notes output and provides clean exports.
    """

    def __init__(self, raw: dict[str, Any]):
        self.notes = self._parse(raw)

    def _parse(self, raw: dict) -> StudyNotes:
        sections = []
        for s in raw.get("sections", []):
            sections.append(NoteSection(
                heading    = str(s.get("heading", "")),
                content    = str(s.get("content", "")),
                key_points = list(s.get("key_points", [])),
            ))
        return StudyNotes(
            title              = str(raw.get("title", "Study Notes")),
            overview           = str(raw.get("overview", "")),
            sections           = sections,
            formulas           = list(raw.get("formulas", [])),
            definitions        = dict(raw.get("definitions", {})),
            important_concepts = list(raw.get("important_concepts", [])),
        )

    # ── Export ────────────────────────────────────────────────────────────────

    def to_markdown(self) -> str:
        n = self.notes
        lines = [
            f"# {n.title}",
            "",
            f"> {n.overview}" if n.overview else "",
            "",
        ]
        for section in n.sections:
            lines += [
                f"## {section.heading}",
                "",
                section.content,
                "",
            ]
            if section.key_points:
                lines.append("**Key Points:**")
                for kp in section.key_points:
                    lines.append(f"- {kp}")
                lines.append("")

        if n.formulas:
            lines += ["## Formulas & Equations", ""]
            for formula in n.formulas:
                lines.append(f"```\n{formula}\n```")
            lines.append("")

        if n.definitions:
            lines += ["## Definitions", ""]
            for term, defn in n.definitions.items():
                lines.append(f"**{term}:** {defn}")
            lines.append("")

        if n.important_concepts:
            lines += ["## Important Concepts", ""]
            for concept in n.important_concepts:
                lines.append(f"- ⭐ {concept}")
            lines.append("")

        return "\n".join(line for line in lines)

    def to_txt(self) -> str:
        n = self.notes
        lines = [n.title.upper(), "=" * 60, "", n.overview, ""]
        for section in n.sections:
            lines += [f"\n{section.heading.upper()}", "-" * 40, section.content, ""]
            for kp in section.key_points:
                lines.append(f"  • {kp}")
        if n.formulas:
            lines += ["", "FORMULAS", "-" * 40]
            for f in n.formulas:
                lines.append(f"  {f}")
        if n.definitions:
            lines += ["", "DEFINITIONS", "-" * 40]
            for term, defn in n.definitions.items():
                lines.append(f"  {term}: {defn}")
        if n.important_concepts:
            lines += ["", "IMPORTANT CONCEPTS", "-" * 40]
            for c in n.important_concepts:
                lines.append(f"  ★ {c}")
        return "\n".join(lines)

    def to_json(self) -> str:
        n = self.notes
        return json.dumps(
            {
                "title":              n.title,
                "overview":           n.overview,
                "sections":           [s.to_dict() for s in n.sections],
                "formulas":           n.formulas,
                "definitions":        n.definitions,
                "important_concepts": n.important_concepts,
            },
            indent=2,
            ensure_ascii=False,
        )

    def save(self, path: Path, fmt: str = "markdown") -> Path:
        writers = {
            "markdown": (self.to_markdown, ".md"),
            "txt":      (self.to_txt,      ".txt"),
            "json":     (self.to_json,     ".json"),
        }
        fn, default_ext = writers.get(fmt, writers["markdown"])
        if not path.suffix:
            path = path.with_suffix(default_ext)
        path.write_text(fn(), encoding="utf-8")
        logger.info(f"Notes saved → {path}")
        return path
