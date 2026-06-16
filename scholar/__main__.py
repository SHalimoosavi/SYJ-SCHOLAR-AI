"""
scholar/__main__.py
Enables:  python -m scholar  (used by the install.sh shell wrapper)
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path when run as a module
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app  # noqa: E402

if __name__ == "__main__":
    app()
