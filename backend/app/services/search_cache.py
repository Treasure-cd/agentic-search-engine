from __future__ import annotations

import time
from typing import Any

from app.core.config import settings


class SearchCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._entries: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    def get(self, key: str) -> list[dict[str, Any]] | None:
        item = self._entries.get(key)
        if not item:
            return None

        expires_at, value = item
        if expires_at < time.time():
            self._entries.pop(key, None)
            return None

        return value

    def set(self, key: str, value: list[dict[str, Any]]) -> None:
        self._entries[key] = (time.time() + self.ttl_seconds, value)


search_cache = SearchCache(ttl_seconds=settings.SEARCH_CACHE_TTL_SECONDS)
