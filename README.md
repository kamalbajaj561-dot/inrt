# JARVIS PRO

A modular, production-ready Python assistant for voice control, automation, coding support, and startup strategy workflows.

## Core pipeline

`Voice → Command → Rule-based intent override → AI intent fallback → Action router → Execution → Smart response`

## Key improvements

- Hybrid intent detection with strict hard-rule priority and AI fallback
- Better natural-language routing for WhatsApp, app opening, coding tasks, and business prompts
- No generic dead-end replies; assistant asks clarifying questions when needed
- INRT Wallet coding-agent actions: open project, run project, fix error guidance, analyze code
- Safer system control with explicit risky-action confirmation
- Voice tuning (`pause_threshold=1`, `energy_threshold=250`) with retry-on-failure

## Project structure

```
jarvis/
├── main.py
├── voice/
│   ├── listen.py
│   └── speak.py
├── ai/
│   ├── brain.py
│   ├── intent.py
│   └── memory.py
├── actions/
│   ├── whatsapp.py
│   ├── system.py
│   ├── apps.py
│   ├── web.py
│   ├── coding_agent.py
│   └── business_agent.py
├── config/
│   ├── settings.py
│   ├── contacts.py
│   └── websites.py
└── utils/
    ├── logger.py
    └── helpers.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional configuration:

```bash
export GROQ_API_KEY="your_key"
export GROQ_MODEL="llama-3.3-70b-versatile"
export INRT_WALLET_PATH="$HOME/projects/INRT-Wallet"
```

## Usage

CLI mode:

```bash
python main.py --mode cli --command "open my project"
python main.py --mode cli --command "run my project"
python main.py --mode cli --command "tell Rahul I will call later"
```

Voice mode:

```bash
python main.py --mode voice
```

Say wake word: **jarvis**.

## Safety

- Dangerous actions (shutdown/restart/lock) are confirmation-gated.
- Errors are caught and returned as friendly messages.
- Logs are written to `jarvis.log`.
