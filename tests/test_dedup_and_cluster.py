from datetime import datetime, timezone

from analyzer.clusterer import cluster_articles
from analyzer.dedup import deduplicate_articles
from collector.models import Article


def article(title: str, url: str) -> Article:
    return Article(
        title=title,
        url=url,
        source="Test",
        published_at=datetime(2026, 7, 6, tzinfo=timezone.utc),
        summary="",
    )


def test_deduplicate_articles_removes_tracking_urls_and_similar_titles():
    articles = [
        article("Fed signals rate path as markets rally", "https://example.com/a?utm_source=x"),
        article("Fed signals rate path as markets rally!", "https://example.com/a?ref=y"),
        article("AI chip demand lifts semiconductor supply chain", "https://example.com/b"),
    ]

    result = deduplicate_articles(articles)

    assert [item.title for item in result] == [
        "Fed signals rate path as markets rally",
        "AI chip demand lifts semiconductor supply chain",
    ]


def test_cluster_articles_groups_related_finance_events():
    articles = [
        article("AI chip demand lifts semiconductor supply chain", "https://example.com/1"),
        article("Semiconductor stocks rise on AI server demand", "https://example.com/2"),
        article("Oil prices fall after supply report", "https://example.com/3"),
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 2
    assert any(len(cluster.articles) == 2 and cluster.category == "科技与半导体" for cluster in clusters)
