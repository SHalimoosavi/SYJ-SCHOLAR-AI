"""
scholar/exports/html_renderer.py

Simple HTML renderer for SYJ Scholar AI.
Compatible with the current simplified JSON schema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def render_html(
    result: dict[str, Any],
    action: str,
    stem: str,
) -> str:
    body = _build_html_body(result, action)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SYJ Scholar AI - {action}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    line-height: 1.6;
}}

.card {{
    border: 1px solid #cccccc;
    padding: 12px;
    margin: 12px 0;
    border-radius: 8px;
}}

.answer {{
    background: #f5f5f5;
    padding: 10px;
    margin-top: 10px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

td, th {{
    border: 1px solid #cccccc;
    padding: 8px;
}}

ul {{
    margin-left: 20px;
}}
</style>
</head>
<body>

<h1>SYJ Scholar AI</h1>

<p>
<strong>Action:</strong> {action}<br>
<strong>Source:</strong> {stem}<br>
<strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}
</p>

<hr>

{body}

</body>
</html>
"""


def _build_html_body(result: dict, action: str) -> str:
    builders = {
        "summarize": _body_summarize,
        "notes": _body_notes,
        "flashcards": _body_flashcards,
        "quiz": _body_quiz,
        "exam": _body_exam,
        "study": _body_study,
    }

    fn = builders.get(action, _body_generic)
    return fn(result)


def _esc(text: Any) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _h(level: int, text: str) -> str:
    return f"<h{level}>{_esc(text)}</h{level}>"


def _p(text: str) -> str:
    return f"<p>{_esc(text)}</p>"


def _ul(items: list) -> str:
    html = "<ul>"

    for item in items:
        html += f"<li>{_esc(item)}</li>"

    html += "</ul>"
    return html


def _body_summarize(r: dict) -> str:
    html = ""

    if title := r.get("title"):
        html += _h(2, title)

    if summary := r.get("summary"):
        html += _h(3, "Summary")
        html += _p(summary)

    if points := r.get("key_points"):
        html += _h(3, "Key Points")
        html += _ul(points)

    return html


def _body_notes(r: dict) -> str:
    html = ""

    if title := r.get("title"):
        html += _h(2, title)

    if overview := r.get("overview"):
        html += _p(overview)

    if notes := r.get("notes"):
        html += _h(3, "Study Notes")
        html += _ul(notes)

    return html


def _body_flashcards(r: dict) -> str:
    html = ""

    if topic := r.get("topic"):
        html += _h(2, f"Flashcards: {topic}")

    for card in r.get("cards", []):
        html += f"""
<div class="card">
<p><strong>Question</strong></p>
<p>{_esc(card.get("question", ""))}</p>

<div class="answer">
<strong>Answer:</strong><br>
{_esc(card.get("answer", ""))}
</div>
</div>
"""

    return html


def _body_quiz(r: dict) -> str:
    html = ""

    if topic := r.get("topic"):
        html += _h(2, f"Quiz: {topic}")

    for i, q in enumerate(r.get("questions", []), 1):
        html += f"""
<div class="card">
<p><strong>Question {i}</strong></p>
<p>{_esc(q.get("question", ""))}</p>

<div class="answer">
<strong>Answer:</strong><br>
{_esc(q.get("answer", ""))}
</div>
</div>
"""

    return html


def _body_exam(r: dict) -> str:
    html = ""

    if topic := r.get("topic"):
        html += _h(2, f"Exam Preparation: {topic}")

    if topics := r.get("important_topics"):
        html += _h(3, "Important Topics")
        html += _ul(topics)

    if questions := r.get("possible_questions"):
        html += _h(3, "Possible Questions")
        html += _ul(questions)

    return html


def _body_study(r: dict) -> str:
    html = "<h2>Full Study Package</h2>"

    if summary := r.get("summary"):
        html += _body_summarize(summary)

    if notes := r.get("notes"):
        if isinstance(notes, list):
            html += _h(3, "Study Notes")
            html += _ul(notes)
        else:
            html += _body_notes(notes)

    if flashcards := r.get("flashcards"):
        if isinstance(flashcards, dict):
            html += _body_flashcards(flashcards)

    if quiz := r.get("quiz"):
        if isinstance(quiz, dict):
            html += _body_quiz(quiz)

    if exam := r.get("exam"):
        if isinstance(exam, dict):
            html += _body_exam(exam)

    return html


def _body_generic(r: dict) -> str:
    import json

    clean = {
        k: v
        for k, v in r.items()
        if not k.startswith("_")
    }

    return (
        "<pre>"
        + _esc(json.dumps(clean, indent=2, ensure_ascii=False))
        + "</pre>"
    )
