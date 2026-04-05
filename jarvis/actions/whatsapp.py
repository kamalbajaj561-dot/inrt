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

    def extract_contact_and_message(self, command: str) -> tuple[str, str]:
        lowered = command.lower()
        contact = ""
        for alias, display in CONTACTS.items():
            if alias in lowered:
                contact = display
                break

        message = command
        for prefix in ("tell", "message", "send", "whatsapp"):
            if lowered.startswith(prefix):
                message = command[len(prefix) :].strip()
        if " that " in lowered:
            message = command.split("that", 1)[1].strip()
        return contact, message

    def send(self, command: str) -> ActionResult:
        contact, message = self.extract_contact_and_message(command)
        if not contact:
            return ActionResult(False, "I couldn't match a saved contact. Please update config/contacts.py.")
        if not message:
            return ActionResult(False, "Message content is empty.")

        if SETTINGS.dry_run:
            return ActionResult(True, f"[DRY RUN] Would send to {contact}: {message}")

        if pyautogui is None:
            return ActionResult(False, "pyautogui unavailable. Install GUI dependencies to automate WhatsApp app.")

        try:
            subprocess.Popen(["whatsapp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            pyautogui.hotkey("ctrl", "f")
            pyautogui.write(contact, interval=0.03)
            pyautogui.press("enter")
            pyautogui.write(message, interval=0.02)
            pyautogui.press("enter")
            self.logger.info("whatsapp_message_sent contact=%s", contact)
            return ActionResult(True, f"Sent message to {contact}.")
        except Exception as exc:
            self.logger.exception("whatsapp_send_failed")
            return ActionResult(False, f"Failed to send WhatsApp message: {exc}")
