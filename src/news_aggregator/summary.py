from __future__ import annotations

from typing import Iterable, List

from .models import Article


def simple_summarize(content: str, max_sentences: int = 3) -> str:
    """基于分句的轻量摘要，适合离线示例或预处理。"""

    if not content:
        return ""
    separators = "。！？!?\n"
    sentences: List[str] = []
    buffer = ""
    for ch in content:
        buffer += ch
        if ch in separators:
            cleaned = buffer.strip()
            if cleaned:
                sentences.append(cleaned)
            buffer = ""
        if len(sentences) >= max_sentences:
            break
    if len(sentences) < max_sentences and buffer.strip():
        sentences.append(buffer.strip())
    return " ".join(sentences[:max_sentences])


def summarize_articles(articles: Iterable[Article]) -> str:
    """将多篇文章的摘要合并成要点列表。"""

    bullet_points = []
    for idx, article in enumerate(articles, start=1):
        snippet = article.summary or simple_summarize(article.content or "")
        if snippet:
            bullet_points.append(f"{idx}. [{article.title}]({article.url}) — {snippet}")
        else:
            bullet_points.append(f"{idx}. [{article.title}]({article.url}) — 暂无摘要")
    return "\n".join(bullet_points)
