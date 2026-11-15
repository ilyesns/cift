import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException


class FailureLimiter:
    """Sliding-window counter per key (client IP).

    Lives in memory, which is right for a single API process. If the API ever runs as
    several processes, move the counters to Redis behind the same three methods.
    """

    def __init__(self, max_attempts: int, window_seconds: int = 60) -> None:
        self._max = max_attempts
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> deque[float]:
        hits = self._hits[key]
        while hits and now - hits[0] > self._window:
            hits.popleft()
        return hits

    def check(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            hits = self._prune(key, now)
            if len(hits) >= self._max:
                retry_after = max(1, int(self._window - (now - hits[0])) + 1)
                raise HTTPException(
                    status_code=429,
                    detail="Too many attempts. Please wait a minute and try again.",
                    headers={"Retry-After": str(retry_after)},
                )

    def record(self, key: str) -> None:
        with self._lock:
            self._hits[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)