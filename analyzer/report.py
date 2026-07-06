from __future__ import annotations

import re
from datetime import date

from collector.models import EventCluster


REQUIRED_SECTIONS = [
    "## 一、市场总览",
    "## 二、今日核心事件",
    "## 三、产业链受益方向",
    "## 四、资金更该关注什么类型的公司",
    "## 五、相关公司映射",
    "## 六、风险提示",
    "## 七、明日关注",
]

_REMOVE_PATTERNS = [
    re.compile(r"强烈买入[^。\n]*[。\n]?", re.UNICODE),
    re.compile(r"建议买入[^。\n]*[。\n]?", re.UNICODE),
    re.compile(r"可以买入[^。\n]*[。\n]?", re.UNICODE),
    re.compile(r"卖出建议[^。\n]*[。\n]?", re.UNICODE),
    re.compile(r"目标价[^。\n]*[。\n]?", re.UNICODE),
    re.compile(r"(buy|sell|target\s*price)[^.]*\.", re.IGNORECASE),
]


def sanitize_investment_advice(markdown: str) -> str:
    result = markdown
    for pattern in _REMOVE_PATTERNS:
        result = pattern.sub("", result)
    return result


def _format_sources(cluster: EventCluster) -> str:
    lines = []
    for article in cluster.articles[:5]:
        lines.append(f"- [{article.title}]({article.url})（{article.source}）")
    return "\n".join(lines)


def _event_block(clusters: list[EventCluster]) -> str:
    blocks: list[str] = []
    for index, cluster in enumerate(clusters[:8], start=1):
        keywords = "、".join(cluster.keywords[:6]) if cluster.keywords else "暂无"
        src_count = cluster.source_count
        if src_count >= 3:
            confidence = "多源交叉验证，可信度较高"
        elif src_count == 2:
            confidence = "双源信息，可适度参考"
        else:
            confidence = "单源信息，需进一步验证"
        blocks.append(
            "\n".join(
                [
                    f"{index}. **{cluster.title}**",
                    f"   - 分类：{cluster.category}",
                    f"   - 关键词：{keywords}",
                    f"   - 置信度：{confidence}",
                    f"   - 来源：\n{_format_sources(cluster)}",
                ]
            )
        )
    return "\n\n".join(blocks) or "最近 24 小时未抓取到可用财经新闻，请检查 RSS 源或网络状态。"


def _cluster_summary(clusters: list[EventCluster]) -> str:
    categories = {c.category for c in clusters[:8]}
    all_sources = set()
    for c in clusters[:8]:
        for a in c.articles:
            all_sources.add(a.source)

    breadth = (
        f"共抓取 **{len(clusters[:8])}** 个事件聚类，覆盖 "
        f"**{len(categories)}** 个行业类别，来自 "
        f"**{len(all_sources)}** 个信息来源。"
    )
    lines = [
        f"- **{cluster.category}**：{cluster.title}（{len(cluster.articles)} 条来源）"
        for cluster in clusters[:8]
    ]
    detail = "\n".join(lines) or "- 最近 24 小时未抓取到可用财经新闻。"
    return f"{breadth}\n\n{detail}"


def build_fallback_report(report_date: date, clusters: list[EventCluster], llm_error: str | None) -> str:
    error_note = (
        f"\n\n> LLM 生成暂不可用，已输出规则模板草稿。错误：{llm_error}\n"
        if llm_error
        else ""
    )
    return "\n\n".join(
        [
            f"# 财经日报-{report_date.isoformat()}",
            REQUIRED_SECTIONS[0],
            f"最近 24 小时财经信息按主题聚合如下：\n\n{_cluster_summary(clusters)}{error_note}",
            REQUIRED_SECTIONS[1],
            _event_block(clusters),
            REQUIRED_SECTIONS[2],
            "事件催化需要继续验证需求端订单、供给端产能、价格变化与政策执行节奏。优先观察上游资源、核心设备、关键零部件、数据/算力基础设施和高壁垒服务环节。",
            REQUIRED_SECTIONS[3],
            "资金更该关注具备现金流韧性、行业份额提升、订单可验证、资产负债表健康、估值与盈利增速匹配的公司类型。本日报不提供买卖指令。",
            REQUIRED_SECTIONS[4],
            "请结合事件逻辑对以下方面进行核实验证：\n"
            "- **所属市场**：确认公司上市地点（A股 / 港股 / 美股）\n"
            "- **产业链环节**：确认公司在产业链中的具体位置\n"
            "- **受益原因**：分析事件与公司业务的实际关联与传导逻辑\n"
            "- **催化强度**：基于订单、政策、需求等可观测证据判断\n"
            "- **风险点**：审查业绩兑现风险、估值波动、行业竞争等\n\n"
            "| 公司 | 所属市场 | 所属产业链环节 | 受益原因 | 催化强度 | 风险点 |\n"
            "|---|---|---|---|---|---|\n"
            "| 待 LLM 补全 | A股 / 港股 / 美股 | 待核验 | 需结合事件与产业链位置确认 | 中 | 信息不足、业绩兑现不及预期 |",
            REQUIRED_SECTIONS[5],
            "- 新闻源可能存在延迟、重复、标题党或付费墙导致的信息缺口。\n- 产业链映射仅用于研究线索，不构成投资建议。\n- 需警惕政策落地不及预期、需求验证不足、估值波动和流动性变化。",
            REQUIRED_SECTIONS[6],
            "- 继续跟踪核心事件是否出现公告、订单、价格、库存、产能或监管文件验证。\n- 关注美股盘后、A股/港股开盘后的资金反馈与产业链扩散方向。",
        ]
    )
