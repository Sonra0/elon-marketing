from elon.strategy.voice import lint


def test_clean_caption_no_violations():
    assert lint("This is a clean caption.", voice={}, forbidden={}) == []


def test_max_length():
    voice = {"max_caption_chars": 20}
    v = lint("a" * 21, voice=voice, forbidden={})
    assert any(x.rule == "max_length" for x in v)


def test_banned_word():
    v = lint("Try our amazing thing", voice={}, forbidden={"words": ["amazing"]})
    assert any(x.rule == "banned_word" and x.detail == "amazing" for x in v)


def test_banned_topic():
    v = lint("we lost an arbitration", voice={}, forbidden={"topics": ["arbitration"]})
    assert any(x.rule == "banned_topic" for x in v)


def test_no_all_caps():
    # The rule fires on runs of 4+ caps so common 3-letter acronyms (USA, CEO) don't trip it.
    v = lint("This is AMAZING news", voice={"no_all_caps": True}, forbidden={})
    assert any(x.rule == "no_all_caps" for x in v)
    # 3-letter acronym should NOT trigger.
    assert not any(x.rule == "no_all_caps"
                    for x in lint("New CEO announced", voice={"no_all_caps": True}, forbidden={}))


def test_per_language_override_strictens():
    voice = {
        "max_caption_chars": 1000,
        "by_language": {"fa": {"max_caption_chars": 5}},
    }
    # English passes, Persian fails because the per-language override is shorter.
    assert lint("hello world", voice=voice, forbidden={}, language="en") == []
    v_fa = lint("hello world", voice=voice, forbidden={}, language="fa")
    assert any(x.rule == "max_length" for x in v_fa)
