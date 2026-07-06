from __future__ import annotations

import re
from collections import defaultdict

from analyzer.classifier import classify_article
from collector.models import Article, EventCluster


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "after",
    "今日",
    "市场",
    "公司",
    "表示",
    "相关",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", text.lower())
    return {word for word in words if len(word) > 1 and word not in STOPWORDS}


def _cluster_title(articles: list[Article], category: str) -> str:
    if not articles:
        return category
    return articles[0].title[:80]


def cluster_articles(articles: list[Article], min_overlap: int = 1) -> list[EventCluster]:
    buckets: dict[str, list[Article]] = defaultdict(list)
    for article in articles:
        article.category = classify_article(article)
        buckets[article.category].append(article)

    clusters: list[EventCluster] = []
    for category, category_articles in buckets.items():
        category_clusters: list[list[Article]] = []
        cluster_tokens: list[set[str]] = []

        for article in category_articles:
            tokens = _tokens(f"{article.title} {article.summary}")
            match_index = None
            for index, existing_tokens in enumerate(cluster_tokens):
                if len(tokens & existing_tokens) >= min_overlap:
                    match_index = index
                    break
            if match_index is None:
                category_clusters.append([article])
                cluster_tokens.append(tokens)
            else:
                category_clusters[match_index].append(article)
                cluster_tokens[match_index] |= tokens

        for articles_group, tokens in zip(category_clusters, cluster_tokens):
            clusters.append(
                EventCluster(
                    title=_cluster_title(articles_group, category),
                    category=category,
                    keywords=sorted(tokens)[:8],
                    articles=articles_group,
                )
            )

    clusters.sort(key=lambda cluster: (len(cluster.articles), cluster.source_count), reverse=True)
    return clusters
