"""Tests de l'analyste IA : structure, priorisation et absence de signal."""

from app.ai.analyst import analyse_batch, analyse_event, compute_priority
from app.ai.knowledge import TOPICS, detect_topics


def test_analysis_has_all_required_sections():
    a = analyse_event("US CPI surprises to the upside", category="release", severity=0.8)
    assert a.summary and a.why_it_matters and a.mechanism
    assert a.markets and a.scenarios
    assert 0 <= a.confidence <= 90
    assert a.priority in {"critical", "high", "normal", "low"}


def test_analysis_never_contains_orders():
    for title in [
        "Fed signals rate hike",
        "War escalates in key shipping corridor",
        "Gold rally accelerates on weak dollar",
    ]:
        a = analyse_event(title, severity=0.7)
        blob = " ".join([a.summary, a.why_it_matters, a.mechanism, *a.scenarios]).lower()
        for banned in ("achetez", "vendez", "stop-loss", "take-profit", "buy ", "sell "):
            assert banned not in blob, f"formulation interdite détectée : {banned}"


def test_priority_escalates_on_critical_topics():
    assert compute_priority("FOMC decision today", "release", 0.5) == "critical"
    assert compute_priority("War breaks out", "geopolitics", 0.5) == "critical"
    assert compute_priority("US CPI released", "release", 0.5) == "high"
    assert compute_priority("Minor market note", "news", 0.05) == "low"


def test_topic_detection():
    topics = detect_topics("Fed hikes rates as CPI inflation stays hot")
    keys = {t.key for t in topics}
    assert "rates" in keys or "inflation" in keys


def test_batch_sorted_by_priority():
    events = [
        {"title": "Small market note", "category": "news", "severity": 0.05},
        {"title": "FOMC decision and rate guidance", "category": "central_bank", "severity": 0.9},
    ]
    out = analyse_batch(events)
    assert out[0].priority == "critical"


def test_batch_ignores_empty_titles():
    assert analyse_batch([{"title": "", "category": "news"}]) == []


def test_knowledge_base_is_complete():
    for topic in TOPICS.values():
        assert topic.why and topic.mechanism
        assert topic.markets, f"{topic.key} doit lister des marchés"
        assert len(topic.scenarios) >= 2, f"{topic.key} doit proposer plusieurs scénarios"


def test_confidence_never_overconfident():
    a = analyse_event("FOMC decision", category="central_bank", severity=1.0)
    assert a.confidence <= 90, "une analyse macro ne doit jamais afficher de fausse certitude"
