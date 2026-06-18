<div align="center">

```
 ███████╗██╗   ██╗     ██╗    ███████╗ ██████╗██╗  ██╗ ██████╗ ██╗      █████╗ ██████╗
 ██╔════╝╚██╗ ██╔╝     ██║    ██╔════╝██╔════╝██║  ██║██╔═══██╗██║     ██╔══██╗██╔══██╗
 ███████╗ ╚████╔╝      ██║    ███████╗██║     ███████║██║   ██║██║     ███████║██████╔╝
 ╚════██║  ╚██╔╝  ██   ██║    ╚════██║██║     ██╔══██║██║   ██║██║     ██╔══██║██╔══██╗
 ███████║   ██║   ╚█████╔╝    ███████║╚██████╗██║  ██║╚██████╔╝███████╗██║  ██║██║  ██║
 ╚══════╝   ╚═╝    ╚════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

### Your Offline AI Study Companion — Built for Android. Owned by No One but You.

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![Termux Ready](https://img.shields.io/badge/Termux-Ready-orange.svg)](https://termux.dev)
[![Offline First](https://img.shields.io/badge/offline-first-purple.svg)](#)
[![GitHub Stars](https://img.shields.io/github/stars/SHalimoosavi/SYJ-SCHOLAR-AI?style=social)](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI)
[![Author](https://img.shields.io/badge/author-Syed%20Ali%20Hasan%20Moosavi-blueviolet)](https://github.com/SHalimoosavi)

*Free. Open-Source. Offline. Built for the phone in your pocket, not the laptop you don't own.*

</div>

---

## Why I Built This

I've spent enough years writing software to know that most "AI study tools" are solving a problem rich students never had. A subscription here, a cloud API key there, a Wi-Fi requirement baked in by people who never once asked what happens when a student has none of those things.

**SYJ Scholar AI** doesn't make that assumption. Hand it a PDF, and it gives you back summaries, structured notes, flashcards, and full quizzes — generated entirely on-device, with an open-source model running inside Termux on an Android phone. No subscription. No cloud round-trip. No data leaving the device, because there's nowhere for it to go.

If you've used "premium" study apps that gatekeep flashcards behind a paywall, you'll understand why this exists.

---

## The Problem, Plainly Stated

| What students actually face | What Scholar AI does about it |
|---|---|
| A pile of PDFs and not enough hours | Instant chapter-level or full-document summaries |
| AI subscriptions that don't fit a student budget | Free, open-source, forever — no tier, no upsell |
| Unreliable or no internet at exam time | Fully offline after a one-time model download |
| Five different apps for notes, cards, and quizzes | One CLI, one workflow, zero app-switching |
| No laptop, only a phone | Native Termux/Android-first design, not a port |
| Exam anxiety from not knowing what's coming | AI-generated likely questions and revision checklists |

---

## Get Running in Under Two Minutes

### One-Line Install — Termux & Linux

```bash
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash
```

Then:

```bash
scholar
```

That's the whole onboarding. No account creation, no email, no "verify your card to start your free trial."

---

## Termux Setup — Step by Step

```bash
# 1 — Install Termux from F-Droid (not the outdated Play Store build)
#     https://f-droid.org/packages/com.termux/

# 2 — Update packages
pkg update && pkg upgrade -y

# 3 — Install Scholar AI
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash

# 4 — Install Ollama, the local AI engine
pkg install ollama

# 5 — Start Ollama and pull a model sized to your device
ollama serve &
ollama pull gemma:2b      # Recommended — fast, ~2GB RAM
# ollama pull phi:mini    # Lighter — ~1.3GB RAM
# ollama pull tinyllama   # Minimal — ~0.6GB RAM

# 6 — Launch
scholar
```

---

## Desktop / Linux Install

```bash
sudo apt install python3 python3-pip tesseract-ocr git

git clone https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI.git
cd SYJ-SCHOLAR-AI

pip install -r requirements.txt

