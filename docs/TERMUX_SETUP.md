# Termux Setup Guide

Step-by-step setup of SYJ Scholar AI on Android via Termux.

---

## Prerequisites

- Android 7.0 or later
- At least **2 GB free storage** (for app + model)
- **Termux from F-Droid** (NOT Google Play — the Play version is outdated)

> ⚠️ **Important:** Install Termux from [F-Droid](https://f-droid.org/packages/com.termux/), NOT Google Play Store. The Play version hasn't been updated since 2020 and will not work.

---

## Step 1: Install Termux

1. Download [F-Droid](https://f-droid.org/) APK on your phone
2. Install F-Droid
3. Search for **Termux** in F-Droid and install it

---

## Step 2: Update Termux Packages

Open Termux and run:

```bash
pkg update && pkg upgrade -y
```

This may take a few minutes on first run.

---

## Step 3: Install SYJ Scholar AI

```bash
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash
```

The installer will:
1. Check your Python version (installs if missing)
2. Install system packages (Tesseract OCR, etc.)
3. Clone the repository
4. Install all Python dependencies
5. Create the `scholar` command

---

## Step 4: Install Ollama (AI Engine)

```bash
# Install Ollama via Termux package manager
pkg install ollama

# Start the Ollama server (run once per Termux session)
ollama serve &

# Pull a model (choose based on your phone's RAM)
ollama pull gemma:2b        # 2 GB RAM required — recommended
# ollama pull phi:mini      # 1.5 GB RAM — lighter alternative
# ollama pull tinyllama     # 0.6 GB RAM — minimal device
```

Pulling the model downloads it to your device (~1–4 GB).
This is a one-time download. After that, everything runs offline.

---

## Step 5: Launch Scholar AI

```bash
scholar
```

You should see the interactive dashboard. 🎉

---

## Quick Reference: Per-Session Commands

Each time you open a new Termux session:

```bash
# Start Ollama (required every session)
ollama serve &

# Then use Scholar AI
scholar
# or
scholar summarize lecture.pdf
```

To avoid typing `ollama serve &` every time, add it to your Termux startup:

```bash
echo "ollama serve &" >> ~/.bashrc
```

---

## Storage and File Access

### Accessing Your Files

To process files from your phone's storage:

```bash
# Grant storage permission
termux-setup-storage

# Your phone storage is then at:
ls ~/storage/

# Common locations:
ls ~/storage/downloads/    # Downloads folder
ls ~/storage/shared/       # Internal storage
```

### Studying a PDF from Downloads

```bash
scholar summarize ~/storage/downloads/lecture.pdf
```

### Where are the outputs saved?

```
~/SYJScholarAI-output/
├── summarize/
├── notes/
├── flashcards/
├── quiz/
├── exam/
└── study/
```

---

## Termux Tips

### Keep Ollama Running in Background

```bash
# Use tmux for persistent sessions
pkg install tmux

tmux new-session -d -s scholar -c ~ "ollama serve"
```

### Wake Lock (Prevent CPU Throttling)

```bash
# Install Termux:API from F-Droid, then:
pkg install termux-api

# Acquire wake lock to prevent sleep during long generations
termux-wake-lock
scholar study big-textbook.pdf
termux-wake-unlock
```

### Check Your RAM

```bash
free -h
```

### Check Storage Space

```bash
df -h ~/
```

---

## Troubleshooting

### "command not found: scholar"

```bash
# Option 1: Re-run the installer
curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash

# Option 2: Run manually
python3 -m scholar

# Option 3: Check PATH
echo $PATH
# If ~/.local/bin is missing:
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### "Ollama not reachable"

```bash
# Make sure Ollama is running
ollama serve &

# Test it
curl http://localhost:11434/api/tags
```

### "No module named 'fitz'"

```bash
pip install PyMuPDF --break-system-packages
```

### "pytesseract not found"

```bash
pkg install tesseract
pip install pytesseract --break-system-packages
```

### "Generation is very slow"

- Use a smaller model: `scholar settings --model tinyllama`
- Plug in your phone charger (prevents CPU throttling)
- Close other apps to free RAM
- Use `pkg install termux-api && termux-wake-lock`

### "Killed" or out-of-memory crash

Your phone doesn't have enough RAM for the current model. Switch to a smaller one:

```bash
ollama rm gemma:2b
ollama pull tinyllama
scholar settings --model tinyllama
```

### OCR not working on scanned PDFs

```bash
# Install Tesseract OCR language packs
pkg install tesseract-lang

# Verify Tesseract works
tesseract --version
echo "hello world" | tesseract stdin stdout
```

### Permission denied accessing files

```bash
termux-setup-storage
# Then grant permissions in Android settings
```

---

## Recommended Termux Packages

```bash
pkg install \
  python \
  git \
  curl \
  wget \
  tesseract \
  poppler \
  tmux \
  nano \
  ollama
```

---

## Performance Benchmarks (Approximate)

| Device | Model | Action | Time |
|--------|-------|--------|------|
| Budget phone (3 GB RAM) | tinyllama | Summarize 20-page PDF | ~45s |
| Mid-range (4 GB RAM) | phi:mini | Summarize 20-page PDF | ~30s |
| Mid-range (4 GB RAM) | gemma:2b | Summarize 20-page PDF | ~40s |
| Flagship (8 GB RAM) | gemma:2b | Full study package | ~3 min |
| Flagship (8 GB RAM) | phi3:mini | Full study package | ~4 min |

---

## Uninstalling

```bash
# Remove Scholar AI
pip uninstall syj-scholar-ai --break-system-packages
rm -rf ~/.local/share/SYJScholarAI
rm -rf ~/.config/SYJScholarAI
rm -rf ~/SYJScholarAI-output

# Remove Ollama and models
pkg remove ollama
rm -rf ~/.ollama
```
