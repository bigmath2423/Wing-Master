#!/usr/bin/env python3
"""Pipeline de recherche : PHASE 1 (valeur des modules) + PHASE 2 (ablation).

    python3 run.py --data XAUUSD_M5.csv --horizon 20 --out out/

Sorties dans --out :
    phase1_modules.csv    classement Excellent / Utile / Neutre / A supprimer
    phase2_ablation.csv   effet de la desactivation de chaque module
    rapport.md            synthese lisible

Rien n'est "valide" sur la periode d'apprentissage seule : chaque chiffre est
rendu en apprentissage ET en validation (donnees jamais vues), et l'ecart entre
les deux est la mesure du sur-ajustement.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import backtest as bt   # noqa: E402
from core import data as dl       # noqa: E402
from core import features as ft   # noqa: E402
from core import study as st      # noqa: E402

# Sens predit par chaque feature : +1 = anticipe une hausse, -1 = une baisse.
SIDES = {
    "bull_bos": 1, "bear_bos": -1, "bull_choch": 1, "bear_choch": -1,
    "bull_sweep": 1, "bear_sweep": -1,
    "bull_sweep_recent": 1, "bear_sweep_recent": -1,
    "bull_break_recent": 1, "bear_break_recent": -1,
    "bull_fvg_touch": 1, "bear_fvg_touch": -1,
    "bull_ob_touch": 1, "bear_ob_touch": -1,
    "in_discount": 1, "in_premium": -1,
    "wy_bull_ctx": 1, "wy_bear_ctx": -1,
    "bull_imb": 1, "bear_imb": -1,
    "bull_breaker": 1, "bear_breaker": -1,
    "struct_bull": 1, "struct_bear": -1,
    "htf_bull": 1, "htf_bear": -1,
    "above_vwap": 1, "below_vwap": -1,
    "bull_fib": 1, "bear_fib": -1,
    "bull_vol_ok": 1, "bear_vol_ok": -1,
    "atr_ok": 1, "adx_trend": 1,
    "kill_zone": 1, "sess_london": 1, "sess_ny": 1,
}

# Reference : la regle de l'indicateur actuel, condition par condition.
BASE_LONG = ["bull_sweep_recent", "bull_break_recent", "zone_long"]
BASE_SHORT = ["bear_sweep_recent", "bear_break_recent", "zone_short"]
OPTIONAL = ["htf_bull", "above_vwap", "atr_ok", "adx_trend", "kill_zone",
            "wy_ctx", "vol_ok", "fib", "pd"]


def build_rule_inputs(f: pd.DataFrame) -> pd.DataFrame:
    g = pd.DataFrame(index=f.index)
    g["zone_long"] = f["bull_ob_touch"] | f["bull_fvg_touch"] | f["in_discount"]
    g["zone_short"] = f["bear_ob_touch"] | f["bear_fvg_touch"] | f["in_premium"]
    for k in ("bull_sweep_recent", "bear_sweep_recent", "bull_break_recent",
              "bear_break_recent", "htf_bull", "htf_bear", "above_vwap",
              "below_vwap", "atr_ok", "adx_trend", "kill_zone", "wy_bull_ctx",
              "wy_bear_ctx", "bull_vol_ok", "bear_vol_ok", "bull_fib",
              "bear_fib", "in_discount", "in_premium"):
        g[k] = f[k].fillna(False).astype(bool)
    g["wy_ctx_long"], g["wy_ctx_short"] = g["wy_bull_ctx"], g["wy_bear_ctx"]
    g["vol_ok_long"], g["vol_ok_short"] = g["bull_vol_ok"], g["bear_vol_ok"]
    g["fib_long"], g["fib_short"] = g["bull_fib"], g["bear_fib"]
    g["pd_long"], g["pd_short"] = g["in_discount"], g["in_premium"]
    g["htf_long"], g["htf_short"] = g["htf_bull"], g["htf_bear"]
    g["vwap_long"], g["vwap_short"] = g["above_vwap"], g["below_vwap"]
    return g


def make_signals(g: pd.DataFrame, active: list[str], cooldown: int = 10):
    """Signal = conjonction des conditions actives, avec anti-rafale."""
    def side(sfx: str, base: list[str]) -> pd.Series:
        m = pd.Series(True, index=g.index)
        for cond in base:
            col = cond if cond in g.columns else f"{cond}_{sfx}"
            if col in g.columns:
                m &= g[col]
        for cond in active:
            col = f"{cond}_{sfx}" if f"{cond}_{sfx}" in g.columns else cond
            if col in g.columns:
                m &= g[col]
        return m
    lg = side("long", ["zone_long", "bull_sweep_recent", "bull_break_recent"])
    sh = side("short", ["zone_short", "bear_sweep_recent", "bear_break_recent"])
    # un signal ne peut pas se repeter avant `cooldown` bougies
    out = []
    for s in (lg, sh):
        arr = s.to_numpy().copy()      # to_numpy() peut renvoyer une vue en lecture seule
        last = -10**9
        for i in range(len(arr)):
            if arr[i]:
                if i - last <= cooldown:
                    arr[i] = False
                else:
                    last = i
        out.append(pd.Series(arr, index=s.index))
    return out[0], out[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="CSV de bougies (TradingView / MT5 / generique)")
    ap.add_argument("--horizon", type=int, default=20, help="horizon d'evaluation, en bougies")
    ap.add_argument("--cost", type=float, default=0.30, help="cout aller-retour en unites de prix")
    ap.add_argument("--sl-atr", type=float, default=1.5)
    ap.add_argument("--out", default="out")
    ap.add_argument("--split", type=float, default=0.6, help="part apprentissage (reste = validation)")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    df = dl.load_ohlcv(a.data)
    print("Donnees :", dl.describe(df))
    f = ft.build_features(df)
    g = build_rule_inputs(f)
    atr_s = f["atr"]

    cut = int(len(df) * a.split)
    parts = {"apprentissage": slice(0, cut), "validation": slice(cut, len(df))}
    print(f"Apprentissage : {df.index[0]:%Y-%m-%d} -> {df.index[cut-1]:%Y-%m-%d} | "
          f"Validation : {df.index[cut]:%Y-%m-%d} -> {df.index[-1]:%Y-%m-%d}")

    # ---------------- PHASE 1 : valeur propre de chaque module ----------------
    ph1 = []
    for nom, sl_ in parts.items():
        r = st.study_features(f.iloc[sl_], df.iloc[sl_], atr_s.iloc[sl_], a.horizon, SIDES)
        if r.empty:
            continue
        r = st.classify(r)
        r.insert(0, "periode", nom)
        ph1.append(r)
    p1 = pd.concat(ph1, ignore_index=True) if ph1 else pd.DataFrame()
    p1.to_csv(f"{a.out}/phase1_modules.csv", index=False)

    # ---------------- PHASE 2 : ablation, un module a la fois ----------------
    plan = bt.ExitPlan(sl_atr=a.sl_atr)
    costs = bt.Costs(per_unit=a.cost)
    rows = []
    full = ["htf", "vwap", "atr_ok", "adx_trend", "kill_zone", "wy_ctx", "vol_ok", "fib", "pd"]
    for nom, sl_ in parts.items():
        d, gg, aa = df.iloc[sl_], g.iloc[sl_], atr_s.iloc[sl_]
        lg, sh = make_signals(gg, full)
        base = bt.metrics(bt.simulate(d, aa, lg, sh, plan, costs), f"REFERENCE ({nom})")
        rows.append({**base, "periode": nom, "module_retire": "-"})
        for mod in full:
            act = [m for m in full if m != mod]
            lg2, sh2 = make_signals(gg, act)
            m = bt.metrics(bt.simulate(d, aa, lg2, sh2, plan, costs), f"sans {mod}")
            rows.append({**bt.compare(base, m), "periode": nom, "module_retire": mod})
    p2 = pd.DataFrame(rows)
    p2.to_csv(f"{a.out}/phase2_ablation.csv", index=False)

    with open(f"{a.out}/rapport.md", "w", encoding="utf-8") as fh:
        fh.write(f"# Rapport de recherche\n\nDonnees : {dl.describe(df)}\n\n")
        fh.write(f"Cout applique : {a.cost} / unite de prix, stop {a.sl_atr} ATR, "
                 f"horizon {a.horizon} bougies.\n\n## PHASE 1 — valeur propre des modules\n\n")
        if not p1.empty:
            cols = ["periode", "feature", "sens", "n", "effet_atr", "ic_bas", "ic_haut", "t_nw", "retenue_fdr", "verdict"]
            fh.write(p1[cols].to_markdown(index=False, floatfmt=".4f"))
        fh.write("\n\n## PHASE 2 — ablation\n\n")
        fh.write(p2.to_markdown(index=False, floatfmt=".3f"))
    print(f"\nEcrit : {a.out}/phase1_modules.csv, phase2_ablation.csv, rapport.md")
    if not p1.empty:
        keep = p1[(p1.periode == "validation") & p1.retenue_fdr]
        print(f"\nModules survivant a la validation out-of-sample + FDR : {len(keep)}")
        for _, r in keep.iterrows():
            print(f"  {r.feature:<22} effet {r.effet_atr:+.4f} ATR  [{r.ic_bas:+.4f};{r.ic_haut:+.4f}]  {r.verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
