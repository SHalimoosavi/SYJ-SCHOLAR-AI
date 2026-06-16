<div align="center">

```
 ███████╗██╗   ██╗     ██╗    ███████╗ ██████╗██╗  ██╗ ██████╗ ██╗      █████╗ ██████╗
 ██╔════╝╚██╗ ██╔╝     ██║    ██╔════╝██╔════╝██║  ██║██╔═══██╗██║     ██╔══██╗██╔══██╗
 ███████╗ ╚████╔╝      ██║    ███████╗██║     ███████║██║   ██║██║     ███████║██████╔╝
 ╚════██║  ╚██╔╝  ██   ██║    ╚════██║██║     ██╔══██║██║   ██║██║     ██╔══██║██╔══██╗
 ███████║   ██║   ╚█████╔╝    ███████║╚██████╗██║  ██║╚██████╔╝███████╗██║  ██║██║  ██║
 ╚══════╝   ╚═╝    ╚════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

**Your Offline AI Study Companion**

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![Termux Ready](https://img.shields.io/badge/Termux-Ready-orange.svg)](https://termux.dev)
[![Offline First](https://img.shields.io/badge/offline-first-purple.svg)](#)
[![GitHub Stars](https://img.shields.io/github/stars/SHalimoosavi/SYJ-SCHOLAR-AI?style=social)](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI)

*Free · Open-Source · Offline · Mobile-First*

</div>

---

## 🎯 What is SYJ Scholar AI?

SYJ Scholar AI transforms any PDF into a complete study package — summaries, notes, flashcards, quizzes, and exam prep — all powered by **free, open-source AI** running entirely on your Android phone through **Termux**. No subscriptions. No internet required after setup. No data leaves your device.

---

## 😩 The Problem

| Challenge | How Scholar AI Solves It |
|-----------|--------------------------|
| Too many PDFs, no time | Instant summaries & key concept extraction |
| Expensive AI subscriptions | 100% free & open-source forever |
| Poor internet connectivity | Works fully offline after model download |
| Multiple apps for notes/cards/quizzes | One tool does everything |
| Mobile students without laptops | Built for Android + Termux |
| Exam prep is hard | AI generates likely questions & checklists |

---

## ⚡ Quick Start

### One-Line Install (Termux & Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash
```

After installation, just type:

```bash
scholar
```

You'll see a beautiful interactive dashboard.

---

## 📱 Termux Setup (Step by Step)

```bash
# 1. Install Termux from F-Droid (NOT Google Play)
#    https://f-droid.org/packages/com.termux/

# 2. Update packages
pkg update && pkg upgrade -y

# 3. Install Scholar AI
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash

# 4. Install Ollama (AI engine)
pkg install ollama

# 5. Start Ollama and pull a model (choose based on your RAM)
ollama serve &
ollama pull gemma:2b      # recommended: fast, 2GB RAM
# ollama pull phi:mini    # lighter: 1.3GB RAM
# ollama pull tinyllama   # minimal: 0.6GB RAM

# 6. Launch!
scholar
```

---

## 🖥️ Desktop / Linux Install

```bash
# Install dependencies
sudo apt install python3 python3-pip tesseract-ocr git

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma:2b

# Install Scholar AI
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash
```

---

## 🎓 Core Commands

### Interactive Dashboard
```bash
scholar
```

### Direct CLI Commands

```bash
# Full study package (all-in-one)
scholar study       lecture.pdf

# PDF Summary
scholar summarize   lecture.pdf

# Structured Notes
scholar notes       lecture.pdf

# Flashcards
scholar flashcards  lecture.pdf

# Quiz (MCQ + True/False + Short + Long)
scholar quiz        lecture.pdf

# Exam Preparation
scholar exam        lecture.pdf
```

### Options

```bash
# Change export format
scholar summarize lecture.pdf --format json
scholar notes     lecture.pdf --format html
scholar quiz      lecture.pdf --format txt

# Set output directory
scholar flashcards lecture.pdf --output ~/Desktop/

# Skip cache (regenerate)
scholar summarize  lecture.pdf --no-cache

# Check for updates
scholar update

# View recent sessions
scholar history --limit 20

# Settings
scholar settings --show
scholar settings --model phi:mini
scholar settings --format markdown
```

---

## 📤 Output Formats

| Format   | Extension | Best For |
|----------|-----------|----------|
| Markdown | `.md`     | GitHub, Obsidian, Notion |
| HTML     | `.html`   | Browser viewing, printing |
| JSON     | `.json`   | Integration, further processing |
| TXT      | `.txt`    | Plain text, any editor |

All exports go to `~/SYJScholarAI-output/<action>/` by default.

---

## 🤖 AI Models

Scholar AI uses **only free and open-source models** via Ollama:

| Model | RAM | Speed | Quality | Command |
|-------|-----|-------|---------|---------|
| `gemma:2b` | 2 GB | Fast | ⭐⭐⭐ | `ollama pull gemma:2b` |
| `phi:mini` | 1.3 GB | Very Fast | ⭐⭐⭐ | `ollama pull phi:mini` |
| `tinyllama` | 0.6 GB | Fastest | ⭐⭐ | `ollama pull tinyllama` |
| `qwen:1.8b` | 1 GB | Fast | ⭐⭐⭐ | `ollama pull qwen:1.8b` |
| `phi3:mini` | 2.3 GB | Medium | ⭐⭐⭐⭐ | `ollama pull phi3:mini` |
| `mistral:7b` | 4 GB | Slower | ⭐⭐⭐⭐⭐ | `ollama pull mistral:7b` |

Switch models anytime:
```bash
scholar settings --model phi3:mini
```

**HuggingFace Fallback** — if Ollama is not available, Scholar AI automatically falls back to HuggingFace Transformers using `Qwen/Qwen1.5-0.5B-Chat` or `microsoft/phi-2`.

---

## 📁 Project Structure

```
SYJ-SCHOLAR-AI/
│
├── scholar/                    # Main Python package
│   ├── __init__.py
│   ├── core/
│   │   ├── cli.py             # Typer CLI commands
│   │   ├── config.py          # App configuration (Pydantic)
│   │   ├── database.py        # SQLite session & cache store
│   │   ├── plugins.py         # Plugin loader
│   │   └── updater.py         # Self-update via GitHub
│   │
│   ├── ai/
│   │   ├── engine.py          # Central AI orchestrator
│   │   ├── ollama_provider.py # Ollama REST integration
│   │   ├── hf_provider.py     # HuggingFace fallback
│   │   └── prompts.py         # All prompt templates
│   │
│   ├── pdf/
│   │   └── reader.py          # PyMuPDF → pdfplumber → OCR pipeline
│   │
│   ├── exports/
│   │   └── exporter.py        # MD / TXT / JSON / HTML export
│   │
│   ├── ui/
│   │   ├── dashboard.py       # Interactive Rich terminal dashboard
│   │   ├── renderer.py        # Per-action result rendering
│   │   ├── progress.py        # Spinner/progress context manager
│   │   └── theme.py           # Rich colour theme
│   │
│   ├── flashcards/            # Flashcard utilities + Anki export
│   ├── notes/                 # Note formatting helpers
│   ├── quiz/                  # Quiz scoring utilities
│   ├── exam/                  # Exam prep helpers
│   └── utils/
│       ├── helpers.py         # Text processing utilities
│       ├── logger.py          # Loguru configuration
│       └── paths.py           # XDG-compatible path helpers
│
├── tests/                     # pytest test suite
│   ├── test_helpers.py
│   ├── test_database.py
│   └── test_prompts.py
│
├── plugins/
│   └── example_plugin/
│       └── plugin.py          # Plugin template
│
├── docs/                      # Extended documentation
├── main.py                    # CLI entry point
├── install.sh                 # One-line installer
├── requirements.txt
├── setup.py
├── LICENSE                    # MIT
└── README.md
```

---

## 🧩 Plugin System

Extend Scholar AI with community plugins:

```python
# ~/.local/share/SYJScholarAI/plugins/my_plugin/plugin.py

import typer
from rich.console import Console

PLUGIN_NAME = "my-plugin"

def register(app: typer.Typer) -> None:
    @app.command("my-command", help="My custom Scholar AI command")
    def my_cmd(pdf: Path = typer.Argument(...)):
        ...
```

Plugins are auto-discovered on startup. Drop a folder in
`~/.local/share/SYJScholarAI/plugins/` and restart `scholar`.

---

## 🛠️ Development

```bash
# Clone
git clone https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI.git
cd SYJ-SCHOLAR-AI

# Create venv
python3 -m venv .venv && source .venv/bin/activate

# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check scholar/

# Format
black scholar/
```

---

## 🗺️ Roadmap

- [ ] v1.1 — Anki `.apkg` export for flashcards
- [ ] v1.2 — Interactive quiz mode (test yourself in terminal)
- [ ] v1.3 — Multi-PDF study sessions
- [ ] v1.4 — Arabic / Urdu / Persian language support
- [ ] v1.5 — Voice output via eSpeak (Termux)
- [ ] v2.0 — Web UI via FastAPI (local server)

---

## 🤝 Contributing

Contributions are warmly welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push and open a Pull Request

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Free forever. Open forever. Study hard! 🎓

---

<div align="center">

Made with ❤️ for students everywhere

**[⭐ Star on GitHub](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/)** · **[🐛 Report Bug](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues)** · **[💡 Request Feature](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues)**

</div>
