from __future__ import annotations

from collections import deque


class MemoryStore:
    """Small in-memory conversational memory placeholder."""

    def __init__(self, max_items: int = 12) -> None:
        self._items: deque[str] = deque(maxlen=max_items)

    def add(self, text: str) -> None:
        self._items.append(text)

    def recent(self) -> list[str]:
        return list(self._items)
