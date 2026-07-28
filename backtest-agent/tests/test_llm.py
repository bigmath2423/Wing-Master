"""Couche LLM : elle doit être strictement optionnelle et se dégrader proprement.

On ne fait AUCUN appel réseau ici : le client Anthropic est remplacé par un
double de test. Ce qu'on vérifie, c'est le contrat : sans clé l'agent reste
pleinement fonctionnel, et avec clé le prompt reçoit bien les chiffres déjà
calculés (le LLM ne doit jamais avoir à inventer une statistique).
"""

from __future__ import annotations

import sys
import types

import pytest

from backtest_agent import llm
from backtest_agent.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from backtest_agent.report import build_report


def test_sans_cle_api_lagent_reste_fonctionnel(structured_df, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert llm.is_available() is False
    res = build_report(structured_df, use_llm=True)
    assert res["llm_used"] is False
    assert "Analyse globale" in res["markdown"]   # le rapport déterministe prend le relais


def test_une_erreur_llm_ne_casse_pas_le_rapport(structured_df, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "cle-de-test")
    monkeypatch.setattr(llm, "generate_narrative",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("API down")))
    res = build_report(structured_df, use_llm=True)
    assert res["llm_used"] is False
    assert "Analyse globale" in res["markdown"]
    assert "API down" in res["payload"]["meta"]["llm_error"]


class _FakeBlock:
    type = "text"
    def __init__(self, text): self.text = text


class _FakeResponse:
    def __init__(self, text): self.content = [_FakeBlock(text)]


def _install_fake_anthropic(monkeypatch, capture: dict):
    """Installe un faux module `anthropic` qui capture les arguments d'appel."""
    module = types.ModuleType("anthropic")

    class _Messages:
        def create(self, **kwargs):
            capture.update(kwargs)
            return _FakeResponse("## 1. Synthèse exécutive\nRapport de test.")

    class _Client:
        def __init__(self, *a, **k): self.messages = _Messages()

    module.Anthropic = _Client
    monkeypatch.setitem(sys.modules, "anthropic", module)


def test_le_prompt_recoit_les_chiffres_deja_calcules(structured_df, monkeypatch):
    capture: dict = {}
    monkeypatch.setenv("ANTHROPIC_API_KEY", "cle-de-test")
    _install_fake_anthropic(monkeypatch, capture)

    res = build_report(structured_df, use_llm=True)
    assert res["llm_used"] is True
    assert "Rapport de test." in res["markdown"]
    # Les statistiques brutes restent jointes au rapport, pour vérification.
    assert "Statistiques brutes" in res["markdown"]

    # Le système impose bien la posture de chercheur.
    assert capture["system"] == SYSTEM_PROMPT
    contenu = capture["messages"][0]["content"]
    for section in ["Analyse globale", "Analyse des pertes",
                    "Analyse des meilleurs trades"]:
        assert section in contenu
    # Le nombre de trades réel doit figurer dans le prompt : le LLM lit, il n'invente pas.
    assert str(len(structured_df)) in contenu


def test_le_system_prompt_interdit_loptimisation_du_win_rate():
    texte = SYSTEM_PROMPT.lower()
    assert "jamais" in texte and "taux de réussite" in texte
    assert "robustesse" in texte
    assert "sur-optimisation" in texte
    assert "hors échantillon" in texte


def test_le_gabarit_utilisateur_expose_toutes_les_sections():
    for cle in ["{meta}", "{global_metrics}", "{losses}", "{winners}", "{suggestions}"]:
        assert cle in USER_TEMPLATE


def test_le_modele_par_defaut_est_surchargeable(structured_df, monkeypatch):
    capture: dict = {}
    monkeypatch.setenv("ANTHROPIC_API_KEY", "cle-de-test")
    _install_fake_anthropic(monkeypatch, capture)
    build_report(structured_df, use_llm=True, model="modele-precis")
    assert capture["model"] == "modele-precis"
