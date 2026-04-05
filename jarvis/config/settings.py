from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "JARVIS PRO"
    wake_word: str = "jarvis"
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    personality: str = (
        "You are JARVIS PRO: smart, confident, slightly witty. "
        "Keep replies short but meaningful."
    )

    always_listening: bool = True
    listen_timeout_sec: int = 5
    phrase_time_limit_sec: int = 12
    ambient_adjust_sec: float = 0.4

    log_path: Path = Path(os.getenv("JARVIS_LOG_PATH", "jarvis.log"))
    screenshots_dir: Path = Path(os.getenv("JARVIS_SCREENSHOTS_DIR", "artifacts/screenshots"))
    projects_root: Path = Path(os.getenv("JARVIS_PROJECTS_ROOT", str(Path.home() / "projects")))
    inrt_wallet_path: Path = Path(os.getenv("INRT_WALLET_PATH", str(Path.home() / "projects/INRT-Wallet")))

    ask_confirmation_for: tuple[str, ...] = (
        "shutdown",
        "restart",
        "lock",
        "delete",
        "format_drive",
    )

    dry_run: bool = os.getenv("JARVIS_DRY_RUN", "false").lower() == "true"


SETTINGS = Settings()
