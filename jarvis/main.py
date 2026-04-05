from __future__ import annotations

import argparse

from jarvis.actions.apps import AppAction
from jarvis.actions.business_agent import BusinessAgent
from jarvis.actions.coding_agent import CodingAgent
from jarvis.actions.system import SystemAction
from jarvis.actions.web import WebAction
from jarvis.actions.whatsapp import WhatsAppAction
from jarvis.ai.brain import Brain
from jarvis.config.settings import SETTINGS
from jarvis.utils.helpers import ActionResult, requires_confirmation
from jarvis.utils.logger import get_logger
from jarvis.voice.listen import Listener
from jarvis.voice.speak import Speaker


class JarvisPro:
    def __init__(self, voice_mode: bool = True) -> None:
        self.logger = get_logger("jarvis.main")
        self.voice_mode = voice_mode
        self.listener = Listener(enabled=voice_mode)
        self.speaker = Speaker(enabled=voice_mode)
        self.brain = Brain()

        self.whatsapp = WhatsAppAction(self.brain)
        self.apps = AppAction()
        self.web = WebAction()
        self.system = SystemAction()
        self.coding = CodingAgent()
        self.business = BusinessAgent()

    def run_voice_loop(self) -> None:
        self.speaker.say("JARVIS PRO online. Waiting for wake word.")
        while True:
            wake = self.listener.wait_for_wake_word(SETTINGS.wake_word)
            if wake.heard:
                self.speaker.say("Yes?")
                cmd = self.listener.listen_once()
                if not cmd.heard:
                    self.speaker.say("I did not catch that. Try again.")
                    continue
                result = self.handle_command(cmd.text)
                self.speaker.say(result.message)

    def handle_command(self, command: str) -> ActionResult:
        intent, confidence = self.brain.detect_intent(command)
        self.logger.info("intent=%s confidence=%.2f command=%s", intent, confidence, command)

        if requires_confirmation(intent, command, SETTINGS.ask_confirmation_for):
            return ActionResult(False, "Risky action detected. Please re-run with --confirm in CLI mode.")

        if intent == "whatsapp":
            return self.whatsapp.send(command)
        if intent == "open_app":
            return self.apps.handle(command)
        if intent in {"search", "play"}:
            return self.web.open_site(command)
        if intent == "system_control":
            return self.system.control(command)
        if intent == "coding":
            return self.coding.handle(command)
        if intent == "business":
            return self.business.advise(command)

        reply = self.brain.generate_response(command)
        return ActionResult(True, reply)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JARVIS PRO assistant")
    parser.add_argument("--mode", choices=["voice", "cli"], default="cli")
    parser.add_argument("--command", help="Single command for cli mode")
    parser.add_argument("--confirm", action="store_true", help="Allow risky commands in this invocation")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    jarvis = JarvisPro(voice_mode=args.mode == "voice")

    if args.mode == "voice":
        jarvis.run_voice_loop()
        return 0

    if not args.command:
        print("Use --command in cli mode.")
        return 1

    if args.confirm and "Risky action" in (res := jarvis.handle_command(args.command)).message:
        # Explicit operator confirmation for risky actions in CLI mode.
        if any(k in args.command.lower() for k in SETTINGS.ask_confirmation_for):
            print(jarvis.system.control(args.command).message)
            return 0
    print(res.message)
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
