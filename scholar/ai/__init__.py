"""scholar.ai — AI engine and provider abstractions."""
from .engine import AIEngine
from .ollama_provider import OllamaProvider
from .hf_provider import HuggingFaceProvider

__all__ = ["AIEngine", "OllamaProvider", "HuggingFaceProvider"]
