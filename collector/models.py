from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Article:
    title: str
    url: str
    source: str
    published_at: datetime | None
    summary: str = ""
    category: str = "综合财经"
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class EventCluster:
    title: str
    category: str
    keywords: list[str]
    articles: list[Article]

    @property
    def source_count(self) -> int:
        return len({article.source for article in self.articles})
