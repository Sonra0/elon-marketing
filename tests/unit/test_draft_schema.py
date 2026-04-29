"""Sanity-check the JSON schema we send to Claude as the forced tool."""

from elon.content.draft import DRAFT_TOOL


def test_schema_has_required_fields():
    s = DRAFT_TOOL["input_schema"]
    assert s["required"] == [
        "idea", "hook", "caption", "cta", "platform", "reason",
        "expected_result", "score", "pillar_id",
    ]
    assert s["properties"]["platform"]["enum"] == ["ig", "tiktok", "fb"]
    score = s["properties"]["score"]
    for k in ("impact", "effort", "risk"):
        assert score["properties"][k]["type"] == "integer"
        assert score["properties"][k]["minimum"] == 0
        assert score["properties"][k]["maximum"] == 100
