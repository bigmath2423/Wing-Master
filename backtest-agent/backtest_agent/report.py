"""Assemblage du rapport final.

Deux sorties :
- `payload` : dict structuré (JSON) avec toutes les statistiques déterministes.
- `markdown` : rapport lisible. Si un LLM est disponible, il rédige la partie
  narrative ; sinon un fallback déterministe rédige un rapport clair sans IA.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from .metrics import global_metrics
from .losses import analyze_losses
from .winners import analyze_winners
from .suggestions import build_suggestions
from . import llm


def _meta(df: pd.DataFrame) -> dict:
    dt = df["datetime"] if "datetime" in df.columns else None
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_trades": int(len(df)),
        "symbols": sorted(df["symbol"].dropna().unique().tolist()) if "symbol" in df else [],
        "timeframes": sorted(df["timeframe"].dropna().unique().tolist()) if "timeframe" in df else [],
        "period_start": str(dt.min()) if dt is not None and dt.notna().any() else None,
        "period_end": str(dt.max()) if dt is not None and dt.notna().any() else None,
        "conditions_detected": df.attrs.get("conditions", []),
    }


def build_payload(df: pd.DataFrame) -> dict:
    return {
        "meta": _meta(df),
        "global_metrics": global_metrics(df).to_dict(),
        "losses": analyze_losses(df),
        "winners": analyze_winners(df),
        "suggestions": build_suggestions(df),
    }


def _fmt_pct(x) -> str:
    try:
        return f"{x*100:.1f}%"
    except (TypeError, ValueError):
        return str(x)


def _deterministic_markdown(payload: dict) -> str:
    m = payload["global_metrics"]
    meta = payload["meta"]
    losses = payload["losses"]
    winners = payload["winners"]
    sugg = payload["suggestions"]
    unit = m["pnl_unit"]

    lines = []
    lines.append("# Rapport d'analyse de backtest\n")
    lines.append(f"_Généré le {meta['generated_at']} — mode déterministe "
                 "(sans LLM). Définissez ANTHROPIC_API_KEY pour la couche "
                 "d'interprétation analyste._\n")

    lines.append("## 1. Analyse globale\n")
    lines.append(f"- Trades analysés : **{m['n_trades']}** "
                 f"({m['n_wins']} gagnants / {m['n_losses']} perdants / "
                 f"{m['n_breakeven']} nuls)")
    lines.append(f"- Taux de réussite : **{_fmt_pct(m['win_rate'])}**")
    lines.append(f"- Profit factor : **{m['profit_factor']}**")
    lines.append(f"- Espérance / trade : **{m['expectancy']} {unit}**")
    lines.append(f"- Ratio gain/perte (payoff) : **{m['payoff_ratio']}** "
                 f"(gain moyen {m['avg_win']} / perte moyenne {m['avg_loss']})")
    lines.append(f"- Drawdown max : **{m['max_drawdown_abs']} {unit}** "
                 f"({_fmt_pct(m['max_drawdown_rel'])} relatif)")
    lines.append(f"- Stabilité (Sharpe par trade) : **{m['sharpe_like']}**")
    lines.append(f"- Séries : {m['max_consecutive_wins']} gains d'affilée max, "
                 f"{m['max_consecutive_losses']} pertes d'affilée max")
    cons = m.get("consistency", {})
    if cons.get("available"):
        lines.append(f"- Régularité : {_fmt_pct(cons['profitable_period_ratio'])} "
                     f"des {cons['periods']} mois profitables "
                     f"(pire mois {cons['worst_period']}, meilleur {cons['best_period']})")
    lines.append("")

    lines.append("## 2. Analyse des pertes\n")
    if losses["structural_hypotheses"]:
        lines.append("**Hypothèses structurelles :**")
        for h in losses["structural_hypotheses"]:
            lines.append(f"- {h}")
    rc = losses["recurring_conditions_before_losses"]
    if rc:
        lines.append("\n**Conditions sur-représentées avant les pertes :**")
        for r in rc[:8]:
            lines.append(f"- `{r['column']} = {r['modality']}` — présent dans "
                         f"{_fmt_pct(r['share_of_losers'])} des pertes "
                         f"(lift {r['loss_lift']}×, espérance {r['expectancy_when_present']})")
    lines.append(f"\n> {losses['note']}\n")

    lines.append("## 3. Analyse des meilleurs trades\n")
    combos = winners["best_filter_combinations"]
    if combos:
        lines.append("**Meilleures combinaisons de filtres (score robuste) :**")
        for c in combos[:6]:
            lines.append(f"- `{c['filters']}` — {c['n_trades']} trades, "
                         f"WR {_fmt_pct(c['win_rate'])}, PF {c['profit_factor']}, "
                         f"espérance {c['expectancy']} (score {c['robust_score']})")
    if winners["best_sessions"]:
        lines.append("\n**Sessions les plus performantes :**")
        for s in winners["best_sessions"][:5]:
            lines.append(f"- {s['modality']} — {s['n_trades']} trades, "
                         f"espérance {s['expectancy']}, PF {s['profit_factor']}")
    rr = winners.get("risk_reward", {})
    if rr.get("available"):
        lines.append(f"\n- R réalisé moyen : {rr['avg_realized_r_all']} "
                     f"(gagnants : {rr['avg_realized_r_winners']})")
    lines.append(f"\n> {winners['note']}\n")

    lines.append("## 4. Suggestions d'amélioration (à TESTER, pas à appliquer)\n")
    if sugg["filters_to_test"]:
        lines.append("**Filtres à tester :**")
        for f in sugg["filters_to_test"]:
            lines.append(f"- {f['filter']} — _{f['rationale']}_ "
                         f"(risque de sur-optimisation : **{f['overfitting_risk']}**)")
    if sugg["parameters_to_test"]:
        lines.append("\n**Paramètres à balayer :**")
        for p in sugg["parameters_to_test"]:
            lines.append(f"- {p['parameter']} : {p['grid_to_test']} — "
                         f"_{p['why']}_ (surveiller : {p['watch']})")
    lines.append("")

    lines.append("## 5. Plan de tests A/B\n")
    for i, t in enumerate(sugg["ab_tests"], 1):
        a, b = t["variant_A_baseline"], t["variant_B_filtered"]
        er = t["expected_result"]
        lines.append(f"### Test A/B #{i}")
        lines.append(f"- **Problème détecté :** {t['problem_detected']}")
        lines.append(f"- **Modification proposée :** {t['proposed_change']}")
        lines.append(f"- **A (baseline) :** {a['n']} trades, PF {a['profit_factor']}, "
                     f"DD {a['max_drawdown']}, espérance {a['expectancy']}")
        lines.append(f"- **B (filtré) :** {b['n']} trades, PF {b['profit_factor']}, "
                     f"DD {b['max_drawdown']}, espérance {b['expectancy']}")
        lines.append(f"- **Résultat attendu :** ΔPF {er['profit_factor_delta']}, "
                     f"Δespérance {er['expectancy_delta']}, ΔDD {er['drawdown_delta']}, "
                     f"{er['trades_removed']} trades supprimés "
                     f"({_fmt_pct(er['trades_retained_ratio'])} conservés)")
        lines.append(f"- **Risque de sur-optimisation :** {t['overfitting_risk']}")
        lines.append(f"- **Règle de décision :** {t['decision_rule']}\n")

    lines.append("## 6. Garde-fous\n")
    for g in sugg["guardrails"]:
        lines.append(f"- {g}")
    lines.append("\n> ⚠️ Aucune modification de l'indicateur/stratégie ne doit être "
                 "appliquée avant une validation walk-forward hors échantillon.")
    return "\n".join(lines)


def build_report(df: pd.DataFrame, use_llm: bool = True,
                 model: str | None = None) -> dict:
    """Retourne {'payload': dict, 'markdown': str, 'llm_used': bool}."""
    payload = build_payload(df)
    narrative = None
    if use_llm and llm.is_available():
        try:
            narrative = llm.generate_narrative(payload, model=model)
        except Exception as exc:  # noqa: BLE001 — on dégrade proprement
            narrative = None
            payload["meta"]["llm_error"] = str(exc)

    if narrative:
        markdown = narrative + "\n\n---\n\n<details><summary>Statistiques brutes "
        markdown += "(déterministes)</summary>\n\n```json\n"
        import json
        markdown += json.dumps(payload, indent=2, ensure_ascii=False, default=str)
        markdown += "\n```\n</details>\n"
    else:
        markdown = _deterministic_markdown(payload)

    return {"payload": payload, "markdown": markdown, "llm_used": bool(narrative)}
