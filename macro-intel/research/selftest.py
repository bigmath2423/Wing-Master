#!/usr/bin/env python3
"""Test a blanc : le moteur trouve-t-il un edge la ou il n'y en a AUCUN ?

On genere une marche aleatoire (aucune structure exploitable par construction),
puis on lui applique exactement le meme pipeline qu'a des donnees reelles.

Un moteur de recherche correct doit rendre ici :
  - des effets de module centres sur zero,
  - quasiment aucun module retenu apres correction des tests multiples,
  - une esperance de backtest egale au cout d'execution, au signe pres.

Si ce test "decouvre" des modules performants, tout resultat produit ensuite sur
des donnees reelles est du bruit. C'est le garde-fou qui separe une recherche
quantitative d'une chasse aux motifs.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import backtest as bt   # noqa: E402
from core import features as ft   # noqa: E402
from core import study as st      # noqa: E402
from run import SIDES, build_rule_inputs, make_signals  # noqa: E402


def random_market(n: int = 120_000, s0: float = 2000.0, seed: int = 7) -> pd.DataFrame:
    """Marche aleatoire en M5 avec volatilite realiste pour l'or (~0.05 %/bougie)."""
    rng = np.random.default_rng(seed)
    ret = rng.normal(0, 0.0005, n)
    close = s0 * np.exp(np.cumsum(ret))
    spread = np.abs(rng.normal(0, 0.0004, n)) * close
    high = close + spread * rng.uniform(0.2, 1.0, n)
    low = close - spread * rng.uniform(0.2, 1.0, n)
    open_ = np.concatenate([[s0], close[:-1]])
    high = np.maximum.reduce([high, open_, close])
    low = np.minimum.reduce([low, open_, close])
    idx = pd.date_range("2020-01-01", periods=n, freq="5min", name="time")
    return pd.DataFrame(dict(open=open_, high=high, low=low, close=close,
                             volume=rng.integers(50, 500, n).astype(float)), index=idx)


def main() -> int:
    print("=== TEST A BLANC : marche aleatoire, aucun edge par construction ===\n")
    df = random_market()
    print(f"Donnees synthetiques : {len(df):,} bougies M5 "
          f"({df.index[0]:%Y-%m-%d} -> {df.index[-1]:%Y-%m-%d})\n")

    f = ft.build_features(df)
    print(f"Features construites : {f.shape[1]} colonnes\n")

    res = st.classify(st.study_features(f, df, f["atr"], horizon=20, feature_sides=SIDES))
    if res.empty:
        print("ECHEC : aucune feature evaluee.")
        return 1

    retenues = int(res["retenue_fdr"].sum())
    print(f"--- PHASE 1 sur du bruit pur ({len(res)} modules testes) ---")
    print(res[["feature", "n", "effet_atr", "ic_bas", "ic_haut", "t_nw", "retenue_fdr"]]
          .head(8).to_string(index=False, float_format=lambda x: f"{x:+.4f}"))
    print(f"\nEffet median          : {res.effet_atr.median():+.4f} ATR (attendu ~0)")
    print(f"Effet max en valeur abs: {res.effet_atr.abs().max():.4f} ATR")
    print(f"Modules retenus (FDR) : {retenues} / {len(res)}  (attendu ~0)")

    g = build_rule_inputs(f)
    lg, sh = make_signals(g, ["htf", "vwap", "atr_ok", "adx_trend"])
    for cost in (0.0, 0.30):
        tr = bt.simulate(df, f["atr"], lg, sh, bt.ExitPlan(), bt.Costs(per_unit=cost))
        m = bt.metrics(tr, f"bruit, cout {cost}")
        if m.get("trades", 0):
            print(f"\n--- Backtest sur bruit, cout {cost:.2f} ---")
            print(f"  trades {m['trades']:>5} | WR {m['win_rate']:.1f} % | PF {m['profit_factor']:.2f} "
                  f"| esperance {m['expectancy_R']:+.4f} R | t {m['t_stat']:+.2f} "
                  f"| cout moyen {m['cout_moy_R']:.4f} R")

    # Criteres de calibration. Juger une TAILLE d'effet brute n'a pas de sens :
    # elle depend du nombre d'observations. Ce qui doit etre calibre, c'est la
    # distribution des t-stats, qui doit ressembler a une loi normale centree.
    med = abs(res.effet_atr.median())
    share_t2 = float((res.t_nw.abs() > 1.96).mean())
    t_mean = float(res.t_nw.mean())
    print(f"\nt-stat moyen          : {t_mean:+.2f} (attendu ~0)")
    print(f"Part des |t| > 1.96   : {share_t2:.1%} (attendu ~5 %, tolere jusqu'a 15 %)")
    if retenues:
        print("Faux positifs retenus :", ", ".join(res[res.retenue_fdr].feature.tolist()))

    ok_center = med < 0.03 and abs(t_mean) < 1.0
    ok_tdist = share_t2 <= 0.15
    ok_fdr = retenues <= max(1, int(0.10 * len(res)))
    print("\n=== VERDICT DU GARDE-FOU ===")
    print(f"  effets centres sur zero              : {'OK' if ok_center else 'ECHEC'}")
    print(f"  distribution des t-stats calibree    : {'OK' if ok_tdist else 'ECHEC'}")
    print(f"  pas de fausse decouverte massive     : {'OK' if ok_fdr else 'ECHEC'}")
    if ok_center and ok_tdist and ok_fdr:
        print("\nLe moteur ne fabrique pas d'edge sur du bruit : il est utilisable sur donnees reelles.")
        return 0
    print("\nLe moteur produit des faux positifs : NE PAS l'utiliser tel quel.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
