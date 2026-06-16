<div align="center">

```
 ███████╗██╗   ██╗     ██╗    ███████╗ ██████╗██╗  ██╗ ██████╗ ██╗      █████╗ ██████╗
 ██╔════╝╚██╗ ██╔╝     ██║    ██╔════╝██╔════╝██║  ██║██╔═══██╗██║     ██╔══██╗██╔══██╗
 ███████╗ ╚████╔╝      ██║    ███████╗██║     ███████║██║   ██║██║     ███████║██████╔╝
 ╚════██║  ╚██╔╝  ██   ██║    ╚════██║██║     ██╔══██║██║   ██║██║     ██╔══██║██╔══██╗
 ███████║   ██║   ╚█████╔╝    ███████║╚██████╗██║  ██║╚██████╔╝███████╗██║  ██║██║  ██║
 ╚══════╝   ╚═╝    ╚════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

### Your Offline AI Study Companion — Built for Android · Powered by Open-Source LLMs

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![Termux Ready](https://img.shields.io/badge/Termux-Ready-orange.svg)](https://termux.dev)
[![Offline First](https://img.shields.io/badge/offline-first-purple.svg)](#)
[![GitHub Stars](https://img.shields.io/github/stars/SHalimoosavi/SYJ-SCHOLAR-AI?style=social)](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI)
[![Author](https://img.shields.io/badge/author-Syed%20Ali%20Hasan%20Moosavi-blueviolet)](https://github.com/SHalimoosavi)

*Free · Open-Source · Offline · Mobile-First*

</div>

---

## 🎯 What is SYJ Scholar AI?

**SYJ Scholar AI** transforms any PDF into a complete study package — summaries, notes, flashcards, quizzes, and exam prep — all powered by **free, open-source AI** running entirely on your Android phone through **Termux**.

> No subscriptions. No internet required after setup. No data leaves your device. Ever.

Built by a developer who codes from an Android phone, for every student who can't afford a laptop or a cloud AI plan.

---

## 😩 The Problem It Solves

| Challenge | How Scholar AI Fixes It |
|-----------|--------------------------|
| Too many PDFs, no time | Instant summaries & key concept extraction |
| Expensive AI subscriptions | 100% free & open-source forever |
| Poor internet connectivity | Fully offline after one-time model download |
| Juggling multiple apps | One CLI tool covers notes, cards, quizzes |
| Mobile students without laptops | Built natively for Android + Termux |
| Exam prep is stressful | AI generates likely questions & checklists |

---

## ⚡ Quick Start

### One-Line Install (Termux & Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash
```

Then launch with:

```bash
scholar
```

You'll see an interactive dashboard with all options ready.

---

## 📱 Termux Setup (Step by Step)

```bash
# Step 1 — Install Termux from F-Droid (NOT Google Play)
#   https://f-droid.org/packages/com.termux/

# Step 2 — Update packages
pkg update && pkg upgrade -y

# Step 3 — Install Scholar AI
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash

# Step 4 — Install Ollama (AI engine)
pkg install ollama

# Step 5 — Start Ollama and pull a model (choose based on your device RAM)
ollama serve &
ollama pull gemma:2b      # Recommended: fast, ~2GB RAM
# ollama pull phi:mini    # Lighter: ~1.3GB RAM
# ollama pull tinyllama   # Minimal: ~0.6GB RAM

# Step 6 — Launch!
scholar
```

---

## 🖥️ Desktop / Linux Install

```bash
# Install system dependencies
sudo apt install python3 python3-pip tesseract-ocr git

# Clone the repo
git clone https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI.git
cd SYJ-SCHOLAR-AI

# Install Python dependencies
pip install -r requirements.txt

# Launch
python scholar.py
```

---

## 🧠 Features

- 📄 **PDF Ingestion** — Feed any PDF; Scholar AI handles text extraction + OCR
- 📝 **Smart Summaries** — Bullet-point summaries by chapter or full document
- 🃏 **Flashcard Generator** — Auto-generates Q&A cards from key concepts
- 📋 **Quiz Mode** — Interactive MCQ & short-answer quizzes with scoring
- 🗒️ **Study Notes** — Structured notes with headings, definitions, and examples
- 🎯 **Exam Prep** — Likely exam questions, checklists, and revision tips
- 🔒 **100% Offline** — All processing on-device after initial model pull
- 📱 **Mobile-First CLI** — Designed for Termux keyboard navigation on small screens

---

## 📁 Project Structure

```
SYJ-SCHOLAR-AI/
├── scholar.py          # Main entry point & interactive dashboard
├── install.sh          # One-line installer for Termux & Linux
├── core/
│   ├── extractor.py    # PDF text extraction + OCR pipeline
│   ├── summarizer.py   # Ollama-powered summarization
│   ├── flashcards.py   # Flashcard generation engine
│   ├── quiz.py         # Quiz generation & scoring
│   └── notes.py        # Structured notes formatter
├── models/
│   └── config.yaml     # Model selection & Ollama settings
├── requirements.txt
└── README.md
```

---

## 🤖 Supported Models

