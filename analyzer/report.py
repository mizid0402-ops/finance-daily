from __future__ import annotations

import re
from datetime import date

from collector.models import EventCluster


REQUIRED_SECTIONS = [
    "【核心事件】",
    "【产业逻辑】",
    "【投资框架】",
    "【资金更该买什么类型的公司】",
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


def _report_title(report_date: date) -> str:
    return f"{report_date.month}月{report_date.day}日信息总结"


def _stock_ideas(cluster: EventCluster) -> list[str]:
    text = f"{cluster.title} {cluster.category} {' '.join(cluster.keywords)}".lower()
    ideas_by_theme = [
        (("ai", "芯片", "半导体", "算力"), ["中芯国际", "北方华创"]),
        (("机器人", "减速器", "执行器", "液冷"), ["汇川技术", "埃斯顿"]),
        (("光通信", "光芯片", "cpo", "pcb"), ["中际旭创", "沪电股份"]),
        (("存储", "封装", "材料", "ddr"), ["长电科技", "雅克科技"]),
        (("新能源", "储能", "电池", "光伏"), ["宁德时代", "阳光电源"]),
    ]
    for tokens, ideas in ideas_by_theme:
        if any(token in text for token in tokens):
            return ideas
    return ["行业龙头", "关键设备/材料卡位公司"]


def _capital_focus(cluster: EventCluster) -> str:
    stock_ideas = "、".join(_stock_ideas(cluster)[:2])
    return (
        "资金应优先寻找订单已验证、客户明确、即将或正在量产的公司；其次关注行业龙头"
        "或关键环节卡位公司，要求具备技术壁垒和议价能力；再筛选受益于高端化、"
        "产品升级、国产替代，且产能释放明确、收入和利润有望连续上修的标的。"
        "若估值合理且市场预期尚未充分反映业绩改善，可作为重点跟踪方向。"
        "仅有概念、无订单、无客户验证或估值过高的公司应提示风险。"
        f"\n\n个股线索：{stock_ideas}（仅作研究线索，需继续核验订单、客户、量产和估值）。"
    )


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
                    f"## {index:02d} {cluster.category}",
                    "",
                    "【核心事件】",
                    f"{cluster.title}。关键词：{keywords}。信息置信度：{confidence}。",
                    "",
                    "【产业逻辑】",
                    "事件催化需要继续验证需求端订单、供给端产能、价格变化与政策执行节奏。"
                    f"当前主题指向 {cluster.category}，资金会更关注从上游资源、核心设备、"
                    "关键零部件到下游应用的兑现链条。",
                    "",
                    "【投资框架】",
                    "围绕“供应链需求 + 国产导入 + 高端产品放量”三条主线，关注订单、客户、"
                    "量产、毛利率和产能利用率的连续验证，避免只按概念热度定价。",
                    "",
                    "【资金更该买什么类型的公司】",
                    _capital_focus(cluster),
                    "",
                    "来源：",
                    _format_sources(cluster),
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
    title = _report_title(report_date)
    summary = _cluster_summary(clusters)
    return "\n\n".join(
        [
            f"# {title}",
            "AI 摘要",
            "阶段重点 | 产业逻辑 | 投资线索",
            f"最近 24 小时财经信息按主题聚合如下：\n\n{summary}{error_note}",
            _event_block(clusters),
            "## 风险提示",
            "- 新闻源可能存在延迟、重复、标题党或付费墙导致的信息缺口。\n"
            "- 个股线索仅用于研究跟踪，不构成投资建议。\n"
            "- 需警惕政策落地不及预期、需求验证不足、估值波动和流动性变化。",
        ]
    )
