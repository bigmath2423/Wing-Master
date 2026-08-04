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

# Tuples et non ensembles : l'ordre est PRIORITAIRE. Avec un set, l'ordre
# d'iteration de Python est arbitraire, et un export MT5 (colonnes <DATE> et
# <TIME> separees) pouvait voir <TIME> retenu comme colonne principale — toutes
# les bougies heritaient alors de la date du jour, sans la moindre erreur levee.
_ALIASES = {
    "open": ("open", "ouverture", "o"),
    "high": ("high", "haut", "max", "h"),
    "low": ("low", "bas", "min", "l"),
    "close": ("close", "cloture", "clot", "price", "last", "c"),
    "volume": ("volume", "tickvol", "tick_volume", "real_volume", "vol", "v"),
}
_TIME = ("datetime", "date et heure", "gmt time", "timestamp", "date", "time")
_TIME_ONLY = ("time", "heure")


def _find(cols: list[str], names: tuple[str, ...]) -> str | None:
    low: dict[str, str] = {}
    for c in cols:
        low.setdefault(c.lower().strip().strip("<>"), c)
    for n in names:                       # priorite : correspondance exacte
        if n in low:
            return low[n]
    for n in names:                       # puis correspondance par prefixe
        for key, orig in low.items():
            if key.startswith(n):
                return orig
    return None


def _read_any(path: str) -> pd.DataFrame:
    """Lit le CSV quels que soient son encodage et son separateur.

    MT5 (Windows) exporte en UTF-16 avec des points-virgules, TradingView en
    UTF-8 avec des virgules, Dukascopy en UTF-8 avec des virgules ou des
    tabulations. On essaie les combinaisons jusqu'a obtenir plusieurs colonnes.
    """
    errors = []
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "latin-1"):
        for sep in (None, ";", ",", "\t"):
            try:
                df = pd.read_csv(path, sep=sep, engine="python", encoding=enc)
            except Exception as e:  # encodage ou separateur invalide
                errors.append(f"{enc}/{sep or 'auto'}: {type(e).__name__}")
                continue
            if df.shape[1] >= 4:
                return df
    raise ValueError(
        "Impossible de lire le fichier comme un CSV de bougies "
        f"(essais : {'; '.join(errors[:6])})"
    )


def _parse_datetime(s: pd.Series) -> pd.Series:
    """Analyse des dates tous formats, y compris le '2024.01.01' de MT5.

    L'ambiguite jour/mois (01.02.2024) ne se tranche pas au jugé : on essaie les
    deux lectures et on retient celle qui produit une serie CHRONOLOGIQUE, ce
    qu'un historique de bougies est forcement.
    """
    txt = s.astype(str).str.strip().str.replace(".", "-", regex=False).str.replace("/", "-", regex=False)

    def score(cand: pd.Series) -> tuple[float, float]:
        ok = float(cand.notna().mean())
        v = cand.dropna()
        mono = float((v.diff().dropna() > pd.Timedelta(0)).mean()) if len(v) > 1 else 0.0
        return (ok, mono)

    # Chemin rapide : formats explicites. Indispensable sur de gros fichiers —
    # sans format, pandas retombe sur dateutil et analyse ligne par ligne, ce qui
    # prend plusieurs minutes sur 250 000 bougies.
    fmts = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d",
            "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%m-%d-%Y %H:%M:%S", "%Y%m%d %H:%M:%S")
    for f in fmts:
        cand = pd.to_datetime(txt, errors="coerce", format=f)
        if cand.notna().mean() > 0.95:
            return cand

    best, best_score = None, (-1.0, -1.0)
    for dayfirst in (False, True):
        try:
            cand = pd.to_datetime(txt, errors="coerce", dayfirst=dayfirst)
        except Exception:
            continue
        sc = score(cand)
        if sc > best_score:
            best, best_score = cand, sc
    return best if best is not None else pd.to_datetime(s, errors="coerce")


def load_ohlcv(path: str, tz: str = "UTC") -> pd.DataFrame:
    """Lit un CSV de bougies et retourne un DataFrame normalise et trie."""
    df = _read_any(path)
    df.columns = [str(c).strip() for c in df.columns]
    cols = list(df.columns)

    tcol = _find(cols, _TIME)
    if tcol is None:
        raise ValueError(
            "Aucune colonne de date/heure : ce fichier ne contient pas de bougies. "
            f"Colonnes trouvees : {cols}"
        )
    # MT5 separe parfois la date et l'heure en deux colonnes
    hcol = _find([c for c in cols if c != tcol], _TIME_ONLY)
    raw = df[tcol]
    if hcol is not None and hcol != tcol:
        ts = _parse_datetime(raw.astype(str) + " " + df[hcol].astype(str))
    elif pd.api.types.is_numeric_dtype(raw):
        unit = "s" if raw.max() < 1e11 else "ms"
        ts = pd.to_datetime(raw, unit=unit, errors="coerce", utc=True).dt.tz_localize(None)
    else:
        ts = _parse_datetime(raw)

    out = pd.DataFrame(index=pd.DatetimeIndex(ts, name="time"))
    for field, names in _ALIASES.items():
        c = _find(cols, names)
        if c is None:
            if field == "volume":
                out[field] = float("nan")  # le volume manque souvent : traite comme absent
                continue
            raise ValueError(f"Colonne '{field}' introuvable dans {cols}")
        # .to_numpy() est indispensable : assigner une Series indexee 0..n a un
        # DataFrame indexe par le temps declencherait un alignement sur l'index
        # et remplirait tout de NaN sans lever la moindre erreur.
        out[field] = pd.to_numeric(df[c], errors="coerce").to_numpy()

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
