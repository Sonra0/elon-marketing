"""Fetch a website + extract textual signals + a small set of representative images."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass
class WebsiteSignals:
    url: str
    title: str = ""
    description: str = ""
    headings: list[str] = field(default_factory=list)
    body_excerpt: str = ""
    image_urls: list[str] = field(default_factory=list)


def fetch(url: str, timeout: float = 15) -> WebsiteSignals:
    r = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"User-Agent": "ElonBot/0.1"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else ""
    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    desc = (desc_tag.get("content") or "").strip() if desc_tag else ""
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2"])][:20]
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    body = " ".join(paragraphs)[:4000]
    base = urlparse(url)
    img_urls: list[str] = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        absolute = urljoin(f"{base.scheme}://{base.netloc}", src)
        if absolute.startswith("http"):
            img_urls.append(absolute)
        if len(img_urls) >= 8:
            break
    return WebsiteSignals(
        url=url, title=title, description=desc, headings=headings, body_excerpt=body, image_urls=img_urls
    )
