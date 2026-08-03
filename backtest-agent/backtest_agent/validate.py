"""ÉTAPE 3 — Boucle fermée : valider un candidat, puis comparer les vrais exports.

Limite assumée : on ne peut PAS exécuter du Pine localement (TradingView est une
plateforme fermée). La boucle se ferme donc en deux temps :

  A. `validate_candidate` — rejoue la PILE COMPLÈTE de filtres sur les trades
     existants. C'est indispensable car des règles validées INDIVIDUELLEMENT
     peuvent très mal se combiner : elles retirent souvent les mêmes trades, et
     l'empilement peut vider l'échantillon. On y ajoute la cohérence par actif,
     par période, et un Monte-Carlo sur le drawdown.

  B. `compare_backtests` — compare deux VRAIS exports TradingView (baseline vs
     candidat) tête-à-tête. C'est l'étape qui ferme réellement la boucle, une
     fois que tu as re-backtesté le fichier candidat.

Aucune des deux ne « décide » à ta place : elles rendent un verdict argumenté.
"""

from __future__ import annotations

import pandas as pd

from .features import bucketize, _pnl_series
from .suggestions import _subset_metrics, pf_delta
from .walkforward import _apply_spec
from .proposals import build_proposals
from .metrics import global_metrics
from .robustness import monte_carlo_drawdown, segment_metrics, add_period_segments

MIN_TRADES_AFTER = 30
MIN_RETAINED = 0.25
MIN_SEGMENT_AGREEMENT = 0.6


def _combined_mask(df: pd.DataFrame, specs: list[dict]) -> pd.Series:
    """ET logique de tous les filtres. Un trade doit satisfaire TOUTES les règles."""
    mask = pd.Series(True, index=df.index)
    for spec in specs:
        mask &= _apply_spec(df, spec)
    return mask


def _verdict(combined: dict, segments: dict, mc_base: dict, mc_filt: dict) -> dict:
    """Verdict transparent : chaque refus est motivé."""
    reasons: list[str] = []
    blocking = False

    n_after = combined["filtered"]["n"]
    retained = combined["retained_ratio"]

    if n_after < MIN_TRADES_AFTER:
        reasons.append(f"Échantillon résiduel trop faible ({n_after} trades < "
                       f"{MIN_TRADES_AFTER}).")
        blocking = True
    if retained < MIN_RETAINED:
        reasons.append(f"La pile de filtres supprime {(1-retained):.0%} des trades : "
                       "stratégie dénaturée.")
        blocking = True
    if combined["expectancy_delta"] <= 0:
        reasons.append("L'espérance ne s'améliore pas une fois les filtres combinés.")
        blocking = True
    if combined["pf_delta"] is not None and combined["pf_delta"] <= 0:
        reasons.append("Le profit factor ne s'améliore pas une fois les filtres combinés.")
        blocking = True

    # Cohérence entre segments (actifs et périodes).
    warnings: list[str] = []
    for label, rows in segments.items():
        usable = [r for r in rows if r.get("applicable")]
        empty = [r for r in rows if not r.get("applicable")]
        if empty:
            warnings.append(
                f"{len(empty)} segment(s) par {label} ne conservent AUCUN trade "
                f"après filtrage ({', '.join(r['segment'] for r in empty)}) : "
                "la stratégie cesserait de trader sur ces portions.")
        if not usable:
            continue
        agree = sum(1 for r in usable if r["improved"]) / len(usable)
        if agree < MIN_SEGMENT_AGREEMENT:
            warnings.append(
                f"Effet incohérent par {label} : seulement {agree:.0%} des segments "
                f"s'améliorent ({len(usable)} segments testés).")

    if mc_base.get("available") and mc_filt.get("available"):
        if mc_filt["simulated_median"] < mc_base["simulated_median"]:
            warnings.append(
                "Le drawdown médian simulé (Monte-Carlo) est PIRE après filtrage "
                f"({mc_filt['simulated_median']} contre {mc_base['simulated_median']}) : "
                "le gain d'espérance se paie en risque de séquence.")

    if blocking:
        verdict = "REJETER"
    elif warnings:
        verdict = "PRUDENCE"
    else:
        verdict = "ADOPTER (sous réserve de re-backtest réel)"

    return {"verdict": verdict, "blocking_reasons": reasons, "warnings": warnings}


