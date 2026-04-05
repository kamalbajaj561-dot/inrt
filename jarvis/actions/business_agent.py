from __future__ import annotations

from jarvis.ai.brain import Brain
from jarvis.utils.helpers import ActionResult


class BusinessAgent:
    def __init__(self, brain: Brain) -> None:
        self.brain = brain

    def advise(self, command: str) -> ActionResult:
        context = (
            "You are advising startup INRT Wallet. Give practical strategic suggestions with 3 concise bullets "
            "focused on growth, product, and revenue."
        )
        suggestion = self.brain.generate_response(command, context=context)
        return ActionResult(True, suggestion)
