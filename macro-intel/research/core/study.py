"""Mesure de l'avantage statistique d'une feature, sans complaisance.

Trois pieges tuent 90 % des "backtests qui marchent". Ils sont traites ici :

1. AUTOCORRELATION. Les rendements futurs sur fenetre glissante se chevauchent :
   deux observations voisines partagent presque toute leur trajectoire. Un
   t-stat naif est alors gonfle d'un facteur sqrt(horizon) et fait passer du
   bruit pour un edge. On utilise un bootstrap par BLOCS, qui reechantillonne
   des segments contigus et preserve donc la dependance temporelle.

2. TESTS MULTIPLES. Tester 30 features au seuil 5 %, c'est s'attendre a ~1,5
   faux positif meme si AUCUNE ne fonctionne. On corrige par Benjamini-Hochberg
   (controle du taux de fausses decouvertes).

3. IN-SAMPLE. Une feature selectionnee sur toute la periode est deja
   sur-ajustee. Chaque mesure est donc rendue separement sur la periode
   d'apprentissage et sur la periode de validation, jamais vue.

Convention : tous les effets sont exprimes en multiples d'ATR (comparable entre
timeframes et regimes de volatilite) et ORIENTES dans le sens de la feature :
un effet positif = la feature anticipe correctement son sens.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def forward_move(df: pd.DataFrame, horizon: int, atr_s: pd.Series) -> pd.Series:
    """Deplacement du prix sur `horizon` bougies, en unites d'ATR de l'entree."""
    fwd = df["close"].shift(-horizon) - df["close"]
    return fwd / atr_s.replace(0, np.nan)


def block_bootstrap_ci(x: np.ndarray, block: int, n_boot: int = 2000,
                       alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    """IC de la moyenne par bootstrap par blocs (preserve l'autocorrelation)."""
    x = x[np.isfinite(x)]
    if len(x) < block * 3:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(len(x) / block))
    starts_max = len(x) - block
    means = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, starts_max + 1, n_blocks)
        sample = np.concatenate([x[s:s + block] for s in starts])[:len(x)]
        means[b] = sample.mean()
    return (float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2)))


def newey_west_t(x: np.ndarray, lags: int) -> float:
    """t-stat de la moyenne robuste a l'autocorrelation (Newey-West)."""
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 30:
        return np.nan
    d = x - x.mean()
    g0 = (d @ d) / n
    var = g0
    for k in range(1, min(lags, n - 1) + 1):
        gk = (d[k:] @ d[:-k]) / n
        var += 2 * (1 - k / (lags + 1)) * gk
    if var <= 0:
        return np.nan
    return float(x.mean() / np.sqrt(var / n))


def benjamini_hochberg(p: np.ndarray, q: float = 0.10) -> np.ndarray:
    """Retourne le masque des hypotheses retenues au taux de fausses decouvertes q."""
    p = np.asarray(p, float)
    ok = np.isfinite(p)
    idx = np.where(ok)[0]
    if len(idx) == 0:
        return np.zeros(len(p), bool)
    order = idx[np.argsort(p[idx])]
    m = len(order)
    thresh = q * np.arange(1, m + 1) / m
    passed = p[order] <= thresh
    keep = np.zeros(len(p), bool)
    if passed.any():
        last = np.where(passed)[0].max()
        keep[order[:last + 1]] = True
    return keep


def _p_from_t(t: float) -> float:
    if not np.isfinite(t):
        return np.nan
    from scipy import stats
    return float(2 * (1 - stats.norm.cdf(abs(t))))


def study_features(feat: pd.DataFrame, df: pd.DataFrame, atr_s: pd.Series,
                   horizon: int, feature_sides: dict[str, int],
                   fdr_q: float = 0.10, seed: int = 0,
                   min_n: int = 300, min_rate: float = 0.02, max_rate: float = 0.98,
                   winsor: float = 10.0) -> pd.DataFrame:
    """Effet de chaque feature sur le deplacement futur, en ATR.

    feature_sides : {nom_feature: +1 si la feature predit la HAUSSE, -1 la BAISSE}

    Deux garde-fous, ajoutes apres qu'un test a blanc sur marche aleatoire ait
    produit un faux positif massif (t = +19,7 sur du bruit pur) :

      - TAUX DE BASE. Une feature vraie 99,9 % du temps laisse un groupe temoin
        minuscule ; l'ecart de moyennes n'y mesure plus que la variance du
        temoin. On exige donc que chaque groupe pese au moins `min_rate` des
        observations et compte `min_n` points.
      - VALEURS ABERRANTES. Diviser par un ATR quasi nul fabrique des
        rendements normalises enormes qui dominent la moyenne. On borne donc le
        deplacement normalise a +/- `winsor` ATR.
    """
    fwd = forward_move(df, horizon, atr_s).clip(-winsor, winsor)
    rows = []
    for name, side in feature_sides.items():
        if name not in feat.columns:
            continue
        mask = feat[name].fillna(False).astype(bool).to_numpy()
        y = (fwd * side).to_numpy(float)
        valid = np.isfinite(y)
        on = y[mask & valid]
        off = y[(~mask) & valid]
        rate = mask.mean()
        if len(on) < min_n or len(off) < min_n or not (min_rate <= rate <= max_rate):
            continue
        # l'effet est l'ECART a la population : une feature qui vaut la moyenne n'apporte rien
        eff = float(on.mean() - off.mean()) if len(off) else float(on.mean())
        t = newey_west_t(on - (off.mean() if len(off) else 0.0), lags=horizon)
        lo, hi = block_bootstrap_ci(on - (off.mean() if len(off) else 0.0),
                                    block=max(horizon, 5), seed=seed)
        rows.append(dict(feature=name, sens="haussier" if side > 0 else "baissier",
                         n=len(on), taux=100 * len(on) / len(mask),
                         effet_atr=eff, ic_bas=lo, ic_haut=hi,
                         t_nw=t, p=_p_from_t(t),
                         wr=100 * float((on > 0).mean())))
    if not rows:
        return pd.DataFrame()
    res = pd.DataFrame(rows)
    res["retenue_fdr"] = benjamini_hochberg(res["p"].to_numpy(), q=fdr_q)
    return res.sort_values("effet_atr", ascending=False).reset_index(drop=True)


def classify(res: pd.DataFrame, strong: float = 0.05, weak: float = 0.02) -> pd.DataFrame:
    """Classement demande : Excellent / Utile / Neutre / A supprimer.

    Le verdict combine la TAILLE de l'effet et sa SIGNIFICATIVITE : un effet
    enorme non significatif reste du bruit, un effet significatif mais minuscule
    ne paiera jamais le spread.
    """
    def verdict(r):
        if not r["retenue_fdr"]:
            return "Neutre" if abs(r["effet_atr"]) < weak else "A supprimer (non significatif)"
        if r["effet_atr"] >= strong:
            return "Excellent"
        if r["effet_atr"] >= weak:
            return "Utile"
        if r["effet_atr"] <= -weak:
            return "A supprimer (effet inverse)"
        return "Neutre"
    out = res.copy()
    out["verdict"] = out.apply(verdict, axis=1)
    return out


def split_walk_forward(df: pd.DataFrame, n_folds: int = 4) -> list[tuple[slice, slice]]:
    """Decoupage ancre : chaque fold apprend sur le passe et valide sur le futur."""
    n = len(df)
    bounds = np.linspace(0, n, n_folds + 2, dtype=int)
    return [(slice(0, bounds[k + 1]), slice(bounds[k + 1], bounds[k + 2]))
            for k in range(n_folds)]
