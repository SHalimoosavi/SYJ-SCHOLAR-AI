"""
tests/test_helpers.py
Unit tests for scholar.utils.helpers
"""

import pytest
from scholar.utils.helpers import (
    slugify, truncate, clean_text, safe_filename,
    human_size, chunk_text,
)


def test_slugify_basic():
    assert slugify("Hello World!") == "hello-world"


def test_slugify_unicode():
    result = slugify("Ünïcödé Tèxt")
    assert result.isascii()


def test_truncate_short():
    assert truncate("hello", 100) == "hello"


def test_truncate_long():
    text = "a" * 400
    result = truncate(text, 300)
    assert len(result) <= 305   # 300 + ellipsis
    assert result.endswith("…")


def test_clean_text():
    messy = "line1\r\n\r\nline2   \n\n\n\nline3"
    result = clean_text(messy)
    assert "\r" not in result
    assert "\n\n\n" not in result


def test_safe_filename():
    name = safe_filename("My Lecture Notes!", ext=".md")
    assert name.endswith(".md")
    assert " " not in name
    assert "!" not in name


def test_human_size():
    assert "B"  in human_size(500)
    assert "KB" in human_size(2048)
    assert "MB" in human_size(2 * 1024 * 1024)


def test_chunk_text_no_overlap():
    text = " ".join(f"word{i}" for i in range(10_000))
    chunks = chunk_text(text, max_tokens=500, overlap=0)
    assert len(chunks) > 1
    # All words should be covered
    reconstructed = " ".join(chunks)
    # Every original word appears somewhere
    assert "word0"    in reconstructed
    assert "word9999" in reconstructed


def test_chunk_text_overlap():
    text = " ".join(str(i) for i in range(1000))
    chunks = chunk_text(text, max_tokens=200, overlap=50)
    assert len(chunks) >= 2
    # Overlap means word at boundary appears in both chunks
    # (weak check — just ensure no crash and multiple chunks)
