from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """新闻条目的简单数据结构。"""

    title: str
    url: str
    source: str
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    content: Optional[str] = None

    def short_source(self) -> str:
        return self.source or "unknown"
