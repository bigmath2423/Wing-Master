"""Tests du calendrier économique : génération, classement, résumé, API."""

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers.economic_calendar import (
    _classify,
    _importance,
    _nth_weekday,
    fetch_calendar,
    fetch_calendar_entries,
    summarise_calendar,
)


# ── Génération ──────────────────────────────────────────────────
def test_entries_are_returned_offline():
    """Sans clé ni réseau, le calendrier reste exploitable (repli récurrent)."""
    entries = fetch_calendar_entries(21)
    assert entries, "le calendrier doit toujours proposer des rendez-vous"
    assert all(e.event and e.event_time for e in entries)


def test_entries_are_chronological():
    entries = fetch_calendar_entries(21)
    times = [e.event_time for e in entries]
    assert times == sorted(times)


def test_recurring_entries_are_flagged_as_estimated():
    """Une date reconstruite ne doit jamais être présentée comme confirmée."""
    entries = fetch_calendar_entries(21)
    if entries[0].source == "recurring":
        assert all(e.estimated_date for e in entries)


def test_entries_within_requested_window():
    now = dt.datetime.now(dt.UTC)
    horizon = now + dt.timedelta(days=21, hours=1)
    for entry in fetch_calendar_entries(21):
        when = dt.datetime.fromisoformat(entry.event_time)
        assert when <= horizon


def test_major_events_are_present():
    """Les rendez-vous structurants doivent apparaître sur une fenêtre longue."""
    names = " ".join(e.event.lower() for e in fetch_calendar_entries(60))
    for expected in ("nfp", "cpi", "fomc", "pce"):
        assert expected in names, f"rendez-vous manquant : {expected}"


# ── Classement ──────────────────────────────────────────────────
@pytest.mark.parametrize(
    ("event", "topic"),
    [
        ("CPI — inflation des prix à la consommation", "inflation"),
        ("FOMC — décision de taux directeur", "rates"),
        ("NFP — créations d'emplois non agricoles", "employment"),
        ("ISM manufacturier (PMI)", "growth"),
        ("Stocks de pétrole brut (EIA)", "energy"),
    ],
)
def test_topic_classification(event, topic):
    assert _classify(event)[0] == topic


def test_classification_always_gives_a_watch_note():
    for event in ("CPI", "Événement inconnu", "FOMC"):
        assert _classify(event)[1]


def test_importance_levels():
    assert _importance("FOMC decision") == 3
    assert _importance("CPI inflation") == 3
    assert _importance("ECB press conference") == 2
    assert _importance("Indice secondaire régional") == 1


def test_nth_weekday_helper():
    # Le 1er vendredi de janvier 2027 est le 1er janvier (un vendredi).
    assert _nth_weekday(2027, 1, 4, 1) == dt.date(2027, 1, 1)
    assert _nth_weekday(2027, 1, 4, 2) == dt.date(2027, 1, 8)


# ── Résumé ──────────────────────────────────────────────────────
def test_summary_shape():
    summary = summarise_calendar(21)
    assert summary.entries
    assert summary.high_impact_48h >= 0
    if summary.next_major is not None:
        assert summary.next_major.importance >= 3


def test_summary_excludes_past_events():
    now = dt.datetime.now(dt.UTC)
    for entry in summarise_calendar(21).entries:
        when = dt.datetime.fromisoformat(entry.event_time)
        assert when >= now - dt.timedelta(hours=12)


def test_legacy_dict_format_still_works():
    """Le pipeline existant consomme des dictionnaires : non-régression."""
    rows = fetch_calendar()
    assert rows
    for row in rows:
        assert {"event_time", "country", "event", "importance"} <= set(row)


# ── API ─────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_calendar_endpoint(client):
    body = client.get("/v1/calendar").json()
    assert body["count"] >= 1
    assert "entries" in body and "estimated" in body and "note" in body


def test_calendar_importance_filter(client):
    majors = client.get("/v1/calendar", params={"importance": 3}).json()
    assert all(e["importance"] >= 3 for e in majors["entries"])


def test_calendar_days_filter_narrows_results(client):
    wide = client.get("/v1/calendar", params={"days": 30}).json()["count"]
    narrow = client.get("/v1/calendar", params={"days": 3}).json()["count"]
    assert narrow <= wide


def test_calendar_rejects_invalid_filters(client):
    assert client.get("/v1/calendar", params={"importance": 9}).status_code == 422
    assert client.get("/v1/calendar", params={"days": 0}).status_code == 422


def test_calendar_present_in_dashboard(client):
    calendar = client.get("/v1/dashboard").json()["calendar"]
    assert calendar is not None
    assert "entries" in calendar


def test_briefing_mentions_upcoming_event(client):
    """Le risque événementiel doit remonter dans la synthèse."""
    briefing = client.get("/v1/briefing").json()["briefing"].lower()
    assert "rendez-vous" in briefing or "aucun événement" in briefing
