from __future__ import annotations

from collector.models import Article


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "科技与半导体": ("ai", "人工智能", "芯片", "半导体", "server", "gpu", "nvidia", "amd", "tsmc", "算力"),
    "宏观与政策": ("fed", "federal reserve", "央行", "利率", "通胀", "政策", "财政", "关税", "cpi", "pmi"),
    "新能源与汽车": ("ev", "electric vehicle", "电动车", "新能源", "锂", "电池", "tesla", "比亚迪", "光伏"),
    "医药与消费": ("pharma", "drug", "fda", "医药", "消费", "retail", "零售", "食品", "旅游"),
    "金融与地产": ("bank", "银行", "保险", "券商", "mortgage", "real estate", "地产", "reits"),
    "能源与大宗": ("oil", "gas", "crude", "opec", "铜", "黄金", "煤炭", "原油", "天然气", "commodity"),
}


def classify_article(article: Article) -> str:
    text = f"{article.title} {article.summary}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in text for keyword in keywords):
            return category
    return "综合财经"
