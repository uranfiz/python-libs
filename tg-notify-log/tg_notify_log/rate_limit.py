"""защита от спама: rate-limit и дедупликация"""

from __future__ import annotations
import hashlib
import time

class TokenBucket:
    """классический token bucket: N сообщений в минуту"""

    def __init__(self, rate_per_minute: int) -> None:
        self.capacity = float(rate_per_minute)
        self.tokens = float(rate_per_minute)
        self.refill_rate = rate_per_minute / 60.0
        self._last = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        self.tokens = min(
            self.capacity,
            self.tokens + (now - self._last) * self.refill_rate,
        )
        self._last = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

class Deduplicator:
    """скользящее окно: не слать одинаковые сообщения чаще N секунд"""

    def __init__(self, window_seconds: int = 60) -> None:
        self.window = max(0, window_seconds)
        self._seen: dict[str, float] = {}

    def is_duplicate(self, text: str) -> bool:
        if self.window == 0:
            return False

        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        now = time.monotonic()

        if self._seen:
            self._seen = {
                k: v for k, v in self._seen.items() if now - v < self.window
            }

        if key in self._seen:
            return True

        self._seen[key] = now
        return False
