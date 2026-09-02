from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitSnapshot:
    tracked_clients: int
    global_starts: int
    active: int


class StartRateLimiter:
    def __init__(
        self,
        max_keys: int = 4096,
        ttl_seconds: float = 900.0,
        client_starts_per_minute: int = 60,
        client_starts_per_ten_minutes: int = 360,
        global_starts_per_minute: int = 120,
    ) -> None:
        self._max_keys = max_keys
        self._ttl_seconds = ttl_seconds
        self._client_starts_per_minute = client_starts_per_minute
        self._client_starts_per_ten_minutes = client_starts_per_ten_minutes
        self._global_starts_per_minute = global_starts_per_minute
        self._clients: dict[str, tuple[deque[float], float]] = {}
        self._global: deque[float] = deque()
        self._active: set[str] = set()
        self._lock = threading.Lock()

    def begin(self, key: str, now: float | None = None) -> str | None:
        timestamp = time.monotonic() if now is None else now
        with self._lock:
            self._purge(timestamp)
            if key in self._active:
                return "client_rate_limited"
            while self._global and timestamp - self._global[0] >= 60.0:
                self._global.popleft()
            if len(self._global) >= self._global_starts_per_minute:
                return "global_start_rate_limited"
            starts, _ = self._clients.get(key, (deque(), timestamp))
            while starts and timestamp - starts[0] >= 600.0:
                starts.popleft()
            starts_in_last_minute = sum(1 for started in starts if timestamp - started < 60.0)
            if starts_in_last_minute >= self._client_starts_per_minute:
                self._clients[key] = (starts, timestamp)
                return "client_rate_limited"
            if len(starts) >= self._client_starts_per_ten_minutes:
                self._clients[key] = (starts, timestamp)
                return "client_rate_limited"
            if key not in self._clients and len(self._clients) >= self._max_keys:
                oldest = min(self._clients, key=lambda item: self._clients[item][1])
                self._clients.pop(oldest, None)
            starts.append(timestamp)
            self._clients[key] = (starts, timestamp)
            self._global.append(timestamp)
            self._active.add(key)
            return None

    def finish(self, key: str) -> None:
        with self._lock:
            self._active.discard(key)

    @property
    def counters(self) -> RateLimitSnapshot:
        with self._lock:
            return RateLimitSnapshot(
                tracked_clients=len(self._clients),
                global_starts=len(self._global),
                active=len(self._active),
            )

    def _purge(self, now: float) -> None:
        expired = [
            key for key, (_, seen) in self._clients.items() if now - seen >= self._ttl_seconds
        ]
        for key in expired:
            self._clients.pop(key, None)
            self._active.discard(key)


class AdmissionController:
    def __init__(self, limit: int = 2, reservation_bytes: int = 17_301_504) -> None:
        self._limit = limit
        self._reservation_bytes = reservation_bytes
        self._active = 0
        self._reserved = 0
        self._lock = threading.Lock()

    def acquire(self) -> bool:
        with self._lock:
            if self._active >= self._limit:
                return False
            self._active += 1
            self._reserved += self._reservation_bytes
            return True

    def release(self) -> None:
        with self._lock:
            if self._active <= 0:
                raise RuntimeError("Admission release without ownership")
            self._active -= 1
            self._reserved -= self._reservation_bytes

    @property
    def counters(self) -> tuple[int, int]:
        with self._lock:
            return self._active, self._reserved
