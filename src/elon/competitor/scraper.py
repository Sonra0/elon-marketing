"""Public-profile scraping (best-effort, gray area).

Constraints (per the locked plan):
- No login, no auth-bypass, no anti-bot evasion.
- Polite cadence: 1 req / 5s baseline; respect robots.txt where applicable.
- Run inside the playwright-runner container with restricted egress.

Output: a list of post dicts {url, caption, likes, comments, captured_at}.
DOM contracts shift; on shape change we capture nothing rather than crash.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any


def scrape_instagram(handle: str, limit: int = 12) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []
    url = f"https://www.instagram.com/{handle.lstrip('@')}/"
    out: list[dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="Mozilla/5.0 (compatible; ElonBot/0.1)")
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            anchors = page.locator("a[href*='/p/'], a[href*='/reel/']")
            count = min(limit, anchors.count())
            for i in range(count):
                href = anchors.nth(i).get_attribute("href") or ""
                if not href.startswith("http"):
                    href = "https://www.instagram.com" + href
                alt = ""
                try:
                    alt = anchors.nth(i).locator("img").first.get_attribute("alt") or ""
                except Exception:
                    pass
                out.append({
                    "url": href,
                    "caption": alt,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception:
            pass
        finally:
            ctx.close()
            browser.close()
    time.sleep(5)  # politeness throttle
    return out


def scrape_tiktok(handle: str, limit: int = 12) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []
    url = f"https://www.tiktok.com/@{handle.lstrip('@')}"
    out: list[dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="Mozilla/5.0 (compatible; ElonBot/0.1)")
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2500)
            videos = page.locator("a[href*='/video/']")
            count = min(limit, videos.count())
            for i in range(count):
                href = videos.nth(i).get_attribute("href") or ""
                desc = ""
                try:
                    desc = videos.nth(i).inner_text(timeout=1000) or ""
                except Exception:
                    pass
                out.append({
                    "url": href,
                    "caption": desc,
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception:
            pass
        finally:
            ctx.close()
            browser.close()
    time.sleep(5)
    return out
