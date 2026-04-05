from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from jarvis.main import JarvisPro


def test_business_intent_route() -> None:
    jarvis = JarvisPro(voice_mode=False)
    result = jarvis.handle_command("give me monetization strategy for INRT")
    assert result.ok
    assert "Monetization" in result.message


def test_risky_action_requires_confirmation() -> None:
    jarvis = JarvisPro(voice_mode=False)
    result = jarvis.handle_command("shutdown my pc")
    assert not result.ok
    assert "Risky action" in result.message


def test_coding_agent_intent() -> None:
    jarvis = JarvisPro(voice_mode=False)
    result = jarvis.handle_command("fix my wallet app error")
    assert result.ok
    assert "Debug flow" in result.message
