"""
tests/test_flashcard_manager.py
Tests for scholar.flashcards.manager
"""

import json
import pytest
from pathlib import Path
from scholar.flashcards.manager import Flashcard, FlashcardManager

SAMPLE_RAW = {
    "topic": "Physics",
    "cards": [
        {"id": 1, "question": "What is Newton's 2nd law?",
         "answer": "F = ma", "difficulty": "easy", "tags": ["mechanics"]},
        {"id": 2, "question": "What is the speed of light?",
         "answer": "3×10⁸ m/s", "difficulty": "medium", "tags": ["optics"]},
        {"id": 3, "question": "State Ohm's law.",
         "answer": "V = IR", "difficulty": "hard", "tags": ["electricity"]},
    ],
}


def test_manager_parses_cards():
    mgr = FlashcardManager(SAMPLE_RAW)
    assert len(mgr) == 3
    assert mgr.topic == "Physics"


def test_card_attributes():
    mgr = FlashcardManager(SAMPLE_RAW)
    card = mgr.cards[0]
    assert card.question == "What is Newton's 2nd law?"
    assert card.answer   == "F = ma"
    assert card.difficulty == "easy"
    assert "mechanics" in card.tags


def test_to_json_roundtrip():
    mgr  = FlashcardManager(SAMPLE_RAW)
    raw  = json.loads(mgr.to_json())
    assert raw["topic"] == "Physics"
    assert len(raw["cards"]) == 3
    assert raw["count"] == 3


def test_to_markdown_contains_questions():
    mgr = FlashcardManager(SAMPLE_RAW)
    md  = mgr.to_markdown()
    assert "Newton" in md
    assert "speed of light" in md
    assert "Ohm" in md
    assert "🟢" in md   # easy
    assert "🔴" in md   # hard


def test_to_anki_csv_format():
    mgr = FlashcardManager(SAMPLE_RAW)
    csv = mgr.to_anki_csv()
    assert "#separator:tab" in csv
    assert "Newton's 2nd law" in csv
    assert "\t" in csv


def test_to_txt():
    mgr = FlashcardManager(SAMPLE_RAW)
    txt = mgr.to_txt()
    assert "FLASHCARDS: Physics" in txt
    assert "Q: What is Newton" in txt


def test_stats():
    mgr   = FlashcardManager(SAMPLE_RAW)
    stats = mgr.stats()
    assert stats["total"] == 3
    assert stats["easy"]   == 1
    assert stats["medium"] == 1
    assert stats["hard"]   == 1


def test_save_markdown(tmp_path):
    mgr  = FlashcardManager(SAMPLE_RAW)
    path = mgr.save(tmp_path / "cards", fmt="markdown")
    assert path.exists()
    assert path.suffix == ".md"
    assert "Newton" in path.read_text()


def test_save_json(tmp_path):
    mgr  = FlashcardManager(SAMPLE_RAW)
    path = mgr.save(tmp_path / "cards", fmt="json")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["topic"] == "Physics"


def test_save_anki(tmp_path):
    mgr  = FlashcardManager(SAMPLE_RAW)
    path = mgr.save(tmp_path / "cards", fmt="anki")
    assert path.exists()
    assert path.suffix == ".csv"


def test_malformed_card_skipped():
    raw = {
        "topic": "Test",
        "cards": [
            {"id": 1, "question": "Good Q", "answer": "Good A"},
            {"id": 2, "question": "", "answer": ""},   # should be skipped (empty)
        ],
    }
    mgr = FlashcardManager(raw)
    assert len(mgr) == 1
