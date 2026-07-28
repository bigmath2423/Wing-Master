"""Walk-forward : le garde-fou anti sur-optimisation."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from backtest_agent.ingest import normalize
from backtest_agent.walkforward import walk_forward, walkforward_markdown, _apply_spec


def test_refuse_de_conclure_sur_un_echantillon_trop_petit(minimal_df):
    wf = walk_forward(minimal_df)
    assert wf["available"] is False
    assert "Pas assez de trades" in wf["reason"]


def test_le_split_est_chronologique_et_sans_recouvrement(structured_df):
    wf = walk_forward(structured_df, split=0.7)
    assert wf["available"] is True
    assert wf["n_in_sample"] + wf["n_out_of_sample"] == wf["n_total"]
    # La période IS doit se terminer avant la fin de la période OOS.
    assert wf["is_period"] is not None and wf["oos_period"] is not None


def test_une_regle_qui_ne_tient_quen_in_sample_est_rejetee():
    """On fabrique un piège : une condition gagnante SEULEMENT sur la 1re moitié.
    Le walk-forward doit refuser de la confirmer."""
    start = datetime(2025, 1, 1, 9, 0)
    rows = []
    for i in range(200):
        piege = (i % 2 == 0)
        premiere_moitie = i < 100
        if piege and premiere_moitie:
            pnl = 3.0          # magnifique... mais uniquement au début
        elif piege:
            pnl = -1.5         # s'effondre ensuite
        else:
            pnl = 0.1
        rows.append({
            "datetime": (start + timedelta(hours=5 * i)).strftime("%Y-%m-%d %H:%M:%S"),
            "side": "buy", "profit": pnl, "piege": piege,
        })
    wf = walk_forward(normalize(pd.DataFrame(rows)), split=0.5)
    regles_piege = [r for r in wf["results"]
                    if "piege" in r["rule"] and "Conserver" in r["rule"]]
    for r in regles_piege:
        assert not r["verdict"].startswith("TIENT"), (
            "Une règle qui s'effondre hors échantillon ne doit jamais être confirmée.")


def test_applique_correctement_un_filtre_keep_et_exclude(structured_df):
    keep = _apply_spec(structured_df, {"column": "bad_ctx", "modality": "True",
                                       "direction": "keep"})
    exclude = _apply_spec(structured_df, {"column": "bad_ctx", "modality": "True",
                                          "direction": "exclude"})
    assert (keep ^ exclude).all(), "keep et exclude doivent être complémentaires."


def test_colonne_absente_ne_fait_pas_planter(structured_df):
    mask = _apply_spec(structured_df, {"column": "colonne_qui_nexiste_pas",
                                       "modality": "X", "direction": "keep"})
    assert not mask.any()


def test_le_markdown_est_lisible_meme_sans_donnees():
    md = walkforward_markdown({"available": False, "reason": "trop peu de trades"})
    assert "Walk-forward" in md and "trop peu de trades" in md
