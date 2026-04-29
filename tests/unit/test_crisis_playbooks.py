from elon.strategy import crisis_playbooks


class _T:
    """Light stand-in for a Tenant ORM row (no DB needed for these tests)."""
    def __init__(self, settings: dict | None = None):
        self.settings_json = settings or {}


def test_default_playbooks_present():
    pb = crisis_playbooks.get_playbooks(_T())
    for k in ("negative_review", "controversy", "sensitive_health", "default"):
        assert k in pb
        assert "response_template" in pb[k]


def test_topic_mapping():
    assert crisis_playbooks.map_topic_to_playbook(["customer_review"]) == "negative_review"
    assert crisis_playbooks.map_topic_to_playbook(["controversial_take"]) == "controversy"
    assert crisis_playbooks.map_topic_to_playbook(["medical claim"]) == "sensitive_health"
    assert crisis_playbooks.map_topic_to_playbook(["random"]) == "default"


def test_deny_list_match():
    t = _T({"crisis": {"deny_list": ["miracle", "guaranteed cure"]}})
    assert crisis_playbooks.violates_deny_list(t, "Try our miracle product") == ["miracle"]
    assert crisis_playbooks.violates_deny_list(t, "Our guaranteed cure works") == ["guaranteed cure"]
    assert crisis_playbooks.violates_deny_list(t, "Try our latest product") == []


def test_double_signoff_flag():
    assert crisis_playbooks.double_signoff_required(_T()) is False
    assert crisis_playbooks.double_signoff_required(_T({"crisis": {"double_signoff": True}})) is True
