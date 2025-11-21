"""新闻热点聚合与总结助手的最小实现。

该包提供关键词检索、正文拉取、去重和摘要的简单管线，
默认包含离线演示数据，便于在无 API Key 或网络受限时体验。
"""

__all__ = [
    "Article",
    "NewsPipeline",
]

from .models import Article
from .pipeline import NewsPipeline
