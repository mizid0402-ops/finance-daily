from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_SITE_URL = "https://example.com/finance-daily"


def get_site_url() -> str:
    """Return SITE_URL from env, falling back to DEFAULT_SITE_URL."""
    return os.environ.get("SITE_URL", "").strip() or DEFAULT_SITE_URL

from analyzer.clusterer import cluster_articles  # noqa: E402
from analyzer.dedup import deduplicate_articles  # noqa: E402
from analyzer.llm import generate_report_with_llm  # noqa: E402
from collector.rss_collector import fetch_rss_articles, load_sources  # noqa: E402
from rss.generator import write_rss  # noqa: E402
from storage.database import FinanceDailyDatabase  # noqa: E402
from storage.markdown import write_markdown_report  # noqa: E402


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    report_date = date.today()
    sources = load_sources(PROJECT_ROOT / "config" / "sources.yml")
    articles = fetch_rss_articles(sources, hours=24)
    unique_articles = deduplicate_articles(articles)
    clusters = cluster_articles(unique_articles)
    report, llm_error = generate_report_with_llm(report_date, clusters)

    db = FinanceDailyDatabase(PROJECT_ROOT / "data" / "finance_daily.sqlite")
    try:
        db.save_articles(unique_articles)
        db.save_report(report_date, report, len(unique_articles))
    finally:
        db.close()

    markdown_path = write_markdown_report(report, report_date, PROJECT_ROOT / "backup")
    rss_path = write_rss(
        report_date=report_date,
        report_markdown=report,
        output_path=PROJECT_ROOT / "rss.xml",
        site_url=get_site_url(),
    )

    print(f"articles={len(articles)} unique={len(unique_articles)} clusters={len(clusters)}")
    print(f"markdown={markdown_path}")
    print(f"rss={rss_path}")
    if llm_error:
        print(f"llm_fallback={llm_error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
