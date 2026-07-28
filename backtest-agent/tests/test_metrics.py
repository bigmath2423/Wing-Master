"""Métriques globales : valeurs exactes sur des cas calculables à la main."""

from __future__ import annotations

import pandas as pd
import pytest

from backtest_agent.ingest import normalize
from backtest_agent.jsonutil import dumps
from backtest_agent.metrics import global_metrics


def _df(pnls: list[float]) -> pd.DataFrame:
    return normalize(pd.DataFrame([
        {"time": f"2025-01-{i+1:02d} 10:00", "side": "buy", "profit": p}
        for i, p in enumerate(pnls)
    ]))


def test_valeurs_exactes_sur_un_cas_calculable_a_la_main():
    # 3 gains de 2, 2 pertes de 1 => PF = 6/2 = 3 ; espérance = 4/5 = 0.8
    m = global_metrics(_df([2, 2, 2, -1, -1]))
    assert m.n_trades == 5
    assert m.n_wins == 3 and m.n_losses == 2
    assert m.win_rate == pytest.approx(0.6)
    assert m.profit_factor == pytest.approx(3.0)
    assert m.expectancy == pytest.approx(0.8)
    assert m.payoff_ratio == pytest.approx(2.0)
    assert m.net_pnl == pytest.approx(4.0)


def test_drawdown_maximal_sur_une_sequence_connue():
    # Équité : 5, 2, 0, 4 -> pic à 5, creux à 0 => drawdown = -5
    m = global_metrics(_df([5, -3, -2, 4]))
    assert m.max_drawdown_abs == pytest.approx(-5.0)


def test_series_consecutives():
    m = global_metrics(_df([1, 1, 1, -1, -1, 1]))
    assert m.max_consecutive_wins == 3
    assert m.max_consecutive_losses == 2


def test_profit_factor_est_none_et_non_infini_sans_perte():
    """Régression : `inf` produisait du JSON invalide (rejeté hors de Python)."""
    m = global_metrics(_df([1, 2, 3]))
    assert m.profit_factor is None
    assert m.payoff_ratio is None


def test_le_json_produit_est_valide_meme_sans_perte():
    """Régression : json.dumps émettait `Infinity`, non conforme RFC 8259."""
    import json
    m = global_metrics(_df([1, 2, 3])).to_dict()
    texte = dumps(m)
    assert "Infinity" not in texte and "NaN" not in texte
    # Un parseur strict doit accepter le fichier.
    json.loads(texte, parse_constant=lambda c: pytest.fail(f"non-JSON: {c}"))


def test_prefere_le_pnl_en_r_quand_il_existe(structured_df):
    m = global_metrics(structured_df)
    assert m.pnl_unit == "R"


def test_regularite_mensuelle(structured_df):
    m = global_metrics(structured_df)
    assert m.consistency["available"] is True
    assert m.consistency["periods"] >= 1
    assert 0.0 <= m.consistency["profitable_period_ratio"] <= 1.0


def test_erreur_claire_sans_aucune_colonne_de_pnl():
    df = pd.DataFrame({"result": ["WIN"], "datetime": ["2025-01-01"]})
    df.attrs["conditions"] = []
    with pytest.raises(ValueError, match="Aucune colonne de PnL"):
        global_metrics(df)
