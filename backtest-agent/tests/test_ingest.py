"""Ingestion : détection des colonnes, dérivations, formats."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from backtest_agent.ingest import load_trades, normalize


def test_detecte_les_alias_francais_et_anglais():
    df = normalize(pd.DataFrame([
        {"Date/Time": "2025-01-01 10:00", "Ticker": "BTCUSDT", "Sens": "achat",
         "Prix entree": 100, "SL": 98, "TP": 104, "Profit": 2.0},
    ]))
    assert "datetime" in df.columns
    assert df.loc[0, "symbol"] == "BTCUSDT"
    assert df.loc[0, "direction"] == "BUY"       # « achat » -> BUY
    assert df.loc[0, "entry_price"] == 100


def test_derive_le_resultat_depuis_le_pnl_quand_result_absent():
    df = normalize(pd.DataFrame([
        {"time": "2025-01-01 10:00", "side": "buy", "profit": 3.0},
        {"time": "2025-01-02 10:00", "side": "sell", "profit": -1.0},
        {"time": "2025-01-03 10:00", "side": "buy", "profit": 0.0},
    ]))
    assert list(df["result"]) == ["WIN", "LOSS", "BE"]


def test_calcule_le_multiple_de_r_avec_le_bon_signe_en_vente():
    """En SELL, le prix descend = gain. Une erreur de signe ici fausserait tout."""
    df = normalize(pd.DataFrame([
        # BUY : risque 2, sortie +4 => +2R
        {"time": "2025-01-01 10:00", "side": "buy", "entry_price": 100,
         "stop_loss": 98, "exit_price": 104, "profit": 4},
        # SELL : risque 2, prix descend de 4 => +2R (et non -2R)
        {"time": "2025-01-02 10:00", "side": "sell", "entry_price": 100,
         "stop_loss": 102, "exit_price": 96, "profit": 4},
    ]))
    assert df.loc[0, "pnl_r"] == pytest.approx(2.0)
    assert df.loc[1, "pnl_r"] == pytest.approx(2.0)


def test_normalise_la_confiance_en_pourcentage_vers_0_1():
    df = normalize(pd.DataFrame([
        {"time": "2025-01-01 10:00", "side": "buy", "profit": 1, "confidence": 80},
        {"time": "2025-01-02 10:00", "side": "buy", "profit": 1, "confidence": 60},
    ]))
    assert df["confidence"].max() <= 1.0


def test_trie_par_date_meme_si_le_fichier_est_desordonne():
    """Le drawdown n'a de sens que sur une séquence chronologique."""
    df = normalize(pd.DataFrame([
        {"time": "2025-03-01 10:00", "side": "buy", "profit": 1},
        {"time": "2025-01-01 10:00", "side": "buy", "profit": 1},
        {"time": "2025-02-01 10:00", "side": "buy", "profit": 1},
    ]))
    assert df["datetime"].is_monotonic_increasing


def test_detecte_les_colonnes_inconnues_comme_conditions():
    df = normalize(pd.DataFrame([
        {"time": "2025-01-01 10:00", "side": "buy", "profit": 1,
         "ob": True, "fvg": False, "un_truc_maison": "A"},
    ]))
    conditions = df.attrs["conditions"]
    assert "ob" in conditions and "fvg" in conditions
    assert "un_truc_maison" in conditions   # inconnue = gardée comme contexte


def test_charge_csv_et_json(tmp_path):
    rows = [{"time": "2025-01-01 10:00", "side": "buy", "profit": 1.0}]
    csv_path = tmp_path / "t.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    json_path = tmp_path / "t.json"
    json_path.write_text(json.dumps(rows), encoding="utf-8")
    assert len(load_trades(csv_path)) == 1
    assert len(load_trades(json_path)) == 1


def test_json_enveloppe_dans_une_cle_trades(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps(
        {"trades": [{"time": "2025-01-01 10:00", "side": "buy", "profit": 1.0}]}),
        encoding="utf-8")
    assert len(load_trades(path)) == 1


def test_erreur_claire_sur_format_non_supporte(tmp_path):
    path = tmp_path / "t.xlsx"
    path.write_text("peu importe", encoding="utf-8")
    with pytest.raises(ValueError, match="Format non supporté"):
        load_trades(path)


def test_erreur_claire_si_aucun_resultat_derivable():
    with pytest.raises(ValueError, match="Impossible de déterminer le résultat"):
        normalize(pd.DataFrame([{"time": "2025-01-01 10:00", "side": "buy"}]))