python scholar.py
```

---

## What's Inside

- **PDF Ingestion** — feed it any PDF; text extraction and OCR are handled automatically
- **Smart Summaries** — clean, bullet-point summaries by chapter or full document
- **Flashcard Generator** — auto-built Q&A cards pulled from the document's key concepts
- **Quiz Mode** — interactive MCQ and short-answer testing with live scoring
- **Study Notes** — structured notes with headings, definitions, and worked examples
- **Exam Prep** — likely questions, revision checklists, and last-mile prep guidance
- **100% Offline** — every byte of processing happens on-device after the initial model pull
- **Mobile-First CLI** — built and tuned for a Termux keyboard on a small screen, not adapted to it after the fact

---

## Under the Hood

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

No magic, no hidden binaries phoning home. Read the code — that's the entire point of open source.

---

## Pick a Model for Your Hardware

| Model | RAM Needed | Speed | Best For |
|---|---|---|---|
| `gemma:2b` | ~2 GB | ⚡⚡⚡ | Recommended default |
| `phi:mini` | ~1.3 GB | ⚡⚡⚡⚡ | Lightweight devices |
| `tinyllama` | ~0.6 GB | ⚡⚡⚡⚡⚡ | Very low-RAM phones |
| `llama3:8b` | ~5 GB | ⚡⚡ | Higher-quality output |
| `mistral:7b` | ~4.5 GB | ⚡⚡ | Best reasoning |

If you're not sure, start with `gemma:2b`. It's the sane default for a reason.

---

## Where This Is Headed

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

## Contributing

I welcome contributions, particularly from people who build mobile-first and understand what "offline-first" actually costs in engineering effort.

```bash
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
```

Open an issue before a large PR — let's agree on direction before either of us spends a weekend on it.

---

## Author & Developer

<div align="center">

**Syed Ali Hasan Moosavi**
Founder & Managing Director — Sayanjali Nexus Private Limited
Automation Engineer · Open-Source Developer · Termux Power User

[![GitHub](https://img.shields.io/badge/GitHub-SHalimoosavi-181717?logo=github)](https://github.com/SHalimoosavi)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://www.linkedin.com/in/syed-ali-hasan-moosavi-237734378/)
[![Twitter/X](https://img.shields.io/badge/X-@SHAliMoosavi-000000?logo=x)](https://x.com/SHAliMoosavi)
[![Portfolio](https://img.shields.io/badge/Portfolio-moosavi-orange)](https://shalimoosavi.github.io/moosavi/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Message-25D366?logo=whatsapp)](https://wa.me/918008123605)

> *I build everything from an Android phone in Termux. If software runs cleanly on constrained hardware, it'll run anywhere — that's not a limitation, it's a stress test I choose to run on myself.*

</div>

---

## More From This Workshop

Every project below shares the same philosophy: **Termux-first, mobile-capable, zero-cost infrastructure.** I don't build things that need a data center to prove a point.

### [SAYANJALI OSINT](https://github.com/SHalimoosavi/sayanjali-osint)
**Geolocation Intelligence Framework for Android**
A lightweight OSINT geolocation framework built specifically for Termux — for security researchers, bug bounty hunters, and CTF players who work from a phone, not a rack.
`Python` · `OSINT` · `Geolocation` · `Termux` · `Security Research`

### [SYJ ONE](https://github.com/SHalimoosavi/syj-one)
**All-in-One Termux Productivity Platform**
A unified CLI replacing a dozen separate tools — automation, SEO analysis, security scanning, and developer utilities, all in one place on Android.
`Python` · `CLI` · `Productivity` · `SEO` · `Security` · `Automation`

### [termux-pro](https://github.com/SHalimoosavi/termux-pro)
**TERMUX ZERO → PRO Guide**
The reference guide for turning a bare Termux install into a full Android Dev + Ethical Hacking + AI Lab. Written for people who learn by doing, not by watching a 4-hour video.
`HTML` · `Termux` · `Android` · `DevGuide` · `AI` · `Hacking`

### [podcaster_crew](https://github.com/SHalimoosavi/podcaster_crew)
**Multi-Agent AI Podcast System**
A crewAI-powered multi-agent template where AI agents plan, research, and produce podcast-style content autonomously — built for N8N and API-driven pipelines.
`Python` · `crewAI` · `Multi-Agent` · `AI Automation` · `Podcast`

### [moosavi (Portfolio)](https://github.com/SHalimoosavi/moosavi)
**Personal Developer Portfolio & Authority Site**
The professional home base — covering N8N pipelines, API systems, GitHub Actions, AI agents, and Web3 operations.
`HTML` · `Portfolio` · `GitHub Pages` · `Web3` · `Automation`

### [antigravity-awesome-skills](https://github.com/SHalimoosavi/antigravity-awesome-skills)
**Agentic Skills Library for Claude Code, Cursor & More**
A curated, installable library of 1,400+ agentic skills for Claude Code, Cursor, Codex CLI, Gemini CLI, and Antigravity — complete with installer CLI, bundles, and workflows.
`Python` · `Claude Code` · `Cursor` · `AI Skills` · `Agentic` · `Open Source`

---

## GitHub Stats

<div align="center">

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=SHalimoosavi&show_icons=true&theme=tokyonight&hide_border=true)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=SHalimoosavi&layout=compact&theme=tokyonight&hide_border=true)

</div>

---

## License

MIT License — see [LICENSE](LICENSE).

Free to use, modify, and distribute. Attribution appreciated. Never required. That's not generosity, that's just what open source means.

---

<div align="center">

**Built with discipline, from an Android phone, in Hyderabad, India.**

*Sayanjali Nexus Private Limited © 2026*

[⭐ Star this repo](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI) · [🐛 Report a Bug](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues) · [💡 Request a Feature](https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues/new)

</div>
