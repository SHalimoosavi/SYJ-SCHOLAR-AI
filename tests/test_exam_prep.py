"""
tests/test_exam_prep.py
Tests for scholar.exam.prep
"""

import json
import pytest
from scholar.exam.prep import ExamPrepEngine, ExamTopic

SAMPLE_RAW = {
    "topic": "Thermodynamics",
    "important_topics": [
        {"topic": "Laws of Thermodynamics", "priority": "high",   "reason": "Core exam topic"},
        {"topic": "Entropy",                "priority": "medium", "reason": "Often tested"},
        {"topic": "PV diagrams",            "priority": "low",    "reason": "Supplementary"},
    ],
    "most_likely_questions": [
        {"question": "State the First Law of Thermodynamics.",
         "type": "short", "hint": "Energy conservation"},
        {"question": "Derive the Carnot efficiency.",
         "type": "long",  "hint": "Use T_H and T_C"},
    ],
    "revision_checklist": [
        {"item": "Review zeroth law", "done": False},
        {"item": "Practice PV problems", "done": True},
    ],
    "high_priority_concepts": ["Entropy", "Enthalpy", "Gibbs free energy"],
    "study_tips": ["Do past papers", "Focus on derivations"],
}


def test_parse_topics():
    engine = ExamPrepEngine(SAMPLE_RAW)
    topics = engine.prep.important_topics
    # Should be sorted: high → medium → low
    assert topics[0].priority == "high"
    assert topics[1].priority == "medium"
    assert topics[2].priority == "low"


def test_parse_questions():
    engine = ExamPrepEngine(SAMPLE_RAW)
    qs     = engine.prep.most_likely_questions
    assert len(qs) == 2
    assert qs[0].qtype == "short"
    assert qs[1].qtype == "long"
    assert "Carnot" in qs[1].question


def test_parse_checklist():
    engine = ExamPrepEngine(SAMPLE_RAW)
    cl     = engine.prep.revision_checklist
    assert len(cl) == 2
    assert cl[1].done is True


def test_parse_high_priority_concepts():
    engine = ExamPrepEngine(SAMPLE_RAW)
    assert "Entropy" in engine.prep.high_priority_concepts


def test_to_markdown_structure():
    engine = ExamPrepEngine(SAMPLE_RAW)
    md     = engine.to_markdown()
    assert "# Exam Preparation: Thermodynamics" in md
    assert "Laws of Thermodynamics" in md
    assert "First Law" in md
    assert "- [ ] Review zeroth law" in md
    assert "- [x] Practice PV problems" in md
    assert "Entropy" in md
    assert "Do past papers" in md


def test_to_json_roundtrip():
    engine = ExamPrepEngine(SAMPLE_RAW)
    data   = json.loads(engine.to_json())
    assert data["topic"] == "Thermodynamics"
    assert len(data["important_topics"]) == 3
    assert len(data["most_likely_questions"]) == 2
    assert "Entropy" in data["high_priority_concepts"]


def test_to_txt():
    engine = ExamPrepEngine(SAMPLE_RAW)
    txt    = engine.to_txt()
    assert "EXAM PREPARATION: Thermodynamics" in txt
    assert "[HIGH]" in txt
    assert "Carnot" in txt


def test_generate_schedule_correct_length():
    engine   = ExamPrepEngine(SAMPLE_RAW)
    schedule = engine.generate_schedule(days_until_exam=7)
    assert len(schedule) == 7


def test_generate_schedule_ends_with_revision():
    engine   = ExamPrepEngine(SAMPLE_RAW)
    schedule = engine.generate_schedule(days_until_exam=5)
    assert schedule[-1]["focus"] == "REVISION DAY"


def test_generate_schedule_single_day():
    engine   = ExamPrepEngine(SAMPLE_RAW)
    schedule = engine.generate_schedule(days_until_exam=1)
    assert len(schedule) == 1
    assert schedule[0]["focus"] == "REVISION DAY"


def test_save_markdown(tmp_path):
    engine = ExamPrepEngine(SAMPLE_RAW)
    path   = engine.save(tmp_path / "exam", fmt="markdown")
    assert path.exists()
    assert "Thermodynamics" in path.read_text()


def test_topic_priority_rank():
    assert ExamTopic("A", "high").priority_rank   == 0
    assert ExamTopic("B", "medium").priority_rank == 1
    assert ExamTopic("C", "low").priority_rank    == 2
    assert ExamTopic("D", "unknown").priority_rank == 1  # default
