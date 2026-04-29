"""Visual signal extraction: dominant palette from a list of image bytes."""

from __future__ import annotations

import io

from colorthief import ColorThief


def palette_from_bytes(data: bytes, color_count: int = 6) -> list[str]:
    """Returns hex strings, e.g. ['#1a1a1a', ...]."""
    try:
        ct = ColorThief(io.BytesIO(data))
        colors = ct.get_palette(color_count=color_count, quality=10)
    except Exception:
        return []
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in colors]
