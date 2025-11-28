from __future__ import annotations

import threading
from collections import OrderedDict
from time import monotonic
from typing import Generic, Hashable, Optional, Tuple, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class ResultCache(Generic[K, V]):
    """轻量级 LRU + TTL 内存缓存，避免重复抓取同一关键词。"""

    def __init__(self, ttl: float = 600.0, max_size: int = 32):
        self.ttl = ttl
        self.max_size = max_size
        self._lock = threading.Lock()
        self._data: "OrderedDict[K, Tuple[float, V]]" = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        now = monotonic()
        with self._lock:
            if key not in self._data:
                return None
            ts, value = self._data.pop(key)
            if now - ts > self.ttl:
                return None
            self._data[key] = (ts, value)
            return value

    def set(self, key: K, value: V) -> V:
        now = monotonic()
        with self._lock:
            if key in self._data:
                self._data.pop(key)
            self._data[key] = (now, value)
            while len(self._data) > self.max_size:
                self._data.popitem(last=False)
        return value

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
