from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import feedparser
import requests
import yaml

from collector.models import Article


DEFAULT_SOURCES = [
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex"},
    {"name": "CNBC Top News", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    {"name": "MarketWatch Top Stories", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
    {"name": "NASDAQ Markets", "url": "https://www.nasdaq.com/feed/rssoutbound?category=Markets"},
    {"name": "WSJ Markets", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"},
    {"name": "Seeking Alpha", "url": "https://seekingalpha.com/feed.xml"},
]


def load_sources(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return DEFAULT_SOURCES
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources = data.get("sources", [])
    return [
        {"name": str(source["name"]), "url": str(source["url"])}
        for source in sources
        if source.get("name") and source.get("url")
    ]


def _entry_datetime(entry: Any) -> datetime | None:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if not value:
            continue
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except (TypeError, ValueError):
            continue
    return None


def _parse_feed(url: str, timeout: int) -> Any:
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "finance-daily-bot/0.1 (+https://example.com/finance-daily)"},
    )
    response.raise_for_status()
    return feedparser.parse(response.content)


def fetch_rss_articles(sources: list[dict[str, str]], hours: int = 24, timeout: int = 8) -> list[Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    articles: list[Article] = []

    for source in sources:
        try:
            feed = _parse_feed(source["url"], timeout)
        except Exception:
            continue
        for entry in feed.get("entries", []):
            published_at = _entry_datetime(entry)
            if published_at and published_at < cutoff:
                continue
            title = str(entry.get("title", "")).strip()
            url = str(entry.get("link", "")).strip()
            if not title or not url:
                continue
            summary = str(entry.get("summary", "") or entry.get("description", "")).strip()
            articles.append(
                Article(
                    title=title,
                    url=url,
                    source=source["name"],
                    published_at=published_at,
                    summary=summary,
                )
            )

    return articles
