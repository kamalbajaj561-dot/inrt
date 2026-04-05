from __future__ import annotations

import subprocess
from pathlib import Path

from jarvis.config.settings import SETTINGS
from jarvis.utils.helpers import ActionResult
from jarvis.utils.logger import get_logger


class CodingAgent:
    """Practical coding assistant for local projects, with INRT Wallet shortcuts."""

    def __init__(self) -> None:
        self.logger = get_logger("jarvis.actions.coding_agent")

    def handle(self, command: str) -> ActionResult:
        text = command.lower()
        if "open my project" in text or "open project" in text:
            return self.open_project(SETTINGS.inrt_wallet_path)
        if "run dev" in text or "start dev server" in text:
            return self.run_dev_server(SETTINGS.inrt_wallet_path)
        if "fix" in text or "debug" in text or "error" in text:
            return self.debug_advice(command)
        if "architecture" in text or "improve" in text:
            return self.architecture_suggestions()
        return ActionResult(True, "Coding agent ready. Ask me to open project, run dev, debug, or suggest architecture.")

    def open_project(self, project_path: Path) -> ActionResult:
        if not project_path.exists():
            return ActionResult(False, f"Project path not found: {project_path}")
        try:
            subprocess.Popen(["code", str(project_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return ActionResult(True, f"Opened project: {project_path}")
        except Exception as exc:
            return ActionResult(False, f"Could not open project in VS Code: {exc}")

    def run_dev_server(self, project_path: Path) -> ActionResult:
        if not project_path.exists():
            return ActionResult(False, f"Project path not found: {project_path}")

        command = ["npm", "run", "dev"]
        try:
            subprocess.Popen(command, cwd=project_path)
            self.logger.info("dev_server_started path=%s", project_path)
            return ActionResult(True, f"Started dev server at {project_path}.")
        except Exception:
            # fallback for Create React App
            try:
                subprocess.Popen(["npm", "start"], cwd=project_path)
                return ActionResult(True, f"Started React app (npm start) at {project_path}.")
            except Exception as exc:
                return ActionResult(False, f"Failed to start dev server: {exc}")

    def debug_advice(self, issue_text: str) -> ActionResult:
        advice = (
            "Debug flow for INRT Wallet:\n"
            "1) Reproduce in local dev and copy exact stack trace.\n"
            "2) Check Firebase env variables and auth rules first.\n"
            "3) Isolate failing component with minimal props.\n"
            "4) Add/adjust tests to lock fix.\n"
            f"Issue seen: {issue_text[:140]}"
        )
        return ActionResult(True, advice)

    def architecture_suggestions(self) -> ActionResult:
        suggestions = (
            "Architecture upgrades for INRT Wallet:\n"
            "- Move API/Firebase access behind service layer.\n"
            "- Add feature-based folders (wallet, onboarding, analytics).\n"
            "- Add typed data contracts and shared validation schemas.\n"
            "- Set up CI with lint + unit tests + preview deploys."
        )
        return ActionResult(True, suggestions)
