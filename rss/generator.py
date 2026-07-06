from __future__ import annotations

from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape


def write_rss(report_date: date, report_markdown: str, output_path: Path, site_url: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    title = f"财经日报-{report_date.isoformat()}"
    link = f"{site_url.rstrip('/')}/backup/{report_date.isoformat()}.md"
    pub_date = format_datetime(datetime.combine(report_date, datetime.min.time(), tzinfo=timezone.utc))
    description = escape(report_markdown[:2000])
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>财经 AI 日报</title>
    <link>{escape(site_url)}</link>
    <description>自动生成的财经新闻、产业链分析与公司映射日报</description>
    <language>zh-CN</language>
    <lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>
    <item>
      <title>{escape(title)}</title>
      <link>{escape(link)}</link>
      <guid>{escape(link)}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{description}</description>
    </item>
  </channel>
</rss>
"""
    output_path.write_text(xml, encoding="utf-8")
    return output_path
