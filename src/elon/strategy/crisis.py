"""Crisis / sensitive-topic classifier.

A short Claude call returns: {sensitive: bool, topics: [str], reason: str}.
Conservative bias: when in doubt, mark sensitive. The agent uses this to
flip `requires_human_review=True` and route through the hardened approval flow.
"""

from __future__ import annotations

import json
from typing import Any

from elon.core.llm import call_claude


SYSTEM = """\
You classify whether a piece of marketing copy touches sensitive ground.
Sensitive includes: medical/health claims, financial advice, politics, religion,
identity, race/ethnicity, alcohol/drugs/gambling, minors, violence, controversy,
or anything that could trigger backlash.

Return ONLY JSON: {"sensitive": bool, "topics": [str], "reason": str}.
When in doubt, mark sensitive=true.
"""


def classify(*, tenant_id: str, text: str) -> dict[str, Any]:
    resp = call_claude(
        tenant_id=tenant_id,
        system_blocks=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": text}],
        max_tokens=300,
    )
    txt = "".join(b.text for b in resp.content if b.type == "text").strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return {"sensitive": True, "topics": ["parse_error"], "reason": txt[:500]}
