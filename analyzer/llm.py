from __future__ import annotations

import os
from datetime import date

from openai import OpenAI

from analyzer.report import build_fallback_report, sanitize_investment_advice
from collector.models import EventCluster


SYSTEM_PROMPT = """你是严谨的财经日报编辑。请用中文输出 Markdown 财经日报。
必须遵守：
1. 输出图片式摘要卡片结构：先写“# AI 摘要”，再写“# M月D日信息总结”，再按主题写“## 01 主题名”；
2. 每个主题卡片必须包含【核心事件】、【产业逻辑】、【投资框架】、【资金更该买什么类型的公司】；
3. 【资金更该买什么类型的公司】可以列出 1 到 2 个个股线索，但重点必须总结资金应优先寻找的公司特征；
4. 公司特征优先级从高到低：订单已验证、客户明确、即将或正在量产；行业龙头或关键环节卡位且有技术壁垒和议价能力；高端化、产品升级、国产替代；产能释放明确且收入利润有望连续上修；估值合理且预期未充分反映改善；
5. 仅有概念、无订单、无客户验证、估值过高的公司必须提示风险；
6. 不输出目标价、收益率承诺、强烈买入/卖出等指令。"""


def _cluster_payload(clusters: list[EventCluster]) -> str:
    blocks: list[str] = []
    for cluster in clusters[:10]:
        articles = "\n".join(
            f"- {article.title} | {article.source} | {article.url} | {article.summary[:300]}"
            for article in cluster.articles[:6]
        )
        blocks.append(
            f"事件：{cluster.title}\n分类：{cluster.category}\n关键词：{', '.join(cluster.keywords)}\n来源：\n{articles}"
        )
    return "\n\n".join(blocks)


def generate_report_with_llm(report_date: date, clusters: list[EventCluster]) -> tuple[str, str | None]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "deepseek-chat")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key:
        return build_fallback_report(report_date, clusters, "OPENAI_API_KEY is not set"), "OPENAI_API_KEY is not set"

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    try:
        client = OpenAI(**client_kwargs)
        completion = client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"请生成 {report_date.isoformat()} 的财经日报。\n\n"
                        "固定结构：\n"
                        "# AI 摘要\n"
                        "# M月D日信息总结\n"
                        "阶段重点 | 产业逻辑 | 投资线索\n\n"
                        "## 01 主题名\n"
                        "【核心事件】\n"
                        "【产业逻辑】\n"
                        "【投资框架】\n"
                        "【资金更该买什么类型的公司】\n\n"
                        "每个主题只列 1 到 2 个个股线索，且必须强调订单、客户、量产、龙头卡位、"
                        "国产替代、产能释放、估值合理性和概念炒作风险。\n\n"
                        f"候选事件：\n{_cluster_payload(clusters)}"
                    ),
                },
            ],
        )
        content = completion.choices[0].message.content or ""
        if not content.strip():
            raise RuntimeError("LLM returned empty content")
        return sanitize_investment_advice(content), None
    except Exception as exc:  # noqa: BLE001 - fallback report must survive provider failures.
        return build_fallback_report(report_date, clusters, str(exc)), str(exc)
