from __future__ import annotations

from dataclasses import dataclass

try:
    import speech_recognition as sr  # type: ignore
except Exception:  # pragma: no cover
    sr = None

from jarvis.config.settings import SETTINGS
from jarvis.utils.logger import get_logger


@dataclass
class ListenResult:
    heard: bool
    text: str
    error: str = ""


class Listener:
    def __init__(self, enabled: bool = True) -> None:
        self.logger = get_logger("jarvis.voice.listen")
        self.enabled = enabled and sr is not None
        self.recognizer = sr.Recognizer() if self.enabled else None
        if self.recognizer is not None:
            self.recognizer.pause_threshold = 1
            self.recognizer.energy_threshold = 250

    def listen_once(self, retries: int = 1) -> ListenResult:
        if not self.enabled or self.recognizer is None or sr is None:
            return ListenResult(False, "", "Voice mode unavailable")

        attempts = retries + 1
        for attempt in range(attempts):
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=SETTINGS.ambient_adjust_sec)
                    audio = self.recognizer.listen(
                        source,
                        timeout=SETTINGS.listen_timeout_sec,
                        phrase_time_limit=SETTINGS.phrase_time_limit_sec,
                    )
                text = self.recognizer.recognize_google(audio)
                return ListenResult(True, text.strip())
            except sr.WaitTimeoutError:
                if attempt < attempts - 1:
                    continue
                return ListenResult(False, "", "Silence detected")
            except sr.UnknownValueError:
                if attempt < attempts - 1:
                    continue
                return ListenResult(False, "", "I could not understand speech")
            except Exception as exc:
                self.logger.exception("listen_failure")
                return ListenResult(False, "", f"Listen failed: {exc}")
        return ListenResult(False, "", "No valid speech captured")

    def wait_for_wake_word(self, wake_word: str) -> ListenResult:
        while True:
            result = self.listen_once(retries=1)
            if not result.heard:
                continue
            lowered = result.text.lower()
            if wake_word in lowered:
                return ListenResult(True, lowered)
