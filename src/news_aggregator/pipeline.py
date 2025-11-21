from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .fetch import fetch_article_content
from .models import Article
from .search import DemoNewsClient, NewsClient
from .summary import simple_summarize, summarize_articles


@dataclass
class NewsResult:
    keyword: str
    articles: List[Article]
    report: str


class NewsPipeline:
    """组装检索、抓取与摘要的最小闭环。"""

    def __init__(self, search_client: NewsClient | None = None):
        self.search_client = search_client or DemoNewsClient()

    def run(self, keyword: str, limit: int = 5) -> NewsResult:
        articles = self.search_client.search(keyword, limit=limit)
        articles = self._deduplicate(articles)
        hydrated = [self._hydrate_content(article) for article in articles]
        for article in hydrated:
            if not article.summary:
                article.summary = simple_summarize(article.content or "")
        report = summarize_articles(hydrated)
        return NewsResult(keyword=keyword, articles=hydrated, report=report)

    @staticmethod
    def _deduplicate(articles: Iterable[Article]) -> List[Article]:
        seen = set()
        unique: List[Article] = []
        for article in articles:
            key = article.title.strip().lower()
            if key and key not in seen:
                seen.add(key)
                unique.append(article)
        return unique

    @staticmethod
    def _hydrate_content(article: Article) -> Article:
        if article.content:
            return article
        article.content = fetch_article_content(article.url) or ""
        return article
