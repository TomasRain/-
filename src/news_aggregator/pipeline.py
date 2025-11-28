from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable, List

from .fetch import fetch_article_content
from .models import Article, PipelineStats
from .search import DemoNewsClient, NewsClient
from .summary import simple_summarize, summarize_articles


@dataclass
class NewsResult:
    keyword: str
    articles: List[Article]
    report: str
    stats: PipelineStats


class NewsPipeline:
    """组装检索、抓取与摘要的最小闭环。"""

    def __init__(self, search_client: NewsClient | None = None, max_workers: int = 8):
        self.search_client = search_client or DemoNewsClient()
        self.max_workers = max_workers

    def run(self, keyword: str, limit: int = 5) -> NewsResult:
        started = perf_counter()
        articles = self.search_client.search(keyword, limit=limit)
        deduped = self._deduplicate(articles)
        hydrated = self._hydrate_batch(deduped)
        summarized = self._summarize_missing(hydrated)
        report = summarize_articles(summarized)
        elapsed_ms = round((perf_counter() - started) * 1000, 1)
        stats = PipelineStats(
            requested=len(articles),
            deduplicated=len(deduped),
            hydrated=sum(1 for a in hydrated if a.content),
            summarized=sum(1 for a in summarized if a.summary),
            duration_ms=elapsed_ms,
        )
        return NewsResult(keyword=keyword, articles=summarized, report=report, stats=stats)

    @staticmethod
    def _deduplicate(articles: Iterable[Article]) -> List[Article]:
        seen = set()
        unique: List[Article] = []
        for article in articles:
            title_key = (article.title or "").strip().lower()
            url_key = (article.url or "").strip().lower()
            key = (title_key, url_key)
            if not any(key):
                continue
            if key not in seen:
                seen.add(key)
                unique.append(article)
        return unique

    def _hydrate_batch(self, articles: Iterable[Article]) -> List[Article]:
        items = list(articles)
        if not items:
            return items
        try:
            from concurrent.futures import ThreadPoolExecutor

            workers = min(self.max_workers, max(1, len(items)))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                return list(executor.map(self._hydrate_content, items))
        except Exception:
            return [self._hydrate_content(article) for article in items]

    def _summarize_missing(self, articles: Iterable[Article]) -> List[Article]:
        items = list(articles)
        to_summarize = [a for a in items if not a.summary]
        if not to_summarize:
            return items
        try:
            from concurrent.futures import ThreadPoolExecutor

            workers = min(self.max_workers, max(1, len(to_summarize)))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                summaries = list(
                    executor.map(lambda art: simple_summarize(art.content or ""), to_summarize)
                )
            for article, summary in zip(to_summarize, summaries):
                article.summary = summary
            return items
        except Exception:
            for article in to_summarize:
                article.summary = simple_summarize(article.content or "")
            return items

    @staticmethod
    def _hydrate_content(article: Article) -> Article:
        if article.content:
            return article
        article.content = fetch_article_content(article.url) or ""
        return article
