from __future__ import annotations

from datetime import date
from pathlib import Path


def write_markdown_report(report_markdown: str, report_date: date, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    path = backup_dir / f"{report_date.isoformat()}.md"
    path.write_text(report_markdown.rstrip() + "\n", encoding="utf-8")
    return path
