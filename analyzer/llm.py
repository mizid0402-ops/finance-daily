from __future__ import annotations

import os
from datetime import date

from openai import OpenAI

from analyzer.report import build_fallback_report, sanitize_investment_advice
from collector.models import EventCluster


SYSTEM_PROMPT = """你是严谨的财经日报编辑。请用中文输出 Markdown 财经日报。
必须遵守：
1. 不给买入、卖出、目标价等投资建议；
2. 所有公司映射都要说明市场、产业链环节、受益原因、催化强度、风险点；
3. 分析链路必须体现：事件催化 -> 产业需求与供给验证 -> 产业链受益环节 -> 资金更该关注什么类型的公司 -> 相关公司映射 -> 风险提示；
4. 保持标题结构完全一致。"""


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
                        "# 财经日报-YYYY-MM-DD\n\n"
                        "## 一、市场总览\n## 二、今日核心事件\n## 三、产业链受益方向\n"
                        "## 四、资金更该关注什么类型的公司\n## 五、相关公司映射\n"
                        "## 六、风险提示\n## 七、明日关注\n\n"
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
