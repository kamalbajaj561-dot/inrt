from __future__ import annotations

from dataclasses import dataclass

from jarvis.utils.helpers import normalize_text

RULE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "whatsapp": ("message", "whatsapp", "text"),
    "open_app": ("open", "launch", "start"),
    "search": ("search", "google"),
    "play": ("play", "youtube"),
    "system_control": ("volume", "shutdown", "restart", "screenshot"),
    "coding": ("project", "code", "error", "fix", "app", "file"),
    "business": ("startup", "growth", "idea", "revenue"),
}

VALID_INTENTS: tuple[str, ...] = (
    "whatsapp",
    "open_app",
    "search",
    "play",
    "system_control",
    "coding",
    "business",
    "general_chat",
)


@dataclass
class IntentResult:
    intent: str
    source: str


class IntentDetector:
    """Hybrid intent detector: hard rule override, AI fallback handled by caller."""

    def detect_by_rules(self, command: str) -> IntentResult | None:
        text = normalize_text(command)
        matches: list[str] = []
        for intent, words in RULE_KEYWORDS.items():
            if any(word in text for word in words):
                matches.append(intent)

        if not matches:
            return None

        priority = ["whatsapp", "system_control", "coding", "search", "play", "open_app", "business"]
        for intent in priority:
            if intent in matches:
                return IntentResult(intent=intent, source="rules")
        return None

    @staticmethod
    def normalize_ai_label(label: str) -> str:
        clean = normalize_text(label).replace(" ", "_")
        return clean if clean in VALID_INTENTS else "general_chat"
