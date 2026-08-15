import time
from collections import defaultdict
from http import HTTPStatus

from fastapi import HTTPException


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = [t for t in self._hits[key] if t > window_start]
        if len(hits) >= self.max_requests:
            raise HTTPException(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                detail='Too many attempts. Please try again later.',
            )
        hits.append(now)
        self._hits[key] = hits


login_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)