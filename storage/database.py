from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from analyzer.dedup import normalize_url
from collector.models import Article


SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    normalized_url TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    published_at TEXT,
    summary TEXT,
    category TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    report_date TEXT PRIMARY KEY,
    markdown TEXT NOT NULL,
    article_count INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


class FinanceDailyDatabase:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def save_articles(self, articles: list[Article]) -> None:
        with self.connection:
            for article in articles:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO articles
                    (title, url, normalized_url, source, published_at, summary, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article.title,
                        article.url,
                        normalize_url(article.url),
                        article.source,
                        article.published_at.isoformat() if article.published_at else None,
                        article.summary,
                        article.category,
                    ),
                )

    def save_report(self, report_date: date, markdown: str, article_count: int) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO reports (report_date, markdown, article_count)
                VALUES (?, ?, ?)
                ON CONFLICT(report_date) DO UPDATE SET
                    markdown = excluded.markdown,
                    article_count = excluded.article_count
                """,
                (report_date.isoformat(), markdown, article_count),
            )
