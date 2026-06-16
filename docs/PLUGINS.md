# Plugin Development Guide

SYJ Scholar AI has a **first-class plugin system** that lets you add custom commands
and features without modifying the core codebase.

---

## How Plugins Work

1. Plugins are Python files placed in `~/.local/share/SYJScholarAI/plugins/<name>/plugin.py`
2. Scholar AI auto-discovers and loads them at startup
3. Each plugin registers one or more Typer sub-commands on the main `scholar` app
4. Plugins appear in `scholar --help` alongside built-in commands

---

## Quick Start

```bash
# Create your plugin directory
mkdir -p ~/.local/share/SYJScholarAI/plugins/my_plugin

# Create the plugin file
nano ~/.local/share/SYJScholarAI/plugins/my_plugin/plugin.py
```

```python
# plugin.py
import typer
from rich.console import Console

PLUGIN_NAME    = "my-plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR  = "Your Name"

console = Console()

def register(app: typer.Typer) -> None:
    @app.command("my-command", help="My custom Scholar AI command.")
    def my_cmd(pdf: str = typer.Argument(..., help="Path to PDF")):
        console.print(f"[cyan]Processing {pdf}…[/cyan]")
```

```bash
# Test it
scholar my-command test.pdf
```

---

## Plugin File Structure

```
~/.local/share/SYJScholarAI/plugins/
└── my_plugin/
    ├── plugin.py          ← required: must expose register()
    ├── requirements.txt   ← optional: plugin-specific deps
    └── README.md          ← optional: plugin documentation
```

---

## The `register()` Function

The **only required export** from your plugin is:

```python
def register(app: typer.Typer) -> None:
    """Called by Scholar AI on startup."""
    ...
```

This function receives the root Typer app and should add commands to it.

---

## Plugin Metadata

Optional but recommended module-level constants:

```python
PLUGIN_NAME        = "my-plugin"       # command prefix / display name
PLUGIN_VERSION     = "1.0.0"           # semver
PLUGIN_AUTHOR      = "Your Name"       # attribution
PLUGIN_DESCRIPTION = "Does cool things"
```

---

## Full Example: Vocabulary Extractor Plugin

```python
"""
Vocabulary Extractor Plugin for SYJ Scholar AI
Extracts difficult vocabulary words from PDFs.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

PLUGIN_NAME    = "vocab-extractor"
PLUGIN_VERSION = "1.0.0"

console = Console()


def register(app: typer.Typer) -> None:

    @app.command("vocab", help="[Plugin] Extract vocabulary words from a PDF.")
    def vocab_cmd(
        pdf: Path = typer.Argument(..., help="Path to PDF file"),
        limit: int = typer.Option(20, "--limit", "-n", help="Number of words"),
        export: Optional[Path] = typer.Option(None, "--output", "-o"),
    ):
        """Extract vocabulary words from a PDF using Scholar AI's pipeline."""

        # Import Scholar AI internals
        from scholar.pdf.reader import PDFReader
        from scholar.ai.engine import AIEngine
        from scholar.core.config import get_config
        from scholar.ui.progress import with_progress

        if not pdf.exists():
            console.print(f"[red]File not found: {pdf}[/red]")
            raise typer.Exit(1)

        cfg = get_config()

        # Custom prompt for vocab extraction
        SYSTEM = (
            "You are a vocabulary extraction assistant. "
            "Respond ONLY in JSON. No markdown fences."
        )
        USER_TMPL = """
Extract the {limit} most important and difficult vocabulary words from this academic text.
Return ONLY this JSON:
{{
  "topic": "<subject area>",
  "words": [
    {{
      "word": "<word or phrase>",
      "definition": "<clear definition>",
      "example": "<example sentence from the text>"
    }}
  ]
}}
TEXT:
{text}
"""

        with with_progress(f"Extracting vocabulary from {pdf.name} …") as prog:
            reader = PDFReader(pdf)
            text   = reader.extract_text()[:8000]
            prog.update_text("Running AI …")

            provider = AIEngine(cfg).provider
            result   = provider.generate_json(
                SYSTEM,
                USER_TMPL.format(limit=limit, text=text),
            )

        # Display
        words = result.get("words", [])
        tbl   = Table(title=f"Vocabulary: {result.get('topic', pdf.stem)}")
        tbl.add_column("Word",       style="bold cyan", min_width=20)
        tbl.add_column("Definition", style="white")
        tbl.add_column("Example",    style="dim",       min_width=30)
        for w in words:
            tbl.add_row(
                w.get("word", ""),
                w.get("definition", ""),
                w.get("example", ""),
            )
        console.print(tbl)

        # Optional export
        if export:
            import json
            export.parent.mkdir(parents=True, exist_ok=True)
            export.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            console.print(f"[green]✓ Saved → {export}[/green]")
```

---

## Accessing Scholar AI Internals

Plugins can import any Scholar AI module:

```python
from scholar.pdf.reader    import PDFReader         # PDF extraction
from scholar.ai.engine     import AIEngine           # AI orchestrator
from scholar.core.config   import get_config         # App config
from scholar.core.database import log_session        # Session logging
from scholar.exports.exporter import export_result  # Multi-format export
from scholar.ui.progress   import with_progress     # Spinner context
from scholar.ui.renderer   import render_result     # Terminal rendering
from scholar.utils.helpers import chunk_text        # Text utilities
from scholar.utils.paths   import get_output_dir    # Output paths
```

---

## Plugin Guidelines

### Do ✅

- Handle all exceptions gracefully — plugin errors must not crash Scholar AI
- Use `with_progress()` for long operations
- Follow the project's Rich colour scheme (`var(--cyan)` for success, etc.)
- Include a `PLUGIN_NAME` constant
- Write tests in a `tests/` subdirectory of your plugin

### Don't ❌

- Modify core Scholar AI modules directly
- Make network calls without user knowledge
- Store data outside Scholar AI's data directories
- Block the main thread for long periods without showing progress
- Require private API keys (Scholar AI is free and open)

---

## Error Handling

```python
def register(app: typer.Typer) -> None:
    @app.command("my-cmd")
    def my_cmd(pdf: Path = typer.Argument(...)):
        try:
            # your logic
            pass
        except FileNotFoundError:
            console.print("[red]File not found.[/red]")
            raise typer.Exit(1)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1)
```

---

## Distributing Your Plugin

1. Create a GitHub repo: `syj-scholar-ai-plugin-myplugin`
2. Users install it with:
   ```bash
   git clone https://github.com/you/syj-scholar-ai-plugin-myplugin \
       ~/.local/share/SYJScholarAI/plugins/myplugin
   ```
3. Submit a PR to add it to the official [Plugin Registry](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/wiki/Plugins)

---

## Plugin API Version

Current plugin API version: **1.0**

Plugins are loaded after all core commands are registered.
The `app` passed to `register()` is the root `typer.Typer` instance from `main.py`.
