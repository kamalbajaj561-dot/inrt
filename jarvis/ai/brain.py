from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from jarvis.ai.intent import IntentDetector
from jarvis.ai.memory import MemoryStore
from jarvis.config.settings import SETTINGS
from jarvis.utils.logger import get_logger


class Brain:
    def __init__(self) -> None:
        self.intent_detector = IntentDetector()
        self.memory = MemoryStore()
        self.logger = get_logger("jarvis.ai.brain")

    def detect_intent(self, command: str) -> tuple[str, float]:
        result = self.intent_detector.detect(command)
        return result.intent, result.confidence

    def generate_response(self, user_text: str, context: str = "") -> str:
        if SETTINGS.groq_api_key:
            try:
                return self._generate_with_groq(user_text, context)
            except Exception as exc:
                self.logger.warning("groq_fallback error=%s", exc)
        return self._fallback_response(user_text, context)

    def _generate_with_groq(self, user_text: str, context: str) -> str:
        url = f"{SETTINGS.groq_base_url}/chat/completions"
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SETTINGS.personality},
            {
                "role": "system",
                "content": "Be safe. Ask confirmation before risky actions. Provide concise responses.",
            },
        ]
        recents = self.memory.recent()
        if recents:
            messages.append({"role": "system", "content": "Recent memory:\n" + "\n".join(recents[-6:])})
        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})
        messages.append({"role": "user", "content": user_text})

        payload = json.dumps({"model": SETTINGS.groq_model, "messages": messages, "temperature": 0.2}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {SETTINGS.groq_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Groq HTTP {exc.code}: {details[:200]}") from exc

        content = data["choices"][0]["message"]["content"].strip()
        self.memory.add(f"user: {user_text[:120]}")
        self.memory.add(f"assistant: {content[:120]}")
        return content

    def _fallback_response(self, user_text: str, context: str) -> str:
        text = user_text.lower()
        if "inrt" in text and any(k in text for k in ("growth", "idea", "strategy")):
            return (
                "For INRT Wallet: prioritize referral loops, merchant rewards, and a lightweight B2B API. "
                "I can draft a 30-day execution plan next."
            )
        if "error" in text or "fix" in text:
            return "I can help debug. Share the exact error output and I will propose a targeted fix path."
        if context:
            return "I analyzed your context. Next, I recommend a small, test-first iteration."
        return "Ready. Give me a command and I will route it safely."
