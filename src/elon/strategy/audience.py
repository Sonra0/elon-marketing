"""Audience segments. Stored in BrandMemory.audience_json.personas: list[dict]."""

from __future__ import annotations

from typing import Any


def personas(brand_memory: dict[str, Any]) -> list[dict]:
    return list((brand_memory.get("audience_json") or {}).get("personas") or [])


def pick_default(brand_memory: dict[str, Any]) -> dict | None:
    ps = personas(brand_memory)
    return ps[0] if ps else None
