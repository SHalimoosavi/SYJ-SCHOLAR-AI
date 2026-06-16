#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  SYJ Scholar AI — Installer
#  Your Offline AI Study Companion
#  https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/
#
#  Usage (one-line):
#    curl -fsSL https://raw.githubusercontent.com/SHalimoosavi/SYJ-SCHOLAR-AI/main/install.sh | bash
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()   { echo -e "${CYAN}${BOLD}[Scholar AI]${RESET} $*"; }
ok()    { echo -e "${GREEN}${BOLD}[✓]${RESET} $*"; }
warn()  { echo -e "${YELLOW}${BOLD}[!]${RESET} $*"; }
error() { echo -e "${RED}${BOLD}[✗]${RESET} $*" >&2; }
die()   { error "$*"; exit 1; }

# ── Banner ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}"
cat << 'EOF'
 ██████╗ ██████╗ ██╗  ██╗ ██████╗ ██╗      █████╗ ██████╗      █████╗ ██╗
██╔════╝██╔════╝ ██║  ██║██╔═══██╗██║     ██╔══██╗██╔══██╗    ██╔══██╗██║
╚█████╗ ╚█████╗  ███████║██║   ██║██║     ███████║██████╔╝    ███████║██║
 ╚═══██╗ ╚═══██╗ ██╔══██║██║   ██║██║     ██╔══██║██╔══██╗    ██╔══██║██║
██████╔╝██████╔╝ ██║  ██║╚██████╔╝███████╗██║  ██║██║  ██║    ██║  ██║██║
╚═════╝ ╚═════╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝
EOF
echo -e "${RESET}"
echo -e "  ${BOLD}Your Offline AI Study Companion${RESET}"
echo -e "  ${CYAN}https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/${RESET}"
echo ""

# ── Detect environment ────────────────────────────────────────────────────────
IS_TERMUX=false
if [[ -n "${TERMUX_VERSION:-}" ]] || [[ "${PREFIX:-}" == *"termux"* ]]; then
    IS_TERMUX=true
    log "Termux environment detected 📱"
else
    log "Linux/Desktop environment detected 🖥"
fi

# ── Package manager helpers ───────────────────────────────────────────────────
install_pkg() {
    if $IS_TERMUX; then
        pkg install -y "$@"
    elif command -v apt-get &>/dev/null; then
        sudo apt-get install -y "$@"
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y "$@"
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm "$@"
    else
        warn "Cannot auto-install $*. Please install manually."
    fi
}

pip_install() {
    if $IS_TERMUX; then
        pip install --quiet "$@"
    else
        pip install --quiet --user "$@"
    fi
}

# ── Step 1: Python ────────────────────────────────────────────────────────────
log "Step 1/7: Checking Python …"
if ! command -v python3 &>/dev/null; then
    warn "Python3 not found. Installing …"
    if $IS_TERMUX; then
        pkg install -y python
    else
        install_pkg python3 python3-pip
    fi
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log "Python ${PYTHON_VERSION} found."

if python3 -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)"; then
    ok "Python version OK (≥ 3.9)"
else
    die "Python 3.9+ required. Found ${PYTHON_VERSION}."
fi

# ── Step 2: pip ───────────────────────────────────────────────────────────────
log "Step 2/7: Checking pip …"
if ! command -v pip &>/dev/null && ! python3 -m pip --version &>/dev/null 2>&1; then
    warn "pip not found. Installing …"
    if $IS_TERMUX; then
        pkg install -y python
    else
        python3 -m ensurepip --upgrade
    fi
fi
ok "pip ready"

# ── Step 3: System deps (Termux) ──────────────────────────────────────────────
log "Step 3/7: Installing system dependencies …"
if $IS_TERMUX; then
    pkg install -y \
        git curl wget \
        tesseract \
        poppler \
        clang \
        libjpeg-turbo \
        libpng \
        zlib \
        2>/dev/null || warn "Some Termux packages may have failed — continuing …"
    ok "Termux packages installed"
else
    # Minimal check for tesseract on desktop
    if ! command -v tesseract &>/dev/null; then
        warn "Tesseract OCR not found. Installing …"
        install_pkg tesseract-ocr tesseract-ocr-eng
    fi
    ok "System packages ready"
fi

# ── Step 4: Clone / update repo ───────────────────────────────────────────────
log "Step 4/7: Setting up SYJ Scholar AI source …"
INSTALL_DIR="${HOME}/.local/opt/syj-scholar-ai"