def validate_candidate(df: pd.DataFrame, split: float = 0.7,
                       min_oos_trades: int = 10, n_sims: int = 2000,
                       n_periods: int = 4) -> dict:
    """Valide la pile complète de filtres proposés (étape 2) sur les données."""
    proposals = build_proposals(df, split=split, min_oos_trades=min_oos_trades)
    if not proposals.get("available"):
        return {"available": False, "reason": proposals.get("reason")}

    specs = [p["filter_spec"] for p in proposals["proposals"] if p.get("filter_spec")]
    if not specs:
        return {"available": True, "n_filters": 0, "proposals": proposals,
                "verdict": {"verdict": "RIEN À VALIDER",
                            "blocking_reasons": [
                                "Aucune règle n'a été confirmée en walk-forward."],
                            "warnings": []},
                "note": "Ne rien changer est ici la décision correcte."}

    # Bucketisation UNE SEULE FOIS sur le jeu complet : sinon les bornes des
    # buckets (ATR) changeraient d'un segment à l'autre et fausseraient tout.
    work = bucketize(df)
    work = add_period_segments(work, n_periods=n_periods)
    mask = _combined_mask(work, specs)

    pnl = _pnl_series(work)
    base = _subset_metrics(pnl)
    filt = _subset_metrics(pnl[mask.values]) if mask.any() else {"n": 0}

    if filt.get("n", 0) == 0:
        return {"available": True, "n_filters": len(specs), "proposals": proposals,
                "verdict": {"verdict": "REJETER",
                            "blocking_reasons": [
                                "La combinaison des filtres ne laisse aucun trade "
                                "exploitable."],
                            "warnings": []}}

    combined = {
        "baseline": base,
        "filtered": filt,
        "expectancy_delta": round(filt["expectancy"] - base["expectancy"], 4),
        "pf_delta": pf_delta(base["profit_factor"], filt["profit_factor"]),
        "drawdown_delta": round(filt["max_drawdown"] - base["max_drawdown"], 4),
        "retained_ratio": round(filt["n"] / base["n"], 3) if base["n"] else 0.0,
        "trades_removed": base["n"] - filt["n"],
    }

    segments = {}
    if "symbol" in work.columns and work["symbol"].nunique() > 1:
        segments["actif"] = segment_metrics(work, mask, "symbol")
    segments["période"] = segment_metrics(work, mask, "_period")

    mc_base = monte_carlo_drawdown(pnl, n_sims=n_sims)
    mc_filt = monte_carlo_drawdown(pnl[mask.values], n_sims=n_sims)

    # Effet marginal de chaque filtre DANS la pile (que perd-on en le retirant ?).
    marginal = []
    for i, spec in enumerate(specs):
        others = [s for j, s in enumerate(specs) if j != i]
        m_others = _combined_mask(work, others) if others else pd.Series(
            True, index=work.index)
        without = _subset_metrics(pnl[m_others.values]) if m_others.any() else {"n": 0}
        if without.get("profit_factor") is not None:
            marginal.append({
                "filter": f"{spec['column']} = {spec['modality']} "
                          f"({spec['direction']})",
                "pf_with_stack": filt["profit_factor"],
                "pf_without_this_filter": without["profit_factor"],
                "marginal_pf_contribution": round(
                    (filt["profit_factor"] or 0) - (without["profit_factor"] or 0), 4),
                "extra_trades_removed": without["n"] - filt["n"],
            })

    return {
        "available": True,
        "n_filters": len(specs),
        "filters": [p["human_change"] for p in proposals["proposals"]],
        "combined": combined,
        "segments": segments,
        "monte_carlo_baseline": mc_base,
        "monte_carlo_filtered": mc_filt,
        "marginal_contributions": marginal,
        "verdict": _verdict(combined, segments, mc_base, mc_filt),
        "proposals": proposals,
        "note": ("Cette validation rejoue les filtres sur les trades EXISTANTS. "
                 "Elle ne remplace pas un re-backtest réel du .pine candidat sur "
                 "TradingView : un filtre change aussi quels trades EXISTENT "
                 "(chaînage des positions), ce qu'un rejeu ne peut pas simuler."),
    }


