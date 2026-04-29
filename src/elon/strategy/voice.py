"""Voice linter. Cheap, deterministic, fast — runs on every caption.

Rules sourced from BrandMemory.voice_json + forbidden_json. Returns a list of
violations; an empty list means the caption is compliant.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Violation:
    rule: str
    detail: str


def lint(caption: str, *, voice: dict, forbidden: dict, language: str | None = None) -> list[Violation]:
    """Lint a caption against voice rules.

    `voice` may be flat (the global rules) or contain a `by_language` map:
        voice = {..., "by_language": {"en": {...}, "fa": {...}}}
    When `language` is set and a per-language override exists, it merges over the
    flat rules. Same merging applies to `forbidden`.
    """
    if language:
        v_over = (voice.get("by_language") or {}).get(language) or {}
        f_over = (forbidden.get("by_language") or {}).get(language) or {}
        voice = {**voice, **v_over}
        forbidden = {**forbidden, **f_over}

    out: list[Violation] = []
    txt = caption or ""

    max_len = int(voice.get("max_caption_chars", 2200))
    if len(txt) > max_len:
        out.append(Violation("max_length", f"{len(txt)} > {max_len}"))

    banned_words: list[str] = forbidden.get("words", [])
    for w in banned_words:
        if re.search(rf"\b{re.escape(w)}\b", txt, flags=re.IGNORECASE):
            out.append(Violation("banned_word", w))

    banned_topics: list[str] = forbidden.get("topics", [])
    lowered = txt.lower()
    for t in banned_topics:
        if t.lower() in lowered:
            out.append(Violation("banned_topic", t))

    if voice.get("no_all_caps") and re.search(r"\b[A-Z]{4,}\b", txt):
        out.append(Violation("no_all_caps", "ALL-CAPS word detected"))

    if voice.get("no_emoji") and re.search(r"[\U0001F300-\U0001FAFF☀-➿]", txt):
        out.append(Violation("no_emoji", "emoji detected"))

    return out
