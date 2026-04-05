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
    """Pipeline: Voice → Command → Rule override → AI fallback → Router → Execution → Response."""

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
        self.business = BusinessAgent(self.brain)

    def run_voice_loop(self) -> None:
        self.speaker.say("JARVIS PRO online. Say jarvis to wake me.")
        while True:
            wake = self.listener.wait_for_wake_word(SETTINGS.wake_word)
            if not wake.heard:
                continue
            self.speaker.say("I'm listening.")
            command = self.listener.listen_once(retries=1)
            if not command.heard:
                self.speaker.say("I didn't catch that. Try saying open YouTube or send a message.")
                continue
            result = self.handle_command(command.text)
            self.speaker.say(result.message)

    def handle_command(self, command: str) -> ActionResult:
        intent, source = self.brain.detect_intent(command)
        self.logger.info("intent=%s source=%s command=%s", intent, source, command)

        # Safety gate
        if requires_confirmation(intent, command, SETTINGS.ask_confirmation_for):
            return ActionResult(False, "This action is risky. Re-run with --confirm to proceed.")

        try:
            if intent == "whatsapp":
                return self.whatsapp.send(command)

            if intent == "open_app":
                app_result = self.apps.handle(command)
                if app_result.ok:
                    return app_result
                return self.web.open_site(command)

            if intent == "coding":
                return self.coding.handle(command)

            if intent == "system_control":
                return self.system.control(command)

            if intent in {"search", "play"}:
                return self.web.open_site(command)

            if intent == "business":
                return self.business.advise(command)

            # general_chat
            reply = self.brain.generate_response(command)
            return ActionResult(True, reply)
        except Exception as exc:
            self.logger.exception("command_handling_failure")
            return ActionResult(False, f"I hit an execution issue: {exc}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JARVIS PRO assistant")
    parser.add_argument("--mode", choices=["voice", "cli"], default="cli")
    parser.add_argument("--command", help="Single command for cli mode")
    parser.add_argument("--confirm", action="store_true", help="Confirm dangerous system actions")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    jarvis = JarvisPro(voice_mode=args.mode == "voice")

    if args.mode == "voice":
        jarvis.run_voice_loop()
        return 0

    if not args.command:
        print("Please provide --command in CLI mode.")
        return 1

    result = jarvis.handle_command(args.command)
    if not result.ok and args.confirm and "risky" in result.message.lower():
        result = jarvis.system.control(args.command)

    print(result.message)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
