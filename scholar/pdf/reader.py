"""
scholar/pdf/reader.py

PDF extraction pipeline for Python 3.13 + Termux

1. pdfplumber
2. pypdf
3. OCR via pdf2image + pytesseract

No PyMuPDF dependency.
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, field

from scholar.utils.logger import get_logger
from scholar.utils.helpers import clean_text, file_hash

logger = get_logger(__name__)


@dataclass
class PDFMeta:
    path: Path
    sha256: str
    page_count: int
    title: str = ""
    author: str = ""
    size_bytes: int = 0


@dataclass
class PDFReader:
    path: Path

    _text: str = field(default="", init=False, repr=False)
    _meta: PDFMeta | None = field(default=None, init=False, repr=False)

    @property
    def meta(self) -> PDFMeta:
        if self._meta is None:
            self._meta = self._build_meta()
        return self._meta

    def extract_text(self, max_pages: int = 0) -> str:
        if self._text:
            return self._text

        text = self._extract_pdfplumber(max_pages)

        if _is_usable(text):
            self._text = text
            return text

        logger.info("pdfplumber yielded little text, trying pypdf...")

        text = self._extract_pypdf(max_pages)

        if _is_usable(text):
            self._text = text
            return text

        logger.info("pypdf yielded little text, trying OCR...")

        text = self._extract_ocr(max_pages)

        self._text = text
        return text

    def _extract_pdfplumber(self, max_pages: int) -> str:
        try:
            import pdfplumber

            parts = []

            with pdfplumber.open(str(self.path)) as pdf:
                pages = pdf.pages if not max_pages else pdf.pages[:max_pages]

                for page in pages:
                    txt = page.extract_text()

                    if txt:
                        parts.append(txt)

            return clean_text("\n".join(parts))

        except Exception as exc:
            logger.warning(f"pdfplumber failed: {exc}")
            return ""

    def _extract_pypdf(self, max_pages: int) -> str:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(self.path))

            pages = reader.pages

            if max_pages:
                pages = pages[:max_pages]

            parts = []

            for page in pages:
                txt = page.extract_text()

                if txt:
                    parts.append(txt)

            return clean_text("\n".join(parts))

        except Exception as exc:
            logger.warning(f"pypdf failed: {exc}")
            return ""

    def _extract_ocr(self, max_pages: int) -> str:
        try:
            from pdf2image import convert_from_path
            import pytesseract

            images = convert_from_path(str(self.path))

            if max_pages:
                images = images[:max_pages]

            parts = []

            for img in images:
                parts.append(
                    pytesseract.image_to_string(img, lang="eng")
                )

            return clean_text("\n".join(parts))

        except Exception as exc:
            logger.error(f"OCR failed: {exc}")
            return ""

    def _build_meta(self) -> PDFMeta:
        page_count = 0
        title = self.path.stem
        author = ""

        try:
            from pypdf import PdfReader

            reader = PdfReader(str(self.path))

            page_count = len(reader.pages)

            meta = reader.metadata

            if meta:
                title = getattr(meta, "title", None) or title
                author = getattr(meta, "author", None) or ""

        except Exception:
            pass

        return PDFMeta(
            path=self.path,
            sha256=file_hash(self.path),
            page_count=page_count,
            title=title,
            author=author,
            size_bytes=self.path.stat().st_size,
        )


def _is_usable(text: str, min_words: int = 15) -> bool:
    """
    Determine whether extracted text is usable.

    Most academic PDFs contain hundreds of words,
    but small handouts, notes, assignments and
    single-page PDFs may contain far fewer.

    A threshold of 15 words prevents unnecessary OCR
    while still rejecting empty or corrupted extraction.
    """
    return len(text.split()) >= min_words
