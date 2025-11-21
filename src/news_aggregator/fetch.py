from __future__ import annotations

from typing import Optional


def fetch_article_content(url: str, timeout: int = 10) -> Optional[str]:
    """拉取网页正文内容，无法提取时返回 ``None``。

    仅在需要真实抓取时调用，离线演示数据会直接携带 ``content`` 字段。
    """

    try:
        import requests
        import trafilatura
    except Exception:
        return None

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        extracted = trafilatura.extract(response.text, include_images=False)
        return extracted
    except Exception:
        return None
