from __future__ import annotations

import subprocess
import time

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None

from jarvis.ai.brain import Brain
from jarvis.config.contacts import CONTACTS
from jarvis.config.settings import SETTINGS
from jarvis.utils.helpers import ActionResult
from jarvis.utils.logger import get_logger


class WhatsAppAction:
    def __init__(self, brain: Brain) -> None:
        self.brain = brain
        self.logger = get_logger("jarvis.actions.whatsapp")

    def _match_contact(self, extracted_contact: str) -> str:
        c = extracted_contact.strip().lower()
        if not c:
            return ""
        if c in CONTACTS:
            return CONTACTS[c]
        for alias, display in CONTACTS.items():
            if c in alias or alias in c or c in display.lower():
                return display
        return ""

    def send(self, command: str) -> ActionResult:
        extracted_contact, message = self.brain.extract_whatsapp_payload(command)
        contact = self._match_contact(extracted_contact)

        if not contact:
            return ActionResult(
                False,
                "I couldn't identify the contact. Please say for example: tell Rahul I will call later.",
            )
        if not message:
            return ActionResult(False, "What should I send to the contact?")

        if SETTINGS.dry_run:
            return ActionResult(True, f"[DRY RUN] Would send to {contact}: {message}")
        if pyautogui is None:
            return ActionResult(False, "pyautogui unavailable. Install GUI dependencies for WhatsApp automation.")

        try:
            subprocess.Popen(["whatsapp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            pyautogui.hotkey("ctrl", "f")
            pyautogui.write(contact, interval=0.03)
            pyautogui.press("enter")
            pyautogui.write(message, interval=0.02)
            pyautogui.press("enter")
            self.logger.info("whatsapp_message_sent contact=%s", contact)
            return ActionResult(True, f"Message sent to {contact}.")
        except Exception as exc:
            self.logger.exception("whatsapp_send_failed")
            return ActionResult(False, f"WhatsApp send failed: {exc}")
