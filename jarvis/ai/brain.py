from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from jarvis.ai.intent import IntentDetector, VALID_INTENTS
from jarvis.ai.memory import MemoryStore
from jarvis.config.settings import SETTINGS
from jarvis.utils.logger import get_logger

INTENT_PROMPT = (
    "Classify the user command into exactly one intent label from: "
    + ", ".join(VALID_INTENTS)
    + ". Return only the label."
)


class Brain:
    def __init__(self) -> None:
        self.intent_detector = IntentDetector()
        self.memory = MemoryStore()
        self.logger = get_logger("jarvis.ai.brain")

    def detect_intent(self, command: str) -> tuple[str, str]:
        rule_match = self.intent_detector.detect_by_rules(command)
        if rule_match:
            return rule_match.intent, rule_match.source

        ai_label = self.classify_intent_with_ai(command)
        return self.intent_detector.normalize_ai_label(ai_label), "ai"

    def classify_intent_with_ai(self, command: str) -> str:
        if SETTINGS.groq_api_key:
            try:
                return self._chat_completion(
                    user_text=command,
                    extra_system=INTENT_PROMPT,
                    temperature=0.0,
                ).strip().lower()
            except Exception as exc:
                self.logger.warning("ai_intent_fallback error=%s", exc)
        return "general_chat"

    def generate_response(self, user_text: str, context: str = "") -> str:
        if SETTINGS.groq_api_key:
            try:
                return self._chat_completion(user_text=user_text, extra_system=context, temperature=0.2)
            except Exception as exc:
                self.logger.warning("groq_response_fallback error=%s", exc)
        return self._fallback_response(user_text)

    def extract_whatsapp_payload(self, command: str) -> tuple[str, str]:
        """Return (contact, message) using AI format contact|message with heuristic fallback."""
        if SETTINGS.groq_api_key:
            prompt = (
                "Extract contact and message from the command. "
                "Output exactly as contact|message. If missing data, still return best guess."
            )
            try:
                raw = self._chat_completion(command, extra_system=prompt, temperature=0.0)
                if "|" in raw:
                    c, m = raw.split("|", 1)
                    return c.strip(), m.strip()
            except Exception as exc:
                self.logger.warning("whatsapp_extract_fallback error=%s", exc)

        text = command.strip()
        lowered = text.lower()
        if lowered.startswith("tell ") and " " in text[5:]:
            rest = text[5:]
            first_space = rest.find(" ")
            return rest[:first_space].strip(), rest[first_space + 1 :].strip()
        if lowered.startswith("message ") and " " in text[8:]:
            rest = text[8:]
            first_space = rest.find(" ")
            return rest[:first_space].strip(), rest[first_space + 1 :].strip()
        return "", text

    def _chat_completion(self, user_text: str, extra_system: str = "", temperature: float = 0.2) -> str:
        url = f"{SETTINGS.groq_base_url}/chat/completions"
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are Jarvis, a smart assistant. Be helpful, confident, and concise. "
                    "If unclear, ask a smart question."
                ),
            }
        ]
        if extra_system:
            messages.append({"role": "system", "content": extra_system})
        recents = self.memory.recent()
        if recents:
            messages.append({"role": "system", "content": "Recent context:\n" + "\n".join(recents[-6:])})
        messages.append({"role": "user", "content": user_text})

        payload = json.dumps(
            {"model": SETTINGS.groq_model, "messages": messages, "temperature": temperature}
        ).encode("utf-8")

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
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Groq HTTP {exc.code}: {detail[:200]}") from exc

        content = data["choices"][0]["message"]["content"].strip()
        self.memory.add(f"user: {user_text[:120]}")
        self.memory.add(f"assistant: {content[:120]}")
        return content

    def _fallback_response(self, user_text: str) -> str:
        lowered = user_text.lower()
        if "help" in lowered:
            return "I can send WhatsApp messages, open apps/sites, run your INRT project, or suggest startup strategy."
        if "inrt" in lowered or "business" in lowered:
            return "For INRT, do you want growth ideas, revenue model suggestions, or roadmap priorities?"
        if "code" in lowered or "error" in lowered or "fix" in lowered:
            return "Do you want me to open your project, run it, or analyze the error details first?"
        return "I didn't catch that clearly. Try saying: open YouTube, run my project, or tell Rahul I will call later."
