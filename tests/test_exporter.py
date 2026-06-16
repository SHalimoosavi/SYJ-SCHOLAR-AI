"""
tests/test_exporter.py
Tests for scholar.exports.exporter
"""

import json
import pytest
from pathlib import Path
from scholar.exports.exporter import (
    export_result, _to_json, _to_txt, _to_markdown, _to_html,
    _flatten_to_lines,
)

SAMPLE_SUMMARY = {
    "title": "Test Document",
    "chapter_summary": "This is a test summary.",
    "key_concepts": ["Concept A", "Concept B"],
    "important_definitions": {"Term": "Definition text"},
    "quick_revision_notes": ["Note 1", "Note 2"],
    "_meta": {"action": "summarize", "model": "gemma:2b", "duration_s": 1.2, "from_cache": False},
}


def test_to_json_clean():
    out = _to_json(SAMPLE_SUMMARY)
    data = json.loads(out)
    # _meta should be stripped from JSON export
    assert "_meta" not in data
    assert data["title"] == "Test Document"


def test_to_txt_contains_title():
    out = _to_txt(SAMPLE_SUMMARY, "summarize")
    assert "SUMMARIZE" in out.upper()
    assert "Test Document" in out


def test_to_markdown_has_header():
    out = _to_markdown(SAMPLE_SUMMARY, "summarize", "lecture")
    assert out.startswith("# SYJ Scholar AI")
    assert "lecture" in out
    assert "Test Document" in out


def test_to_html_is_valid_html():
    out = _to_html(SAMPLE_SUMMARY, "summarize", "lecture")
    assert "<!DOCTYPE html>" in out
    assert "<title>" in out
    assert "</html>" in out


def test_export_result_creates_file(tmp_path):
    result = export_result(
        SAMPLE_SUMMARY,
        action="summarize",
        stem="test-doc",
        fmt="markdown",
        out_dir=tmp_path / "summarize",
    )
    assert result is not None
    assert result.exists()
    content = result.read_text()
    assert "SYJ Scholar AI" in content


def test_export_result_json(tmp_path):
    result = export_result(
        SAMPLE_SUMMARY,
        action="summarize",
        stem="test-doc",
        fmt="json",
        out_dir=tmp_path / "summarize",
    )
    assert result is not None
    assert result.suffix == ".json"
    data = json.loads(result.read_text())
    assert "title" in data


def test_export_result_html(tmp_path):
    result = export_result(
        SAMPLE_SUMMARY,
        action="summarize",
        stem="test-doc",
        fmt="html",
        out_dir=tmp_path / "summarize",
    )
    assert result is not None
    assert result.suffix == ".html"
    assert "<!DOCTYPE html>" in result.read_text()


def test_export_result_txt(tmp_path):
    result = export_result(
        SAMPLE_SUMMARY,
        action="summarize",
        stem="test-doc",
        fmt="txt",
        out_dir=tmp_path / "summarize",
    )
    assert result is not None
    assert result.suffix == ".txt"


def test_flatten_to_lines_dict():
    lines = []
    _flatten_to_lines({"key": "value", "nested": {"a": "b"}}, lines)
    joined = "\n".join(lines)
    assert "Key:" in joined
    assert "value" in joined


def test_flatten_to_lines_list():
    lines = []
    _flatten_to_lines(["item1", "item2", "item3"], lines)
    assert any("item1" in l for l in lines)
    assert any("item2" in l for l in lines)
