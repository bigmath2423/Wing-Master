"""ÉTAPE 2 — Agent qui PROPOSE des modifications d'indicateur/stratégie.

Différence essentielle avec l'étape 1 : ici l'agent produit du CODE Pine concret.
Mais il reste un chercheur, pas un bricoleur de win rate :

  * Il ne propose QUE des règles ayant le verdict `TIENT` en walk-forward
    (améliorent PF ET espérance in-sample ET out-of-sample). Rien d'autre.
  * Chaque proposition est livrée avec : l'hypothèse validée, la preuve chiffrée
    (IS + OOS), le risque de sur-optimisation, le code Pine exact, et un plan de
    rollback.
  * Il ne « pousse » jamais la modification : il génère un fichier CANDIDAT que
    l'utilisateur doit RE-BACKTESTER avant toute décision.

Le coeur technique est un traducteur `condition validée -> expression Pine`, qui
transforme un `filter_spec` (colonne/modalité/sens) en une garde d'entrée Pine.
Les colonnes qu'il ne sait pas traduire de façon sûre sont marquées `TODO` plutôt
que produire du code faux.
"""

from __future__ import annotations

import re
from pathlib import Path

from .walkforward import walk_forward

# Marqueurs d'insertion dans strategy_template.pine
_BEGIN = "// <<< AGENT_FILTERS_BEGIN >>>"
_END = "// <<< AGENT_FILTERS_END >>>"

# Correspondance colonne de condition -> variable Pine exposée par le template.
_BOOL_PINE = {
    "ob": "cond_ob",
    "fvg": "cond_fvg",
    "sweep": "cond_sweep",
    "vwap_up": "cond_vwap_up",
    "structure_up": "cond_structure",
}

_SESSION_HOURS = {
    "Asie": "(hour(time) >= 0 and hour(time) < 7)",
    "Londres": "(hour(time) >= 7 and hour(time) < 12)",
    "Londres/NY overlap": "(hour(time) >= 12 and hour(time) < 16)",
    "New York": "(hour(time) >= 16 and hour(time) < 21)",
    "After-hours": "(hour(time) >= 21)",
}

_DOW_PINE = {
    "Monday": "dayofweek.monday", "Tuesday": "dayofweek.tuesday",
    "Wednesday": "dayofweek.wednesday", "Thursday": "dayofweek.thursday",
    "Friday": "dayofweek.friday", "Saturday": "dayofweek.saturday",
    "Sunday": "dayofweek.sunday",
}


def _truthy(modality: str) -> bool:
    return str(modality).strip().lower() in {"true", "1", "yes", "oui", "1.0"}


def _conf_threshold(modality: str) -> str | None:
    """'75-100%' -> confidence >= 75 (le template émet confidence en 0..100)."""
    m = re.match(r"\s*(\d+)\s*-\s*(\d+)%", str(modality))
    if not m:
        return None
    low = int(m.group(1))
    return f"confidence >= {low}"


def _atr_range(modality: str) -> str | None:
    """'(50.4, 157.5]' -> (atr > 50.4 and atr <= 157.5)."""
    m = re.match(r"\s*[\(\[]\s*([-\d.]+)\s*,\s*([-\d.]+)\s*[\)\]]", str(modality))
    if not m:
        return None
    lo, hi = float(m.group(1)), float(m.group(2))
    return f"(atr > {lo} and atr <= {hi})"


