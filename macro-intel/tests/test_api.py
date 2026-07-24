"""Tests d'intégration de l'API (routes macro + webhook TradingView)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    # Le lifespan exécute un cycle -> l'état macro est prêt pour les tests.
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_latest_shape(client):
    d = client.get("/macro/latest").json()
    assert set(d) >= {"generated_at", "assets", "gold_drivers", "sources"}
    assert "gold" in d["assets"]
    assert -100 <= d["assets"]["gold"]["score"] <= 100


def test_pine_format(client):
    d = client.get("/macro/gold/pine").json()
    assert set(d) == {"MACRO_SCORE", "MACRO_BIAS", "CONFIANCE", "RISK_LEVEL", "NEWS_IMPACT"}
    assert d["MACRO_BIAS"] in {"HAUSSIER", "BAISSIER", "NEUTRE"}


def test_unknown_asset_404(client):
    assert client.get("/macro/dogecoin").status_code == 404


def test_history_endpoint(client):
    r = client.get("/macro/history/gold", params={"limit": 5})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_webhook_requires_valid_secret(client):
    bad = client.post(
        "/tradingview/webhook",
        json={
            "secret": "wrong",
            "symbol": "XAUUSD",
            "side": "buy",
            "technical_score": 80,
        },
    )
    assert bad.status_code == 401


def test_webhook_fusion_ok(client):
    r = client.post(
        "/tradingview/webhook",
        json={
            "secret": "change-me-please",
            "symbol": "XAUUSD",
            "side": "buy",
            "technical_score": 88,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] in {"reinforced", "warning", "standard"}
    assert 0 <= body["final_confidence"] <= 100


def test_webhook_normalizes_long_short(client):
    # "long"/"short" doivent être acceptés et normalisés en buy/sell.
    r = client.post(
        "/tradingview/webhook",
        json={
            "secret": "change-me-please",
            "symbol": "XAUUSD",
            "side": "LONG",
            "technical_score": 70,
        },
    )
    assert r.status_code == 200
    assert r.json()["side"] == "buy"


def test_webhook_rejects_invalid_side(client):
    r = client.post(
        "/tradingview/webhook",
        json={
            "secret": "change-me-please",
            "symbol": "XAUUSD",
            "side": "hodl",
            "technical_score": 70,
        },
    )
    assert r.status_code == 422


def test_webhook_rejects_out_of_range_score(client):
    r = client.post(
        "/tradingview/webhook",
        json={
            "secret": "change-me-please",
            "symbol": "XAUUSD",
            "side": "buy",
            "technical_score": 150,
        },
    )
    assert r.status_code == 422
