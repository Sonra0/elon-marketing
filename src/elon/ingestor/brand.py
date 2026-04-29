"""Brand ingestor entrypoint.

Inputs:
  - website_url: optional
  - asset_keys: list of S3 keys for already-uploaded raw assets (image/video/pdf)
  - notes: free-text from the operator (industry, audience hints, anything)

Output: persisted BrandMemory v1 + MemoryEvent + a Telegram confirmation card.
"""

from __future__ import annotations

import base64
import json
from typing import Any
from uuid import UUID

import httpx

from elon.core.db import session_scope
from elon.core.llm import call_claude
from elon.core.logging import get_logger
from elon.core.models import User
from elon.core.storage import get_object
from elon.ingestor.visual import palette_from_bytes
from elon.ingestor.website import fetch as fetch_website
from elon.memory.brand import write_new_version
from elon.memory.events import append as append_event
from sqlalchemy import select

log = get_logger(__name__)


SYSTEM = """\
You are extracting a brand identity profile from raw inputs (website text, palette,
operator notes, optional images). Produce ONLY JSON matching:

{
  "voice_json": {"tone": [str], "do": [str], "dont": [str], "max_caption_chars": int},
  "visual_json": {"palette": [hex...], "typography": {"primary": str, "accent": str},
                   "mood": [str]},
  "offering_json": {"category": str, "products_or_services": [str], "value_props": [str]},
  "audience_json": {"personas": [{"id": str, "name": str, "summary": str, "needs": [str]}]},
  "positioning_json": {"oneliner": str, "differentiators": [str]},
  "pillars_json": [{"id": str, "name": str, "description": str, "weight": 0-1}],
  "forbidden_json": {"words": [str], "topics": [str]}
}

Be concrete. Pick 3-5 pillars. Be conservative with claims - if the inputs do not
support a field, leave it empty rather than inventing.
"""


def _image_block(image_bytes: bytes, media_type: str = "image/jpeg") -> dict[str, Any]:
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64.b64encode(image_bytes).decode("ascii"),
        },
    }


def _maybe_fetch_image(url: str, max_bytes: int = 2_000_000) -> bytes | None:
    try:
        r = httpx.get(url, timeout=10, follow_redirects=True, headers={"User-Agent": "ElonBot/0.1"})
        r.raise_for_status()
        if len(r.content) > max_bytes:
            return None
        return r.content
    except Exception:
        return None


def ingest_brand(
    *,
    tenant_id: str,
    website_url: str | None = None,
    asset_keys: list[str] | None = None,
    notes: str | None = None,
    notify_telegram: bool = True,
) -> dict[str, Any]:
    tenant_uuid = UUID(tenant_id)
    sources: list[dict] = []
    image_blocks: list[dict] = []
    palettes: list[list[str]] = []

    if website_url:
        site = fetch_website(website_url)
        sources.append(
            {"kind": "website", "url": site.url, "title": site.title, "description": site.description,
             "headings": site.headings, "body_excerpt": site.body_excerpt}
        )
        # pull a couple of representative images for vision + palette
        for img_url in site.image_urls[:3]:
            data = _maybe_fetch_image(img_url)
            if not data:
                continue
            palettes.append(palette_from_bytes(data))
            image_blocks.append(_image_block(data))

    if asset_keys:
        for key in asset_keys[:5]:
            try:
                data = get_object(key)
            except Exception as e:
                log.warning("asset_fetch_failed", key=key, error=str(e))
                continue
            palettes.append(palette_from_bytes(data))
            # Best-effort: assume image for vision; non-images skipped silently.
            if data[:3] in (b"\xff\xd8\xff", b"\x89PN", b"GIF") or data[:4] == b"RIFF":
                image_blocks.append(_image_block(data))
            sources.append({"kind": "asset", "s3_key": key})

    user_text = "Operator notes:\n" + (notes or "(none)") + "\n\nSources:\n" + json.dumps(sources, indent=2)
    if palettes:
        user_text += f"\n\nDetected palettes (dominant first): {palettes}"

    user_content: list[dict] = [{"type": "text", "text": user_text}, *image_blocks]

    resp = call_claude(
        tenant_id=tenant_id,
        system_blocks=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_content}],
        max_tokens=2000,
    )
    raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    try:
        memory = json.loads(raw)
    except json.JSONDecodeError as e:
        log.error("ingest_parse_failed", error=str(e), raw_excerpt=raw[:500])
        raise

    with session_scope() as db:
        bm = write_new_version(
            db,
            tenant_uuid,
            voice_json=memory.get("voice_json", {}),
            visual_json=memory.get("visual_json", {}),
            offering_json=memory.get("offering_json", {}),
            audience_json=memory.get("audience_json", {}),
            positioning_json=memory.get("positioning_json", {}),
            pillars_json=memory.get("pillars_json", []),
            forbidden_json=memory.get("forbidden_json", {}),
            source_refs=sources,
        )
        append_event(
            db, tenant_uuid,
            type="brand_memory_v" + str(bm.version),
            actor="agent",
            payload={"version": bm.version, "summary": memory.get("positioning_json", {})},
        )
        owner = db.execute(
            select(User).where(User.tenant_id == tenant_uuid, User.role == "owner")
        ).scalar_one_or_none()
        owner_chat_id = owner.telegram_user_id if owner else None

    if notify_telegram and owner_chat_id:
        from elon.chat.notify import send_telegram
        summary = (
            f"Brand memory v{bm.version} drafted.\n\n"
            f"Positioning: {memory.get('positioning_json', {}).get('oneliner','-')}\n"
            f"Pillars: {', '.join(p.get('name','') for p in memory.get('pillars_json', []))}\n"
            f"Voice tone: {', '.join(memory.get('voice_json', {}).get('tone', []))}\n\n"
            f"Reply with 'confirm v{bm.version}' to lock it in or send corrections."
        )
        send_telegram(owner_chat_id, summary)

    return {"version": bm.version, "memory": memory}