| Model | RAM Needed | Speed | Best For |
|-------|-----------|-------|----------|
| `gemma:2b` | ~2 GB | ⚡⚡⚡ | Recommended default |
| `phi:mini` | ~1.3 GB | ⚡⚡⚡⚡ | Lightweight devices |
| `tinyllama` | ~0.6 GB | ⚡⚡⚡⚡⚡ | Very low RAM |
| `llama3:8b` | ~5 GB | ⚡⚡ | High-quality output |
| `mistral:7b` | ~4.5 GB | ⚡⚡ | Best reasoning |

---

## 🛣️ Roadmap

- [x] PDF text extraction + OCR
- [x] AI-powered summaries
- [x] Flashcard generator
- [x] Quiz mode with scoring
- [ ] Export to Anki `.apkg` format
- [ ] Multi-PDF batch processing
- [ ] Voice-to-text note input (Termux:API)
- [ ] WhatsApp study bot integration
- [ ] Web UI via local Flask server

---

## 🤝 Contributing

Contributions are welcome — especially from Termux and mobile-first developers.

```bash
# Fork → Clone → Branch → PR
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
```

Please open an issue first for large changes so we can discuss the direction.

---

## 👨‍💻 Author & Developer

<div align="center">

**Syed Ali Hasan Moosavi**
*Founder & Managing Director — SAYANJALI NEXUS PRIVATE LIMITED*
*Automation Engineer · Open-Source Developer · Termux Power User*

[![GitHub](https://img.shields.io/badge/GitHub-SHalimoosavi-181717?logo=github)](https://github.com/SHalimoosavi)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://www.linkedin.com/in/syed-ali-hasan-moosavi-237734378/)
[![Twitter/X](https://img.shields.io/badge/X-@SHAliMoosavi-000000?logo=x)](https://x.com/SHAliMoosavi)
[![Portfolio](https://img.shields.io/badge/Portfolio-moosavi-orange)](https://shalimoosavi.github.io/moosavi/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Message-25D366?logo=whatsapp)](https://wa.me/918008123605)

> *"I build everything from an Android phone in Termux. If it runs on constrained hardware, it runs anywhere."*

</div>

---

## 🚀 Other Open-Source Projects by the Author

> All projects are designed with a **Termux-first** philosophy — mobile, offline-capable, zero-cost infrastructure.

---

### 🔍 [SAYANJALI OSINT](https://github.com/SHalimoosavi/sayanjali-osint)
**Geolocation Intelligence Framework for Android**

A lightweight yet powerful OSINT geolocation framework designed specifically for Termux environments. Built for security researchers, bug bounty hunters, and CTF players who work from mobile devices.

`Python` · `OSINT` · `Geolocation` · `Termux` · `Security Research`

---

### 🛠️ [SYJ ONE](https://github.com/SHalimoosavi/syj-one)
**All-in-One Termux Productivity Platform**

An open-source, all-in-one productivity · business · developer · SEO · security platform built specifically for Termux on Android. Replaces a dozen separate tools with one unified CLI experience covering automation, SEO analysis, security scanning, and developer utilities.

`Python` · `CLI` · `Productivity` · `SEO` · `Security` · `Automation`

---

### 📱 [termux-pro](https://github.com/SHalimoosavi/termux-pro)
**TERMUX ZERO → PRO Guide**

Comprehensive HTML guide and toolkit for transforming a bare Termux install into a full Android Dev + Ethical Hacking + AI Lab environment. The definitive reference for mobile developers.

`HTML` · `Termux` · `Android` · `DevGuide` · `AI` · `Hacking`

---

### 🤖 [podcaster_crew](https://github.com/SHalimoosavi/podcaster_crew)
**Multi-Agent AI Podcast System**

A multi-agent AI system template powered by crewAI, enabling collaborative AI agents to plan, research, and produce podcast-style content autonomously. Built for N8N and API-driven automation pipelines.

`Python` · `crewAI` · `Multi-Agent` · `AI Automation` · `Podcast`

---

### 🌐 [moosavi (Portfolio)](https://github.com/SHalimoosavi/moosavi)
**Personal Developer Portfolio & Authority Site**

Professional portfolio site for Syed Ali Hasan Moosavi — automation engineer, open-source developer, and founder of SAYANJALI NEXUS. Covers N8N pipelines, API systems, GitHub Actions, AI agents, and Web3 operations.

`HTML` · `Portfolio` · `GitHub Pages` · `Web3` · `Automation`

---

### 🧩 [antigravity-awesome-skills](https://github.com/SHalimoosavi/antigravity-awesome-skills)
**Agentic Skills Library for Claude Code, Cursor & More**

A curated installable library of 1,400+ agentic skills for Claude Code, Cursor, Codex CLI, Gemini CLI, Antigravity, and other AI coding environments. Includes an installer CLI, bundles, workflows, and community-contributed skill collections.

`Python` · `Claude Code` · `Cursor` · `AI Skills` · `Agentic` · `Open Source`

---

## 📊 GitHub Stats

<div align="center">

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=SHalimoosavi&show_icons=true&theme=tokyonight&hide_border=true)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=SHalimoosavi&layout=compact&theme=tokyonight&hide_border=true)

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for full details.

Free to use, modify, and distribute. Attribution appreciated but not required.

---

<div align="center">

**Built with ❤️ from an Android phone · Hyderabad, India**

*SAYANJALI NEXUS PRIVATE LIMITED © 2025*

[⭐ Star this repo](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI) · [🐛 Report a Bug](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues) · [💡 Request a Feature](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues/new)

</div>
