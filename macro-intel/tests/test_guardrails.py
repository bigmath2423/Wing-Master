"""Tests des garde-fous anti-signal — exigence produit non négociable (Tome 0 §9).

La plateforme doit expliquer sans jamais ordonner. Ces tests vérifient qu'aucune
formulation prescriptive ne peut atteindre l'utilisateur.
"""

import pytest

from app.ai import guardrails


@pytest.mark.parametrize(
    "prescriptive",
    [
        "Achetez l'or maintenant, le contexte est favorable.",
        "Il faut vendre le dollar avant la publication.",
        "Je recommande de prendre position sur le CAC.",
        "Entrez en position longue sur XAUUSD.",
        "Buy gold now.",
        "Placez un stop-loss sous le support.",
        "Take-profit à 2100.",
        "Objectif de prix : 2150 dollars.",
        "Signal d'achat confirmé sur le Bitcoin.",
        "Opportunité d'achat sur les indices.",
    ],
)
def test_prescriptive_language_is_neutralised(prescriptive):
    report = guardrails.enforce(prescriptive)
    assert not report.clean, "la formulation prescriptive aurait dû être détectée"
    lowered = report.text.lower()
    for banned in ("achetez", "vendre le dollar", "buy gold", "stop-loss", "take-profit"):
        assert banned not in lowered


def test_trading_levels_are_stripped():
    report = guardrails.enforce("Configuration intéressante — SL 1920 et TP: 2050.")
    assert "1920" not in report.text
    assert "2050" not in report.text
    assert "[niveau retiré]" in report.text


def test_descriptive_text_is_preserved():
    original = (
        "L'inflation ressort au-dessus du consensus, ce qui renforce historiquement "
        "les anticipations de resserrement monétaire et soutient le dollar."
    )
    report = guardrails.enforce(original)
    assert report.clean
    assert report.text == original


def test_empty_input_is_safe():
    report = guardrails.enforce("")
    assert report.text == ""
    assert report.clean


def test_enforce_many_collects_violations():
    cleaned, violations = guardrails.enforce_many(["Analyse neutre du contexte.", "Achetez immédiatement."])
    assert len(cleaned) == 2
    assert violations
    assert "achetez" not in cleaned[1].lower()


def test_system_rules_forbid_orders():
    rules = guardrails.SYSTEM_RULES.lower()
    assert "jamais" in rules
    assert "stop-loss" in rules
    assert "take-profit" in rules
