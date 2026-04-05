from __future__ import annotations

import subprocess
from pathlib import Path

from jarvis.config.settings import SETTINGS
from jarvis.utils.helpers import ActionResult
from jarvis.utils.logger import get_logger


class CodingAgent:
    """Coding workflows for INRT Wallet project operations and guidance."""

    def __init__(self) -> None:
        self.logger = get_logger("jarvis.actions.coding_agent")

    def handle(self, command: str) -> ActionResult:
        text = command.lower()
        project = SETTINGS.inrt_wallet_path

        if "open my project" in text or "open project" in text:
            return self.open_project(project)
        if "run my project" in text or "run project" in text or "run app" in text:
            return self.run_project(project)
        if "fix my app error" in text or "fix" in text or "error" in text:
            return self.fix_error_guidance(command)
        if "analyze my code" in text or "analyze" in text:
            return self.analyze_codebase(project)

        return ActionResult(
            False,
            "Do you want me to open your project, run it, fix an error, or analyze your code?",
        )

    def open_project(self, project_path: Path) -> ActionResult:
        if not project_path.exists():
            return ActionResult(False, f"INRT project not found at {project_path}. Set INRT_WALLET_PATH correctly.")
        try:
            subprocess.Popen(["code", str(project_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return ActionResult(True, f"Opened INRT Wallet in VS Code from {project_path}.")
        except Exception as exc:
            return ActionResult(False, f"Couldn't open VS Code automatically: {exc}")

    def run_project(self, project_path: Path) -> ActionResult:
        if not project_path.exists():
            return ActionResult(False, f"INRT project path missing: {project_path}")

        try:
            node_modules = project_path / "node_modules"
            if not node_modules.exists():
                install_proc = subprocess.run(
                    ["npm", "install"],
                    cwd=project_path,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if install_proc.returncode != 0:
                    return ActionResult(False, f"npm install failed: {install_proc.stderr[-240:]}")

            dev_proc = subprocess.Popen(["npm", "run", "dev"], cwd=project_path)
            self.logger.info("dev_server_started pid=%s path=%s", dev_proc.pid, project_path)
            return ActionResult(True, "INRT project is starting with npm run dev.")
        except Exception as exc:
            return ActionResult(False, f"Failed to run project: {exc}")

    def fix_error_guidance(self, issue_text: str) -> ActionResult:
        return ActionResult(
            True,
            (
                "Let's fix it fast: share the exact error log, then I will identify root cause, "
                "propose patch steps, and suggest verification checks. "
                f"Issue summary: {issue_text[:120]}"
            ),
        )

    def analyze_codebase(self, project_path: Path) -> ActionResult:
        if not project_path.exists():
            return ActionResult(False, f"Project path missing: {project_path}")

        checks = [
            "Use a service layer for Firebase and API calls.",
            "Add stricter TypeScript/prop validation at boundaries.",
            "Create feature folders: auth, wallet, transactions, analytics.",
            "Add CI checks: lint, unit tests, and preview build.",
        ]
        return ActionResult(True, "Code analysis suggestions:\n- " + "\n- ".join(checks))
