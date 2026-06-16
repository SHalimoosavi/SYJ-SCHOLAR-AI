"""
scholar/ui/theme.py
Centralised Rich styling tokens for SYJ Scholar AI.
"""

from rich.theme import Theme

SCHOLAR_THEME = Theme(
    {
        # Brand
        "brand":       "bold cyan",
        "brand.dim":   "cyan",
        "brand.title": "bold bright_cyan",

        # Status
        "success":  "bold green",
        "warning":  "bold yellow",
        "error":    "bold red",
        "info":     "bold blue",
        "muted":    "dim white",

        # Content
        "heading":     "bold white",
        "subheading":  "bold cyan",
        "bullet":      "yellow",
        "definition":  "italic magenta",
        "formula":     "bold green",
        "question":    "bold white",
        "answer":      "green",
        "correct":     "bold green",
        "highlight":   "bold yellow",

        # UI chrome
        "border":      "cyan",
        "menu.key":    "bold cyan",
        "menu.label":  "white",
        "menu.sel":    "bold bright_white on blue",
        "footer":      "dim cyan",
    }
)

# Separator lines
SEP  = "━" * 50
SEP2 = "─" * 50
SEP3 = "═" * 50