def spec_to_pine(spec: dict) -> dict:
    """Traduit un filter_spec en garde Pine. Retourne
    {'pine': str|None, 'human': str, 'translatable': bool}."""
    col = spec["column"]
    modality = spec["modality"]
    keep = spec["direction"] == "keep"

    def wrap(expr: str, human: str) -> dict:
        pine = expr if keep else f"not ({expr})"
        verb = "Ne trader que si" if keep else "Ne pas trader si"
        return {"pine": pine, "human": f"{verb} {human}", "translatable": True}

    if col in _BOOL_PINE:
        var = _BOOL_PINE[col]
        # modalité booléenne : keep True => var ; exclude True => not var
        base = var if _truthy(modality) else f"not {var}"
        pine = base if keep else f"not ({base})"
        state = "présent" if _truthy(modality) else "absent"
        return {"pine": pine,
                "human": f"{'exiger' if keep else 'écarter'} la condition "
                         f"{col} {state}", "translatable": True}

    if col == "_hour":
        try:
            h = int(float(modality))
        except (TypeError, ValueError):
            return {"pine": None, "human": f"heure={modality}", "translatable": False}
        return wrap(f"hour(time) == {h}", f"l'heure d'entrée est {h}h (UTC)")

    if col == "_session":
        expr = _SESSION_HOURS.get(str(modality))
        if expr:
            return wrap(expr, f"la session est « {modality} »")
        return {"pine": None, "human": f"session={modality}", "translatable": False}

    if col == "_dow":
        dow = _DOW_PINE.get(str(modality))
        if dow:
            return wrap(f"dayofweek == {dow}", f"le jour est {modality}")
        return {"pine": None, "human": f"jour={modality}", "translatable": False}

    if col == "_conf_bucket":
        expr = _conf_threshold(modality)
        if expr and keep:
            return {"pine": expr, "human": f"exiger un score de confiance élevé "
                    f"(tranche {modality})", "translatable": True}
        return {"pine": None, "human": f"confiance={modality}", "translatable": False}

    if col == "_atr_bucket":
        expr = _atr_range(modality)
        if expr:
            return wrap(expr, f"l'ATR est dans la plage {modality}")
        return {"pine": None, "human": f"ATR={modality}", "translatable": False}

    if col == "direction":
        return {"pine": None,
                "human": f"filtrer la direction ({modality}) — à décider "
                         "manuellement, un biais directionnel est structurant",
                "translatable": False}

    return {"pine": None, "human": f"{col}={modality}", "translatable": False}


def build_proposals(df, split: float = 0.7, min_oos_trades: int = 10,
                    max_proposals: int = 6) -> dict:
    """Génère des propositions de modification à partir des règles validées."""
    wf = walk_forward(df, split=split, min_oos_trades=min_oos_trades)
    if not wf.get("available"):
        return {"available": False, "reason": wf.get("reason"), "walk_forward": wf}

    confirmed = [r for r in wf["results"] if r["verdict"].startswith("TIENT")]
    proposals = []
    gates = []
    for r in confirmed[:max_proposals]:
        spec = None
        # Retrouver le filter_spec : on relance la traduction depuis la règle
        # décrite. On l'a stocké dans walk-forward via build_suggestions ->
        # ici on le récupère via r (ajouté ci-dessous dans walk_forward).
        spec = r.get("filter_spec")
        if not spec:
            continue
        trans = spec_to_pine(spec)
        proposal = {
            "hypothesis": r["rationale"],
            "rule": r["rule"],
            "validation": {
                "verdict": r["verdict"],
                "in_sample": r["in_sample"],
                "out_of_sample": r["out_of_sample"],
            },
            "pine_gate": trans["pine"],
            "human_change": trans["human"],
            "translatable": trans["translatable"],
            "rollback": "Remettre passFilters = true (ou retirer cette garde) et "
                        "re-backtester pour comparer.",
        }
        proposals.append(proposal)
        if trans["translatable"] and trans["pine"]:
            gates.append((trans["pine"], r["rule"]))

    return {
        "available": True,
        "n_confirmed_rules": len(confirmed),
        "n_proposals": len(proposals),
        "proposals": proposals,
        "pine_filter_block": _render_filter_block(gates),
        "walk_forward_summary": {
            "n_in_sample": wf["n_in_sample"],
            "n_out_of_sample": wf["n_out_of_sample"],
            "rules_evaluated": wf["rules_evaluated"],
            "rules_confirmed": wf["rules_confirmed"],
        },
        "guardrails": [
            "Ces propositions découlent UNIQUEMENT de règles validées in + out-of-sample.",
            "Aucune n'est prouvée : re-backtester le fichier candidat avant décision.",
            "Combiner plusieurs gardes réduit fortement le nombre de trades : vérifier "
            "qu'il en reste assez.",
            "Valider aussi sur d'autres actifs / périodes avant d'adopter.",
        ],
    }


