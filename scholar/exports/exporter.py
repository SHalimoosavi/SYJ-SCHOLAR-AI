"""
scholar/exports/exporter.py

Export results to Markdown, TXT, JSON and HTML.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from scholar.utils.logger import get_logger
from scholar.utils.paths import get_output_dir
from scholar.utils.helpers import safe_filename, timestamped_name

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Main Export Function
# ---------------------------------------------------------------------

def export_result(
    result: dict[str, Any],
    action: str,
    stem: str,
    fmt: str = "markdown",
    out_dir: Path | None = None,
) -> Path | None:

    out_dir = out_dir or (get_output_dir() / action)
    out_dir.mkdir(parents=True, exist_ok=True)

    ext_map = {
        "markdown": ".md",
        "txt": ".txt",
        "json": ".json",
        "html": ".html",
    }

    ext = ext_map.get(fmt, ".md")

    filename = timestamped_name(
        f"{safe_filename(stem)}-{action}",
        ext,
    )

    out_path = out_dir / filename

    try:

        if fmt == "json":
            content = _to_json(result)

        elif fmt == "html":
            try:
                from scholar.exports.html_renderer import render_html

                content = render_html(
                    result,
                    action,
                    stem,
                )
            except Exception:
                content = _to_html(
                    result,
                    action,
                    stem,
                )

        elif fmt == "txt":
            content = _to_txt(
                result,
                action,
            )

        else:
            content = _to_markdown(
                result,
                action,
                stem,
            )

        out_path.write_text(
            content,
            encoding="utf-8",
        )

        logger.info(f"Exported {action} -> {out_path}")

        return out_path

    except Exception as exc:
        logger.error(f"Export failed: {exc}")
        return None


# ---------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------

def _to_json(result: dict) -> str:
    clean = {
        k: v
        for k, v in result.items()
        if not k.startswith("_")
    }

    return json.dumps(
        clean,
        indent=2,
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------

def _to_txt(
    result: dict,
    action: str,
) -> str:

    lines = [
        f"SYJ SCHOLAR AI - {action.upper()}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
    ]

    _flatten_to_lines(
        result,
        lines,
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------
# MARKDOWN
# ---------------------------------------------------------------------

def _to_markdown(
    result: dict,
    action: str,
    stem: str,
) -> str:

    lines = [
        f"# SYJ Scholar AI — {action.title()}",
        f"> **Source:** {stem}  |  **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    if action == "summarize":

        if title := result.get("title"):
            lines += [
                "## Title",
                "",
                title,
                "",
            ]

        if summary := result.get("summary"):
            lines += [
                "## Summary",
                "",
                summary,
                "",
            ]

        if points := result.get("key_points"):
            lines += [
                "## Key Points",
                "",
            ]

            for item in points:
                lines.append(f"- {item}")

            lines.append("")

    elif action == "notes":

        if title := result.get("title"):
            lines += [
                "## Title",
                "",
                title,
                "",
            ]

        if overview := result.get("overview"):
            lines += [
                "## Overview",
                "",
                overview,
                "",
            ]

        if notes := result.get("notes"):
            lines += [
                "## Study Notes",
                "",
            ]

            for item in notes:
                lines.append(f"- {item}")

            lines.append("")

    elif action == "flashcards":

        if topic := result.get("topic"):
            lines += [
                "## Topic",
                "",
                topic,
                "",
            ]

        for i, card in enumerate(
            result.get("cards", []),
            1,
        ):
            lines += [
                f"### Flashcard {i}",
                "",
                f"**Question:** {card.get('question', '')}",
                "",
                f"**Answer:** {card.get('answer', '')}",
                "",
            ]

    elif action == "quiz":

        if topic := result.get("topic"):
            lines += [
                "## Topic",
                "",
                topic,
                "",
            ]

        for i, q in enumerate(
            result.get("questions", []),
            1,
        ):
            lines += [
                f"### Question {i}",
                "",
                q.get("question", ""),
                "",
                f"**Answer:** {q.get('answer', '')}",
                "",
            ]

    elif action == "exam":

        if topic := result.get("topic"):
            lines += [
                "## Topic",
                "",
                topic,
                "",
            ]

        if topics := result.get("important_topics"):
            lines += [
                "## Important Topics",
                "",
            ]

            for item in topics:
                lines.append(f"- {item}")

            lines.append("")

        if questions := result.get("possible_questions"):
            lines += [
                "## Possible Questions",
                "",
            ]

            for item in questions:
                lines.append(f"- {item}")

            lines.append("")

    elif action == "study":

        if summary := result.get("summary"):
            lines += [
                "## Summary",
                "",
                summary.get("summary", ""),
                "",
            ]

        if notes := result.get("notes"):
            lines += [
                "## Notes",
                "",
            ]

            for item in notes:
                lines.append(f"- {item}")

            lines.append("")

    else:
        lines.append(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

    lines += [
        "",
        "---",
        "*Generated by SYJ Scholar AI — Your Offline AI Study Companion*",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------

def _to_html(
    result: dict,
    action: str,
    stem: str,
) -> str:

    md = _to_markdown(
        result,
        action,
        stem,
    )

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SYJ Scholar AI</title>
</head>
<body>
<pre>{md}</pre>
</body>
</html>
"""


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _flatten_to_lines(
    obj: Any,
    lines: list[str],
    indent: int = 0,
) -> None:

    pad = "  " * indent

    if isinstance(obj, dict):

        for k, v in obj.items():

            if k.startswith("_"):
                continue

            lines.append(
                f"{pad}{k.replace('_', ' ').title()}:"
            )

            _flatten_to_lines(
                v,
                lines,
                indent + 1,
            )

    elif isinstance(obj, list):

        for item in obj:

            if isinstance(
                item,
                (dict, list),
            ):
                _flatten_to_lines(
                    item,
                    lines,
                    indent + 1,
                )
            else:
                lines.append(
                    f"{pad}- {item}"
                )

    else:
        lines.append(
            f"{pad}{obj}"
        )
