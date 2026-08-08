"""Tests du fil d'actualité : normalisation, dédup, fraîcheur, API."""

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app.engine.ai_classifier import classify_batch
from app.main import app
from app.providers.news import NewsItem, _normalise, fetch_news, fetch_news_items


# ── Déduplication ───────────────────────────────────────────────
def test_normalise_ignores_case_accents_punctuation():
    assert _normalise("L'inflation ACCÉLÈRE !") == _normalise("l inflation accelere")


def test_normalise_collapses_spaces():
    assert _normalise("Fed   maintient    ses taux") == "fed maintient ses taux"


def test_duplicates_are_removed(monkeypatch):
    now = dt.datetime.now(dt.UTC)
    duplicated = [
        NewsItem("La Fed maintient ses taux", "u1", "A", now, "macro"),
        NewsItem("La Fed maintient ses taux !", "u2", "B", now, "macro"),  # doublon
        NewsItem("Le pétrole recule", "u3", "C", now, "markets"),
    ]
    monkeypatch.setattr("app.providers.news._from_finnhub", lambda: [])
    monkeypatch.setattr("app.providers.news._from_rss", lambda: duplicated)
    items = fetch_news_items()
    assert len(items) == 2, "les doublons de titre doivent être fusionnés"


def test_stale_items_are_dropped(monkeypatch):
    old = dt.datetime.now(dt.UTC) - dt.timedelta(days=10)
    fresh = dt.datetime.now(dt.UTC)
    monkeypatch.setattr("app.providers.news._from_finnhub", lambda: [])
    monkeypatch.setattr(
        "app.providers.news._from_rss",
        lambda: [
            NewsItem("Vieille dépêche", "u1", "A", old, "macro"),
            NewsItem("Dépêche récente", "u2", "B", fresh, "macro"),
        ],
    )
    titles = [n.title for n in fetch_news_items()]
    assert titles == ["Dépêche récente"]


def test_items_sorted_most_recent_first(monkeypatch):
    now = dt.datetime.now(dt.UTC)
    monkeypatch.setattr("app.providers.news._from_finnhub", lambda: [])
    monkeypatch.setattr(
        "app.providers.news._from_rss",
        lambda: [
            NewsItem("Ancienne", "u1", "A", now - dt.timedelta(hours=5), "macro"),
            NewsItem("Récente", "u2", "B", now, "macro"),
            NewsItem("Intermédiaire", "u3", "C", now - dt.timedelta(hours=2), "macro"),
        ],
    )
    assert [n.title for n in fetch_news_items()] == ["Récente", "Intermédiaire", "Ancienne"]


def test_sources_are_merged_not_exclusive(monkeypatch):
    """Finnhub et RSS doivent se compléter, pas s'exclure."""
    now = dt.datetime.now(dt.UTC)
    monkeypatch.setattr(
        "app.providers.news._from_finnhub", lambda: [NewsItem("Via Finnhub", "u1", "F", now, "macro")]
    )
    monkeypatch.setattr(
        "app.providers.news._from_rss", lambda: [NewsItem("Via RSS", "u2", "R", now, "markets")]
    )
    titles = {n.title for n in fetch_news_items()}
    assert titles == {"Via Finnhub", "Via RSS"}


def test_empty_sources_do_not_raise(monkeypatch):
    monkeypatch.setattr("app.providers.news._from_finnhub", lambda: [])
    monkeypatch.setattr("app.providers.news._from_rss", lambda: [])
    assert fetch_news_items() == []


def test_legacy_dict_format(monkeypatch):
    now = dt.datetime.now(dt.UTC)
    monkeypatch.setattr("app.providers.news._from_finnhub", lambda: [])
    monkeypatch.setattr(
        "app.providers.news._from_rss", lambda: [NewsItem("Titre", "http://x", "S", now, "macro")]
    )
    rows = fetch_news()
    assert rows and {"title", "url", "source", "ts", "category"} <= set(rows[0])


# ── Classification : les métadonnées doivent survivre ───────────
def test_classification_preserves_metadata():
    ts = dt.datetime(2026, 5, 1, 12, 0, tzinfo=dt.UTC)
    out = classify_batch(
        [
            {
                "title": "Fed hikes rates",
                "category": "macro",
                "source": "Reuters",
                "url": "http://example.test/a",
                "ts": ts,
            }
        ]
    )
    assert len(out) == 1
    assert out[0].source == "Reuters"
    assert out[0].url == "http://example.test/a"
    assert out[0].ts == ts


def test_classification_skips_empty_titles():
    assert classify_batch([{"title": "  ", "category": "macro"}]) == []


# ── API ─────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_news_endpoint_shape(client):
    body = client.get("/v1/news").json()
    assert {"count", "items", "disclaimer"} <= set(body)
    assert isinstance(body["items"], list)


def test_news_category_filter_validates(client):
    assert client.get("/v1/news", params={"category": "macro"}).status_code == 200
    assert client.get("/v1/news", params={"category": "peu_importe"}).status_code == 422


def test_news_limit_bounds(client):
    assert client.get("/v1/news", params={"limit": 5}).status_code == 200
    assert client.get("/v1/news", params={"limit": 0}).status_code == 422
    assert client.get("/v1/news", params={"limit": 500}).status_code == 422


def test_news_present_in_dashboard(client):
    assert "news" in client.get("/v1/dashboard").json()
