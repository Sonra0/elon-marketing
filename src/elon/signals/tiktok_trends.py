"""TikTok Creative Center trending keywords scrape via Playwright.

Creative Center is public and doesn't require auth, but its DOM changes; we
extract via a robust selector chain and fall back gracefully if the page schema
shifts. Treat output as best-effort.
"""

from __future__ import annotations

import json
from typing import Any

URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"


def fetch_trending_hashtags(country: str = "US", limit: int = 20) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []
    out: list[dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="Mozilla/5.0 (compatible; ElonBot/0.1)")
        page = ctx.new_page()
        try:
            page.goto(URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            # Pull JSON-LD or any embedded next-data; Creative Center ships __NEXT_DATA__.
            next_data = page.locator("#__NEXT_DATA__").inner_text(timeout=5000)
            tree = json.loads(next_data)
            buckets = (
                tree.get("props", {})
                .get("pageProps", {})
                .get("hashtagList", [])
            )
            for entry in buckets[:limit]:
                out.append({
                    "topic": entry.get("hashtag_name") or entry.get("hashtag"),
                    "score": float(entry.get("trend_score", 0) or 0),
                    "evidence": {k: entry.get(k) for k in ("publish_cnt", "video_views", "rank")},
                })
        except Exception:
            pass
        finally:
            ctx.close()
            browser.close()
    return out
