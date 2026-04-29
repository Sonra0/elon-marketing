"""Gap analysis: given the tenant's own pillars + recent competitor content, ask
Claude to surface themes competitors over/under-index on relative to the brand.
"""

from __future__ import annotations

import json
from typing import Any

from elon.core.llm import call_claude

SYSTEM = """\
You are a competitive content analyst. Compare a brand's pillars to competitors'
recent posts. Identify:
  - over_indexed: themes competitors push that the brand barely touches.
  - under_indexed: themes the brand owns that competitors ignore (defensible).
  - white_space: themes neither side pushes that fit the brand.
Return ONLY JSON: {"over_indexed":[str], "under_indexed":[str], "white_space":[str]}.
"""


def find_gaps(*, tenant_id: str, brand_pillars: list[dict], competitor_posts: list[dict]) -> dict[str, Any]:
    user_payload = json.dumps({
        "brand_pillars": brand_pillars,
        "competitor_posts": [
            {"caption": p.get("caption", "")[:300], "url": p.get("url")} for p in competitor_posts[:50]
        ],
    })
    resp = call_claude(
        tenant_id=tenant_id,
        system_blocks=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_payload}],
        max_tokens=600,
    )
    txt = "".join(b.text for b in resp.content if b.type == "text").strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return {"over_indexed": [], "under_indexed": [], "white_space": [], "raw": txt[:500]}
