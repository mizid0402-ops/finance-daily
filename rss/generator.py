from __future__ import annotations

from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape


def _item_title(report_date: date) -> str:
    return f"{report_date.month}月{report_date.day}日信息总结"


def _render_summary_html(report_markdown: str) -> str:
    lines = report_markdown.splitlines()
    html: list[str] = [
        '<div class="ai-summary" style="background:#eef5ff;padding:16px;font-family:Arial,Helvetica,sans-serif;color:#1f2937;">'
    ]
    in_card = False
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html.append("</ul>")
            in_list = False

    def close_card() -> None:
        nonlocal in_card
        close_list()
        if in_card:
            html.append("</div>")
            in_card = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            close_list()
            continue
        if line in {"# AI 摘要", "AI 摘要"}:
            html.append(
                '<span style="display:inline-block;background:white;border-radius:4px;padding:4px 12px;font-weight:700;">AI 摘要</span>'
            )
            continue
        if line.startswith("# "):
            title = escape(line[2:])
            html.append(f'<h1 style="font-size:24px;margin:16px 0 8px;color:#0f3f76;">{title}</h1>')
            continue
        if line.startswith("## ") and line[3:5].isdigit():
            close_card()
            number, heading = line[3:5], line[6:]
            html.append(
                '<div class="summary-card" style="background:white;border-left:5px solid #0b77b7;'
                'border-radius:8px;margin:16px 0;padding:16px;box-shadow:0 2px 10px rgba(15,63,118,.12);">'
            )
            html.append(
                f'<h2 style="font-size:20px;margin:0 0 12px;"><span style="background:#0b77b7;color:white;'
                f'border-radius:4px;padding:3px 8px;font-size:13px;margin-right:8px;">{number}</span>{escape(heading)}</h2>'
            )
            in_card = True
            continue
        if line.startswith("## "):
            close_card()
            html.append(f'<h2 style="font-size:18px;margin:16px 0 8px;color:#0f3f76;">{escape(line[3:])}</h2>')
            continue
        if line.startswith("【") and line.endswith("】"):
            close_list()
            html.append(f'<h3 style="font-size:15px;margin:12px 0 6px;color:#9a4f00;">{escape(line)}</h3>')
            continue
        if line.startswith("- "):
            if not in_list:
                html.append('<ul style="margin:6px 0 10px 18px;padding:0;">')
                in_list = True
            html.append(f"<li>{escape(line[2:])}</li>")
            continue
        close_list()
        html.append(f'<p style="line-height:1.7;margin:6px 0;">{escape(line)}</p>')

    close_card()
    html.append("</div>")
    return "".join(html)


def write_rss(report_date: date, report_markdown: str, output_path: Path, site_url: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    title = _item_title(report_date)
    link = f"{site_url.rstrip('/')}/backup/{report_date.isoformat()}.md"
    pub_date = format_datetime(datetime.combine(report_date, datetime.min.time(), tzinfo=timezone.utc))
    description = escape(_render_summary_html(report_markdown))
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
