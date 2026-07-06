from __future__ import annotations

import re
from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit

from collector.models import Article


_SPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\u4e00-\u9fff]+", re.UNICODE)


def normalize_url(url: str) -> str:
    parts = urlsplit((url or "").strip())
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower() or "https", netloc, path, "", ""))


def normalize_title(title: str) -> str:
    compact = _PUNCT_RE.sub(" ", (title or "").lower())
    return _SPACE_RE.sub(" ", compact).strip()


def title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_title(left), normalize_title(right)).ratio()


def deduplicate_articles(articles: list[Article], title_threshold: float = 0.9) -> list[Article]:
    result: list[Article] = []
    seen_urls: set[str] = set()
    seen_titles: list[str] = []

    for article in articles:
        normalized_url = normalize_url(article.url)
        normalized_title = normalize_title(article.title)
        if not normalized_title:
            continue
        if normalized_url in seen_urls:
            continue
        if any(title_similarity(normalized_title, title) >= title_threshold for title in seen_titles):
            continue
        seen_urls.add(normalized_url)
        seen_titles.append(normalized_title)
        result.append(article)

    return result
