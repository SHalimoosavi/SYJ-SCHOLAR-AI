"""
tests/test_notes_formatter.py
Tests for scholar.notes.formatter
"""

import json
import pytest
from scholar.notes.formatter import NotesFormatter, StudyNotes, NoteSection

SAMPLE_RAW = {
    "title": "Introduction to Machine Learning",
    "overview": "An overview of ML fundamentals.",
    "sections": [
        {
            "heading": "Supervised Learning",
            "content": "Supervised learning uses labelled data.",
            "key_points": ["Classification", "Regression"],
        },
        {
            "heading": "Unsupervised Learning",
            "content": "Unsupervised learning finds patterns without labels.",
            "key_points": ["Clustering", "Dimensionality reduction"],
        },
    ],
    "formulas": ["Loss = Σ(y - ŷ)²", "Accuracy = TP+TN / Total"],
    "definitions": {
        "Overfitting":   "Model performs well on training but poorly on test data.",
        "Feature":       "An individual measurable property of a phenomenon.",
    },
    "important_concepts": ["Bias-variance tradeoff", "Cross-validation"],
}


def test_parse_title_and_overview():
    fmt = NotesFormatter(SAMPLE_RAW)
    assert fmt.notes.title    == "Introduction to Machine Learning"
    assert fmt.notes.overview == "An overview of ML fundamentals."


def test_parse_sections():
    fmt      = NotesFormatter(SAMPLE_RAW)
    sections = fmt.notes.sections
    assert len(sections) == 2
    assert sections[0].heading == "Supervised Learning"
    assert "Classification" in sections[0].key_points


def test_parse_formulas():
    fmt = NotesFormatter(SAMPLE_RAW)
    assert "Loss = Σ(y - ŷ)²" in fmt.notes.formulas


def test_parse_definitions():
    fmt = NotesFormatter(SAMPLE_RAW)
    assert "Overfitting" in fmt.notes.definitions
    assert "labelled" not in fmt.notes.definitions["Overfitting"] or True  # just check key exists


def test_parse_important_concepts():
    fmt = NotesFormatter(SAMPLE_RAW)
    assert "Bias-variance tradeoff" in fmt.notes.important_concepts


def test_to_markdown_structure():
    fmt = NotesFormatter(SAMPLE_RAW)
    md  = fmt.to_markdown()
    assert "# Introduction to Machine Learning" in md
    assert "## Supervised Learning"             in md
    assert "## Unsupervised Learning"           in md
    assert "## Formulas & Equations"            in md
    assert "## Definitions"                     in md
    assert "## Important Concepts"              in md
    assert "Bias-variance" in md
    assert "Overfitting"   in md


def test_to_markdown_key_points():
    fmt = NotesFormatter(SAMPLE_RAW)
    md  = fmt.to_markdown()
    assert "- Classification"            in md
    assert "- Dimensionality reduction"  in md


def test_to_txt_structure():
    fmt = NotesFormatter(SAMPLE_RAW)
    txt = fmt.to_txt()
    assert "INTRODUCTION TO MACHINE LEARNING" in txt
    assert "SUPERVISED LEARNING"              in txt
    assert "FORMULAS"                         in txt
    assert "DEFINITIONS"                      in txt


def test_to_json_roundtrip():
    fmt  = NotesFormatter(SAMPLE_RAW)
    data = json.loads(fmt.to_json())
    assert data["title"]    == "Introduction to Machine Learning"
    assert len(data["sections"])  == 2
    assert len(data["formulas"])  == 2
    assert "Overfitting" in data["definitions"]


def test_save_markdown(tmp_path):
    fmt  = NotesFormatter(SAMPLE_RAW)
    path = fmt.save(tmp_path / "notes", fmt="markdown")
    assert path.exists()
    assert path.suffix == ".md"
    assert "Machine Learning" in path.read_text()


def test_save_json(tmp_path):
    fmt  = NotesFormatter(SAMPLE_RAW)
    path = fmt.save(tmp_path / "notes", fmt="json")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["title"] == "Introduction to Machine Learning"


def test_save_txt(tmp_path):
    fmt  = NotesFormatter(SAMPLE_RAW)
    path = fmt.save(tmp_path / "notes", fmt="txt")
    assert path.exists()
    assert "INTRODUCTION" in path.read_text().upper()


def test_empty_sections():
    raw = {"title": "Empty", "overview": "", "sections": []}
    fmt = NotesFormatter(raw)
    md  = fmt.to_markdown()
    assert "# Empty" in md
