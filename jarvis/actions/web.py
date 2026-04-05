from __future__ import annotations

import re
import urllib.parse
import webbrowser

from jarvis.config.websites import WEBSITES
from jarvis.utils.helpers import ActionResult


class WebAction:
    def open_site(self, command: str) -> ActionResult:
        text = command.lower().strip()

        for key, url in WEBSITES.items():
            if key in text:
                webbrowser.open(url)
                return ActionResult(True, f"Opening {key}.")

        if "search" in text or "google" in text:
            query = text.replace("search", "").replace("google", "").replace("for", "").strip()
            if not query:
                return ActionResult(False, "What should I search for?")
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}")
            return ActionResult(True, f"Searching Google for {query}.")

        if "youtube" in text or "play" in text:
            query = text.replace("youtube", "").replace("play", "").strip()
            if query:
                webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}")
                return ActionResult(True, f"Opening YouTube results for {query}.")
            webbrowser.open("https://youtube.com")
            return ActionResult(True, "Opening YouTube.")

        domain_match = re.search(r"([a-zA-Z0-9-]+\.[a-zA-Z]{2,})(/\S*)?", text)
        if domain_match:
            domain = domain_match.group(0)
            target = domain if domain.startswith("http") else f"https://{domain}"
            webbrowser.open(target)
            return ActionResult(True, f"Opening {target}.")

        return ActionResult(False, "I couldn't identify the web target. Try saying open youtube or search startup ideas.")
