# AI Models Guide

SYJ Scholar AI works entirely with **free, open-source AI models**.
No API keys. No subscriptions. No data sent to third-party servers.

---

## Quick Decision Chart

```
Your device RAM?
├── < 1 GB  → tinyllama       (0.6 GB, minimal quality)
├── 1–2 GB  → phi:mini        (1.3 GB, great quality)  ← Best for budget phones
├── 2–4 GB  → gemma:2b        (2.0 GB, excellent)      ← Recommended default
│            phi3:mini        (2.3 GB, excellent)
└── 4+ GB   → mistral:7b      (4.1 GB, best quality)
```

---

## Recommended Models

### 1. `gemma:2b` — Recommended Default
| | |
|--|--|
| **Developer** | Google DeepMind |
| **Parameters** | 2 billion |
| **RAM needed** | ~2 GB |
| **Speed** | Fast (10–30s per action on mid-range phone) |
| **Quality** | ⭐⭐⭐⭐ |
| **Best for** | All study actions |

```bash
ollama pull gemma:2b
scholar settings --model gemma:2b
```

---

### 2. `phi:mini` — Best Budget Option
| | |
|--|--|
| **Developer** | Microsoft |
| **Parameters** | 3.8 billion (quantised to ~1.3 GB) |
| **RAM needed** | ~1.5 GB |
| **Speed** | Very fast |
| **Quality** | ⭐⭐⭐⭐ |
| **Best for** | Phones with limited RAM |

```bash
ollama pull phi:mini
scholar settings --model phi:mini
```

---

### 3. `phi3:mini` — High Quality Compact
| | |
|--|--|
| **Developer** | Microsoft |
| **Parameters** | 3.8 billion |
| **RAM needed** | ~2.3 GB |
| **Speed** | Medium |
| **Quality** | ⭐⭐⭐⭐⭐ |
| **Best for** | Complex academic content |

```bash
ollama pull phi3:mini
```

---

### 4. `qwen:1.8b` — Ultra Lightweight
| | |
|--|--|
| **Developer** | Alibaba |
| **Parameters** | 1.8 billion |
| **RAM needed** | ~1.0 GB |
| **Speed** | Very fast |
| **Quality** | ⭐⭐⭐ |
| **Best for** | Very low RAM devices |

```bash
ollama pull qwen:1.8b
```

---

### 5. `tinyllama` — Absolute Minimum
| | |
|--|--|
| **Developer** | TinyLlama Team |
| **Parameters** | 1.1 billion |
| **RAM needed** | ~0.6 GB |
| **Speed** | Fastest |
| **Quality** | ⭐⭐ |
| **Best for** | Emergency use, very old devices |

```bash
ollama pull tinyllama
```

---

### 6. `mistral:7b` — Best Quality
| | |
|--|--|
| **Developer** | Mistral AI |
| **Parameters** | 7 billion |
| **RAM needed** | ~4.1 GB |
| **Speed** | Slower (2–5 min on phone CPU) |
| **Quality** | ⭐⭐⭐⭐⭐ |
| **Best for** | High-quality summaries, complex subjects |

```bash
ollama pull mistral:7b
```

---

## HuggingFace Fallback Models

Used automatically when Ollama is not running.
Downloaded to `~/.cache/huggingface/` on first use.

| Model | RAM | Quality |
|-------|-----|---------|
| `Qwen/Qwen1.5-0.5B-Chat` | 0.5 GB | ⭐⭐ |
| `microsoft/phi-2`          | 1.5 GB | ⭐⭐⭐ |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 0.8 GB | ⭐⭐ |

```bash
# Install HuggingFace support
pip install transformers torch

# Change HF model
scholar settings --provider huggingface
# Edit hf_model_id in ~/.config/SYJScholarAI/config.json
```

---

## Switching Models

```bash
# Via CLI
scholar settings --model gemma2:2b

# Via interactive dashboard
scholar → Settings → Edit

# Via config file
nano ~/.config/SYJScholarAI/config.json
```

---

## Pulling Models in Termux

```bash
# Start Ollama (run once per session)
ollama serve &

# Pull a model
ollama pull gemma:2b

# List pulled models
ollama list

# Remove a model (free up space)
ollama rm tinyllama
```

---

## Troubleshooting

### "Ollama model not found locally"

```bash
ollama pull gemma:2b
```

### "Ollama not reachable"

```bash
# Start Ollama server
ollama serve &

# Or check if it's already running
curl http://localhost:11434/api/tags
```

### "Generation is very slow"

- Switch to a smaller model: `scholar settings --model tinyllama`
- Close other apps to free RAM
- Let your phone charge while studying (CPU throttles at low battery)

### "Out of memory"

```bash
ollama pull tinyllama
scholar settings --model tinyllama
```

### "JSON parse error"

The model returned non-JSON output. This is rare but can happen with very small models.
Try `--no-cache` to regenerate, or switch to a larger model.

---

## Tips for Best Results

1. **Match model to content complexity**: simple flashcards → tinyllama; full study package → phi3:mini
2. **Use `--no-cache` if a result is poor**: forces a fresh generation
3. **Temperature 0.2–0.4 works best** for structured study material (default is 0.3)
4. **Max tokens 1024–2048** covers most study outputs without slowdown

```bash
# Advanced: edit config directly for fine-tuning
nano ~/.config/SYJScholarAI/config.json
```