def compare_backtests(baseline: pd.DataFrame, candidate: pd.DataFrame) -> dict:
    """Compare deux VRAIS exports TradingView (baseline vs candidat re-backtesté).

    C'est l'étape qui ferme la boucle : ici les deux jeux viennent réellement du
    Strategy Tester, donc le chaînage des positions est correct des deux côtés.
    """
    a = global_metrics(baseline).to_dict()
    b = global_metrics(candidate).to_dict()

    def delta(key: str) -> float | None:
        va, vb = a.get(key), b.get(key)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            return round(vb - va, 4)
        return None

    keys = ["n_trades", "win_rate", "profit_factor", "expectancy", "payoff_ratio",
            "net_pnl", "max_drawdown_abs", "sharpe_like", "max_consecutive_losses"]
    deltas = {k: delta(k) for k in keys}

    reasons: list[str] = []
    warnings: list[str] = []
    if (deltas.get("profit_factor") or 0) <= 0:
        reasons.append("Le profit factor ne s'améliore pas sur le re-backtest réel.")
    if (deltas.get("expectancy") or 0) <= 0:
        reasons.append("L'espérance par trade ne s'améliore pas.")
    if a["n_trades"] and b["n_trades"] / a["n_trades"] < MIN_RETAINED:
        reasons.append(f"Le candidat ne conserve que "
                       f"{b['n_trades']/a['n_trades']:.0%} des trades.")
    if b["n_trades"] < MIN_TRADES_AFTER:
        reasons.append(f"Trop peu de trades sur le candidat ({b['n_trades']}).")
    # Drawdown : plus proche de 0 = meilleur (les deux sont négatifs).
    if (deltas.get("max_drawdown_abs") or 0) < 0:
        warnings.append("Le drawdown maximal se dégrade sur le candidat.")
    if (deltas.get("sharpe_like") or 0) < 0:
        warnings.append("La régularité (Sharpe par trade) se dégrade.")

    verdict = "REJETER" if reasons else ("PRUDENCE" if warnings else "ADOPTER")

    return {
        "baseline": a,
        "candidate": b,
        "deltas": deltas,
        "verdict": {"verdict": verdict, "blocking_reasons": reasons,
                    "warnings": warnings},
        "note": ("Comparaison de deux backtests réels. Vérifie qu'ils couvrent la "
                 "MÊME période et le MÊME actif, sinon la comparaison n'a pas de sens."),
    }


# --------------------------------------------------------------------------
# Rendu Markdown
# --------------------------------------------------------------------------

def _fmt_delta(x) -> str:
    """« indéfini » n'est pas « zéro » : on l'affiche comme tel plutôt que de
    laisser un format numérique planter sur None."""
    return "indéfini (aucune perte)" if x is None else f"{x:+}"


def _verdict_badge(v: dict) -> str:
    icon = {"ADOPTER": "✅", "ADOPTER (sous réserve de re-backtest réel)": "✅",
            "PRUDENCE": "⚠️", "REJETER": "❌", "RIEN À VALIDER": "⏸️"}
    return f"{icon.get(v['verdict'], '•')} **{v['verdict']}**"


