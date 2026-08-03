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


# --- Repli des accents ------------------------------------------------------

def test_clean_key_replie_les_accents_au_lieu_de_les_supprimer():
    """Régression : la regex de nettoyage SUPPRIMAIT les lettres accentuées
    plutôt que de les convertir, cassant silencieusement toute correspondance
    censée reconnaître « Numéro », « Durée », « cumulé »..."""
    from backtest_agent.ingest import _clean_key
    assert _clean_key("Numéro de trade") == "numerodetrade"
    assert _clean_key("Durée (barres)") == "dureebarres"
    assert _clean_key("P&L cumulé USD") == "plcumuleusd"


# --- Format TradingView « deux lignes par trade » ---------------------------

def _export_tradingview_deux_lignes(n_trades: int = 3) -> pd.DataFrame:
    """Reproduit la forme réelle du « List of Trades » du Strategy Tester :
    une ligne d'entrée et une ligne de sortie par trade, numéro partagé."""
    lignes = []
    for i in range(1, n_trades + 1):
        sens = "short" if i % 2 else "long"
        entree, sortie = (100.0, 95.0) if sens == "short" else (100.0, 105.0)
        pnl = (entree - sortie) if sens == "short" else (sortie - entree)
        lignes.append({
            "Numéro de trade": i, "Type": f"Entrer {sens}",
            "Date et heure": f"2025-01-{i:02d} 10:00", "Signal": "SELL" if sens == "short" else "BUY",
            "Prix USD": entree, "P&L net USD": pnl, "Durée (barres)": 10 + i,
            "Commission USD": 0, "Retour %": 1.0,
            "Excursion favorable USD": 2.0, "Excursion adverse USD": -1.0,
            "P&L cumulé USD": pnl,
        })
        lignes.append({
            "Numéro de trade": i, "Type": f"Sortir du {sens}",
            "Date et heure": f"2025-01-{i:02d} 14:00", "Signal": "TP1",
            "Prix USD": sortie, "P&L net USD": pnl, "Durée (barres)": 10 + i,
            "Commission USD": 0, "Retour %": 1.0,
            "Excursion favorable USD": 2.0, "Excursion adverse USD": -1.0,
            "P&L cumulé USD": pnl,
        })
    return pd.DataFrame(lignes)


def test_fusionne_les_paires_entree_sortie_tradingview():
    df = normalize(_export_tradingview_deux_lignes(4))
    assert len(df) == 4, "Deux lignes par trade doivent devenir UNE seule ligne."
    assert set(df["direction"]) == {"BUY", "SELL"}
    assert (df["result"].isin(["WIN", "LOSS"])).all()


def test_ne_double_compte_pas_les_trades():
    """La régression centrale : sans la fusion, chaque trade était compté deux
    fois dans toutes les statistiques, en silence."""
    df = normalize(_export_tradingview_deux_lignes(10))
    assert len(df) == 10


def test_prix_entree_et_sortie_corrects_apres_fusion():
    df = normalize(_export_tradingview_deux_lignes(1))
    # Trade 1 = short : entrée 100, sortie 95, gain (short gagnant).
    row = df.iloc[0]
    assert row["entry_price"] == pytest.approx(100.0)
    assert row["exit_price"] == pytest.approx(95.0)
    assert row["direction"] == "SELL"
    assert row["result"] == "WIN"


def test_conserve_le_contexte_supplementaire_comme_conditions():
    df = normalize(_export_tradingview_deux_lignes(6))
    assert "exit_signal" in df.columns
    assert "duration_bars" in df.columns
    assert "exit_signal" in df.attrs["conditions"]


def test_trade_ouvert_sans_ligne_de_sortie_est_ignore_sans_planter():
    """Un trade encore en cours (entrée sans sortie exportée) ne doit ni
    planter ni être compté comme un trade complet."""
    df_brut = _export_tradingview_deux_lignes(3)
    # Supprime la ligne de sortie du dernier trade : position encore ouverte.
    df_brut = df_brut[~((df_brut["Numéro de trade"] == 3)
                        & (df_brut["Type"].str.startswith("Sortir")))]
    df = normalize(df_brut)
    assert len(df) == 2  # seuls les 2 trades complets sont conservés


def test_format_a_une_ligne_par_trade_nest_pas_affecte():
    """Garde-fou anti-régression : le format normal (une ligne = un trade) ne
    doit JAMAIS être détecté à tort comme le format à deux lignes."""
    df = normalize(pd.DataFrame([
        {"datetime": "2025-01-01 10:00", "side": "buy", "profit": 1.0},
        {"datetime": "2025-01-02 10:00", "side": "sell", "profit": -0.5},
    ]))
    assert len(df) == 2


# --- Décodage du score enrichi (Module 6 / Decision Engine) -----------------

def test_extrait_le_score_du_signal_enrichi():
    """Le Signal d'entrée peut porter la décomposition du score injectée via
    `comment=` côté Pine : `S<total> L<liquidite> T<structure> Z<zone>
    W<wyckoff> H<htf> V<volume> P<vwap>`."""
    lignes = [
        {"Numéro de trade": 1, "Type": "Entrer short",
         "Date et heure": "2025-01-01 10:00",
         "Signal": "S100 L20 T20 Z12 W10 H10 V5 P5",
         "Prix USD": 100.0, "P&L net USD": 5.0},
        {"Numéro de trade": 1, "Type": "Sortir du short",
         "Date et heure": "2025-01-01 14:00", "Signal": "TP1s",
         "Prix USD": 95.0, "P&L net USD": 5.0},
    ]
    df = normalize(pd.DataFrame(lignes))
    row = df.iloc[0]
    assert row["score_total"] == 100
    assert row["score_liquidity"] == 20
    assert row["score_structure"] == 20
    assert row["score_zone"] == 12
    assert row["score_wyckoff"] == 10
    assert row["score_htf"] == 10
    assert row["score_volume"] == 5
    assert row["score_vwap"] == 5
    assert "score_total" in df.attrs["conditions"]


def test_signal_classique_ne_produit_pas_de_colonnes_de_score():
    """Un export sans enrichissement (Signal = 'BUY'/'SELL' classique) ne doit
    faire apparaître aucune colonne de score : il n'y a rien à décoder."""
    df = normalize(_export_tradingview_deux_lignes(2))
    assert "score_total" not in df.columns


def test_parse_score_signal_ignore_le_texte_non_conforme():
    from backtest_agent.ingest import _parse_score_signal
    assert _parse_score_signal("BUY") is None
    assert _parse_score_signal("TP1s") is None
    assert _parse_score_signal(float("nan")) is None


def test_pivot_retourne_none_sans_colonnes_indispensables():
    from backtest_agent.ingest import _pivot_entry_exit_pairs
    df = pd.DataFrame([
        {"Numéro de trade": 1, "Type": "Entrer long"},
        {"Numéro de trade": 1, "Type": "Sortir du long"},
    ])
    assert _pivot_entry_exit_pairs(df) is None
