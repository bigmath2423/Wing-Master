"""Couche d'ingestion : lit un fichier de backtest (CSV/JSON) et le normalise
vers un schéma interne stable, quelle que soit la source (export TradingView,
webhook, fichier maison).

Le point délicat avec TradingView : les noms de colonnes changent selon la
langue de l'interface et la version. On passe donc par une table de
correspondance souple + une détection heuristique.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

# Schéma interne cible. Toute la suite du code ne connaît QUE ces colonnes.
CANONICAL_COLUMNS = [
    "datetime",        # datetime d'entrée du trade (tz-aware si possible)
    "symbol",          # actif tradé (ex: BTCUSDT)
    "timeframe",       # ex: 5m, 1h, 4h
    "direction",       # BUY / SELL
    "entry_price",
    "stop_loss",
    "take_profit",
    "exit_price",
    "result",          # WIN / LOSS / BE (dérivé si absent)
    "pnl",             # gain/perte en devise ou en R
    "pnl_r",           # gain/perte en R (dérivé si possible)
    "duration_min",    # durée du trade en minutes
    "confidence",      # score de confiance du signal [0..1] ou [0..100]
]

# Colonnes de conditions de marché : on ne les liste pas en dur, on détecte
# toute colonne booléenne / catégorielle supplémentaire comme "condition".
KNOWN_CONDITION_HINTS = [
    "ob", "orderblock", "order_block", "fvg", "sweep", "liquidity",
    "vwap", "structure", "bos", "choch", "atr", "trend", "session",
    "rsi", "ema", "volume", "imbalance", "premium", "discount",
    "score", "wyckoff", "zone", "htf",
]

# Correspondances (source -> canonique). Clés en minuscules, sans espaces.
ALIASES: dict[str, list[str]] = {
    "datetime": [
        "datetime", "date/time", "date_time", "time", "date", "opentime",
        "entrytime", "entry_time", "dateheure", "date_heure", "date et heure",
        "timestamp",
    ],
    "symbol": ["symbol", "ticker", "actif", "asset", "instrument", "pair"],
    "timeframe": ["timeframe", "tf", "resolution", "interval", "ut"],
    "direction": ["direction", "side", "type", "sens", "signal", "position"],
    "entry_price": ["entryprice", "entry_price", "entry", "price", "openprice",
                    "prixentree", "prix_entree", "avgprice"],
    "stop_loss": ["stoploss", "stop_loss", "sl", "stop"],
    "take_profit": ["takeprofit", "take_profit", "tp", "target"],
    "exit_price": ["exitprice", "exit_price", "exit", "closeprice",
                   "prixsortie", "prix_sortie"],
    "result": ["result", "outcome", "resultat", "issue", "status", "win"],
    "pnl": ["pnl", "profit", "netprofit", "net_profit", "gain", "gainperte",
            "gain_perte", "p&l", "pl", "realizedpnl", "profitusd",
            "p&l net usd", "pnl net", "net p&l"],
    "pnl_r": ["pnl_r", "r", "rr", "r_multiple", "rmultiple", "risque"],
    "duration_min": ["duration_min", "duration", "duree", "bars_held",
                     "barsheld", "holdingtime", "temps"],
    "confidence": ["confidence", "score", "confiance", "conf", "proba",
                   "probability", "signal_score", "signalscore"],
}


def _clean_key(name: str) -> str:
    """Normalise un nom de colonne pour la comparaison : minuscules, accents
    repliés vers leur lettre ASCII (« Numéro » -> « numero », pas « numro »),
    puis tout caractère non alphanumérique supprimé.

    Sans le repli d'accents, la regex `[^a-z0-9]` supprime purement et
    simplement les lettres accentuées au lieu de les convertir — « Durée »
    devenait « dure » et « cumulé » devenait « cumul », cassant silencieusement
    toute correspondance qui s'attendait à « duree »/« cumule ».
    """
    texte = unicodedata.normalize("NFKD", str(name).strip().lower())
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", texte)


def _build_reverse_map(columns: Iterable[str]) -> dict[str, str]:
    """Associe chaque colonne source à une colonne canonique quand c'est possible."""
    reverse: dict[str, str] = {}
    cleaned = {col: _clean_key(col) for col in columns}
    for canonical, aliases in ALIASES.items():
        alias_set = {_clean_key(a) for a in aliases}
        for src, ckey in cleaned.items():
            if ckey in alias_set and canonical not in reverse.values():
                reverse[src] = canonical
                break
    return reverse


