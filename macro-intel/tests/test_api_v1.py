"""Tests d'intégration de l'API v1 (surface consommée par l'application)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_dashboard_shape(client):
    d = client.get("/v1/dashboard").json()
    for key in (
        "generated_at",
        "regime",
        "curve",
        "briefing",
        "indicators",
        "assets",
        "prices",
        "analyses",
        "correlations",
        "data_quality",
        "disclaimer",
    ):
        assert key in d, f"clé manquante dans le tableau de bord : {key}"


def test_dashboard_regime_is_valid(client):
    regime = client.get("/v1/dashboard").json()["regime"]
    assert regime["regime"] in {
        "risk_off",
        "risk_on",
        "tightening",
        "easing",
        "reflation",
        "stagflation_watch",
        "neutral",
    }
    assert 0 <= regime["confidence"] <= 92


def test_briefing_contains_no_order(client):
    briefing = client.get("/v1/briefing").json()["briefing"].lower()
    for banned in ("achetez", "vendez", "stop-loss", "take-profit"):
        assert banned not in briefing


def test_disclaimer_is_present(client):
    assert "conseil" in client.get("/v1/dashboard").json()["disclaimer"].lower()


def test_events_endpoint(client):
    body = client.get("/v1/events").json()
    assert "count" in body and "events" in body


def test_events_priority_filter_validates(client):
    assert client.get("/v1/events", params={"priority": "high"}).status_code == 200
    assert client.get("/v1/events", params={"priority": "n_importe_quoi"}).status_code == 422


def test_explain_endpoint_returns_structured_analysis(client):
    r = client.post("/v1/explain", params={"title": "Fed maintient ses taux directeurs"})
    assert r.status_code == 200
    body = r.json()
    assert body["summary"] and body["mechanism"]
    assert body["priority"] in {"critical", "high", "normal", "low"}


def test_explain_rejects_too_short_title(client):
    assert client.post("/v1/explain", params={"title": "a"}).status_code == 422


def test_topics_endpoint(client):
    body = client.get("/v1/topics").json()
    assert body["count"] >= 8
    assert all("mechanism" in t for t in body["topics"])


def test_correlations_endpoint(client):
    assert client.get("/v1/correlations").status_code == 200
    assert client.get("/v1/correlations", params={"window": 30}).status_code == 200


def test_legacy_endpoints_still_work(client):
    """Non-régression : l'API existante reste disponible."""
    assert client.get("/macro/latest").status_code == 200
    assert client.get("/macro/gold/pine").status_code == 200
    assert client.get("/health").status_code == 200


def test_app_is_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "MacroLens" in r.text
