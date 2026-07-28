"""Walk-forward glissant.

La propriété la plus critique testée ici : ABSENCE DE FUITE. Si une fenêtre
d'apprentissage voyait ne serait-ce qu'un trade de sa fenêtre de test, tous les
verdicts du module seraient faux tout en paraissant excellents.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from backtest_agent.ingest import normalize
from backtest_agent.rolling import (
    make_folds, rolling_walk_forward, optimize_threshold,
    rolling_markdown, threshold_markdown, _wfe_interpretation, _stability_verdict,
)


# --- Découpage -------------------------------------------------------------

def test_les_fenetres_ne_se_chevauchent_jamais():
    """Aucun trade de test ne doit apparaître dans l'apprentissage : sans ça,
    tout le module mentirait."""
    for anchored in (False, True):
        for fold in make_folds(500, n_folds=5, train_window=3, anchored=anchored):
            train = set(range(fold.train_start, fold.train_end))
            test = set(range(fold.test_start, fold.test_end))
            assert not (train & test), (
                f"Fuite détectée (anchored={anchored}, fenêtre {fold.index})")


def test_lapprentissage_precede_toujours_le_test():
    """On ne doit jamais apprendre sur le futur."""
    for fold in make_folds(500, n_folds=5, train_window=3):
        assert fold.train_end <= fold.test_start


def test_le_mode_glissant_garde_une_fenetre_de_taille_fixe():
    folds = make_folds(800, n_folds=5, train_window=3, anchored=False)
    tailles = {f.train_end - f.train_start for f in folds}
    assert len(tailles) == 1, f"La fenêtre glissante doit rester constante : {tailles}"


def test_le_mode_ancre_fait_grandir_la_fenetre():
    folds = make_folds(800, n_folds=5, train_window=3, anchored=True)
    tailles = [f.train_end - f.train_start for f in folds]
    assert tailles == sorted(tailles) and tailles[0] < tailles[-1]
    assert all(f.train_start == 0 for f in folds)


def test_la_derniere_fenetre_consomme_les_trades_restants():
    folds = make_folds(503, n_folds=5, train_window=3)
    assert folds[-1].test_end == 503, "Aucun trade ne doit être perdu."


def test_refuse_de_decouper_un_echantillon_trop_petit():
    assert make_folds(40, n_folds=5, train_window=3) == []


# --- Exécution -------------------------------------------------------------

def _serie(n: int, pnl_fn, **cols) -> pd.DataFrame:
    """Série de trades espacés IRRÉGULIÈREMENT.

    Un espacement régulier serait piégeux : avec un pas de 5 h, l'heure du trade
    vaut (9 + 5i) mod 24, dont la parité est exactement celle de i. Un drapeau
    défini par `i % 2` serait alors indiscernable d'une règle horaire, et le test
    validerait la mauvaise colonne. Le jitter casse cet alias.
    """
    rng = np.random.default_rng(99)
    start = datetime(2025, 1, 1, 9, 0)
    horodatage = start
    rows = []
    for i in range(n):
        horodatage += timedelta(minutes=int(rng.integers(90, 600)))
        row = {"datetime": horodatage.strftime("%Y-%m-%d %H:%M:%S"),
               "side": "buy", "profit": pnl_fn(i)}
        for k, fn in cols.items():
            row[k] = fn(i)
        rows.append(row)
    return normalize(pd.DataFrame(rows))


def test_message_clair_si_pas_assez_de_trades(minimal_df):
    res = rolling_walk_forward(minimal_df, n_folds=5)
    assert res["available"] is False
    assert "Pas assez de trades" in res["reason"]


def test_une_regle_valable_partout_est_jugee_robuste():
    """Signal franc et CONSTANT dans le temps : doit ressortir robuste."""
    df = _serie(600, lambda i: 1.5 if i % 2 == 0 else -1.0,
                bon=lambda i: i % 2 == 0)
    res = rolling_walk_forward(df, n_folds=5, train_window=3)
    assert res["available"] is True
    noms = " ".join(r["rule"] for r in res["robust_rules"])
    assert "bon" in noms, (
        f"Un effet constant doit être reconnu robuste. Obtenu : "
        f"{[(r['rule'], r['verdict']) for r in res['rule_stability']]}")


def test_une_regle_qui_seffondre_dans_le_temps_est_rejetee():
    """Piège : l'effet n'existe que sur la première moitié de l'historique.
    Un split unique pourrait le confirmer ; le glissant doit le rejeter."""
    def pnl(i):
        if i % 2 == 0:
            return 2.0 if i < 300 else -1.2   # s'effondre à mi-parcours
        return 0.05
    df = _serie(600, pnl, piege=lambda i: i % 2 == 0)
    res = rolling_walk_forward(df, n_folds=5, train_window=3)
    pieges = [r for r in res["rule_stability"] if "piege" in r["rule"]]
    for r in pieges:
        assert r["verdict"] != "ROBUSTE", (
            "Une règle qui cesse de fonctionner ne doit jamais être dite robuste.")


def test_sur_du_bruit_pur_aucune_regle_nest_robuste():
    rng = np.random.default_rng(11)
    df = _serie(600, lambda i: float(rng.normal(0, 1)),
                flag=lambda i: bool(rng.integers(0, 2)))
    res = rolling_walk_forward(df, n_folds=5, train_window=3)
    assert res["robust_rules"] == [], (
        f"Bruit pur : aucune règle robuste attendue, obtenu {res['robust_rules']}")


def test_lefficacite_walk_forward_est_calculee():
    df = _serie(600, lambda i: 1.5 if i % 2 == 0 else -1.0, bon=lambda i: i % 2 == 0)
    eff = rolling_walk_forward(df, n_folds=5)["efficiency"]
    assert eff["available"] is True
    assert eff["walk_forward_efficiency"] is not None


@pytest.mark.parametrize("wfe,attendu", [
    (None, "Aucun avantage"),
    (-0.2, "DISPARAÎT"),
    (0.1, "sur-optimisation"),
    (0.45, "prudent"),
    (0.9, "se transfère bien"),
])
def test_interpretation_de_lefficacite(wfe, attendu):
    assert attendu in _wfe_interpretation(wfe)


def test_une_regle_vue_une_seule_fois_nest_pas_concluante():
    assert "INSUFFISANT" in _stability_verdict(held=1, proposed=1, deltas=[0.5])


def test_une_regle_qui_explose_sur_une_fenetre_nest_pas_robuste():
    """Même avec un bon taux, une fenêtre catastrophique doit disqualifier."""
    verdict = _stability_verdict(held=3, proposed=4, deltas=[0.4, 0.3, 0.2, -0.9])
    assert verdict != "ROBUSTE"


# --- Optimisation de seuil -------------------------------------------------

def test_le_seuil_est_optimise_et_verifie_hors_echantillon():
    """La confiance prédit le résultat : le seuil doit battre la baseline."""
    rng = np.random.default_rng(3)
    def conf(i):
        return float(rng.uniform(0, 1))
    confs = [conf(i) for i in range(600)]
    start = datetime(2025, 1, 1, 9, 0)
    rows = [{
        "datetime": (start + timedelta(hours=5 * i)).strftime("%Y-%m-%d %H:%M:%S"),
        "side": "buy",
        "confidence": confs[i],
        "profit": 1.5 if confs[i] > 0.6 else -0.8,
    } for i in range(600)]
    res = optimize_threshold(normalize(pd.DataFrame(rows)), column="confidence",
                             n_folds=5)
    assert res["available"] is True
    beat, total = res["folds_beating_baseline"].split("/")
    assert int(beat) >= int(total) * 0.6, (
        f"Un seuil réellement prédictif doit battre la baseline : {res['folds']}")


def test_message_clair_si_la_colonne_est_absente(structured_df):
    res = optimize_threshold(structured_df, column="colonne_inexistante")
    assert res["available"] is False
    assert "absente" in res["reason"]


def test_le_seuil_ne_garde_jamais_une_poignee_de_trades():
    """Garde-fou : un seuil qui ne laisse presque rien doit être écarté."""
    rng = np.random.default_rng(5)
    start = datetime(2025, 1, 1, 9, 0)
    rows = [{
        "datetime": (start + timedelta(hours=5 * i)).strftime("%Y-%m-%d %H:%M:%S"),
        "side": "buy", "confidence": float(rng.uniform(0, 1)),
        "profit": float(rng.normal(0, 1)),
    } for i in range(600)]
    res = optimize_threshold(normalize(pd.DataFrame(rows)), column="confidence",
                             n_folds=5)
    if res.get("available"):
        for f in res["folds"]:
            assert f["n_test_kept"] > 0


# --- Rendu -----------------------------------------------------------------

def test_le_markdown_reste_lisible_sans_donnees():
    assert "⚠️" in rolling_markdown({"available": False, "reason": "trop peu"})
    assert "⚠️" in threshold_markdown({"available": False, "reason": "trop peu"})


def test_le_markdown_previent_que_le_decoupage_est_par_trade():
    """Sans cette précision, un bord de fenêtre à la même date ressemble à une fuite."""
    df = _serie(600, lambda i: 1.0 if i % 2 else -0.5, bon=lambda i: i % 2 == 0)
    md = rolling_markdown(rolling_walk_forward(df, n_folds=5))
    assert "NUMÉRO DE TRADE" in md and "disjoints" in md
