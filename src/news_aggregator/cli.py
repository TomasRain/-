from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Optional

from .pipeline import NewsPipeline
from .search import DemoNewsClient, SerperNewsClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="news-aggregator",
        description="根据关键词聚合新闻并输出摘要",
    )
    parser.add_argument("keyword", help="热点关键词，如：AI 新模型")
    parser.add_argument("--limit", type=int, default=5, help="最大返回条数")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="使用离线演示数据（默认）",
    )
    parser.add_argument(
        "--serper",
        action="store_true",
        help="使用 Serper.dev 实时搜索，需要 SERPER_API_KEY",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="以 JSON 输出，便于调试",
    )
    return parser


def _resolve_client(args: argparse.Namespace):
    if args.serper:
        return SerperNewsClient()
    return DemoNewsClient()


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    client = _resolve_client(args)
    pipeline = NewsPipeline(search_client=client)
    result = pipeline.run(args.keyword, limit=args.limit)

    if args.as_json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=str))
        return

    print(f"\n# 关键词：{result.keyword}")
    print("## 汇总摘要")
    print(result.report)
    print("\n## 指标")
    print(
        f"请求 {result.stats.requested} 条，去重后 {result.stats.deduplicated} 条，"
        f"抓取正文 {result.stats.hydrated} 条，生成摘要 {result.stats.summarized} 条，"
        f"耗时约 {result.stats.duration_ms} ms"
    )
    print("\n## 详情")
    for idx, article in enumerate(result.articles, start=1):
        print(f"{idx}. {article.title} — {article.short_source()}")
        print(f"   链接: {article.url}")
        if article.summary:
            print(f"   摘要: {article.summary}")
        elif article.content:
            snippet = article.content[:150].replace("\n", " ")
            print(f"   正文摘录: {snippet}...")
        else:
            print("   暂无正文")


if __name__ == "__main__":
    main()
