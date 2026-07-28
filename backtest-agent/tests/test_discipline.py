"""LE test le plus important du projet.

Toute la valeur de cet agent tient à une promesse : il ne recommande pas une
modification juste parce qu'elle fait monter un chiffre. Ces tests vérifient
que cette discipline est réellement appliquée par le CODE, et pas seulement
écrite dans le prompt (où rien ne la garantit).
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import pytest

from backtest_agent.ingest import normalize
from backtest_agent.suggestions import build_suggestions, _overfit_risk
from backtest_agent.winners import _robust_score
from backtest_agent.validate import validate_candidate


def test_le_score_robuste_prefere_un_effet_stable_a_une_pepite():
    """Une espérance énorme sur 5 trades ne doit pas battre un effet net sur 150."""
    pepite = _robust_score(expectancy=3.0, n=5)
    stable = _robust_score(expectancy=0.5, n=150)
    assert stable > pepite, (
        f"Une pépite sur 5 trades ({pepite}) ne doit jamais primer sur "
        f"un effet stable sur 150 trades ({stable}).")


def test_le_risque_de_suroptimisation_est_eleve_sur_petit_echantillon():
    assert _overfit_risk(n_after=8, n_before=300, effect=5.0) == "ÉLEVÉ"


def test_le_risque_est_eleve_si_on_jette_la_majorite_des_trades():
    # 60 trades restants sur 300 = 20% conservés : sous le seuil de 25%.
    assert _overfit_risk(n_after=60, n_before=300, effect=0.2) == "ÉLEVÉ"


def test_le_risque_est_faible_sur_un_effet_modeste_et_bien_dote():
    assert _overfit_risk(n_after=200, n_before=300, effect=0.2) == "FAIBLE"


def _df_avec_pepite() -> pd.DataFrame:
    """Jeu piégé : une condition rarissime a un PnL énorme (pur bruit), pendant
    qu'une condition fréquente a un effet modeste mais réel."""
    start = datetime(2025, 1, 1, 9, 0)
    rows = []
    for i in range(200):
        rare = (i % 50 == 0)             # 4 trades seulement
        frequent = (i % 2 == 0)
        pnl = 25.0 if rare else (0.4 if frequent else -0.2)
        rows.append({
            "datetime": (start + timedelta(hours=5 * i)).strftime("%Y-%m-%d %H:%M:%S"),
            "side": "buy", "profit": pnl,
            "pepite_rare": rare, "effet_frequent": frequent,
        })
    return normalize(pd.DataFrame(rows))


def test_la_pepite_bruyante_est_declassee_dans_les_tests_ab():
    """Le filtre « garder la pépite » a un ΔPF gigantesque mais doit être
    classé ÉLEVÉ en risque, donc ne pas remonter en tête."""
    sugg = build_suggestions(_df_avec_pepite())
    tests = sugg["ab_tests"]
    assert tests, "Des tests A/B devraient être proposés."
    pepites = [t for t in tests
               if "pepite_rare" in t["proposed_change"] and "Conserver" in t["proposed_change"]]
    for t in pepites:
        assert t["overfitting_risk"] == "ÉLEVÉ"
    # Et surtout : le tout premier test proposé ne doit pas être la pépite.
    assert tests[0]["overfitting_risk"] != "ÉLEVÉ" or not pepites


def test_les_garde_fous_sont_toujours_presents(structured_df):
    sugg = build_suggestions(structured_df)
    texte = " ".join(sugg["guardrails"]).lower()
    assert "win rate" in texte, "Le garde-fou anti win-rate doit être explicite."
    assert "hors échantillon" in texte or "walk-forward" in texte


def test_validate_rejette_une_pile_qui_vide_lechantillon():
    """Cas central : des règles bonnes isolément mais destructrices combinées."""
    res = validate_candidate(_df_avec_pepite(), n_sims=200)
    if res.get("available") and res.get("n_filters", 0) > 0:
        combined = res["combined"]
        if combined["retained_ratio"] < 0.25:
            assert res["verdict"]["verdict"] == "REJETER"
            assert any("supprime" in r for r in res["verdict"]["blocking_reasons"])


def test_aucune_proposition_quand_rien_nest_valide():
    """Sur des données purement aléatoires sans structure, l'agent ne doit rien
    proposer — ne rien changer est la bonne réponse."""
    import numpy as np
    rng = np.random.default_rng(7)
    start = datetime(2025, 1, 1)
    rows = [{
        "datetime": (start + timedelta(hours=4 * i)).strftime("%Y-%m-%d %H:%M:%S"),
        "side": "buy", "profit": float(rng.normal(0, 1)),
        "flag_a": bool(rng.integers(0, 2)), "flag_b": bool(rng.integers(0, 2)),
    } for i in range(200)]
    res = validate_candidate(normalize(pd.DataFrame(rows)), n_sims=200)
    verdict = res.get("verdict", {}).get("verdict", "")
    assert verdict in {"RIEN À VALIDER", "REJETER", "PRUDENCE"}, (
        f"Sur du bruit pur, l'agent ne doit pas conclure ADOPTER (obtenu: {verdict}).")


def test_un_filtre_qui_supprime_toutes_les_pertes_nest_pas_jete():
    """Régression : un profit factor indéfini (aucune perte) était confondu avec
    « inexploitable », si bien que le MEILLEUR filtre possible — celui qui retire
    tous les perdants — était silencieusement écarté."""
    import pandas as pd
    from datetime import datetime, timedelta
    from backtest_agent.ingest import normalize
    from backtest_agent.suggestions import build_suggestions, pf_delta, improved

    start = datetime(2025, 1, 1, 9, 0)
    rng = __import__("numpy").random.default_rng(4)
    ts, rows = start, []
    for i in range(200):
        ts += timedelta(minutes=int(rng.integers(90, 600)))
        rows.append({"datetime": ts.strftime("%Y-%m-%d %H:%M:%S"), "side": "buy",
                     "profit": 1.5 if i % 2 == 0 else -1.0, "parfait": i % 2 == 0})
    sugg = build_suggestions(normalize(pd.DataFrame(rows)))
    noms = " ".join(t["proposed_change"] for t in sugg["ab_tests"])
    assert "parfait" in noms, (
        f"Le filtre parfait doit être proposé. Obtenu : {noms}")


def test_un_profit_factor_indefini_nest_pas_traite_comme_zero():
    """`None` veut dire « aucune perte » (le meilleur cas), surtout pas zéro."""
    from backtest_agent.suggestions import pf_delta, improved
    assert pf_delta(2.0, None) is None       # indéfini, pas -2.0
    assert pf_delta(None, 2.0) is None
    assert pf_delta(1.0, 3.0) == 2.0
    # Une espérance en hausse avec un PF indéfini reste une amélioration.
    assert improved({"expectancy_delta": 0.5, "pf_delta": None}) is True
    assert improved({"expectancy_delta": -0.5, "pf_delta": None}) is False