def validation_markdown(res: dict) -> str:
    if not res.get("available"):
        return (f"# Validation du candidat\n\n⚠️ Impossible : "
                f"{res.get('reason', 'données insuffisantes')}.\n")
    lines = ["# Validation du candidat (étape 3 — boucle fermée)\n"]
    lines.append(f"## Verdict : {_verdict_badge(res['verdict'])}\n")
    for r in res["verdict"]["blocking_reasons"]:
        lines.append(f"- ❌ {r}")
    for w in res["verdict"]["warnings"]:
        lines.append(f"- ⚠️ {w}")
    lines.append("")

    if res.get("n_filters", 0) == 0:
        lines.append(f"> {res.get('note', '')}")
        return "\n".join(lines)

    lines.append(f"**Pile de {res['n_filters']} filtre(s) testée conjointement :**")
    for f in res["filters"]:
        lines.append(f"- {f}")
    lines.append("")

    c = res["combined"]
    lines.append("## Effet combiné\n")
    lines.append("| | Baseline | Filtré | Δ |")
    lines.append("|---|---|---|---|")
    lines.append(f"| Trades | {c['baseline']['n']} | {c['filtered']['n']} | "
                 f"-{c['trades_removed']} ({c['retained_ratio']:.0%} conservés) |")
    lines.append(f"| Profit factor | {c['baseline']['profit_factor']} | "
                 f"{c['filtered']['profit_factor']} | {_fmt_delta(c['pf_delta'])} |")
    lines.append(f"| Espérance | {c['baseline']['expectancy']} | "
                 f"{c['filtered']['expectancy']} | {c['expectancy_delta']:+} |")
    lines.append(f"| Drawdown max | {c['baseline']['max_drawdown']} | "
                 f"{c['filtered']['max_drawdown']} | {c['drawdown_delta']:+} |")
    lines.append("")

    if res.get("marginal_contributions"):
        lines.append("## Contribution marginale de chaque filtre\n")
        lines.append("_Ce que la pile perd si on retire ce filtre seul._\n")
        for m in res["marginal_contributions"]:
            lines.append(f"- `{m['filter']}` → apport PF "
                         f"{m['marginal_pf_contribution']:+}, "
                         f"retire {m['extra_trades_removed']} trades supplémentaires")
        lines.append("")

    for label, rows in res.get("segments", {}).items():
        usable = [r for r in rows if r.get("applicable")]
        empty = [r for r in rows if not r.get("applicable")]
        if not usable and not empty:
            continue
        agree = (sum(1 for r in usable if r["improved"]) / len(usable)) if usable else 0.0
        lines.append(f"## Cohérence par {label} — {agree:.0%} des segments s'améliorent\n")
        if empty:
            noms = ", ".join(r["segment"] for r in empty)
            lines.append(f"> ⚠️ Segment(s) sans aucun trade après filtrage : **{noms}**. "
                         "Un segment vide signifie que la stratégie cesserait "
                         "totalement de trader sur cette portion.\n")
        if not usable:
            lines.append("")
            continue
        lines.append(f"| {label.capitalize()} | Trades | Espérance base → filtrée | ΔPF |")
        lines.append("|---|---|---|---|")
        for r in usable:
            arrow = "✅" if r["improved"] else "❌"
            lines.append(f"| {arrow} {r['segment']} | {r['n_baseline']}→{r['n_filtered']} | "
                         f"{r['baseline_expectancy']} → {r['filtered_expectancy']} | "
                         f"{_fmt_delta(r['pf_delta'])} |")
        lines.append("")

    mb, mf = res.get("monte_carlo_baseline", {}), res.get("monte_carlo_filtered", {})
    if mb.get("available"):
        lines.append("## Monte-Carlo — robustesse du drawdown\n")
        lines.append(f"_{mb['n_sims']} rebattages de l'ordre des trades._\n")
        lines.append("| | Observé | Médiane simulée | Pire 5% |")
        lines.append("|---|---|---|---|")
        lines.append(f"| Baseline | {mb['observed_max_drawdown']} | "
                     f"{mb['simulated_median']} | {mb['simulated_p05_worst']} |")
        if mf.get("available"):
            lines.append(f"| Filtré | {mf['observed_max_drawdown']} | "
                         f"{mf['simulated_median']} | {mf['simulated_p05_worst']} |")
        lines.append(f"\n> {mb['interpretation']}\n")

    lines.append(f"> ⚠️ {res['note']}")
    return "\n".join(lines)


def comparison_markdown(res: dict) -> str:
    a, b, d = res["baseline"], res["candidate"], res["deltas"]
    lines = ["# Comparaison baseline vs candidat (re-backtests réels)\n"]
    lines.append(f"## Verdict : {_verdict_badge(res['verdict'])}\n")
    for r in res["verdict"]["blocking_reasons"]:
        lines.append(f"- ❌ {r}")
    for w in res["verdict"]["warnings"]:
        lines.append(f"- ⚠️ {w}")
    lines.append("")
    labels = {
        "n_trades": "Trades", "win_rate": "Taux de réussite",
        "profit_factor": "Profit factor", "expectancy": "Espérance/trade",
        "payoff_ratio": "Ratio gain/perte", "net_pnl": "PnL net",
        "max_drawdown_abs": "Drawdown max", "sharpe_like": "Sharpe/trade",
        "max_consecutive_losses": "Pertes consécutives max",
    }
    lines.append("| Métrique | Baseline | Candidat | Δ |")
    lines.append("|---|---|---|---|")
    for k, label in labels.items():
        lines.append(f"| {label} | {a.get(k)} | {b.get(k)} | "
                     f"{d.get(k) if d.get(k) is not None else '—'} |")
    lines.append(f"\n> {res['note']}")
    return "\n".join(lines)
