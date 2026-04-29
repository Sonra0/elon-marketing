from elon.analytics.anomaly import detect


def test_no_history_no_anomaly():
    assert detect({"reach": 1000}, []) == []


def test_spike_flagged():
    history = [{"reach": 100} for _ in range(10)]
    out = detect({"reach": 500}, history)
    assert any(a["metric"] == "reach" and a["kind"] == "spike" for a in out)


def test_drop_flagged():
    history = [{"reach": 1000} for _ in range(10)]
    out = detect({"reach": 100}, history)
    assert any(a["metric"] == "reach" and a["kind"] == "drop" for a in out)


def test_within_band_no_flag():
    history = [{"reach": 100 + i} for i in range(10)]
    out = detect({"reach": 110}, history)
    assert out == []
