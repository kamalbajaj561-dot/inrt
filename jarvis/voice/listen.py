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

    def listen_once(self) -> ListenResult:
        if not self.enabled or self.recognizer is None or sr is None:
            return ListenResult(False, "", "Voice mode unavailable")

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
            return ListenResult(False, "", "No speech detected")
        except sr.UnknownValueError:
            return ListenResult(False, "", "Could not understand audio")
        except Exception as exc:
            self.logger.exception("listen_failure")
            return ListenResult(False, "", f"Listen failed: {exc}")

    def wait_for_wake_word(self, wake_word: str) -> ListenResult:
        """Always-listening loop with wake-word filtering."""
        while True:
            result = self.listen_once()
            if not result.heard:
                self.logger.debug("silence_or_error=%s", result.error)
                continue
            lowered = result.text.lower()
            if wake_word in lowered:
                return ListenResult(True, lowered)