if [[ -d "${INSTALL_DIR}/.git" ]]; then
    log "Updating existing installation …"
    git -C "${INSTALL_DIR}" pull --ff-only 2>/dev/null || warn "git pull failed — using existing version"
else
    log "Cloning repository …"
    git clone --depth 1 \
        https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI.git \
        "${INSTALL_DIR}" 2>/dev/null || {
        warn "git clone failed. Falling back to pip install …"
        INSTALL_DIR=""
    }
fi

# ── Step 5: Install Python packages ──────────────────────────────────────────
log "Step 5/7: Installing Python dependencies …"

if $IS_TERMUX; then
    # On Termux we need --break-system-packages for pip ≥ 23
    PIP_EXTRA="--break-system-packages"
else
    PIP_EXTRA="--user"
fi

# Core deps always installed
python3 -m pip install ${PIP_EXTRA} --quiet \
    rich click typer prompt_toolkit \
    PyMuPDF pdfplumber pypdf \
    Pillow pytesseract \
    ollama requests httpx \
    pydantic python-dotenv loguru tqdm \
    platformdirs packaging markdown jinja2

ok "Core Python packages installed"

# Optional: HuggingFace (larger — ask user)
echo ""
read -r -p "$(echo -e "${CYAN}Install HuggingFace Transformers (offline fallback AI)? [y/N]: ${RESET}")" HF_CHOICE
if [[ "${HF_CHOICE:-N}" =~ ^[Yy]$ ]]; then
    python3 -m pip install ${PIP_EXTRA} --quiet \
        huggingface-hub transformers 2>/dev/null \
        && ok "HuggingFace Transformers installed" \
        || warn "HF install failed — Ollama will be used as primary provider"
fi

# ── Step 6: Install Scholar AI itself ─────────────────────────────────────────
log "Step 6/7: Installing SYJ Scholar AI …"
if [[ -n "${INSTALL_DIR}" && -f "${INSTALL_DIR}/setup.py" ]]; then
    python3 -m pip install ${PIP_EXTRA} --quiet -e "${INSTALL_DIR}"
    ok "Scholar AI installed in editable mode from ${INSTALL_DIR}"
else
    python3 -m pip install ${PIP_EXTRA} --quiet \
        git+https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI.git \
        && ok "Scholar AI installed via pip"
fi

# ── Step 7: Create `scholar` shell alias / wrapper ────────────────────────────
log "Step 7/7: Creating 'scholar' command …"

if $IS_TERMUX; then
    BIN_DIR="${PREFIX}/bin"
else
    BIN_DIR="${HOME}/.local/bin"
    mkdir -p "${BIN_DIR}"
fi

# Check if 'scholar' entry point landed on PATH
if command -v scholar &>/dev/null; then
    ok "'scholar' command is available"
else
    # Write a thin wrapper
    WRAPPER="${BIN_DIR}/scholar"
    cat > "${WRAPPER}" << WRAPPER_EOF
#!/usr/bin/env bash
exec python3 -m scholar.main "\$@"
WRAPPER_EOF
    chmod +x "${WRAPPER}"
    ok "Created wrapper: ${WRAPPER}"
fi

# ── Ollama recommendation ─────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Recommended: Install Ollama for offline AI"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
if $IS_TERMUX; then
    echo -e "  ${CYAN}Termux:${RESET} pkg install ollama"
    echo -e "  Then:   ${CYAN}ollama serve &${RESET}"
    echo -e "          ${CYAN}ollama pull gemma:2b${RESET}"
else
    echo -e "  ${CYAN}curl -fsSL https://ollama.com/install.sh | sh${RESET}"
    echo -e "  Then:   ${CYAN}ollama pull gemma:2b${RESET}"
fi
echo ""

# ── Done ──────────────────────────────────────────────────────────────────────
echo -e "${GREEN}${BOLD}"
echo "  ╔════════════════════════════════════════╗"
echo "  ║   SYJ Scholar AI installed! 🎓         ║"
echo "  ║   Run:  scholar                        ║"
echo "  ║   Help: scholar --help                 ║"
echo "  ╚════════════════════════════════════════╝"
echo -e "${RESET}"

# Auto-launch if interactive
if [[ -t 0 ]]; then
    read -r -p "$(echo -e "${CYAN}Launch Scholar AI now? [Y/n]: ${RESET}")" LAUNCH
    if [[ ! "${LAUNCH:-Y}" =~ ^[Nn]$ ]]; then
        exec scholar
    fi
fi
