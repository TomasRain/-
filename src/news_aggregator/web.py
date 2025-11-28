from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .cache import ResultCache
from .pipeline import NewsPipeline
from .search import DemoNewsClient, SerperNewsClient

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="新闻聚合助手", version="0.2.0")
CACHE = ResultCache[Tuple[str, str, int], Any](ttl=600.0, max_size=32)


def _build_pipeline(source: str) -> NewsPipeline:
    if source == "serper":
        return NewsPipeline(search_client=SerperNewsClient())
    return NewsPipeline(search_client=DemoNewsClient())


def _serialize_result(result, cached: bool = False) -> Dict[str, Any]:
    data = asdict(result)
    for article in data["articles"]:
        published_at: Optional[datetime] = article.get("published_at")
        if published_at:
            article["published_at"] = datetime.fromisoformat(str(published_at)).isoformat()
    data["cached"] = cached
    return data


def _run_with_cache(keyword: str, source: str, limit: int):
    cache_key = (source, keyword, limit)
    cached = CACHE.get(cache_key)
    if cached:
        return cached, True
    pipeline = _build_pipeline(source)
    result = pipeline.run(keyword, limit=limit)
    CACHE.set(cache_key, result)
    return result, False


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    q: str = Query("", description="关键词"),
    source: str = Query("demo", description="数据源 demo/serper"),
    limit: int = Query(5, ge=1, le=10),
):
    result = None
    error = None
    cached = False
    if q:
        try:
            result, cached = _run_with_cache(q, source, limit)
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "keyword": q,
            "source": source,
            "limit": limit,
            "cached": cached,
            "error": error,
        },
    )


@app.get("/api/search", response_class=JSONResponse)
async def api_search(
    q: str = Query(..., description="关键词"),
    source: str = Query("demo", description="数据源 demo/serper"),
    limit: int = Query(5, ge=1, le=10),
):
    result, cached = _run_with_cache(q, source, limit)
    return _serialize_result(result, cached=cached)


__all__ = ["app"]
