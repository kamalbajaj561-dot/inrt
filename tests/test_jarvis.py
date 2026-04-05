from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from jarvis.main import JarvisPro


def _jarvis() -> JarvisPro:
    return JarvisPro(voice_mode=False)


def test_open_my_project(monkeypatch) -> None:
    jarvis = _jarvis()
    monkeypatch.setattr(jarvis.coding, "open_project", lambda _: type("R", (), {"ok": True, "message": "Opened INRT Wallet in VS Code.", "data": None})())
    result = jarvis.handle_command("open my project")
    assert result.ok


def test_run_my_project(monkeypatch) -> None:
    jarvis = _jarvis()
    monkeypatch.setattr(jarvis.coding, "run_project", lambda _: type("R", (), {"ok": True, "message": "INRT project is starting with npm run dev.", "data": None})())
    result = jarvis.handle_command("run my project")
    assert result.ok
    assert "starting" in result.message.lower()


def test_fix_my_app_error() -> None:
    jarvis = _jarvis()
    result = jarvis.handle_command("fix my app error")
    assert result.ok
    assert "fix it fast" in result.message.lower()


def test_tell_rahul_message(monkeypatch) -> None:
    jarvis = _jarvis()
    monkeypatch.setattr(jarvis.whatsapp, "send", lambda _: type("R", (), {"ok": True, "message": "Message sent to Rahul.", "data": None})())
    result = jarvis.handle_command("tell Rahul I will call later")
    assert result.ok
    assert "rahul" in result.message.lower()


def test_open_youtube(monkeypatch) -> None:
    jarvis = _jarvis()
    monkeypatch.setattr(jarvis.web, "open_site", lambda _: type("R", (), {"ok": True, "message": "Opening YouTube.", "data": None})())
    result = jarvis.handle_command("open youtube")
    assert result.ok


def test_search_startup_ideas(monkeypatch) -> None:
    jarvis = _jarvis()
    monkeypatch.setattr(jarvis.web, "open_site", lambda _: type("R", (), {"ok": True, "message": "Searching Google for startup ideas.", "data": None})())
    result = jarvis.handle_command("search for startup ideas")
    assert result.ok


def test_business_ideas_for_inrt(monkeypatch) -> None:
    jarvis = _jarvis()
    monkeypatch.setattr(jarvis.business, "advise", lambda _: type("R", (), {"ok": True, "message": "Try referral loops and merchant rewards.", "data": None})())
    result = jarvis.handle_command("give me business ideas for INRT")
    assert result.ok


def test_risky_action_requires_confirmation() -> None:
    jarvis = _jarvis()
    result = jarvis.handle_command("shutdown my pc")
    assert not result.ok
    assert "risky" in result.message.lower()
