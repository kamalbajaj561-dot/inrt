from __future__ import annotations

import urllib.parse
import webbrowser

from jarvis.config.websites import WEBSITES
from jarvis.utils.helpers import ActionResult


class WebAction:
    def open_site(self, command: str) -> ActionResult:
        text = command.lower()
        for key, url in WEBSITES.items():
            if key in text:
                webbrowser.open(url)
                return ActionResult(True, f"Opening {key}.")

        if "google" in text or "search" in text:
            query = text.replace("google", "").replace("search", "").strip()
            target = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
            webbrowser.open(target)
            return ActionResult(True, f"Searching Google for: {query}")

        if "youtube" in text or "play" in text:
            query = text.replace("youtube", "").replace("play", "").strip()
            target = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
            webbrowser.open(target)
            return ActionResult(True, f"Opening YouTube for: {query}")

        return ActionResult(False, "No web target recognized.")
