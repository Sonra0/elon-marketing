"""Content pillars helpers.

Pillars live in BrandMemory.pillars_json as a list of dicts:
  [{"id": str, "name": str, "description": str, "weight": float}, ...]
"""

from __future__ import annotations

from typing import Any


def list_pillars(brand_memory: dict[str, Any]) -> list[dict]:
    return list(brand_memory.get("pillars_json") or [])


def find(brand_memory: dict[str, Any], pillar_id: str) -> dict | None:
    for p in list_pillars(brand_memory):
        if p.get("id") == pillar_id:
            return p
    return None
