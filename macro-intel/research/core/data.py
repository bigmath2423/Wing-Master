"""Chargement et normalisation des donnees OHLCV.

Accepte sans configuration les exports les plus courants :
  - TradingView  ("Exporter les donnees du graphique")  : time,open,high,low,close,Volume
  - MetaTrader 5 ("Outils > Centre d'historique > Exporter"): DATE,TIME,OPEN,...
  - Dukascopy / generique                                  : timestamp,o,h,l,c,v

Le reste du moteur ne voit qu'un DataFrame indexe par le temps (UTC) avec les
colonnes open/high/low/close/volume, ce qui isole totalement la recherche du
format de la source.
"""
from __future__ import annotations

import pandas as pd

_ALIASES = {
    "open": {"open", "o", "ouverture"},
    "high": {"high", "h", "haut", "max"},
    "low": {"low", "l", "bas", "min"},
    "close": {"close", "c", "cloture", "clot", "price", "last"},
    "volume": {"volume", "v", "vol", "tickvol", "tick_volume", "real_volume"},
}
_TIME = {"time", "date", "datetime", "timestamp", "date et heure", "<date>", "gmt time"}


def _find(cols: list[str], names: set[str]) -> str | None:
    low = {c.lower().strip().strip("<>"): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    for key, orig in low.items():
        if any(key.startswith(n) for n in names):
            return orig
    return None


def load_ohlcv(path: str, tz: str = "UTC") -> pd.DataFrame:
    """Lit un CSV de bougies et retourne un DataFrame normalise et trie."""
    sep = "\t" if str(path).endswith((".tsv", ".txt")) else None
    df = pd.read_csv(path, sep=sep, engine="python", encoding="utf-8-sig")
    cols = list(df.columns)

    tcol = _find(cols, _TIME)
    if tcol is None:
        raise ValueError(f"Aucune colonne de temps reconnue dans {cols}")
    # MT5 separe parfois la date et l'heure en deux colonnes
    hcol = _find([c for c in cols if c != tcol], {"time", "heure", "<time>"})
    if hcol is not None and hcol != tcol:
        ts = pd.to_datetime(
            df[tcol].astype(str) + " " + df[hcol].astype(str), errors="coerce", format="mixed"
        )
    else:
        raw = df[tcol]
        if pd.api.types.is_numeric_dtype(raw):
            unit = "s" if raw.max() < 1e11 else "ms"
            ts = pd.to_datetime(raw, unit=unit, errors="coerce", utc=True).tz_localize(None)
        else:
            ts = pd.to_datetime(raw, errors="coerce", format="mixed")

    out = pd.DataFrame(index=pd.DatetimeIndex(ts, name="time"))
    for field, names in _ALIASES.items():
        c = _find(cols, names)
        if c is None:
            if field == "volume":
                out[field] = float("nan")  # le volume manque souvent : traite comme absent
                continue
            raise ValueError(f"Colonne '{field}' introuvable dans {cols}")
        out[field] = pd.to_numeric(df[c], errors="coerce")

    out = out[~out.index.isna()].sort_index()
    out = out[~out.index.duplicated(keep="last")]
    out = out.dropna(subset=["open", "high", "low", "close"])
    if out.empty:
        raise ValueError(f"Aucune bougie exploitable dans {path}")
    return out


def infer_timeframe_minutes(df: pd.DataFrame) -> float:
    """Timeframe median en minutes (robuste aux trous de week-end)."""
    d = df.index.to_series().diff().dt.total_seconds().dropna()
    return float(d.median() / 60.0) if len(d) else float("nan")


def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Re-echantillonne en bougies superieures ('15min', '1h', '4h', '1D')."""
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    return df.resample(rule, label="left", closed="left").agg(agg).dropna(subset=["open"])


def describe(df: pd.DataFrame) -> str:
    tf = infer_timeframe_minutes(df)
    return (
        f"{len(df):,} bougies | TF median {tf:.0f} min | "
        f"{df.index[0]:%Y-%m-%d} -> {df.index[-1]:%Y-%m-%d} | "
        f"volume {'present' if df['volume'].notna().any() else 'ABSENT'}"
    )
