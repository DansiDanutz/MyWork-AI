# 🤖 AI Features Guide

MyWork-AI includes a full suite of AI-powered development tools accessible via `mw ai`.

## Quick Start

```bash
# Ask a coding question
mw ai ask "How do I handle async errors in Python?"

# Generate a file from description
mw ai generate api/auth.py "FastAPI auth endpoint with JWT tokens"

# Review your staged changes
mw ai review --staged
```

## Commands

### Code Generation & Editing

| Command | Description |
|---------|-------------|
| `mw ai generate <file> "desc"` | Generate a complete file from a natural language description |
| `mw ai fix <file>` | Detect and fix bugs in a file |
| `mw ai fix --diff` | Review your git diff for issues |
| `mw ai refactor <file>` | Get refactoring suggestions with optional `--focus` area |
| `mw ai optimize <file\|dir>` | Find performance improvements |

### Code Understanding

| Command | Description |
|---------|-------------|
| `mw ai ask "question"` | Ask any coding question |
| `mw ai explain <file>` | Explain what code does (use `--lines 10-50` for specific ranges) |
| `mw ai doc <file>` | Generate documentation (`--readme` for README format) |

### Git Integration

| Command | Description |
|---------|-------------|
| `mw ai commit` | Auto-generate a commit message from staged changes |
| `mw ai commit --push` | Commit and push in one step |
| `mw ai review` | AI code review of changes (`--staged` or `--branch main`) |
| `mw ai changelog` | Generate changelog from recent commits |

### Testing

| Command | Description |
|---------|-------------|
| `mw ai test <file>` | Generate unit tests (`--framework pytest\|jest\|mocha`) |

### Interactive Chat

```bash
# Start a chat session (default: DeepSeek)
mw ai chat

# Use a specific model
mw ai chat --model gemini
mw ai chat --model claude
```

## Supported Providers

MyWork-AI auto-detects configured API keys from your environment:

| Provider | Models | Env Variable |
|----------|--------|-------------|
| **DeepSeek** (default) | deepseek-chat, deepseek-coder | `DEEPSEEK_API_KEY` |
| **OpenRouter** | 100+ models (Claude, GPT, Gemini, etc.) | `OPENROUTER_API_KEY` |
| **OpenAI** | GPT-4, GPT-4o | `OPENAI_API_KEY` |
| **Google Gemini** | gemini-2.5-pro, gemini-2.5-flash | `GOOGLE_API_KEY` |

## Model Shortcuts

Use these shortcuts with `--model`:

- `deepseek` → DeepSeek Chat (fastest, cheapest)
- `claude` → Claude via OpenRouter
- `gpt4` → GPT-4o via OpenRouter
- `gemini` → Gemini 2.5 Flash
- `gemini-pro` → Gemini 2.5 Pro
- `kimi` → Kimi K2 via OpenRouter
- `llama` → Llama via OpenRouter

## Examples

```bash
# Fix a bug with error context
mw ai fix src/api.py --error "TypeError: NoneType has no attribute 'get'"

# Generate tests for a module
mw ai test tools/brain.py --framework pytest

# Explain specific lines
mw ai explain tools/mw.py --lines 100-150

# Full code review against main branch
mw ai review --branch main
```

## Configuration

AI features work out of the box with any configured API key. Set your preferred provider in `.env`:

```bash
DEEPSEEK_API_KEY=sk-xxx        # Recommended: fast and cheap
OPENROUTER_API_KEY=sk-or-xxx   # Most models available
```
