from __future__ import annotations

from dataclasses import dataclass

from jarvis.utils.helpers import normalize_text


INTENTS = (
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
    confidence: float


class IntentDetector:
    def detect(self, command: str) -> IntentResult:
        text = normalize_text(command)

        if any(word in text for word in ("whatsapp", "message", "text ", "tell ")):
            return IntentResult("whatsapp", 0.82)
        if any(word in text for word in ("open ", "launch ", "start app", "close ")):
            return IntentResult("open_app", 0.78)
        if any(word in text for word in ("search", "google", "look up")):
            return IntentResult("search", 0.8)
        if any(word in text for word in ("play", "youtube", "song", "music")):
            return IntentResult("play", 0.8)
        if any(word in text for word in ("shutdown", "restart", "lock", "volume", "mute", "screenshot")):
            return IntentResult("system_control", 0.9)
        if any(word in text for word in ("fix", "debug", "code", "project", "inrt wallet", "component")):
            return IntentResult("coding", 0.88)
        if any(word in text for word in ("growth", "monetization", "strategy", "ceo", "business", "startup")):
            return IntentResult("business", 0.85)
        return IntentResult("general_chat", 0.6)
