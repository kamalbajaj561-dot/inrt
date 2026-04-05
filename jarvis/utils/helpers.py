from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ActionResult:
    ok: bool
    message: str
    data: dict | None = None


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def requires_confirmation(intent: str, text: str, risky_keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return intent == "system_control" and any(keyword in lowered for keyword in risky_keywords)
