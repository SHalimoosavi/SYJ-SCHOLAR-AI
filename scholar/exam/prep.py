"""
scholar/exam/prep.py
ExamPrepEngine — parses AI exam preparation output, ranks topics by
priority, generates printable revision checklists, and suggests a
study schedule.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from scholar.utils.logger import get_logger

logger = get_logger(__name__)


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class ExamTopic:
    topic:    str
    priority: str   # high | medium | low
    reason:   str = ""

    @property
    def priority_rank(self) -> int:
        return {"high": 0, "medium": 1, "low": 2}.get(self.priority, 1)


@dataclass
class LikelyQuestion:
    question: str
    qtype:    str   # long | short | mcq
    hint:     str = ""


@dataclass
class ChecklistItem:
    item: str
    done: bool = False


@dataclass
class ExamPrep:
    topic:                str
    important_topics:     list[ExamTopic]      = field(default_factory=list)
    most_likely_questions: list[LikelyQuestion] = field(default_factory=list)
    revision_checklist:   list[ChecklistItem]  = field(default_factory=list)
    high_priority_concepts: list[str]          = field(default_factory=list)
    study_tips:           list[str]            = field(default_factory=list)


# ── Engine ────────────────────────────────────────────────────────────────────

class ExamPrepEngine:
    """
    Wraps raw AI exam prep output and provides export + scheduling.
    """

    def __init__(self, raw: dict[str, Any]):
        self.prep = self._parse(raw)

    def _parse(self, raw: dict) -> ExamPrep:
        topics = []
        for t in raw.get("important_topics", []):
            topics.append(ExamTopic(
                topic    = str(t.get("topic", "")),
                priority = str(t.get("priority", "medium")).lower(),
                reason   = str(t.get("reason", "")),
            ))
        # Sort by priority rank (high → medium → low)
        topics.sort(key=lambda t: t.priority_rank)

        questions = []
        for q in raw.get("most_likely_questions", []):
            questions.append(LikelyQuestion(
                question = str(q.get("question", "")),
                qtype    = str(q.get("type", "long")),
                hint     = str(q.get("hint", "")),
            ))

        checklist = []
        for item in raw.get("revision_checklist", []):
            if isinstance(item, dict):
                checklist.append(ChecklistItem(
                    item = str(item.get("item", "")),
                    done = bool(item.get("done", False)),
                ))
            else:
                checklist.append(ChecklistItem(item=str(item)))

        return ExamPrep(
            topic                 = str(raw.get("topic", "Exam Preparation")),
            important_topics      = topics,
            most_likely_questions = questions,
            revision_checklist    = checklist,
            high_priority_concepts= list(raw.get("high_priority_concepts", [])),
            study_tips            = list(raw.get("study_tips", [])),
        )

    # ── Study schedule ────────────────────────────────────────────────────────

    def generate_schedule(self, days_until_exam: int = 7) -> list[dict[str, Any]]:
        """
        Return a simple day-by-day study schedule based on topic priorities.
        """
        if days_until_exam <= 1:
            today = date.today()
            return [{
                "date":  today.isoformat(),
                "day":   1,
                "focus": "REVISION DAY",
                "topic": "Full review + practice questions",
            }]

        high   = [t for t in self.prep.important_topics if t.priority == "high"]
        medium = [t for t in self.prep.important_topics if t.priority == "medium"]
        low    = [t for t in self.prep.important_topics if t.priority == "low"]

        schedule: list[dict[str, Any]] = []
        today = date.today()

        # Reserve 1 day for revision; distribute the rest 50/30/20
        study_days  = days_until_exam - 1
        high_days   = max(1, int(study_days * 0.5))
        medium_days = max(0, int(study_days * 0.3))
        low_days    = max(0, study_days - high_days - medium_days)

        day_offset = 0
        for i in range(high_days):
            topic = high[i % len(high)].topic if high else "High-priority review"
            schedule.append({
                "date":  (today + timedelta(days=day_offset)).isoformat(),
                "day":   day_offset + 1,
                "focus": "HIGH PRIORITY",
                "topic": topic,
            })
            day_offset += 1

        for i in range(medium_days):
            topic = medium[i % len(medium)].topic if medium else "Medium-priority review"
            schedule.append({
                "date":  (today + timedelta(days=day_offset)).isoformat(),
                "day":   day_offset + 1,
                "focus": "MEDIUM PRIORITY",
                "topic": topic,
            })
            day_offset += 1

        for i in range(low_days):
            topic = low[i % len(low)].topic if low else "Supplementary topics"
            schedule.append({
                "date":  (today + timedelta(days=day_offset)).isoformat(),
                "day":   day_offset + 1,
                "focus": "LOW PRIORITY",
                "topic": topic,
            })
            day_offset += 1

        schedule.append({
            "date":  (today + timedelta(days=day_offset)).isoformat(),
            "day":   day_offset + 1,
            "focus": "REVISION DAY",
            "topic": "Full review + practice questions",
        })
        return schedule

    # ── Export ────────────────────────────────────────────────────────────────

    def to_markdown(self) -> str:
        p = self.prep
        lines = [f"# Exam Preparation: {p.topic}", ""]

        if p.important_topics:
            lines += ["## 📌 Important Topics (by Priority)", ""]
            pri_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            for t in p.important_topics:
                emoji = pri_emoji.get(t.priority, "⚪")
                lines.append(f"### {emoji} {t.topic} `[{t.priority.upper()}]`")
                if t.reason:
                    lines.append(f"> {t.reason}")
                lines.append("")

        if p.most_likely_questions:
            lines += ["## 🎯 Most Likely Exam Questions", ""]
            for i, q in enumerate(p.most_likely_questions, 1):
                lines.append(f"**{i}. [{q.qtype.upper()}]** {q.question}")
                if q.hint:
                    lines.append(f"> 💡 Hint: {q.hint}")
                lines.append("")

        if p.revision_checklist:
            lines += ["## ✅ Revision Checklist", ""]
            for item in p.revision_checklist:
                tick = "- [x]" if item.done else "- [ ]"
                lines.append(f"{tick} {item.item}")
            lines.append("")

        if p.high_priority_concepts:
            lines += ["## 🔥 High Priority Concepts", ""]
            for concept in p.high_priority_concepts:
                lines.append(f"- ⭐ {concept}")
            lines.append("")

        if p.study_tips:
            lines += ["## 💡 Study Tips", ""]
            for tip in p.study_tips:
                lines.append(f"- {tip}")
            lines.append("")

        return "\n".join(lines)

    def to_json(self) -> str:
        p = self.prep
        return json.dumps(
            {
                "topic":                  p.topic,
                "important_topics":       [{"topic": t.topic, "priority": t.priority,
                                            "reason": t.reason} for t in p.important_topics],
                "most_likely_questions":  [{"question": q.question, "type": q.qtype,
                                            "hint": q.hint} for q in p.most_likely_questions],
                "revision_checklist":     [{"item": c.item, "done": c.done}
                                           for c in p.revision_checklist],
                "high_priority_concepts": p.high_priority_concepts,
                "study_tips":             p.study_tips,
            },
            indent=2,
            ensure_ascii=False,
        )

    def to_txt(self) -> str:
        p = self.prep
        lines = [f"EXAM PREPARATION: {p.topic}", "=" * 60, ""]
        if p.important_topics:
            lines += ["IMPORTANT TOPICS", "-" * 40, ""]
            for t in p.important_topics:
                lines.append(f"[{t.priority.upper()}] {t.topic}")
                if t.reason:
                    lines.append(f"  → {t.reason}")
                lines.append("")
        if p.most_likely_questions:
            lines += ["MOST LIKELY QUESTIONS", "-" * 40, ""]
            for i, q in enumerate(p.most_likely_questions, 1):
                lines.append(f"{i}. [{q.qtype.upper()}] {q.question}")
                if q.hint:
                    lines.append(f"   Hint: {q.hint}")
                lines.append("")
        if p.revision_checklist:
            lines += ["REVISION CHECKLIST", "-" * 40, ""]
            for c in p.revision_checklist:
                tick = "[✓]" if c.done else "[ ]"
                lines.append(f"  {tick} {c.item}")
            lines.append("")
        if p.high_priority_concepts:
            lines += ["HIGH PRIORITY CONCEPTS", "-" * 40, ""]
            for c in p.high_priority_concepts:
                lines.append(f"  ★ {c}")
            lines.append("")
        if p.study_tips:
            lines += ["STUDY TIPS", "-" * 40, ""]
            for tip in p.study_tips:
                lines.append(f"  • {tip}")
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
        logger.info(f"Exam prep saved → {path}")
        return path
