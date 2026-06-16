"""scholar.exports — multi-format output generation (MD, TXT, JSON, HTML)."""
from .exporter import export_result, _to_json, _to_txt, _to_markdown, _to_html
from .html_renderer import render_html

__all__ = ["export_result", "_to_json", "_to_txt", "_to_markdown", "_to_html", "render_html"]
