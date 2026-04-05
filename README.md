# JARVIS PRO

JARVIS PRO is a modular Python assistant with voice + CLI control, task routing, coding-agent workflows, and CEO-style business guidance for **INRT Wallet**.

## Features

- Wake-word flow (`jarvis`) with always-listening voice mode
- Intent routing (`whatsapp`, `open_app`, `search`, `play`, `system_control`, `coding`, `business`, `general_chat`)
- Groq-backed response generation (Llama-family model) with local fallback
- WhatsApp automation through desktop app workflow (not WhatsApp Web)
- System controls with safety guardrails
- Coding agent actions for INRT Wallet (open project, run dev server, debug and architecture guidance)
- Business advisor mode for startup strategy and monetization ideas
- Action logging with rotating file output

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

Set optional environment variables:

```bash
export GROQ_API_KEY="your_key"
export GROQ_MODEL="llama-3.3-70b-versatile"
export INRT_WALLET_PATH="$HOME/projects/INRT-Wallet"
```

## Usage

CLI mode:

```bash
python main.py --mode cli --command "open my project"
python main.py --mode cli --command "fix my wallet app error"
python main.py --mode cli --command "give me growth ideas for INRT"
```

Voice mode:

```bash
python main.py --mode voice
```

Say wake-word **jarvis**, then command.

## Safety model

- High-risk system actions require explicit CLI confirmation (`--confirm`)
- All actions are logged to `jarvis.log`
- Exceptions are handled gracefully with clear error responses

## Notes

- WhatsApp automation relies on local GUI automation (`pyautogui`) and an installed app binary.
- Some system commands are Linux oriented; adapt for your OS where needed.