def _render_filter_block(gates: list[tuple[str, str]]) -> str:
    """Construit le bloc Pine à insérer entre les marqueurs."""
    if not gates:
        return f"{_BEGIN}\npassFilters = true\n{_END}"
    lines = [_BEGIN,
             "// Gardes générées depuis des règles validées en walk-forward.",
             "// Chaque ligne correspond à une hypothèse confirmée in + out-of-sample."]
    exprs = []
    for i, (pine, rule) in enumerate(gates, 1):
        lines.append(f"filter{i} = {pine}  // {rule}")
        exprs.append(f"filter{i}")
    lines.append(f"passFilters = {' and '.join(exprs)}")
    lines.append(_END)
    return "\n".join(lines)


def apply_to_template(template_text: str, filter_block: str) -> str:
    """Remplace le bloc entre marqueurs par le nouveau bloc de filtres."""
    pattern = re.compile(re.escape(_BEGIN) + r".*?" + re.escape(_END), re.DOTALL)
    if not pattern.search(template_text):
        raise ValueError("Marqueurs AGENT_FILTERS introuvables dans le template.")
    return pattern.sub(lambda _: filter_block, template_text)


def generate_candidate_pine(df, template_path: str | Path, out_path: str | Path,
                            **kwargs) -> dict:
    """Produit un fichier .pine CANDIDAT avec les filtres validés insérés."""
    result = build_proposals(df, **kwargs)
    if not result.get("available"):
        return result
    template = Path(template_path).read_text(encoding="utf-8")
    candidate = apply_to_template(template, result["pine_filter_block"])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(candidate, encoding="utf-8")
    result["candidate_path"] = str(out_path)
    return result


def proposals_markdown(result: dict) -> str:
    if not result.get("available"):
        return (f"# Propositions de modification\n\n⚠️ Impossible : "
                f"{result.get('reason', 'données insuffisantes pour valider quoi que ce soit')}.\n"
                "Aucune règle ne peut être proposée sans validation walk-forward.\n")
    wf = result["walk_forward_summary"]
    lines = ["# Propositions de modification de l'indicateur (étape 2)\n"]
    lines.append(f"_Basé sur {wf['rules_confirmed']}/{wf['rules_evaluated']} "
                 f"règles confirmées en walk-forward "
                 f"({wf['n_in_sample']} IS / {wf['n_out_of_sample']} OOS)._\n")
    if result["n_proposals"] == 0:
        lines.append("**Aucune modification proposée.** Aucune règle n'a passé la "
                     "validation hors échantillon. C'est un résultat sain : mieux "
                     "vaut ne rien changer que sur-optimiser.\n")
        return "\n".join(lines)

    for i, p in enumerate(result["proposals"], 1):
        v = p["validation"]
        is_r, oos = v["in_sample"], v["out_of_sample"]
        lines.append(f"## Proposition #{i}")
        lines.append(f"- **Hypothèse validée :** {p['hypothesis']}")
        lines.append(f"- **Modification :** {p['human_change']}")
        lines.append(f"- **Preuve in-sample :** ΔPF {is_r.get('pf_delta')}, "
                     f"Δespérance {is_r.get('expectancy_delta')} "
                     f"({is_r.get('n_after')} trades)")
        lines.append(f"- **Preuve out-of-sample :** ΔPF {oos.get('pf_delta')}, "
                     f"Δespérance {oos.get('expectancy_delta')} "
                     f"({oos.get('n_after')} trades)")
        if p["translatable"] and p["pine_gate"]:
            lines.append(f"- **Code Pine :**\n  ```pine\n  {p['pine_gate']}\n  ```")
        else:
            lines.append("- **Code Pine :** _traduction automatique non sûre pour "
                         "cette condition → à implémenter manuellement._")
        lines.append(f"- **Rollback :** {p['rollback']}\n")

    lines.append("## Bloc de filtres généré (à insérer dans la stratégie)\n")
    lines.append("```pine")
    lines.append(result["pine_filter_block"])
    lines.append("```\n")
    if result.get("candidate_path"):
        lines.append(f"➡️ Fichier candidat prêt à re-backtester : "
                     f"`{result['candidate_path']}`\n")
    lines.append("## Garde-fous")
    for g in result["guardrails"]:
        lines.append(f"- {g}")
    lines.append("\n> ⚠️ Ces propositions ne sont PAS des vérités : re-backteste le "
                 "fichier candidat sur TradingView, idéalement sur d'autres actifs "
                 "et d'autres périodes, avant d'adopter quoi que ce soit.")
    return "\n".join(lines)
