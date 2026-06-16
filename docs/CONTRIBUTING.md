# Contributing to SYJ Scholar AI

Thank you for helping make **SYJ Scholar AI** better! 🎓

This document covers everything you need to contribute code, docs, plugins, or bug reports.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Writing Plugins](#writing-plugins)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We welcome contributors from all backgrounds and skill levels.

---

## How to Contribute

| Type | What to do |
|------|-----------|
| 🐛 Bug fix | Fork → fix → PR |
| ✨ New feature | Open an issue first to discuss |
| 📚 Documentation | Edit any `.md` file and PR |
| 🧩 Plugin | Add to `plugins/` and PR |
| 🌐 Translation | Open an issue to coordinate |
| 🤖 New AI model | Update `scholar/ai/` and PR |

---

## Development Setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/SYJ-SCHOLAR-AI.git
cd SYJ-SCHOLAR-AI

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Linux / macOS / Termux
# .venv\Scripts\activate.bat    # Windows

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Install system dependencies (Ubuntu / Debian)
sudo apt install tesseract-ocr tesseract-ocr-eng

# 5. Install and start Ollama (for integration tests)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma:2b

# 6. Verify everything works
scholar --version
scholar --help
```

---

## Project Structure

```
scholar/
├── core/       # config, CLI, database, updater, plugins
├── ai/         # providers (Ollama, HuggingFace), prompts, engine
├── pdf/        # PDF extraction pipeline
├── flashcards/ # FlashcardManager + exports
├── notes/      # NotesFormatter + exports
├── quiz/       # QuizRunner + interactive self-test
├── exam/       # ExamPrepEngine + study scheduler
├── exports/    # Multi-format exporter + HTML renderer
├── ui/         # dashboard, renderer, progress, theme, templates
└── utils/      # logger, paths, helpers
```

Each sub-package has an `__init__.py` that re-exports its public API.

---

## Running Tests

```bash
# Run all tests (fast — no actual AI calls)
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=scholar --cov-report=term-missing

# Run a specific test file
pytest tests/test_flashcard_manager.py -v

# Run only tests matching a keyword
pytest tests/ -k "flashcard" -v

# Run the full suite including PDF tests (requires PyMuPDF)
pytest tests/ -v --tb=short
```

All tests mock AI provider calls — no Ollama instance required for the test suite.

---

## Code Style

We use **Ruff** for linting and **Black** for formatting.

```bash
# Lint
ruff check scholar/ tests/

# Format
black scholar/ tests/ main.py

# Type check (optional but appreciated)
mypy scholar/
```

Rules are defined in `pyproject.toml`. Key points:

- Line length: **100 characters**
- String quotes: **double quotes** (`"`)
- Import order: `stdlib → third-party → local` (Ruff `I` rules)
- Type hints encouraged for all public functions
- Docstrings on all public classes and functions

---

## Submitting a Pull Request

1. Create a branch from `main`:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

2. Make your changes with clear, focused commits:
   ```bash
   git commit -m "feat: add Anki export for flashcards"
   ```

3. Ensure tests pass and linting is clean:
   ```bash
   pytest tests/ && ruff check scholar/ && black --check scholar/
   ```

4. Push and open a PR against `main`:
   ```bash
   git push origin feature/my-awesome-feature
   ```

5. Fill out the PR template describing **what**, **why**, and **how to test**.

### Commit Message Format

We loosely follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `test:` | Adding or fixing tests |
| `refactor:` | Code change without feature/fix |
| `chore:` | Build, deps, CI |
| `perf:` | Performance improvement |

---

## Writing Plugins

Plugins extend Scholar AI without touching the core.

```python
# ~/.local/share/SYJScholarAI/plugins/my_plugin/plugin.py
import typer
from rich.console import Console
from pathlib import Path

PLUGIN_NAME    = "my-plugin"
PLUGIN_VERSION = "1.0.0"

console = Console()

def register(app: typer.Typer) -> None:
    """Called at startup — add your commands here."""

    @app.command("my-command", help="My custom Scholar AI command.")
    def my_cmd(
        pdf: Path = typer.Argument(..., help="PDF file to process"),
    ):
        console.print(f"[cyan]Processing {pdf.name}…[/cyan]")
        # Your logic here
```

**Plugin rules:**
- Must expose a `register(app: typer.Typer)` function
- Must define `PLUGIN_NAME` string
- Must not modify core Scholar AI internals
- Should handle its own errors gracefully
- Must follow the same code style as core

To test your plugin:
```bash
# Copy to the plugins dir
cp -r my_plugin ~/.local/share/SYJScholarAI/plugins/

# Launch Scholar AI — plugin loads automatically
scholar
scholar my-command test.pdf
```

---

## Reporting Bugs

Please use [GitHub Issues](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues) and include:

1. **Scholar AI version** (`scholar --version`)
2. **Python version** (`python3 --version`)
3. **Environment** (Termux / Ubuntu / etc.)
4. **Steps to reproduce**
5. **Expected vs actual behaviour**
6. **Error output** (paste the full traceback)

---

## Feature Requests

Open an issue with the `enhancement` label. Describe:

- **The problem** you're trying to solve
- **Your proposed solution**
- **Alternatives considered**

---

## Questions?

Open a [Discussion](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/discussions) or an Issue.

Thank you for contributing! 🚀
