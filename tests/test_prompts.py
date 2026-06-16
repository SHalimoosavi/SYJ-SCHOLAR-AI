"""
tests/test_prompts.py
Tests for scholar.ai.prompts
"""

import pytest
from scholar.ai.prompts import (
    get_prompt, summarize_prompt, notes_prompt,
    flashcards_prompt, quiz_prompt, exam_prompt, study_prompt,
    PROMPT_MAP,
)

SAMPLE_TEXT = "Photosynthesis is the process by which plants convert sunlight into food. " * 20


def test_get_prompt_returns_tuple():
    system, user = get_prompt("summarize", SAMPLE_TEXT)
    assert isinstance(system, str)
    assert isinstance(user, str)
    assert len(system) > 10
    assert len(user) > 10


def test_all_actions_in_map():
    for action in ["summarize", "notes", "flashcards", "quiz", "exam", "study"]:
        sys_p, user_p = get_prompt(action, SAMPLE_TEXT)
        assert "JSON" in sys_p or "json" in user_p


def test_unknown_action_raises():
    with pytest.raises(ValueError, match="Unknown action"):
        get_prompt("nonexistent", SAMPLE_TEXT)


def test_text_truncated_in_prompt():
    long_text = "x " * 20_000
    _, user = summarize_prompt(long_text)
    # The prompt must not be enormous (text is sliced at 6000 chars)
    assert len(user) < 15_000


def test_quiz_prompt_includes_count():
    _, user = quiz_prompt(SAMPLE_TEXT, count=7)
    assert "7" in user


def test_flashcards_prompt_asks_for_cards():
    _, user = flashcards_prompt(SAMPLE_TEXT)
    assert "flashcard" in user.lower() or "card" in user.lower()
