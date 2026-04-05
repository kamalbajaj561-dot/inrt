from __future__ import annotations

from jarvis.utils.helpers import ActionResult


class BusinessAgent:
    def advise(self, command: str) -> ActionResult:
        text = command.lower()
        if "monetization" in text:
            return ActionResult(
                True,
                "Monetization ideas: premium transfers, white-label wallet APIs, and merchant analytics subscription.",
            )
        if "scale" in text:
            return ActionResult(
                True,
                "Scaling plan: optimize onboarding funnel, launch referral cohorts, and instrument activation metrics weekly.",
            )
        if "gap" in text or "feature" in text:
            return ActionResult(
                True,
                "Feature gap analysis: strongest opportunities are bill-splitting, automated savings goals, and smarter fraud alerts.",
            )
        return ActionResult(
            True,
            "CEO mode ready: ask for growth, monetization, product roadmap, or go-to-market strategy for INRT Wallet.",
        )
