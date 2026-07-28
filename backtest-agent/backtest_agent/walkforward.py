"""Validation walk-forward : la vraie protection contre la sur-optimisation.

L'idée : une règle découverte sur les données passées ne vaut rien si elle ne
tient pas sur des données qu'elle n'a jamais « vues ». On découpe donc le backtest
chronologiquement en IN-SAMPLE (IS, on cherche des pistes) et OUT-OF-SAMPLE (OOS,
on vérifie). On ne retient une règle QUE si son effet se confirme en OOS.

Ce module ne remplace pas un vrai re-backtest de l'indicateur : il rejoue le
FILTRE sur les trades existants. C'est déjà un filtre à hypothèses bien plus
sévère qu'une simple analyse in-sample.
"""

from __future__ import annotations

import pandas as pd

from .features import bucketize
from .suggestions import build_suggestions, _subset_metrics, _pnl_series


def _apply_spec(df: pd.DataFrame, spec: dict) -> pd.Series:
    """Retourne le masque booléen correspondant à un filter_spec."""
    col = spec["column"]
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    same = df[col].astype(str) == str(spec["modality"])
    return same if spec["direction"] == "keep" else ~same


def _evaluate_on(df: pd.DataFrame, spec: dict) -> dict:
    """Mesure l'effet d'un filtre sur un jeu de données (baseline vs filtré)."""
    df = bucketize(df)
    pnl = _pnl_series(df)
    mask = _apply_spec(df, spec)
    n_after = int(mask.sum())
    base = _subset_metrics(pnl)
    filt = _subset_metrics(pnl[mask.values]) if n_after > 0 else {"n": 0}
    if filt.get("profit_factor") is None or base.get("profit_factor") is None:
        return {"applicable": False, "n_after": n_after}
    return {
        "applicable": n_after > 0,
        "n_after": n_after,
        "baseline_pf": base["profit_factor"],
        "filtered_pf": filt["profit_factor"],
        "pf_delta": round((filt["profit_factor"] or 0) - (base["profit_factor"] or 0), 4),
        "baseline_expectancy": base["expectancy"],
        "filtered_expectancy": filt["expectancy"],
        "expectancy_delta": round(filt["expectancy"] - base["expectancy"], 4),
        "retained_ratio": round(n_after / base["n"], 3) if base["n"] else 0.0,
    }


def _verdict(is_res: dict, oos_res: dict, min_oos_trades: int) -> str:
    """Une règle TIENT si elle améliore l'espérance en IS ET en OOS, avec un
    échantillon OOS suffisant et sans effondrer le nombre de trades."""
    if not oos_res.get("applicable") or oos_res.get("n_after", 0) < min_oos_trades:
        return "NON TESTABLE (échantillon OOS insuffisant)"
    is_good = is_res["expectancy_delta"] > 0 and is_res["pf_delta"] > 0
    oos_good = oos_res["expectancy_delta"] > 0 and oos_res["pf_delta"] > 0
    if is_good and oos_good:
        return "TIENT (confirmé hors échantillon)"
    if is_good and not oos_good:
        return "REJETÉ (effet in-sample uniquement → sur-optimisation probable)"
    return "AMBIGU (effet instable)"


def walk_forward(df: pd.DataFrame, split: float = 0.7,
                 min_oos_trades: int = 10, max_rules: int = 8) -> dict:
    """Découpe chronologiquement, cherche des filtres sur l'IS, les valide sur
    l'OOS, et rend un verdict par règle."""
    if "datetime" in df.columns and df["datetime"].notna().any():
        df = df.sort_values("datetime").reset_index(drop=True)
    n = len(df)
    cut = int(n * split)
    if cut < 20 or (n - cut) < 20:
        return {"available": False,
                "reason": f"Pas assez de trades pour un split fiable (n={n})."}

    is_df = df.iloc[:cut].copy()
    oos_df = df.iloc[cut:].copy()
    is_df.attrs["conditions"] = df.attrs.get("conditions", [])
    oos_df.attrs["conditions"] = df.attrs.get("conditions", [])

    is_suggestions = build_suggestions(is_df)
    results = []
    for t in is_suggestions["ab_tests"][:max_rules]:
        spec = t.get("filter_spec")
        if not spec:
            continue
        is_res = _evaluate_on(is_df, spec)
        oos_res = _evaluate_on(oos_df, spec)
        results.append({
            "rule": t["proposed_change"],
            "rationale": t["problem_detected"],
            "filter_spec": spec,          # conservé pour l'étape 2 (propositions)
            "in_sample": is_res,
            "out_of_sample": oos_res,
            "verdict": _verdict(is_res, oos_res, min_oos_trades),
        })

    kept = [r for r in results if r["verdict"].startswith("TIENT")]
    return {
        "available": True,
        "split": split,
        "n_total": n,
        "n_in_sample": cut,
        "n_out_of_sample": n - cut,
        "is_period": _period_str(is_df),
        "oos_period": _period_str(oos_df),
        "rules_evaluated": len(results),
        "rules_confirmed": len(kept),
        "results": results,
        "note": (
            "Seules les règles au verdict 'TIENT' méritent d'être envisagées, et "
            "encore : idéalement re-testées par un vrai re-backtest de l'indicateur "
            "et sur plusieurs actifs / régimes de marché."
        ),
    }


def _period_str(df: pd.DataFrame) -> str | None:
    if "datetime" in df.columns and df["datetime"].notna().any():
        return f"{df['datetime'].min()} → {df['datetime'].max()}"
    return None


def walkforward_markdown(wf: dict) -> str:
    if not wf.get("available"):
        return f"# Walk-forward\n\n⚠️ {wf.get('reason', 'non disponible')}\n"
    lines = ["# Validation walk-forward\n"]
    lines.append(f"- Split : {int(wf['split']*100)}% in-sample / "
                 f"{100-int(wf['split']*100)}% out-of-sample")
    lines.append(f"- In-sample : {wf['n_in_sample']} trades ({wf['is_period']})")
    lines.append(f"- Out-of-sample : {wf['n_out_of_sample']} trades ({wf['oos_period']})")
    lines.append(f"- Règles testées : **{wf['rules_evaluated']}** — "
                 f"confirmées hors échantillon : **{wf['rules_confirmed']}**\n")
    for i, r in enumerate(wf["results"], 1):
        is_r, oos = r["in_sample"], r["out_of_sample"]
        lines.append(f"## Règle #{i} — {r['verdict']}")
        lines.append(f"- **Règle :** {r['rule']}")
        lines.append(f"- _{r['rationale']}_")
        lines.append(f"- **In-sample :** ΔPF {is_r.get('pf_delta')}, "
                     f"Δespérance {is_r.get('expectancy_delta')} "
                     f"({is_r.get('n_after')} trades, {is_r.get('retained_ratio')} conservés)")
        if oos.get("applicable"):
            lines.append(f"- **Out-of-sample :** ΔPF {oos.get('pf_delta')}, "
                         f"Δespérance {oos.get('expectancy_delta')} "
                         f"({oos.get('n_after')} trades, {oos.get('retained_ratio')} conservés)")
        else:
            lines.append(f"- **Out-of-sample :** non testable "
                         f"({oos.get('n_after', 0)} trades)")
        lines.append("")
    lines.append(f"> {wf['note']}")
    return "\n".join(lines)
