from __future__ import annotations

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover
    pyttsx3 = None

from jarvis.utils.logger import get_logger


class Speaker:
    def __init__(self, enabled: bool = True) -> None:
        self.logger = get_logger("jarvis.voice.speak")
        self.enabled = enabled and pyttsx3 is not None
        self.engine = pyttsx3.init() if self.enabled else None

    def say(self, message: str) -> None:
        self.logger.info("assistant_response=%s", message)
        print(f"JARVIS: {message}")
        if self.engine:
            self.engine.say(message)
            self.engine.runAndWait()
