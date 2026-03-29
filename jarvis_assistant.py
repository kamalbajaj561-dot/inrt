#!/usr/bin/env python3
"""Local voice assistant with secure automation and knowledgeable Q&A.

Security model:
- No hardcoded API keys.
- Risky actions require explicit confirmation by default.
- File access is constrained to WORKSPACE_ROOT.
- Shell execution is constrained to ALLOWED_COMMANDS.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import subprocess
import textwrap
import urllib.error
import urllib.request
from collections import deque
from typing import Any

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - optional dependency in test env
    pyttsx3 = None

try:
    import speech_recognition as sr  # type: ignore
except Exception:  # pragma: no cover - optional dependency in test env
    sr = None


WORKSPACE_ROOT = pathlib.Path.home() / "projects"
AUDIT_LOG = pathlib.Path("jarvis_audit.log")
MAX_CONTEXT_FILES = 5
MAX_FILE_BYTES = 30_000

ALLOWED_COMMANDS: dict[str, list[str]] = {
    "run tests": ["pytest"],
    "format code": ["ruff", "format", "."],
    "lint code": ["ruff", "check", "."],
}
APP_START_CMD = ["python", "app.py"]


@dataclasses.dataclass
class ActionResult:
    ok: bool
    message: str


class KnowledgeEngine:
    """Pluggable knowledge backend.

    Uses OpenAI-compatible Chat Completions if OPENAI_API_KEY is set.
    Falls back to local deterministic guidance otherwise.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def answer(self, question: str, workspace_context: str, memory: list[str]) -> str:
        if self.api_key:
            try:
                return self._answer_with_openai(question, workspace_context, memory)
            except Exception as exc:
                return (
                    "Model endpoint failed, so I used local reasoning. "
                    f"Error: {exc}\n\n"
                    + self._answer_locally(question, workspace_context)
                )
        return self._answer_locally(question, workspace_context)

    def _answer_with_openai(self, question: str, workspace_context: str, memory: list[str]) -> str:
        url = f"{self.base_url}/chat/completions"
        system_prompt = textwrap.dedent(
            """
            You are JARVIS, a precise senior software engineer.
            - Be concise but complete.
            - State uncertainty clearly.
            - Prefer practical steps and examples.
            - Use provided workspace context when relevant.
            """
        ).strip()

        messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        if memory:
            messages.append(
                {
                    "role": "system",
                    "content": "Recent conversation memory:\n" + "\n".join(f"- {item}" for item in memory),
                }
            )
        if workspace_context:
            messages.append({"role": "system", "content": "Workspace snippets:\n" + workspace_context})
        messages.append({"role": "user", "content": question})

        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {exc.code}: {detail[:400]}") from exc

        data = json.loads(raw)
        return data["choices"][0]["message"]["content"].strip()

    def _answer_locally(self, question: str, workspace_context: str) -> str:
        q = question.strip().lower()
        if any(k in q for k in ["bug", "error", "traceback", "exception"]):
            return (
                "Debug plan:\n"
                "1) Reproduce consistently.\n"
                "2) Capture exact stack trace/logs.\n"
                "3) Isolate the smallest failing case.\n"
                "4) Validate assumptions (inputs/env/versions).\n"
                "5) Write a regression test before applying fix."
            )
        if any(k in q for k in ["refactor", "clean", "improve code"]):
            return (
                "Refactor plan: identify hotspots, add characterization tests, extract pure functions, "
                "reduce shared mutable state, and enforce with lint/type checks."
            )
        if workspace_context:
            return (
                "I do not have a cloud model configured, but I can still help from local context. "
                "Ask a narrower question about a specific file/function and I can reason through it."
            )
        return (
            "I can answer coding questions, architecture tradeoffs, debugging strategy, and implementation steps. "
            "For richer model responses, set OPENAI_API_KEY (and optionally OPENAI_MODEL / OPENAI_BASE_URL)."
        )


