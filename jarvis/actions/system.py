from __future__ import annotations

import platform
import subprocess
from datetime import datetime

from jarvis.config.settings import SETTINGS
from jarvis.utils.helpers import ActionResult
from jarvis.utils.logger import get_logger


class SystemAction:
    def __init__(self) -> None:
        self.logger = get_logger("jarvis.actions.system")
        SETTINGS.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def control(self, command: str) -> ActionResult:
        text = command.lower()
        if "screenshot" in text:
            return self.take_screenshot()
        if "volume up" in text:
            return self._run(["amixer", "-D", "pulse", "sset", "Master", "5%+"])
        if "volume down" in text:
            return self._run(["amixer", "-D", "pulse", "sset", "Master", "5%-"])
        if "mute" in text:
            return self._run(["amixer", "-D", "pulse", "sset", "Master", "mute"])
        if "shutdown" in text:
            return self._run(["shutdown", "-h", "now"])
        if "restart" in text:
            return self._run(["shutdown", "-r", "now"])
        if "lock" in text:
            return self._run(["loginctl", "lock-session"])
        return ActionResult(False, "Unsupported system control command.")

    def take_screenshot(self) -> ActionResult:
        target = SETTINGS.screenshots_dir / f"shot-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.png"
        if platform.system() != "Linux":
            return ActionResult(False, "Screenshot helper is currently wired for Linux.")
        return self._run(["import", "-window", "root", str(target)], success_msg=f"Screenshot saved: {target}")

    def _run(self, cmd: list[str], success_msg: str | None = None) -> ActionResult:
        if SETTINGS.dry_run:
            return ActionResult(True, f"[DRY RUN] {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("system_command=%s", " ".join(cmd))
            return ActionResult(True, success_msg or "Done.")
        except Exception as exc:
            self.logger.error("system_command_failed cmd=%s error=%s", " ".join(cmd), exc)
            return ActionResult(False, f"System command failed: {exc}")
