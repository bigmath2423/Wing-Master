"""Étape 3 : Monte-Carlo, cohérence par segment, validation combinée, comparaison."""

from __future__ import annotations

import pandas as pd
import pytest

from backtest_agent.ingest import normalize
from backtest_agent.robustness import monte_carlo_drawdown, add_period_segments
from backtest_agent.validate import (
    compare_backtests, validate_candidate, _combined_mask, comparison_markdown,
)


def test_monte_carlo_refuse_de_conclure_sur_trop_peu_de_trades():
    mc = monte_carlo_drawdown(pd.Series([1.0, -1.0, 1.0]), n_sims=50)
    assert mc["available"] is False


def test_monte_carlo_donne_des_percentiles_coherents(structured_df):
    from backtest_agent.features import _pnl_series
    mc = monte_carlo_drawdown(_pnl_series(structured_df), n_sims=500)
    assert mc["available"] is True
    # Pire 5% <= médiane <= meilleur 5% (drawdowns négatifs).
    assert mc["simulated_p05_worst"] <= mc["simulated_median"] <= mc["simulated_p95_best"]
    assert 0.0 <= mc["share_of_sims_worse_than_observed"] <= 1.0


def test_monte_carlo_est_reproductible(structured_df):
    """Une analyse quantitative doit donner le même résultat deux fois."""
    from backtest_agent.features import _pnl_series
    pnl = _pnl_series(structured_df)
    a = monte_carlo_drawdown(pnl, n_sims=300, seed=1)
    b = monte_carlo_drawdown(pnl, n_sims=300, seed=1)
    assert a["simulated_median"] == b["simulated_median"]


def test_le_drawdown_dune_serie_toujours_gagnante_est_nul():
    mc = monte_carlo_drawdown(pd.Series([1.0] * 30), n_sims=100)
    assert mc["observed_max_drawdown"] == pytest.approx(0.0)


def test_la_pile_de_filtres_est_un_et_logique(structured_df):
    specs = [
        {"column": "bad_ctx", "modality": "False", "direction": "keep"},
        {"column": "good_setup", "modality": "True", "direction": "keep"},
    ]
    mask = _combined_mask(structured_df, specs)
    # bad_ctx=False et good_setup=True désignent les mêmes trades ici.
    assert mask.sum() == (~structured_df["bad_ctx"].astype(bool)).sum()


def test_les_tranches_de_periode_couvrent_tous_les_trades(structured_df):
    seg = add_period_segments(structured_df, n_periods=4)
    assert seg["_period"].notna().all()
    assert seg["_period"].nunique() == 4


def test_comparaison_detecte_une_amelioration_reelle():
    base = normalize(pd.DataFrame([
        {"time": f"2025-01-{i+1:02d} 10:00", "side": "buy",
         "profit": 1.0 if i % 2 else -1.0} for i in range(40)]))
    # Candidat : mêmes trades mais on a retiré quelques perdants.
    cand = normalize(pd.DataFrame([
        {"time": f"2025-01-{i+1:02d} 10:00", "side": "buy",
         "profit": 1.0 if i % 3 else -1.0} for i in range(40)]))
    res = compare_backtests(base, cand)
    assert res["deltas"]["profit_factor"] > 0
    assert res["verdict"]["verdict"] in {"ADOPTER", "PRUDENCE"}


def test_comparaison_rejette_un_candidat_qui_vide_la_strategie():
    base = normalize(pd.DataFrame([
        {"time": f"2025-01-{i+1:02d} 10:00", "side": "buy",
         "profit": 1.0 if i % 2 else -0.5} for i in range(60)]))
    cand = normalize(pd.DataFrame([
        {"time": "2025-01-01 10:00", "side": "buy", "profit": 5.0},
        {"time": "2025-01-02 10:00", "side": "buy", "profit": 5.0},
    ]))
    res = compare_backtests(base, cand)
    assert res["verdict"]["verdict"] == "REJETER"
    assert any("trades" in r for r in res["verdict"]["blocking_reasons"])


def test_le_markdown_de_comparaison_contient_les_deux_colonnes():
    base = normalize(pd.DataFrame([
        {"time": f"2025-01-{i+1:02d} 10:00", "side": "buy",
         "profit": 1.0 if i % 2 else -1.0} for i in range(40)]))
    md = comparison_markdown(compare_backtests(base, base))
    assert "Baseline" in md and "Candidat" in md and "Profit factor" in md


def test_validate_degrade_proprement_sur_petit_echantillon(minimal_df):
    res = validate_candidate(minimal_df, n_sims=100)
    assert res["available"] is False
