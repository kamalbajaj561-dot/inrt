from __future__ import annotations

import subprocess

from jarvis.utils.helpers import ActionResult
from jarvis.utils.logger import get_logger


class AppAction:
    APP_MAP = {
        "chrome": ["google-chrome"],
        "vscode": ["code"],
        "terminal": ["gnome-terminal"],
        "whatsapp": ["whatsapp"],
    }

    def __init__(self) -> None:
        self.logger = get_logger("jarvis.actions.apps")

    def handle(self, command: str) -> ActionResult:
        text = command.lower()
        close_mode = "close" in text or "stop" in text

        app = next((name for name in self.APP_MAP if name in text), None)
        if not app:
            return ActionResult(False, "App not recognized. Update APP_MAP in actions/apps.py.")

        try:
            if close_mode:
                subprocess.run(["pkill", "-f", app], check=False)
                return ActionResult(True, f"Closed {app}.")
            subprocess.Popen(self.APP_MAP[app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.logger.info("app_opened=%s", app)
            return ActionResult(True, f"Opened {app}.")
        except Exception as exc:
            self.logger.exception("app_action_failed")
            return ActionResult(False, f"Failed to control {app}: {exc}")
