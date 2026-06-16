"""
tests/test_quiz_runner.py
Tests for scholar.quiz.runner (non-interactive parts)
"""

import json
import pytest
from scholar.quiz.runner import QuizRunner, QuizResult

SAMPLE_RAW = {
    "topic": "Biology",
    "mcqs": [
        {
            "id": 1,
            "question": "What is the powerhouse of the cell?",
            "options": {"A": "Nucleus", "B": "Mitochondria", "C": "Ribosome", "D": "Golgi"},
            "correct": "B",
            "explanation": "Mitochondria produce ATP via cellular respiration.",
        }
    ],
    "true_false": [
        {
            "id": 1,
            "statement": "DNA is double-stranded.",
            "answer": True,
            "explanation": "DNA has a double helix structure.",
        }
    ],
    "short_questions": [
        {
            "id": 1,
            "question": "What is photosynthesis?",
            "model_answer": "Process by which plants convert sunlight into glucose.",
        }
    ],
    "long_questions": [
        {
            "id": 1,
            "question": "Explain the cell cycle.",
            "key_points": ["G1 phase", "S phase", "G2 phase", "M phase"],
        }
    ],
}


def test_runner_parses_all_types():
    runner = QuizRunner(SAMPLE_RAW)
    assert len(runner.mcqs)       == 1
    assert len(runner.true_false) == 1
    assert len(runner.short_qs)   == 1
    assert len(runner.long_qs)    == 1
    assert runner.topic           == "Biology"


def test_stats():
    runner = QuizRunner(SAMPLE_RAW)
    stats  = runner.stats()
    assert stats["mcqs"]           == 1
    assert stats["true_false"]     == 1
    assert stats["short_questions"] == 1
    assert stats["long_questions"]  == 1
    assert stats["total"]          == 4


def test_mcq_fields():
    runner = QuizRunner(SAMPLE_RAW)
    mcq    = runner.mcqs[0]
    assert mcq.question           == "What is the powerhouse of the cell?"
    assert mcq.correct            == "B"
    assert "Mitochondria"         in mcq.options.values()
    assert "Mitochondria produce" in mcq.explanation


def test_to_markdown_contains_all_sections():
    runner = QuizRunner(SAMPLE_RAW)
    md     = runner.to_markdown()
    assert "Multiple Choice"     in md
    assert "True / False"        in md
    assert "Short Answer"        in md
    assert "Long / Essay"        in md
    assert "powerhouse"          in md
    assert "✓" in md   # correct MCQ marker


def test_to_json_roundtrip():
    runner = QuizRunner(SAMPLE_RAW)
    data   = json.loads(runner.to_json())
    assert data["topic"]              == "Biology"
    assert len(data["mcqs"])          == 1
    assert len(data["true_false"])    == 1
    assert len(data["short_questions"]) == 1
    assert len(data["long_questions"])  == 1


def test_to_txt():
    runner = QuizRunner(SAMPLE_RAW)
    txt    = runner.to_txt()
    assert "QUIZ: Biology"   in txt
    assert "MULTIPLE CHOICE" in txt
    assert "TRUE / FALSE"    in txt


def test_save_markdown(tmp_path):
    runner = QuizRunner(SAMPLE_RAW)
    path   = runner.save(tmp_path / "quiz", fmt="markdown")
    assert path.exists()
    assert "powerhouse" in path.read_text()


def test_save_json(tmp_path):
    runner = QuizRunner(SAMPLE_RAW)
    path   = runner.save(tmp_path / "quiz", fmt="json")
    assert path.exists()
    data   = json.loads(path.read_text())
    assert data["topic"] == "Biology"


def test_quiz_result_grade():
    assert QuizResult(10, 10,  0, 0, 100.0).grade().startswith("A+")
    assert QuizResult(10,  8,  2, 0,  80.0).grade().startswith("A")
    assert QuizResult(10,  5,  5, 0,  50.0).grade().startswith("D")
    assert QuizResult(10,  3,  7, 0,  30.0).grade().startswith("F")


def test_empty_quiz_parses_ok():
    runner = QuizRunner({"topic": "Empty"})
    assert len(runner.mcqs)       == 0
    assert len(runner.true_false) == 0
    stats = runner.stats()
    assert stats["total"] == 0
