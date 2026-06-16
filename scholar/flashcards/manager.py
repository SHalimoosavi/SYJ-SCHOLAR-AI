"""
scholar/flashcards/manager.py
FlashcardManager — post-processes raw AI card output and provides
rich export options: Markdown, JSON, Anki CSV, and plain TXT.
"""

from __future__ import annotations

import json
import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scholar.utils.logger import get_logger

logger = get_logger(__name__)


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Flashcard:
    id:         int
    question:   str
    answer:     str
    difficulty: str = "medium"   # easy | medium | hard
    tags:       list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id":         self.id,
            "question":   self.question,
            "answer":     self.answer,
            "difficulty": self.difficulty,
            "tags":       self.tags,
        }


# ── Manager ───────────────────────────────────────────────────────────────────

class FlashcardManager:
    """
    Wraps raw AI-generated flashcard result dicts and provides
    clean export methods.
    """

    def __init__(self, raw: dict[str, Any]):
        self.topic = raw.get("topic", "Untitled")
        self.cards = self._parse_cards(raw.get("cards", []))

    def _parse_cards(self, raw_cards: list[dict]) -> list[Flashcard]:
        cards = []
        for i, c in enumerate(raw_cards, start=1):
            try:
                card = Flashcard(
                    id         = int(c.get("id", i)),
                    question   = str(c.get("question", "")),
                    answer     = str(c.get("answer", "")),
                    difficulty = str(c.get("difficulty", "medium")).lower(),
                    tags       = list(c.get("tags", [])),
                )
                if card.question and card.answer:
                    cards.append(card)
            except Exception as exc:
                logger.warning(f"Skipping malformed card #{i}: {exc}")
        return cards

    def __len__(self) -> int:
        return len(self.cards)

    # ── Export methods ────────────────────────────────────────────────────────

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(
            {
                "topic": self.topic,
                "count": len(self.cards),
                "cards": [c.to_dict() for c in self.cards],
            },
            indent=indent,
            ensure_ascii=False,
        )

    def to_markdown(self) -> str:
        lines = [
            f"# Flashcards: {self.topic}",
            f"\n> {len(self.cards)} cards\n",
        ]
        diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        for card in self.cards:
            emoji = diff_emoji.get(card.difficulty, "⚪")
            tags  = " ".join(f"`{t}`" for t in card.tags)
            lines += [
                f"---",
                f"### Card {card.id}  {emoji}",
                f"",
                f"**Q:** {card.question}",
                f"",
                f"**A:** {card.answer}",
                f"",
                f"{tags}",
                f"",
            ]
        return "\n".join(lines)

    def to_anki_csv(self) -> str:
        """Anki-importable tab-separated CSV: Front TAB Back [TAB Tags]"""
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["#separator:tab"])
        writer.writerow(["#html:false"])
        for card in self.cards:
            tags = " ".join(card.tags)
            writer.writerow([card.question, card.answer, tags])
        return buf.getvalue()

    def to_txt(self) -> str:
        lines = [f"FLASHCARDS: {self.topic}", f"{'='*50}", ""]
        for card in self.cards:
            lines += [
                f"[{card.id}] Q: {card.question}",
                f"     A: {card.answer}",
                f"     Difficulty: {card.difficulty.upper()}",
                "",
            ]
        return "\n".join(lines)

    def save(self, path: Path, fmt: str = "markdown") -> Path:
        """Write cards to *path* in *fmt* format. Returns path."""
        writers = {
            "markdown": (self.to_markdown, ".md"),
            "json":     (self.to_json,     ".json"),
            "anki":     (self.to_anki_csv, ".csv"),
            "txt":      (self.to_txt,      ".txt"),
        }
        if fmt not in writers:
            fmt = "markdown"
        fn, default_ext = writers[fmt]
        if not path.suffix:
            path = path.with_suffix(default_ext)
        path.write_text(fn(), encoding="utf-8")
        logger.info(f"Flashcards saved → {path}")
        return path

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict[str, int]:
        counts = {"easy": 0, "medium": 0, "hard": 0, "total": len(self.cards)}
        for c in self.cards:
            key = c.difficulty if c.difficulty in counts else "medium"
            counts[key] += 1
        return counts
