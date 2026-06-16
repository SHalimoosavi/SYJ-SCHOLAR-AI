"""
tests/conftest.py
Shared pytest fixtures for SYJ Scholar AI test suite.

Fixtures here are auto-available to all test modules without importing.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Path fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def tmp_output(tmp_path) -> Path:
    """Temporary output directory, cleaned up after each test."""
    out = tmp_path / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ── Database isolation ────────────────────────────────────────────────────────

@pytest.fixture(autouse=False)
def isolated_db(tmp_path, monkeypatch):
    """
    Redirect the Scholar AI SQLite DB to a temp path.
    Use this fixture explicitly in DB-dependent tests.
    """
    db_path = tmp_path / "test_scholar.db"
    import scholar.core.database as db_module
    monkeypatch.setattr(db_module, "DB_PATH", db_path)
    db_module.init_db()
    yield db_path


# ── Config isolation ──────────────────────────────────────────────────────────

@pytest.fixture(autouse=False)
def isolated_config(tmp_path, monkeypatch):
    """Redirect Scholar AI config file to a temp path."""
    cfg_path = tmp_path / "config.json"
    import scholar.core.config as cfg_module
    monkeypatch.setattr(cfg_module, "CONFIG_FILE", cfg_path)
    yield cfg_path


# ── Sample data fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def sample_summarize_result() -> dict:
    return {
        "title": "Introduction to Thermodynamics",
        "chapter_summary": (
            "Thermodynamics studies energy and its transformations. "
            "The field covers heat, work, temperature, and entropy."
        ),
        "key_concepts": ["Energy conservation", "Entropy", "Enthalpy", "Gibbs free energy"],
        "important_definitions": {
            "Entropy":  "A measure of disorder or randomness in a system.",
            "Enthalpy": "Total heat content of a system at constant pressure.",
        },
        "quick_revision_notes": [
            "First Law: Energy cannot be created or destroyed.",
            "Second Law: Entropy of an isolated system always increases.",
            "Third Law: Entropy of a perfect crystal at 0 K is zero.",
        ],
        "_meta": {
            "action":     "summarize",
            "model":      "gemma:2b",
            "duration_s": 3.5,
            "from_cache": False,
        },
    }


@pytest.fixture
def sample_flashcard_result() -> dict:
    return {
        "topic": "Physics — Newton's Laws",
        "cards": [
            {
                "id": 1,
                "question": "State Newton's First Law of Motion.",
                "answer": "An object at rest stays at rest; an object in motion stays in motion "
                          "unless acted upon by an external force.",
                "difficulty": "easy",
                "tags": ["mechanics", "newton"],
            },
            {
                "id": 2,
                "question": "What does F = ma represent?",
                "answer": "Newton's Second Law: Force equals mass times acceleration.",
                "difficulty": "easy",
                "tags": ["mechanics", "formula"],
            },
            {
                "id": 3,
                "question": "State Newton's Third Law of Motion.",
                "answer": "For every action there is an equal and opposite reaction.",
                "difficulty": "medium",
                "tags": ["mechanics", "newton"],
            },
        ],
    }


@pytest.fixture
def sample_quiz_result() -> dict:
    return {
        "topic": "Cell Biology",
        "mcqs": [
            {
                "id": 1,
                "question": "Which organelle is the powerhouse of the cell?",
                "options": {
                    "A": "Nucleus",
                    "B": "Mitochondria",
                    "C": "Ribosome",
                    "D": "Vacuole",
                },
                "correct": "B",
                "explanation": "Mitochondria produce ATP through cellular respiration.",
            }
        ],
        "true_false": [
            {
                "id": 1,
                "statement": "The cell membrane is selectively permeable.",
                "answer": True,
                "explanation": "It controls what enters and exits the cell.",
            }
        ],
        "short_questions": [
            {
                "id": 1,
                "question": "What is the function of the nucleus?",
                "model_answer": "The nucleus stores genetic information (DNA) and controls cell activities.",
            }
        ],
        "long_questions": [
            {
                "id": 1,
                "question": "Describe the process of mitosis.",
                "key_points": ["Prophase", "Metaphase", "Anaphase", "Telophase", "Cytokinesis"],
            }
        ],
    }


@pytest.fixture
def sample_exam_result() -> dict:
    return {
        "topic": "Organic Chemistry",
        "important_topics": [
            {"topic": "Functional groups",    "priority": "high",   "reason": "Always examined"},
            {"topic": "Reaction mechanisms",  "priority": "high",   "reason": "Core concept"},
            {"topic": "Stereochemistry",      "priority": "medium", "reason": "Common marks"},
            {"topic": "Spectroscopy basics",  "priority": "low",    "reason": "Supplementary"},
        ],
        "most_likely_questions": [
            {
                "question": "Explain SN1 vs SN2 reaction mechanisms.",
                "type": "long",
                "hint": "Compare rate laws, stereochemistry, substrate effects.",
            },
            {
                "question": "Identify the functional groups in ethanol.",
                "type": "short",
                "hint": "Look for -OH group.",
            },
        ],
        "revision_checklist": [
            {"item": "Memorise functional group names",        "done": False},
            {"item": "Practice drawing reaction mechanisms",   "done": False},
            {"item": "Complete past paper questions",          "done": False},
        ],
        "high_priority_concepts": [
            "Nucleophilic substitution",
            "Electrophilic addition",
            "Aromaticity",
        ],
        "study_tips": [
            "Draw mechanisms by hand to build muscle memory.",
            "Use flashcards for functional groups.",
        ],
    }


@pytest.fixture
def minimal_pdf_bytes() -> bytes:
    """Return a syntactically valid minimal PDF as bytes."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
        b"/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
        b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
        b"5 0 obj<</Length 44>>\nstream\n"
        b"BT /F1 12 Tf 72 720 Td (Scholar AI Test PDF) Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000274 00000 n \n"
        b"0000000352 00000 n \n"
        b"trailer<</Size 6/Root 1 0 R>>\n"
        b"startxref\n448\n%%EOF"
    )


@pytest.fixture
def sample_pdf_file(tmp_path, minimal_pdf_bytes) -> Path:
    """Write minimal PDF bytes to a temp file and return the path."""
    p = tmp_path / "sample.pdf"
    p.write_bytes(minimal_pdf_bytes)
    return p


# ── Ollama mock ───────────────────────────────────────────────────────────────

@pytest.fixture
def mock_ollama_available():
    """Patch OllamaProvider so is_available() returns True."""
    with patch("scholar.ai.ollama_provider.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        yield mock_get


@pytest.fixture
def mock_ollama_generate(sample_summarize_result):
    """
    Patch OllamaProvider.generate_json to return a summarize result.
    Override `return_value` in individual tests for other actions.
    """
    with patch(
        "scholar.ai.ollama_provider.OllamaProvider.generate_json",
        return_value=sample_summarize_result,
    ) as mock:
        yield mock
