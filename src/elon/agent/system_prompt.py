"""Builds the cached system prompt for an agent session.

Layout (from stable to volatile so cache stays warm):
1. Static instructions (role + global rules).         <- cache_control
2. Brand memory (voice + pillars + audience).         <- cache_control
3. Recent feedback + last analytics deltas.            (no cache; volatile)
"""

from __future__ import annotations

from typing import Any

STATIC_INSTRUCTIONS = """\
You are Elon, an autonomous senior brand-marketing specialist. You collaborate with one human operator per tenant.

Knowledge-conflict resolution (in order, top wins):
1. Explicit user instruction in this conversation.
2. The tenant's brand memory.
3. Analytics signal from this tenant's prior posts.
4. External trends.

Operating rules:
- Every post must cite a pillar from the brand memory.
- Every caption must obey the voice rules; if it cannot, return a caveat in `reason`.
- For sensitive topics (health claims, politics, identity, crisis), set requires_human_review=true.
- Output strict JSON when the user asks for a draft. The contract is:
  {"idea": str, "hook": str, "caption": str, "cta": str,
   "platform": "ig"|"tiktok"|"fb",
   "reason": str, "expected_result": str,
   "score": {"impact": 0-100, "effort": 0-100, "risk": 0-100}}
- Prefer concise, platform-native writing. Hooks are <=12 words. Captions respect platform character limits.
- Use tools for retrieval and persistence; do not invent facts about the brand.
"""


def build_system_blocks(
    *,
    brand_memory: dict[str, Any] | None,
    recent_feedback: list[dict] | None = None,
    analytics_snapshot: dict | None = None,
) -> list[dict]:
    blocks: list[dict] = [
        {"type": "text", "text": STATIC_INSTRUCTIONS, "cache_control": {"type": "ephemeral"}},
    ]
    if brand_memory:
        bm_text = (
            "Brand memory (current version):\n"
            f"- voice: {brand_memory.get('voice_json', {})}\n"
            f"- pillars: {brand_memory.get('pillars_json', [])}\n"
            f"- audience: {brand_memory.get('audience_json', {})}\n"
            f"- offering: {brand_memory.get('offering_json', {})}\n"
            f"- positioning: {brand_memory.get('positioning_json', {})}\n"
            f"- forbidden: {brand_memory.get('forbidden_json', {})}\n"
        )
        blocks.append({"type": "text", "text": bm_text, "cache_control": {"type": "ephemeral"}})
    volatile_parts: list[str] = []
    if recent_feedback:
        volatile_parts.append("Recent operator feedback:\n" + "\n".join(
            f"- [{f.get('sentiment','?')}] {f.get('free_text','')}" for f in recent_feedback
        ))
    if analytics_snapshot:
        volatile_parts.append(f"Latest analytics rollup: {analytics_snapshot}")
    if volatile_parts:
        blocks.append({"type": "text", "text": "\n\n".join(volatile_parts)})
    return blocks