class JarvisAssistant:
    def __init__(self, workspace_root: pathlib.Path = WORKSPACE_ROOT, voice_enabled: bool = True) -> None:
        self.workspace_root = workspace_root.resolve()
        self.voice_enabled = bool(voice_enabled and sr is not None and pyttsx3 is not None)
        self.recognizer = sr.Recognizer() if self.voice_enabled else None
        self.tts = pyttsx3.init() if self.voice_enabled else None
        self.app_process: subprocess.Popen | None = None
        self.confirm_required = True
        self.knowledge = KnowledgeEngine()
        self.memory: deque[str] = deque(maxlen=12)

    def speak(self, text: str) -> None:
        print(f"JARVIS: {text}")
        if self.tts:
            self.tts.say(text)
            self.tts.runAndWait()

    def log(self, event: str) -> None:
        stamp = dt.datetime.utcnow().isoformat(timespec="seconds")
        previous = AUDIT_LOG.read_text(encoding="utf-8") if AUDIT_LOG.exists() else ""
        AUDIT_LOG.write_text(previous + f"{stamp}Z {event}\n", encoding="utf-8")

    def listen_once(self) -> str:
        if not self.voice_enabled or not self.recognizer or sr is None:
            raise RuntimeError("Voice mode is unavailable. Use --text mode.")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=14)
        text = self.recognizer.recognize_sphinx(audio)
        return text.lower().strip()

    def maybe_confirm(self, prompt: str) -> bool:
        if not self.confirm_required:
            return True
        if self.voice_enabled:
            self.speak(prompt + " Say 'confirm' to continue.")
            try:
                heard = self.listen_once()
            except Exception:
                return False
            return "confirm" in heard

        answer = input(f"{prompt} [type 'confirm' to continue]: ").strip().lower()
        return answer == "confirm"

    def secure_path(self, relative_path: str) -> pathlib.Path:
        candidate = (self.workspace_root / relative_path).resolve()
        if not str(candidate).startswith(str(self.workspace_root)):
            raise ValueError("Path escapes workspace root")
        return candidate

    def _workspace_snippets(self, question: str) -> str:
        tokens = [t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", question.lower()) if len(t) > 2]
        if not tokens or not self.workspace_root.exists():
            return ""

        matches: list[pathlib.Path] = []
        for ext in ("*.py", "*.js", "*.ts", "*.tsx", "*.md", "*.json", "*.yaml", "*.yml"):
            for p in self.workspace_root.rglob(ext):
                if any(tok in p.name.lower() for tok in tokens):
                    matches.append(p)
                if len(matches) >= MAX_CONTEXT_FILES:
                    break
            if len(matches) >= MAX_CONTEXT_FILES:
                break

        snippets: list[str] = []
        for p in matches[:MAX_CONTEXT_FILES]:
            try:
                if p.stat().st_size > MAX_FILE_BYTES:
                    continue
                body = p.read_text(encoding="utf-8", errors="ignore")
                preview = "\n".join(body.splitlines()[:60])
                rel = p.relative_to(self.workspace_root)
                snippets.append(f"## {rel}\n{preview}")
            except Exception:
                continue
        return "\n\n".join(snippets)

    def ask_question(self, question: str) -> ActionResult:
        question = question.strip()
        if not question:
            return ActionResult(False, "Please ask a non-empty question.")
        ctx = self._workspace_snippets(question)
        answer = self.knowledge.answer(question, ctx, list(self.memory))
        self.memory.append(f"Q: {question}")
        self.memory.append(f"A: {answer[:240]}")
        self.log(f"ASK question={question[:120]}")
        return ActionResult(True, answer)

    def open_file(self, relative_path: str) -> ActionResult:
        try:
            target = self.secure_path(relative_path)
            if not target.exists():
                return ActionResult(False, f"File not found: {relative_path}")
            content = target.read_text(encoding="utf-8")
            preview = "\n".join(content.splitlines()[:30])
            self.log(f"OPEN_FILE path={target}")
            return ActionResult(True, f"Preview of {relative_path}:\n{preview}")
        except Exception as exc:
            return ActionResult(False, f"Open failed: {exc}")

    def summarize_file(self, relative_path: str) -> ActionResult:
        try:
            target = self.secure_path(relative_path)
            if not target.exists():
                return ActionResult(False, f"File not found: {relative_path}")
            body = target.read_text(encoding="utf-8", errors="ignore")[:MAX_FILE_BYTES]
            prompt = (
                "Summarize this file with: purpose, key functions/classes, risks, and next actions.\n\n"
                f"File: {relative_path}\n\n{body}"
            )
            result = self.ask_question(prompt)
            self.log(f"SUMMARIZE_FILE path={target}")
            return result
        except Exception as exc:
            return ActionResult(False, f"Summarize failed: {exc}")

    def write_file(self, relative_path: str, body: str) -> ActionResult:
        try:
            target = self.secure_path(relative_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not self.maybe_confirm(f"Write to {relative_path}?"):
                return ActionResult(False, "Cancelled.")
            target.write_text(body + "\n", encoding="utf-8")
            self.log(f"WRITE_FILE path={target} bytes={len(body)}")
            return ActionResult(True, f"Wrote {relative_path}")
        except Exception as exc:
            return ActionResult(False, f"Write failed: {exc}")

    def run_allowed_command(self, intent: str) -> ActionResult:
        cmd = ALLOWED_COMMANDS.get(intent)
        if not cmd:
            return ActionResult(False, "Command not allowed")
        pretty = " ".join(shlex.quote(c) for c in cmd)
        if not self.maybe_confirm(f"Run command: {pretty}?"):
            return ActionResult(False, "Cancelled.")
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.log(f"RUN_CMD intent={intent} rc={proc.returncode}")
            msg = f"Exit code {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            return ActionResult(proc.returncode == 0, msg)
        except Exception as exc:
            return ActionResult(False, f"Execution failed: {exc}")

    def start_app(self) -> ActionResult:
        if self.app_process and self.app_process.poll() is None:
            return ActionResult(False, "App is already running")
        if not self.maybe_confirm("Start the app process?"):
            return ActionResult(False, "Cancelled.")
        try:
            self.app_process = subprocess.Popen(APP_START_CMD, cwd=self.workspace_root)
            self.log(f"APP_START pid={self.app_process.pid}")
            return ActionResult(True, "App started")
        except Exception as exc:
            return ActionResult(False, f"Start failed: {exc}")

    def stop_app(self) -> ActionResult:
        if not self.app_process or self.app_process.poll() is not None:
            return ActionResult(False, "App is not running")
        if not self.maybe_confirm("Stop the app process?"):
            return ActionResult(False, "Cancelled.")
        self.app_process.terminate()
        self.log("APP_STOP")
        return ActionResult(True, "App stopped")

    def _help_text(self) -> str:
        return (
            "Commands: ask <question>, summarize file <path>, open file <path>, "
            "write file <path> <content>, run tests, format code, lint code, "
            "start app, stop app, enable confirmations, disable confirmations."
        )

    def handle_command(self, heard: str) -> ActionResult:
        clean = re.sub(r"\s+", " ", heard.strip().lower())
        self.log(f"HEARD text={clean}")

        if clean in {"help", "jarvis help"}:
            return ActionResult(True, self._help_text())
        if clean.startswith("ask "):
            return self.ask_question(clean.removeprefix("ask ").strip())
        if not clean.startswith("jarvis"):
            return ActionResult(False, "Wake word missing")

        payload = clean.removeprefix("jarvis").strip()
        if payload in ALLOWED_COMMANDS:
            return self.run_allowed_command(payload)
        if payload in {"help", "commands"}:
            return ActionResult(True, self._help_text())
        if payload.startswith("ask "):
            return self.ask_question(payload.removeprefix("ask ").strip())
        if payload == "start app":
            return self.start_app()
        if payload == "stop app":
            return self.stop_app()
        if payload.startswith("open file "):
            return self.open_file(payload.removeprefix("open file ").strip())
        if payload.startswith("summarize file "):
            return self.summarize_file(payload.removeprefix("summarize file ").strip())
        if payload.startswith("write file "):
            parts = payload.split(" ", 3)
            if len(parts) < 4:
                return ActionResult(False, "Usage: jarvis write file <path> <content>")
            return self.write_file(parts[2], parts[3])
        if payload == "disable confirmations":
            self.confirm_required = False
            self.log("CONFIRMATIONS disabled")
            return ActionResult(True, "Confirmations disabled")
        if payload == "enable confirmations":
            self.confirm_required = True
            self.log("CONFIRMATIONS enabled")
            return ActionResult(True, "Confirmations enabled")

        return ActionResult(False, f"Unknown command: {payload}")

    def run_voice_loop(self) -> None:
        if not self.voice_enabled:
            raise RuntimeError("Voice mode unavailable. Install voice deps or use --text mode.")
        self.speak("Jarvis is online. Say help for commands.")
        while True:
            try:
                heard = self.listen_once()
                result = self.handle_command(heard)
                self.speak(result.message if result.ok else f"Sorry. {result.message}")
            except KeyboardInterrupt:
                self.speak("Shutting down.")
                break
            except Exception as exc:
                self.log(f"ERROR {exc}")
                self.speak(f"Unexpected error: {exc}")

    def run_text_loop(self) -> None:
        print("JARVIS (text mode). Type 'exit' to quit.")
        while True:
            try:
                line = input("you> ").strip()
            except EOFError:
                break
            if line.lower() in {"exit", "quit"}:
                break
            result = self.handle_command(line)
            print(f"jarvis> {result.message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local JARVIS assistant")
    parser.add_argument("--text", action="store_true", help="Run interactive text mode instead of voice mode")
    parser.add_argument("--once", type=str, default="", help="Run a single command and exit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    assistant = JarvisAssistant(voice_enabled=not args.text)
    if args.once:
        result = assistant.handle_command(args.once)
        print(result.message)
        raise SystemExit(0 if result.ok else 1)
    if args.text:
        assistant.run_text_loop()
    else:
        assistant.run_voice_loop()


if __name__ == "__main__":
    main()
