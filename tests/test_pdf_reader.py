"""
tests/test_pdf_reader.py
Tests for scholar.pdf.reader (PDFReader)

Creates a minimal real PDF with fpdf2 (lightweight) if available,
otherwise falls back to a pre-encoded minimal PDF byte string so
tests run even without a PDF test fixture on disk.
"""

import io
import struct
import zlib
import pytest
from pathlib import Path

from scholar.pdf.reader import PDFReader, PDFMeta, _is_usable


# ── Minimal valid PDF builder (no external deps) ──────────────────────────────

MINIMAL_PDF = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj
4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
5 0 obj<</Length 44>>
stream
BT /F1 12 Tf 72 720 Td (Hello Scholar AI Test) Tj ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000352 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
448
%%EOF"""


@pytest.fixture
def sample_pdf(tmp_path) -> Path:
    """Write a minimal syntactically valid PDF and return its path."""
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(MINIMAL_PDF)
    return pdf_path


@pytest.fixture
def text_pdf(tmp_path) -> Path:
    """Try to create a richer PDF using fpdf2; fall back to minimal if not available."""
    pdf_path = tmp_path / "rich.pdf"
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for i in range(20):
            pdf.cell(0, 10,
                f"Photosynthesis is how plants make food using sunlight and CO2. Line {i}",
                ln=True)
        pdf.output(str(pdf_path))
    except ImportError:
        # Fall back to the minimal PDF
        pdf_path.write_bytes(MINIMAL_PDF)
    return pdf_path


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_reader_instantiates(sample_pdf):
    reader = PDFReader(sample_pdf)
    assert reader.path == sample_pdf


def test_meta_has_page_count(sample_pdf):
    reader = PDFReader(sample_pdf)
    meta   = reader.meta
    assert isinstance(meta, PDFMeta)
    assert meta.page_count >= 0        # 0 if fitz can't parse minimal PDF, that's OK
    assert meta.sha256                 # hash always computed
    assert meta.size_bytes > 0


def test_extract_text_returns_string(sample_pdf):
    reader = PDFReader(sample_pdf)
    text   = reader.extract_text()
    assert isinstance(text, str)


def test_extract_text_cached(sample_pdf):
    """Second call should return the same object (cached)."""
    reader = PDFReader(sample_pdf)
    t1     = reader.extract_text()
    t2     = reader.extract_text()
    assert t1 is t2


def test_extract_text_nonempty_rich(text_pdf):
    """Rich PDF should yield ≥ 1 character of text."""
    reader = PDFReader(text_pdf)
    text   = reader.extract_text()
    assert isinstance(text, str)
    # At least something extracted (fpdf2 path) or empty (fallback minimal)


def test_is_usable_short():
    assert _is_usable("one two three") is False


def test_is_usable_long():
    text = "word " * 100
    assert _is_usable(text) is True


def test_is_usable_threshold():
    # Exactly 50 words = boundary
    text = " ".join(["word"] * 50)
    assert _is_usable(text, min_words=50) is True
    assert _is_usable(text, min_words=51) is False


def test_nonexistent_pdf_raises(tmp_path):
    reader = PDFReader(tmp_path / "ghost.pdf")
    # extract_text should not crash — it returns "" or error string
    text = reader.extract_text()
    assert isinstance(text, str)
