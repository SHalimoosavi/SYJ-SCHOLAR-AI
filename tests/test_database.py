"""
tests/test_database.py
Tests for scholar.core.database
"""

import pytest
from scholar.core.database import (
    init_db, log_session, get_recent_sessions,
    get_cached_result, cache_result,
    kv_set, kv_get,
)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Redirect DB to a temp path for each test."""
    db = tmp_path / "test.db"
    import scholar.core.database as db_module
    monkeypatch.setattr(db_module, "DB_PATH", db)
    init_db()


def test_log_and_fetch_session():
    session_id = log_session(
        pdf_path="test.pdf",
        pdf_hash="abc123",
        action="summarize",
        model="gemma:2b",
        duration_s=5.2,
    )
    assert session_id is not None

    sessions = get_recent_sessions(limit=5)
    assert len(sessions) == 1
    assert sessions[0]["action"] == "summarize"
    assert sessions[0]["model"]  == "gemma:2b"


def test_cache_result_roundtrip():
    data = {"title": "Test", "key_concepts": ["a", "b"]}
    cache_result("hash1", "summarize", "gemma:2b", data)

    retrieved = get_cached_result("hash1", "summarize", "gemma:2b")
    assert retrieved is not None
    assert retrieved["title"] == "Test"
    assert "a" in retrieved["key_concepts"]


def test_cache_miss():
    result = get_cached_result("nonexistent", "notes", "phi:mini")
    assert result is None


def test_kv_set_get():
    kv_set("last_model", "tinyllama")
    assert kv_get("last_model") == "tinyllama"


def test_kv_get_default():
    assert kv_get("does_not_exist", default="fallback") == "fallback"


def test_kv_overwrite():
    kv_set("key", "value1")
    kv_set("key", "value2")
    assert kv_get("key") == "value2"
