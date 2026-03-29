# Local Voice Assistant (JARVIS-style, privacy-first + knowledgeable Q&A)

This project provides a **voice-enabled local assistant** that helps with coding, app management, and technical Q&A while keeping you in control.

## Security first

A system with "complete control" is risky. This implementation intentionally adds guardrails:

- No hardcoded API keys
- Explicit confirmation for risky actions
- Allowlisted command execution (no arbitrary shell access)
- Workspace-restricted file operations
- Audit log of every action

## Knowledge features

- `jarvis ask <question>` for architecture/debugging/coding Q&A
- `jarvis summarize file <path>` to explain a file
- Lightweight conversation memory
- Optional OpenAI-compatible backend for richer reasoning
- Local fallback mode if no API key is configured

## Modes

- **Voice mode** (default): microphone + TTS
- **Text mode**: easy to test and debug from terminal

## Quick start

1. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure your workspace path and allowlisted commands in `jarvis_assistant.py`.

3. Set environment variables (recommended, do not paste keys into source files):

```bash
export OPENAI_API_KEY="your_key_here"
export OPENAI_MODEL="gpt-4.1-mini"
# optional:
# export OPENAI_BASE_URL="https://api.openai.com/v1"
```

4. Run:

```bash
# voice mode
python jarvis_assistant.py

# text mode
python jarvis_assistant.py --text

# one-off command
python jarvis_assistant.py --text --once "jarvis ask how to optimize postgres indexes"
```

## Example commands

- `jarvis ask why is my API timing out`
- `jarvis summarize file src/main.py`
- `jarvis open file src/main.py`
- `jarvis run tests`
- `jarvis start app`
- `jarvis stop app`

## Disclaimer

Use responsibly and only on systems you own or are authorized to manage.
