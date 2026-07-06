from datetime import date, datetime, timezone
from xml.etree import ElementTree

from analyzer.llm import generate_report_with_llm
from analyzer.report import build_fallback_report
from collector.models import Article, EventCluster
from rss.generator import write_rss
from storage.markdown import write_markdown_report


def sample_cluster() -> EventCluster:
    article = Article(
        title="AI chip demand lifts semiconductor supply chain",
        url="https://example.com/ai-chip?utm_source=test",
        source="Example Finance",
        published_at=datetime(2026, 7, 6, tzinfo=timezone.utc),
        summary="Server demand pushes upstream suppliers higher.",
        category="科技与半导体",
    )
    return EventCluster(
        title="AI 芯片需求带动半导体产业链",
        category="科技与半导体",
        keywords=["AI", "芯片", "半导体"],
        articles=[article],
    )


def test_fallback_report_contains_required_sections_and_no_buy_advice():
    report = build_fallback_report(date(2026, 7, 6), [sample_cluster()], llm_error="missing api key")

    required_headings = [
        "# 7月6日信息总结",
        "AI 摘要",
        "## 01 科技与半导体",
        "【核心事件】",
        "【产业逻辑】",
        "【投资框架】",
        "【资金更该买什么类型的公司】",
        "## 风险提示",
    ]
    for heading in required_headings:
        assert heading in report
    assert "买入" not in report
    assert "卖出" not in report
    assert "目标价" not in report
    assert "missing api key" in report


def test_generate_report_uses_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    report, error = generate_report_with_llm(date(2026, 7, 6), [sample_cluster()])

    assert error == "OPENAI_API_KEY is not set"
    assert report.startswith("# 7月6日信息总结")
    assert "规则模板草稿" in report


def test_fallback_market_breadth():
    """Section 一 must include a breadth/coverage summary (clusters, categories, sources)."""
    cluster = sample_cluster()
    report = build_fallback_report(date(2026, 7, 6), [cluster], llm_error=None)

    assert "共抓取 **1** 个事件聚类" in report
    assert "覆盖 **1** 个行业类别" in report
    assert "来自 **1** 个信息来源" in report
    assert "科技与半导体" in report


def test_fallback_source_confidence():
    """Single-source events get cautious confidence; multi-source events get stronger wording."""
    # Single source (sample_cluster has 1 article from 1 source)
    report = build_fallback_report(date(2026, 7, 6), [sample_cluster()], llm_error=None)
    assert "单源" in report

    # Multi-source (3 unique sources)
    articles = [
        Article(
            title=f"A{i}",
            url=f"https://ex.com/{i}",
            source=f"Src{i}",
            published_at=datetime(2026, 7, 6, tzinfo=timezone.utc),
            summary="s",
            category="科技",
        )
        for i in range(3)
    ]
    multi = EventCluster(
        title="Multi-source event", category="科技与半导体", keywords=["m"], articles=articles
    )
    report2 = build_fallback_report(date(2026, 7, 6), [multi], llm_error=None)
    assert "多源" in report2


def test_fallback_capital_focus_asks_verification():
    """Capital focus asks to verify orders, customers, mass production, valuation, and risk."""
    report = build_fallback_report(date(2026, 7, 6), [sample_cluster()], llm_error=None)

    capital_section = report[
        report.index("【资金更该买什么类型的公司】") : report.index("来源：")
    ]
    assert "订单" in capital_section
    assert "客户" in capital_section
    assert "量产" in capital_section
    assert "估值" in capital_section
    assert "风险" in capital_section


def test_fallback_report_uses_summary_card_format_with_capital_focus():
    report = build_fallback_report(date(2026, 7, 6), [sample_cluster()], llm_error=None)

    assert report.startswith("# 7月6日信息总结")
    assert "AI 摘要" in report
    assert "## 01 科技与半导体" in report
    assert "【核心事件】" in report
    assert "【产业逻辑】" in report
    assert "【投资框架】" in report
    assert "【资金更该买什么类型的公司】" in report
    assert "订单已验证、客户明确、即将或正在量产" in report
    assert "行业龙头或关键环节卡位" in report
    assert "AI 芯片需求带动半导体产业链" in report
    assert report.count("个股线索：") == 1


def test_markdown_and_rss_outputs_are_written_as_valid_xml(tmp_path):
    report = build_fallback_report(date(2026, 7, 6), [sample_cluster()], llm_error=None)

    markdown_path = write_markdown_report(report, date(2026, 7, 6), tmp_path / "backup")
    rss_path = write_rss(
        report_date=date(2026, 7, 6),
        report_markdown=report,
        output_path=tmp_path / "rss.xml",
        site_url="https://example.com/finance-daily",
    )

    assert markdown_path.name == "2026-07-06.md"
    assert markdown_path.read_text(encoding="utf-8").startswith("# 7月6日信息总结")

    root = ElementTree.fromstring(rss_path.read_text(encoding="utf-8"))
    assert root.tag == "rss"
    channel = root.find("channel")
    assert channel is not None
    assert channel.findtext("title") == "财经 AI 日报"
    assert channel.findtext("description") == "自动生成的财经新闻、产业链分析与公司映射日报"
    assert channel.findtext("item/title") == "7月6日信息总结"
    item_description = channel.findtext("item/description")
    assert item_description is not None
    assert 'class="summary-card"' in item_description
    assert "【资金更该买什么类型的公司】" in item_description


# ── SITE_URL configurable base URL ──────────────────────────────────────────

def test_get_site_url_default(monkeypatch):
    """Return DEFAULT_SITE_URL when SITE_URL env var is unset."""
    monkeypatch.delenv("SITE_URL", raising=False)
    from src.main import get_site_url

    assert get_site_url() == "https://example.com/finance-daily"


def test_get_site_url_from_env(monkeypatch):
    """Respect SITE_URL env var when set."""
    monkeypatch.setenv("SITE_URL", "https://daily.myapp.com")
    from src.main import get_site_url

    assert get_site_url() == "https://daily.myapp.com"


def test_get_site_url_blank_fallback(monkeypatch):
    """Fall back to DEFAULT_SITE_URL when SITE_URL is set to empty string."""
    monkeypatch.setenv("SITE_URL", "")
    from src.main import get_site_url

    assert get_site_url() == "https://example.com/finance-daily"


def test_trailing_slash_no_double_slash_in_item_link(tmp_path):
    """Trailing slash on site_url must not produce // in item links."""
    rss_path = write_rss(
        report_date=date(2026, 7, 6),
        report_markdown="# test",
        output_path=tmp_path / "rss.xml",
        site_url="https://example.com/",
    )
    root = ElementTree.fromstring(rss_path.read_text(encoding="utf-8"))
    channel = root.find("channel")
    assert channel is not None
    item_link = channel.findtext("item/link")
    assert item_link is not None
    assert "example.com//backup" not in item_link
    assert item_link == "https://example.com/backup/2026-07-06.md"