def _read_raw(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt", ".tsv"}:
        sep = "\t" if suffix == ".tsv" else None
        # sep=None + engine="python" => détection automatique du séparateur.
        return pd.read_csv(path, sep=sep, engine="python")
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            # Formats fréquents: {"trades": [...]} ou {"data": [...]}
            for key in ("trades", "data", "rows", "records"):
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
        return pd.DataFrame(data)
    raise ValueError(f"Format non supporté : {suffix}")


def _detect_conditions(df: pd.DataFrame, used: set[str]) -> list[str]:
    """Toute colonne non canonique est considérée comme une condition de marché."""
    conditions = []
    for col in df.columns:
        if col in used:
            continue
        ckey = _clean_key(col)
        looks_known = any(hint in ckey for hint in KNOWN_CONDITION_HINTS)
        # On garde aussi les colonnes inconnues : mieux vaut trop de contexte.
        if looks_known or df[col].nunique(dropna=True) <= max(20, len(df) // 5):
            conditions.append(col)
    return conditions


def _coerce_direction(series: pd.Series) -> pd.Series:
    def to_dir(v):
        s = str(v).strip().lower()
        if s in {"buy", "long", "achat", "1", "b", "up"}:
            return "BUY"
        if s in {"sell", "short", "vente", "-1", "s", "down"}:
            return "SELL"
        return str(v).upper()
    return series.map(to_dir)


def _derive_result(df: pd.DataFrame) -> pd.Series:
    if "result" in df.columns and df["result"].notna().any():
        def to_res(v):
            s = str(v).strip().lower()
            if s in {"win", "tp", "gagnant", "gain", "true", "1", "profit"}:
                return "WIN"
            if s in {"loss", "sl", "perdant", "perte", "false", "0"}:
                return "LOSS"
            if s in {"be", "breakeven", "flat", "nul"}:
                return "BE"
            return str(v).upper()
        return df["result"].map(to_res)
    # Sinon on dérive depuis le pnl.
    if "pnl" in df.columns:
        return np.where(df["pnl"] > 0, "WIN",
                        np.where(df["pnl"] < 0, "LOSS", "BE"))
    raise ValueError("Impossible de déterminer le résultat : ni 'result' ni 'pnl'.")


def _derive_pnl_r(df: pd.DataFrame) -> pd.Series | None:
    """Calcule le multiple de R (gain/perte rapporté au risque initial)."""
    if "pnl_r" in df.columns and df["pnl_r"].notna().any():
        return pd.to_numeric(df["pnl_r"], errors="coerce")
    needed = {"entry_price", "stop_loss", "exit_price"}
    if needed.issubset(df.columns):
        risk = (df["entry_price"] - df["stop_loss"]).abs()
        signed = np.where(df["direction"].eq("SELL"),
                          df["entry_price"] - df["exit_price"],
                          df["exit_price"] - df["entry_price"])
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(risk > 0, signed / risk, np.nan)
        return pd.Series(r, index=df.index)
    return None


_ENTRY_HINTS = ("entrer", "entry")
_EXIT_HINTS = ("sortir", "exit")

# Décodage du texte de diagnostic injecté via `comment=` sur `strategy.entry()`
# côté Pine : `S<total> L<liquidite> T<structure> Z<zone> W<wyckoff> H<htf>
# V<volume> P<vwap>`, un par composante du score du Module 6 (Decision Engine).
# Optionnel : n'existe que si le script Pine a été enrichi pour l'exporter.
_SCORE_SIGNAL_RE = re.compile(
    r"^S(-?\d+)\s+L(-?\d+)\s+T(-?\d+)\s+Z(-?\d+)\s+W(-?\d+)\s+H(-?\d+)\s+"
    r"V(-?\d+)\s+P(-?\d+)$"
)
_SCORE_FIELDS = [
    "score_total", "score_liquidity", "score_structure", "score_zone",
    "score_wyckoff", "score_htf", "score_volume", "score_vwap",
]


def _parse_score_signal(text: object) -> dict[str, int] | None:
    """Décode la décomposition du score si le Signal d'entrée suit le format
    enrichi ci-dessus ; retourne None pour un signal classique (« BUY »/« SELL »)
    ou tout texte qui ne correspond pas exactement au motif."""
    match = _SCORE_SIGNAL_RE.match(str(text).strip())
    if match is None:
        return None
    return dict(zip(_SCORE_FIELDS, (int(g) for g in match.groups())))


def _find_col(columns: Iterable[str], *substrings: str) -> str | None:
    """Cherche la première colonne dont le nom nettoyé CONTIENT l'un des motifs.

    Contrairement à `_build_reverse_map` (égalité exacte après nettoyage), cette
    recherche est volontairement souple : elle sert uniquement à détecter le
    format « deux lignes par trade » de TradingView, où les en-têtes portent des
    suffixes de devise variables (« Prix USD », « P&L net USD »...).
    """
    for col in columns:
        ckey = _clean_key(col)
        if any(s in ckey for s in substrings):
            return col
    return None


def _pivot_entry_exit_pairs(df: pd.DataFrame) -> pd.DataFrame | None:
    """Reconnaît et fusionne le format « List of Trades » du Strategy Tester
    TradingView quand il exporte DEUX lignes par trade — une d'entrée
    (« Entrer long/short »), une de sortie (« Sortir du long/short »), reliées
    par un numéro de trade commun — plutôt qu'une ligne unique par trade.

    Sans cette fusion, chaque trade serait compté DEUX FOIS dans toutes les
    statistiques (taux de réussite, profit factor, drawdown...) : une erreur
    silencieuse qui fausserait tout le rapport sans qu'aucun message n'alerte
    l'utilisateur. C'est précisément ce que ce paquet s'interdit de faire.

    Retourne None si le fichier n'a pas cette forme (une ligne par trade déjà,
    ou colonnes indispensables absentes) : `normalize()` poursuit alors sans
    modification, comme avant.
    """
    id_col = _find_col(df.columns, "numerodetrade", "tradenumber", "trade")
    type_col = _find_col(df.columns, "type")
    if id_col is None or type_col is None:
        return None

    types = df[type_col].astype(str).str.lower()
    motif_entree = "|".join(_ENTRY_HINTS)
    motif_sortie = "|".join(_EXIT_HINTS)
    est_entree = types.str.contains(motif_entree, regex=True)
    est_sortie = types.str.contains(motif_sortie, regex=True)
    if not est_entree.any() or not est_sortie.any():
        return None  # pas le format à deux lignes : rien à fusionner

    dt_col = _find_col(df.columns, "dateheure", "datetime", "date")
    prix_col = _find_col(df.columns, "prix", "price")
    # "P&L" perd son « & » au nettoyage (_clean_key) et devient "pl", pas "pnl" :
    # "P&L net USD" -> "plnetusd". D'où "plnet" en plus de "pnlnet".
    pnl_col = _find_col(df.columns, "plnet", "pnlnet", "profit", "pnl", "gain")
    if dt_col is None or prix_col is None or pnl_col is None:
        return None  # champs indispensables absents : on ne devine pas

    signal_col = _find_col(df.columns, "signal")
    duree_col = _find_col(df.columns, "duree", "duration", "bars")
    commission_col = _find_col(df.columns, "commission")
    retour_col = _find_col(df.columns, "retour", "return")
    cum_pnl_col = _find_col(df.columns, "cumule", "cumulative", "cumprofit")
    mfe_col = _find_col(df.columns, "excursionfavorable", "runup")
    mae_col = _find_col(df.columns, "excursionadverse", "drawdown")

    rows = []
    for trade_id, groupe in df.groupby(id_col):
        idx = groupe.index
        entree = groupe[est_entree.loc[idx]]
        sortie = groupe[est_sortie.loc[idx]]
        if entree.empty or sortie.empty:
            continue  # trade encore ouvert ou ligne incomplète : ignoré
        e, s = entree.iloc[0], sortie.iloc[0]

        direction = "SELL" if "short" in str(e[type_col]).lower() else "BUY"
        row = {
            "datetime": e[dt_col],
            "direction": direction,
            "entry_price": e[prix_col],
            "exit_price": s[prix_col],
            "pnl": s[pnl_col],
            "trade_id": trade_id,
        }
        if signal_col is not None:
            row["exit_signal"] = s[signal_col]
            score = _parse_score_signal(e[signal_col])
            if score is not None:
                row.update(score)
        if duree_col is not None:
            row["duration_bars"] = s[duree_col]
        if commission_col is not None:
            row["commission"] = s[commission_col]
        if retour_col is not None:
            row["return_pct"] = s[retour_col]
        if cum_pnl_col is not None:
            row["cum_pnl"] = s[cum_pnl_col]
        if mfe_col is not None:
            row["mfe"] = s[mfe_col]
        if mae_col is not None:
            row["mae"] = s[mae_col]
        rows.append(row)

    return pd.DataFrame(rows) if rows else None


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme un DataFrame brut en schéma interne + attache la liste des
    colonnes de conditions dans df.attrs['conditions']."""
    pivote = _pivot_entry_exit_pairs(df)
    if pivote is not None:
        df = pivote  # déjà en schéma canonique ; le renommage ci-dessous est un no-op

    reverse = _build_reverse_map(df.columns)
    renamed = df.rename(columns=reverse).copy()

    # Types.
    if "datetime" in renamed.columns:
        renamed["datetime"] = pd.to_datetime(renamed["datetime"], errors="coerce",
                                              utc=False)
    for col in ["entry_price", "stop_loss", "take_profit", "exit_price",
                "pnl", "confidence", "duration_min"]:
        if col in renamed.columns:
            renamed[col] = pd.to_numeric(renamed[col], errors="coerce")

    if "direction" in renamed.columns:
        renamed["direction"] = _coerce_direction(renamed["direction"])

    renamed["result"] = _derive_result(renamed)

    pnl_r = _derive_pnl_r(renamed)
    if pnl_r is not None:
        renamed["pnl_r"] = pnl_r

    # Normalise la confiance sur [0..1] si elle semble être en pourcentage.
    if "confidence" in renamed.columns:
        conf = renamed["confidence"]
        if conf.dropna().gt(1).mean() > 0.5:
            renamed["confidence"] = conf / 100.0

    conditions = _detect_conditions(renamed, set(CANONICAL_COLUMNS))
    renamed.attrs["conditions"] = conditions

    # Trie chronologiquement quand c'est possible : indispensable pour le drawdown.
    if "datetime" in renamed.columns and renamed["datetime"].notna().any():
        renamed = renamed.sort_values("datetime").reset_index(drop=True)

    return renamed


def load_trades(path: str | Path) -> pd.DataFrame:
    """Point d'entrée : chemin de fichier -> DataFrame normalisé."""
    raw = _read_raw(path)
    if raw.empty:
        raise ValueError("Fichier de backtest vide.")
    return normalize(raw)
