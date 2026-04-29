"""Anthropic client wrapper with prompt caching + per-tenant spend tracking.

Approximate pricing per 1M tokens (USD). Update when Anthropic changes rates.
Sonnet is the default; Opus is reserved for the planner and crisis classification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import anthropic

from elon.core.logging import get_logger
from elon.core.settings import get_settings
from elon.core.spend import add_cost

log = get_logger(__name__)


@dataclass(frozen=True)
class Price:
    input: float
    output: float
    cache_read: float
    cache_write: float


PRICES: dict[str, Price] = {
    # claude-sonnet-4-6
    "claude-sonnet-4-6": Price(input=3.0, output=15.0, cache_read=0.30, cache_write=3.75),
    # claude-opus-4-7
    "claude-opus-4-7": Price(input=15.0, output=75.0, cache_read=1.50, cache_write=18.75),
}


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=get_settings().anthropic_api_key)


def cost_usd(model: str, usage: Any) -> float:
    p = PRICES.get(model)
    if p is None:
        return 0.0
    inp = getattr(usage, "input_tokens", 0) or 0
    out = getattr(usage, "output_tokens", 0) or 0
    cw = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cr = getattr(usage, "cache_read_input_tokens", 0) or 0
    return (inp * p.input + out * p.output + cw * p.cache_write + cr * p.cache_read) / 1_000_000


def call_claude(
    *,
    tenant_id: str,
    system_blocks: list[dict],
    messages: list[dict],
    tools: list[dict] | None = None,
    tool_choice: dict | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
) -> Any:
    # Per-tenant LLM rate gate: 60 calls / minute by default.
    from elon.core.ratelimit import hit
    hit("llm", tenant_id, capacity=60, window_s=60)
    """Single Claude call. `system_blocks` is a list of content blocks (so the
    long, stable parts can carry `cache_control`). Tracks spend per tenant.
    """
    settings = get_settings()
    mdl = model or settings.anthropic_model_default
    kwargs: dict[str, Any] = {
        "model": mdl,
        "max_tokens": max_tokens,
        "system": system_blocks,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
    if tool_choice:
        kwargs["tool_choice"] = tool_choice

    resp = _client().messages.create(**kwargs)
    usd = cost_usd(mdl, resp.usage)
    add_cost(tenant_id, usd, kind=f"llm:{mdl}")
    return resp
