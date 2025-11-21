from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .pipeline import NewsPipeline
from .search import DemoNewsClient, SerperNewsClient

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="新闻聚合助手", version="0.1.0")


def _build_pipeline(source: str) -> NewsPipeline:
    if source == "serper":
        return NewsPipeline(search_client=SerperNewsClient())
    return NewsPipeline(search_client=DemoNewsClient())


def _serialize_result(result) -> Dict[str, Any]:
    data = asdict(result)
    for article in data["articles"]:
        published_at: Optional[datetime] = article.get("published_at")
        if published_at:
            article["published_at"] = datetime.fromisoformat(str(published_at)).isoformat()
    return data


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    q: str = Query("", description="关键词"),
    source: str = Query("demo", description="数据源 demo/serper"),
    limit: int = Query(5, ge=1, le=10),
):
    result = None
    error = None
    if q:
        try:
            pipeline = _build_pipeline(source)
            result = pipeline.run(q, limit=limit)
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
            "error": error,
        },
    )


@app.get("/api/search", response_class=JSONResponse)
async def api_search(
    q: str = Query(..., description="关键词"),
    source: str = Query("demo", description="数据源 demo/serper"),
    limit: int = Query(5, ge=1, le=10),
):
    pipeline = _build_pipeline(source)
    result = pipeline.run(q, limit=limit)
    return _serialize_result(result)


__all__ = ["app"]
