"""News + general web search via Tavily.

Tavily returns ranked results with summaries, ideal for daily topic discovery.
Falls back to no-op silently when the API key is missing.
"""

from __future__ import annotations

from typing import Any

import httpx

from elon.core.settings import get_settings


def search(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.tavily_api_key:
        return []
    r = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": settings.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "topic": "news",
            "max_results": max_results,
            "include_answer": False,
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json().get("results", [])
