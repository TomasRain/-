from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, List

from .models import Article


class NewsClient:
    """新闻检索客户端接口。"""

    def search(self, keyword: str, limit: int = 5) -> List[Article]:
        raise NotImplementedError


class DemoNewsClient(NewsClient):
    """提供离线演示数据，便于快速体验。"""

    SAMPLE = [
        Article(
            title="新一代大模型在医疗总结场景表现突出",
            url="https://example.com/ai-healthcare",
            source="TechDaily",
            published_at=datetime.utcnow(),
            content=(
                "多家研究机构宣布合作测试新一代中文大模型，在医疗总结场景中"
                "展现出更高的准确率和可解释性。研究团队表示，新模型在"
                "病例摘要、影像报告草稿生成上均取得显著提升。"
            ),
        ),
        Article(
            title="国际巨头加码可持续能源，新能源投资创新高",
            url="https://example.com/green-energy",
            source="GlobalNews",
            published_at=datetime.utcnow(),
            content=(
                "最新财报显示，国际能源巨头在可持续能源领域的投资规模持续扩大，"
                "风电与光伏项目带动整体营收增长。业内分析指出，政策激励与"
                "储能技术进步共同促成本轮增长。"
            ),
        ),
        Article(
            title="高校团队发布开源多模态模型，强调低算力友好",
            url="https://example.com/open-source-mm",
            source="CampusLab",
            published_at=datetime.utcnow(),
            content=(
                "一支高校研究团队发布了低算力友好的开源多模态模型，"
                "支持图文问答与描述生成。项目在 README 中提供了详尽的部署教程，"
                "并特别针对 8GB GPU 环境做了优化。"
            ),
        ),
    ]

    def search(self, keyword: str, limit: int = 5) -> List[Article]:
        sliced = self.SAMPLE[:limit]
        return [Article(**article.__dict__) for article in sliced]


class SerperNewsClient(NewsClient):
    """简单封装 Serper.dev 新闻搜索 API。"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("需要 SERPER_API_KEY 环境变量或传入 api_key。")

    def search(self, keyword: str, limit: int = 5) -> List[Article]:
        url = "https://google.serper.dev/search"
        payload = {"q": keyword, "gl": "cn", "hl": "zh-cn", "num": limit}
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        import requests

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        organic: Iterable[dict] = data.get("news", [])
        articles: List[Article] = []
        for item in organic:
            articles.append(
                Article(
                    title=item.get("title") or "",
                    url=item.get("link") or "",
                    source=item.get("source") or "unknown",
                    published_at=_parse_datetime(item.get("date")),
                )
            )
        return articles[:limit]


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None
