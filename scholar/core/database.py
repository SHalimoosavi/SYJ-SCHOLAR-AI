"""
scholar/core/database.py
Lightweight SQLite store for sessions, history, and cached results.
Uses only stdlib sqlite3 — no ORM overhead on Termux.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Any

from scholar.utils.paths import get_db_path
from scholar.utils.logger import get_logger

logger = get_logger(__name__)
DB_PATH: Path = get_db_path()


# ── Schema ─────────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_path    TEXT    NOT NULL,
    pdf_hash    TEXT    NOT NULL,
    action      TEXT    NOT NULL,   -- summarize | notes | flashcards | quiz | exam | study
    model       TEXT    NOT NULL,
    created_at  TEXT    NOT NULL,
    duration_s  REAL,
    output_path TEXT
);

CREATE TABLE IF NOT EXISTS results_cache (
    pdf_hash    TEXT    NOT NULL,
    action      TEXT    NOT NULL,
    model       TEXT    NOT NULL,
    result_json TEXT    NOT NULL,
    created_at  TEXT    NOT NULL,
    PRIMARY KEY (pdf_hash, action, model)
);

CREATE TABLE IF NOT EXISTS settings_kv (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);
"""


# ── Connection helper ──────────────────────────────────────────────────────────

@contextmanager
def get_conn() -> Generator[sqlite3.Connection, None, None]:
    """Yield a thread-safe connection with WAL mode enabled."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables on first run."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)
    logger.debug(f"Database initialised → {DB_PATH}")


# ── Sessions ───────────────────────────────────────────────────────────────────

def log_session(
    pdf_path: str,
    pdf_hash: str,
    action: str,
    model: str,
    duration_s: float | None = None,
    output_path: str | None = None,
) -> int:
    """Insert a session record and return its row id."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO sessions (pdf_path, pdf_hash, action, model, created_at, duration_s, output_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pdf_path, pdf_hash, action, model,
                datetime.utcnow().isoformat(),
                duration_s, output_path,
            ),
        )
        return cur.lastrowid


def get_recent_sessions(limit: int = 20) -> list[dict[str, Any]]:
    """Return the *limit* most recent sessions."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Result Cache ───────────────────────────────────────────────────────────────

def get_cached_result(pdf_hash: str, action: str, model: str) -> dict | None:
    """Return cached result dict, or None if not present."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT result_json FROM results_cache WHERE pdf_hash=? AND action=? AND model=?",
            (pdf_hash, action, model),
        ).fetchone()
    if row:
        return json.loads(row["result_json"])
    return None


def cache_result(pdf_hash: str, action: str, model: str, result: dict) -> None:
    """Upsert a result into the cache."""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO results_cache (pdf_hash, action, model, result_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (pdf_hash, action, model, json.dumps(result), datetime.utcnow().isoformat()),
        )


# ── Key-Value settings ─────────────────────────────────────────────────────────

def kv_set(key: str, value: Any) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings_kv (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )


def kv_get(key: str, default: Any = None) -> Any:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM settings_kv WHERE key=?", (key,)
        ).fetchone()
    if row:
        return json.loads(row["value"])
    return default


# Auto-initialise on import
init_db()
