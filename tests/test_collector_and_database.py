from datetime import date, datetime, timezone

from collector.models import Article
from collector.rss_collector import fetch_rss_articles
from storage.database import FinanceDailyDatabase


class FakeResponse:
    def __init__(self, content: bytes = b"", status_error: Exception | None = None) -> None:
        self.content = content
        self._status_error = status_error

    def raise_for_status(self) -> None:
        if self._status_error:
            raise self._status_error


def test_fetch_rss_articles_skips_bad_feeds(monkeypatch):
    def fake_get(url: str, timeout: int, headers: dict[str, str]):
        assert timeout == 8
        assert headers["User-Agent"].startswith("finance-daily-bot/")
        if "bad" in url:
            raise RuntimeError("feed unavailable")
        return FakeResponse(b"<rss></rss>")

    def fake_parse(content: bytes):
        assert content == b"<rss></rss>"
        return {
            "entries": [
                {
                    "title": "AI chip demand lifts semiconductor supply chain",
                    "link": "https://example.com/ai-chip",
                    "published": "Mon, 06 Jul 2026 00:00:00 GMT",
                    "summary": "Server demand pushes upstream suppliers higher.",
                }
            ]
        }

    monkeypatch.setattr("collector.rss_collector.requests.get", fake_get)
    monkeypatch.setattr("collector.rss_collector.feedparser.parse", fake_parse)

    articles = fetch_rss_articles(
        [
            {"name": "Bad Feed", "url": "https://example.com/bad.xml"},
            {"name": "Good Feed", "url": "https://example.com/good.xml"},
        ],
        hours=24 * 365,
    )

    assert len(articles) == 1
    assert articles[0].source == "Good Feed"
    assert articles[0].title == "AI chip demand lifts semiconductor supply chain"


def test_database_saves_articles_and_report(tmp_path):
    db = FinanceDailyDatabase(tmp_path / "finance_daily.sqlite")
    article = Article(
        title="Fed signals rate path as markets rally",
        url="https://example.com/fed?utm_source=test",
        source="Example Finance",
        published_at=datetime(2026, 7, 6, tzinfo=timezone.utc),
        summary="Markets rose after rate comments.",
        category="宏观与政策",
    )

    try:
        db.save_articles([article])
        db.save_report(date(2026, 7, 6), "# 财经日报-2026-07-06", 1)

        saved_article_count = db.connection.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        saved_report = db.connection.execute(
            "SELECT markdown, article_count FROM reports WHERE report_date = ?",
            ("2026-07-06",),
        ).fetchone()
    finally:
        db.close()

    assert saved_article_count == 1
    assert saved_report == ("# 财经日报-2026-07-06", 1)
