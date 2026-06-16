"""
scholar/utils/helpers.py
General-purpose helper functions.
"""

from __future__ import annotations

import re
import hashlib
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Any


# ── Text sanitisation ─────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert *text* to a filesystem-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def truncate(text: str, max_chars: int = 300, suffix: str = "…") -> str:
    """Truncate *text* to *max_chars*, appending *suffix* if trimmed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + suffix


def clean_text(text: str) -> str:
    """Remove excessive whitespace and control characters."""
    text = re.sub(r"[\r\n]+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── File helpers ──────────────────────────────────────────────────────────────

def file_hash(path: Path, algorithm: str = "sha256") -> str:
    """Return hex digest of a file (for caching / dedup)."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_filename(name: str, ext: str = "") -> str:
    """Make *name* safe for use as a filename."""
    base = slugify(name) or "untitled"
    if ext and not ext.startswith("."):
        ext = "." + ext
    return base + ext


def timestamped_name(stem: str, ext: str) -> str:
    """E.g.  timestamped_name('notes', '.md') → 'notes-2024-06-15T14-30.md'"""
    ts = datetime.now().strftime("%Y-%m-%dT%H-%M")
    return f"{stem}-{ts}{ext}"


# ── Miscellaneous ─────────────────────────────────────────────────────────────

def human_size(num_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def chunk_text(text: str, max_tokens: int = 2000, overlap: int = 200) -> list[str]:
    """
    Split *text* into overlapping word chunks for feeding to an LLM.
    *max_tokens* is a rough word-count limit (1 token ≈ 0.75 words).
    """
    words = text.split()
    max_words = int(max_tokens * 0.75)
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks


def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    """Flatten a nested dictionary."""
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
