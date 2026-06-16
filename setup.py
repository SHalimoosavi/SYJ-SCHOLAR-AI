"""
SYJ Scholar AI — setup.py
Your Offline AI Study Companion
https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
req_file = this_dir / "requirements.txt"
if req_file.exists():
    for line in req_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            requirements.append(line)

setup(
    name="syj-scholar-ai",
    version="1.0.0",
    author="SHalimoosavi",
    author_email="scholar@syj.dev",
    description="Your Offline AI Study Companion — Transform PDFs into study material",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/",
    project_urls={
        "Bug Tracker": "https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/issues",
        "Documentation": "https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/wiki",
        "Source Code": "https://github.com/SHalimoosavi/SYJ-SCHOLAR-AI/",
    },
    packages=find_packages(exclude=["tests*", "docs*", "plugins*"]),
    include_package_data=True,
    package_data={
        "scholar": [
            "ui/templates/*.html",
            "ui/assets/*.css",
        ],
    },
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "black>=24.0.0",
            "ruff>=0.4.0",
            "mypy>=1.10.0",
        ],
        "ocr": [
            "pytesseract>=0.3.10",
            "pdf2image>=1.17.0",
        ],
        "hf": [
            "transformers>=4.40.0",
            "torch>=2.3.0",
            "sentencepiece>=0.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Main dashboard launcher
            "scholar=main:app",
            # Subcommand aliases for power users
            "scholar-summarize=scholar.core.cli:summarize_cmd",
            "scholar-notes=scholar.core.cli:notes_cmd",
            "scholar-flashcards=scholar.core.cli:flashcards_cmd",
            "scholar-quiz=scholar.core.cli:quiz_cmd",
            "scholar-exam=scholar.core.cli:exam_cmd",
            "scholar-study=scholar.core.cli:study_cmd",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Android",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    keywords=[
        "study", "ai", "pdf", "termux", "android", "offline",
        "flashcards", "quiz", "notes", "summarizer", "education",
        "ollama", "llm", "open-source",
    ],
    license="MIT",
    zip_safe=False,
)
