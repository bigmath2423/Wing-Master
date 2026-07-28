"""Walk-forward GLISSANT : la validation la plus sévère de l'agent.

Le walk-forward simple (`walkforward.py`) coupe une fois : 70% pour chercher,
30% pour vérifier. C'est déjà bien, mais ça ne répond pas à la vraie question :
« l'effet survit-il au PASSAGE DU TEMPS et au changement de régime de marché ? »

Ici on découpe la série en plusieurs fenêtres successives et on rejoue le cycle
« chercher puis vérifier » sur chacune. Une règle qui tient sur 5 fenêtres
consécutives est une découverte ; une règle qui ne tient que sur 1 fenêtre est
du bruit qu'un split unique aurait pu faire passer pour un signal.

Deux modes :
  * `rolling`  — fenêtre d'apprentissage de taille FIXE qui glisse (oublie le
    passé lointain : adapté aux marchés qui changent de régime).
  * `anchored` — fenêtre d'apprentissage qui GRANDIT depuis le début (utilise
    tout l'historique : adapté quand on croit l'effet stationnaire).

LIMITE ASSUMÉE : on optimise des SEUILS DE FILTRAGE sur les trades existants
(seuil de confiance, plage d'ATR…). On ne peut pas balayer un paramètre qui
change QUELS trades existent (un multiplicateur de stop, par exemple) : ça
demanderait de rejouer la stratégie, donc TradingView. Cette limite est
rappelée dans le rapport.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from .features import bucketize, _pnl_series
from .suggestions import build_suggestions, _subset_metrics, pf_delta, improved
from .walkforward import _apply_spec

MIN_CHUNK = 15          # taille minimale d'une fenêtre pour qu'elle ait un sens
MIN_FOLD_TRADES = 10    # en dessous, on ne juge pas une fenêtre OOS


@dataclass
class Fold:
    """Une fenêtre : on apprend sur `train`, on vérifie sur `test`."""
    index: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    train_period: str | None = None
    test_period: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def make_folds(n: int, n_folds: int = 5, train_window: int = 3,
               anchored: bool = False) -> list[Fold]:
    """Découpe [0, n) en fenêtres successives.

    On divise en `n_folds + train_window` tranches égales. La fenêtre i
    s'entraîne sur `train_window` tranches (ou sur tout le passé si `anchored`)
    et se teste sur la tranche suivante — jamais sur des données déjà vues.
    """
    total_chunks = n_folds + train_window
    chunk = n // total_chunks
    if chunk < MIN_CHUNK:
        return []

    folds: list[Fold] = []
    for i in range(n_folds):
        test_chunk = train_window + i
        train_start = 0 if anchored else i * chunk
        train_end = test_chunk * chunk
        test_start = train_end
        test_end = (test_chunk + 1) * chunk if i < n_folds - 1 else n
        folds.append(Fold(index=i + 1, train_start=train_start, train_end=train_end,
                          test_start=test_start, test_end=test_end))
    return folds


def _period(df: pd.DataFrame, start: int, end: int) -> str | None:
    if "datetime" not in df.columns or df["datetime"].isna().all():
        return None
    sub = df.iloc[start:end]["datetime"]
    if sub.isna().all():
        return None
    return f"{sub.min():%Y-%m-%d} → {sub.max():%Y-%m-%d}"


def _eval_spec(pnl: pd.Series, mask: pd.Series) -> dict | None:
    """Effet d'un filtre sur une tranche : baseline vs filtré."""
    n_after = int(mask.sum())
    if n_after == 0:
        return None
    base = _subset_metrics(pnl)
    filt = _subset_metrics(pnl[mask.values])
    if filt.get("n", 0) == 0:
        return None
    return {
        "n": n_after,
        "expectancy": filt["expectancy"],
        "baseline_expectancy": base["expectancy"],
        "expectancy_delta": round(filt["expectancy"] - base["expectancy"], 4),
        "pf_delta": pf_delta(base["profit_factor"], filt["profit_factor"]),
        "retained_ratio": round(n_after / base["n"], 3) if base["n"] else 0.0,
    }


def _spec_key(spec: dict) -> str:
    return f"{spec['column']}={spec['modality']}({spec['direction']})"


def rolling_walk_forward(df: pd.DataFrame, n_folds: int = 5, train_window: int = 3,
                         anchored: bool = False, max_rules_per_fold: int = 6) -> dict:
    """Rejoue « chercher puis vérifier » sur plusieurs fenêtres successives."""
    if "datetime" in df.columns and df["datetime"].notna().any():
        df = df.sort_values("datetime")
    df = df.reset_index(drop=True)

    # Bucketisation UNE SEULE FOIS sur tout le jeu : sinon les bornes des
    # buckets (ATR, confiance) changeraient d'une fenêtre à l'autre et les
    # règles ne seraient plus comparables entre elles.
    conditions = df.attrs.get("conditions", [])
    work = bucketize(df)
    work.attrs["conditions"] = conditions
    pnl_all = _pnl_series(work)
    # Volatilité d'un trade : sert d'échelle pour juger si un effet
    # mesuré est économiquement significatif ou juste du bruit.
    pnl_std = float(pnl_all.std(ddof=1)) if len(pnl_all) > 1 else None

    folds = make_folds(len(work), n_folds=n_folds, train_window=train_window,
                       anchored=anchored)
    if not folds:
        besoin = (n_folds + train_window) * MIN_CHUNK
        return {"available": False,
                "reason": (f"Pas assez de trades pour {n_folds} fenêtres "
                           f"(n={len(work)}, il en faudrait ~{besoin}).")}

    per_fold = []
    stats: dict[str, dict] = {}

    for fold in folds:
        fold.train_period = _period(work, fold.train_start, fold.train_end)
        fold.test_period = _period(work, fold.test_start, fold.test_end)

        train = work.iloc[fold.train_start:fold.train_end].copy()
        train.attrs["conditions"] = conditions
        test = work.iloc[fold.test_start:fold.test_end]
        pnl_train = pnl_all.iloc[fold.train_start:fold.train_end]
        pnl_test = pnl_all.iloc[fold.test_start:fold.test_end]

        if len(test) < MIN_FOLD_TRADES:
            per_fold.append({**fold.to_dict(), "usable": False,
                             "reason": "fenêtre de test trop courte"})
            continue

        # 1. Chercher des règles UNIQUEMENT sur la fenêtre d'apprentissage.
        try:
            suggestions = build_suggestions(train, max_ab=max_rules_per_fold)
        except (ValueError, KeyError):
            per_fold.append({**fold.to_dict(), "usable": False,
                             "reason": "aucune règle dérivable"})
            continue

        # 2. Vérifier chaque règle sur la fenêtre de test, jamais vue.
        rules = []
        for t in suggestions["ab_tests"]:
            spec = t.get("filter_spec")
            if not spec:
                continue
            is_res = _eval_spec(pnl_train, _apply_spec(train, spec))
            oos_res = _eval_spec(pnl_test, _apply_spec(test, spec))
            if is_res is None:
                continue
            held = bool(improved(oos_res) and oos_res["n"] >= MIN_FOLD_TRADES)
            rules.append({
                "rule": t["proposed_change"], "spec": spec,
                "in_sample": is_res, "out_of_sample": oos_res, "held": held,
            })
            s = stats.setdefault(_spec_key(spec), {
                "rule": t["proposed_change"], "spec": spec,
                "proposed_in": 0, "held_in": 0, "oos_deltas": []})
            s["proposed_in"] += 1
            s["held_in"] += int(held)
            if oos_res:
                s["oos_deltas"].append(oos_res["expectancy_delta"])

        per_fold.append({
            **fold.to_dict(), "usable": True,
            "n_train": fold.train_end - fold.train_start,
            "n_test": len(test),
            "baseline_test_expectancy": round(float(pnl_test.mean()), 4),
            "rules": rules,
        })

    # 3. Agréger : une règle vaut par sa CONSTANCE, pas par son meilleur score.
    stability = []
    for key, s in stats.items():
        deltas = s["oos_deltas"]
        stability.append({
            "rule": s["rule"], "spec": s["spec"],
            "folds_proposed": s["proposed_in"],
            "folds_held": s["held_in"],
            "hold_rate": round(s["held_in"] / s["proposed_in"], 3) if s["proposed_in"] else 0.0,
            "mean_oos_expectancy_delta": round(float(np.mean(deltas)), 4) if deltas else None,
            "worst_oos_expectancy_delta": round(float(np.min(deltas)), 4) if deltas else None,
            "t_stat": (round(_t_stat(deltas), 2)
                       if np.isfinite(_t_stat(deltas)) else None),
            "effect_size": (round(float(np.mean(deltas)) / pnl_std, 3)
                            if pnl_std and deltas else None),
            "verdict": _stability_verdict(s["held_in"], s["proposed_in"],
                                          deltas, pnl_std),
        })
    stability.sort(key=lambda r: (r["hold_rate"], r["folds_held"]), reverse=True)

    usable = [f for f in per_fold if f.get("usable")]
    return {
        "available": True,
        "mode": "anchored (fenêtre qui grandit)" if anchored else "rolling (fenêtre glissante)",
        "n_trades": len(work),
        "n_folds_requested": n_folds,
        "n_folds_usable": len(usable),
        "train_window_chunks": train_window,
        "folds": per_fold,
        "rule_stability": stability,
        "efficiency": _efficiency(usable),
        "robust_rules": [r for r in stability if r["verdict"] == "ROBUSTE"],
        "note": ("Une règle n'est ROBUSTE que si elle tient sur la majorité des "
                 "fenêtres ET n'explose sur aucune. Un fort score sur une seule "
                 "fenêtre reste du bruit."),
    }


MIN_FOLDS_FOR_CLAIM = 3   # en dessous, « ça tient dans le temps » n'est pas une mesure
MIN_T_STAT = 2.0          # l'effet doit dépasser sa propre dispersion
MIN_EFFECT_SIZE = 0.15    # ...et peser au moins 15% de la volatilité d'un trade


def _t_stat(deltas: list[float]) -> float:
    """Effet moyen rapporté à son erreur-type.

    Sans ça, une règle « 2 fenêtres sur 2 » passe pour robuste alors qu'un tirage
    à pile ou face donne ce résultat une fois sur quatre. Le t compare l'ampleur
    de l'effet à sa variabilité : sur du bruit il reste petit, même quand le
    signe est bon plusieurs fois de suite.
    """
    if not deltas:
        return 0.0
    mean = float(np.mean(deltas))
    if len(deltas) < 2:
        return 0.0
    std = float(np.std(deltas, ddof=1))
    if std == 0:
        return float("inf") if mean > 0 else 0.0
    return mean / (std / np.sqrt(len(deltas)))


def _stability_verdict(held: int, proposed: int, deltas: list[float],
                       pnl_std: float | None = None) -> str:
    """Verdict de stabilité. Quatre exigences cumulatives, chacune bouchant un
    trou par lequel du bruit passait :

    1. assez de fenêtres      — « 2 fois sur 2 » arrive une fois sur quatre au hasard ;
    2. effet moyen positif    — évidence de base ;
    3. t suffisant            — l'effet dépasse sa propre dispersion ;
    4. taille d'effet         — et il pèse assez face à la volatilité d'un trade.
       Sans le point 4, un gain de 0,07R sur des trades d'écart-type 1,0R passe
       pour « robuste » alors qu'il est économiquement nul.
    """
    if proposed == 0 or not deltas:
        return "NON TESTÉE"
    if proposed < MIN_FOLDS_FOR_CLAIM:
        return (f"INSUFFISANT (vue sur {proposed} fenêtre(s), "
                f"il en faut {MIN_FOLDS_FOR_CLAIM})")

    rate = held / proposed
    mean_delta = float(np.mean(deltas))
    if mean_delta <= 0:
        return "REJETÉE"

    effect_size = (mean_delta / pnl_std) if pnl_std else None
    assez_gros = effect_size is None or effect_size >= MIN_EFFECT_SIZE

    if (rate >= 0.7 and min(deltas) > -0.05
            and _t_stat(deltas) >= MIN_T_STAT and assez_gros):
        return "ROBUSTE"
    if not assez_gros and rate >= 0.7:
        return "NÉGLIGEABLE (effet trop petit face à la volatilité)"
    if rate >= 0.5:
        return "INSTABLE"
    return "REJETÉE"


def _efficiency(folds: list[dict]) -> dict:
    """Walk-forward efficiency : quelle part de l'avantage trouvé en apprentissage
    survit réellement hors échantillon ?

    ~1.0 = l'effet se reproduit intégralement (rare, et suspect si systématique).
    ~0.5 = la moitié de l'avantage survit : résultat honnête.
    <=0  = aucun avantage hors échantillon : l'apprentissage ne captait que du bruit.
    """
    is_deltas, oos_deltas = [], []
    for f in folds:
        for r in f.get("rules", []):
            if r["in_sample"] and r["out_of_sample"]:
                is_deltas.append(r["in_sample"]["expectancy_delta"])
                oos_deltas.append(r["out_of_sample"]["expectancy_delta"])
    if not is_deltas:
        return {"available": False}
    mean_is = float(np.mean(is_deltas))
    mean_oos = float(np.mean(oos_deltas))
    wfe = (mean_oos / mean_is) if mean_is > 0 else None
    return {
        "available": True,
        "mean_in_sample_edge": round(mean_is, 4),
        "mean_out_of_sample_edge": round(mean_oos, 4),
        "walk_forward_efficiency": round(wfe, 3) if wfe is not None else None,
        "interpretation": _wfe_interpretation(wfe),
        "n_observations": len(is_deltas),
    }


def _wfe_interpretation(wfe: float | None) -> str:
    if wfe is None:
        return "Aucun avantage mesurable en apprentissage : rien à transférer."
    if wfe <= 0:
        return ("L'avantage trouvé en apprentissage DISPARAÎT hors échantillon : "
                "la recherche de règles ne capte que du bruit sur ces données.")
    if wfe < 0.3:
        return ("Moins de 30% de l'avantage survit : forte sur-optimisation. "
                "Ne rien adopter en l'état.")
    if wfe < 0.6:
        return ("Une part significative de l'avantage survit, mais la dégradation "
                "reste importante : rester prudent et exiger d'autres validations.")
    return ("L'avantage se transfère bien hors échantillon. Vérifier tout de même "
            "sur d'autres actifs avant d'adopter.")


# --------------------------------------------------------------------------
# Optimisation de seuil en walk-forward
# --------------------------------------------------------------------------

def optimize_threshold(df: pd.DataFrame, column: str, n_folds: int = 5,
                       train_window: int = 3, anchored: bool = False,
                       n_candidates: int = 6) -> dict:
    """Choisit un seuil `column >= x` sur chaque fenêtre d'apprentissage, puis
    mesure ce que ce seuil donne réellement sur la fenêtre suivante.

    Le diagnostic le plus utile n'est pas le gain moyen : c'est la STABILITÉ du
    seuil retenu. Si le meilleur seuil saute d'une fenêtre à l'autre, c'est qu'il
    s'ajuste au bruit — et aucune valeur ne mérite d'être figée dans l'indicateur.
    """
    if "datetime" in df.columns and df["datetime"].notna().any():
        df = df.sort_values("datetime")
    df = df.reset_index(drop=True)
    if column not in df.columns:
        return {"available": False, "reason": f"Colonne « {column} » absente."}

    values = pd.to_numeric(df[column], errors="coerce")
    if values.notna().sum() < MIN_CHUNK * 2:
        return {"available": False,
                "reason": f"Trop peu de valeurs numériques dans « {column} »."}

    # Grille de seuils = quantiles, pour rester adapté à l'échelle des données.
    quantiles = np.linspace(0.1, 0.7, n_candidates)
    grid = sorted({round(float(values.quantile(q)), 6) for q in quantiles})
    pnl_all = _pnl_series(df)

    folds = make_folds(len(df), n_folds=n_folds, train_window=train_window,
                       anchored=anchored)
    if not folds:
        return {"available": False,
                "reason": f"Pas assez de trades pour {n_folds} fenêtres (n={len(df)})."}

    results, chosen = [], []
    for fold in folds:
        pnl_train = pnl_all.iloc[fold.train_start:fold.train_end]
        pnl_test = pnl_all.iloc[fold.test_start:fold.test_end]
        v_train = values.iloc[fold.train_start:fold.train_end]
        v_test = values.iloc[fold.test_start:fold.test_end]
        if len(pnl_test) < MIN_FOLD_TRADES:
            continue

        best, best_exp = None, -np.inf
        for seuil in grid:
            m = (v_train >= seuil).fillna(False)
            # On refuse un seuil qui ne laisse presque plus de trades.
            if m.sum() < max(MIN_FOLD_TRADES, int(0.25 * len(pnl_train))):
                continue
            exp = float(pnl_train[m.values].mean())
            if exp > best_exp:
                best, best_exp = seuil, exp
        if best is None:
            continue

        m_test = (v_test >= best).fillna(False)
        oos_exp = float(pnl_test[m_test.values].mean()) if m_test.any() else None
        results.append({
            "fold": fold.index,
            "test_period": _period(df, fold.test_start, fold.test_end),
            "chosen_threshold": best,
            "in_sample_expectancy": round(best_exp, 4),
            "out_of_sample_expectancy": round(oos_exp, 4) if oos_exp is not None else None,
            "baseline_out_of_sample": round(float(pnl_test.mean()), 4),
            "n_test_kept": int(m_test.sum()),
            "n_test_total": len(pnl_test),
        })
        chosen.append(best)

    if not results:
        return {"available": False,
                "reason": "Aucune fenêtre exploitable pour ce paramètre."}

    spread = (max(chosen) - min(chosen)) if chosen else 0.0
    mean_choice = float(np.mean(chosen))
    instability = (spread / abs(mean_choice)) if mean_choice else float("inf")
    beat = [r for r in results
            if r["out_of_sample_expectancy"] is not None
            and r["out_of_sample_expectancy"] > r["baseline_out_of_sample"]]

    return {
        "available": True,
        "column": column,
        "grid_tested": grid,
        "folds": results,
        "chosen_thresholds": chosen,
        "threshold_spread": round(float(spread), 6),
        "threshold_instability": (round(float(instability), 3)
                                  if np.isfinite(instability) else None),
        "folds_beating_baseline": f"{len(beat)}/{len(results)}",
        "verdict": _threshold_verdict(instability, len(beat), len(results)),
        "note": ("Un seuil qui change beaucoup d'une fenêtre à l'autre s'ajuste au "
                 "bruit : aucune valeur ne mérite alors d'être figée. On ne peut "
                 "optimiser ici que des seuils de FILTRAGE — un paramètre qui change "
                 "quels trades existent (multiplicateur de stop…) exige un vrai "
                 "re-backtest TradingView."),
    }


def _threshold_verdict(instability: float, beat: int, total: int) -> str:
    if total == 0:
        return "NON TESTABLE"
    taux = beat / total
    if instability > 0.5:
        return "INSTABLE (le seuil optimal saute d'une fenêtre à l'autre)"
    if taux >= 0.7:
        return "STABLE ET UTILE"
    if taux >= 0.5:
        return "STABLE MAIS PEU CONCLUANT"
    return "REJETÉ (ne bat pas la baseline hors échantillon)"


# --------------------------------------------------------------------------
# Rendu Markdown
# --------------------------------------------------------------------------

def rolling_markdown(res: dict) -> str:
    if not res.get("available"):
        return f"# Walk-forward glissant\n\n⚠️ {res.get('reason', 'non disponible')}\n"

    lines = ["# Walk-forward glissant\n"]
    lines.append(f"- Mode : **{res['mode']}**")
    lines.append(f"- Trades : {res['n_trades']}")
    lines.append(f"- Fenêtres exploitables : **{res['n_folds_usable']}/"
                 f"{res['n_folds_requested']}**\n")

    eff = res.get("efficiency", {})
    if eff.get("available"):
        wfe = eff["walk_forward_efficiency"]
        lines.append("## Efficacité walk-forward\n")
        lines.append(f"- Avantage moyen en apprentissage : **{eff['mean_in_sample_edge']}**")
        lines.append(f"- Avantage moyen hors échantillon : **{eff['mean_out_of_sample_edge']}**")
        lines.append(f"- **WFE = {wfe if wfe is not None else '—'}** "
                     f"({eff['n_observations']} observations)\n")
        lines.append(f"> {eff['interpretation']}\n")

    lines.append("## Stabilité des règles\n")
    stab = res.get("rule_stability", [])
    if not stab:
        lines.append("_Aucune règle n'a pu être évaluée sur plusieurs fenêtres._\n")
    else:
        lines.append("| Règle | Tenue | Δ espérance OOS | Taille d'effet | t | Verdict |")
        lines.append("|---|---|---|---|---|---|")
        for r in stab[:12]:
            icone = "✅" if r["verdict"] == "ROBUSTE" else (
                "❌" if r["verdict"].startswith("REJET") else "⚠️")
            lines.append(
                f"| {r['rule']} | {r['folds_held']}/{r['folds_proposed']} | "
                f"{r['mean_oos_expectancy_delta']} (pire {r['worst_oos_expectancy_delta']}) | "
                f"{r.get('effect_size')} | {r.get('t_stat')} | "
                f"{icone} {r['verdict']} |")
        lines.append("")

    robustes = res.get("robust_rules", [])
    if robustes:
        lines.append(f"### {len(robustes)} règle(s) robuste(s) à travers le temps\n")
        for r in robustes:
            lines.append(f"- **{r['rule']}** — tient sur {r['folds_held']}/"
                         f"{r['folds_proposed']} fenêtres "
                         f"(Δ espérance OOS moyen {r['mean_oos_expectancy_delta']})")
        lines.append("")
    else:
        lines.append("### Aucune règle robuste\n")
        lines.append("Aucune règle ne tient sur la majorité des fenêtres. C'est un "
                     "résultat exploitable : ne rien modifier vaut mieux que figer "
                     "une règle qui ne survit pas au changement de régime.\n")

    lines.append("## Détail par fenêtre\n")
    lines.append("_Le découpage se fait par NUMÉRO DE TRADE, pas par date : deux "
                 "fenêtres voisines peuvent afficher la même date de bord si "
                 "plusieurs trades tombent ce jour-là. Les trades restent "
                 "strictement disjoints — aucune donnée de test n'est vue en "
                 "apprentissage._\n")
    lines.append("| # | Apprentissage | Test | Trades test | Espérance test |")
    lines.append("|---|---|---|---|---|")
    for f in res["folds"]:
        if not f.get("usable"):
            lines.append(f"| {f['index']} | — | — | — | _{f.get('reason', 'inutilisable')}_ |")
            continue
        lines.append(f"| {f['index']} | {f.get('train_period') or '—'} | "
                     f"{f.get('test_period') or '—'} | {f['n_test']} | "
                     f"{f['baseline_test_expectancy']} |")
    lines.append(f"\n> {res['note']}")
    return "\n".join(lines)


def threshold_markdown(res: dict) -> str:
    if not res.get("available"):
        return f"# Optimisation de seuil\n\n⚠️ {res.get('reason', 'non disponible')}\n"
    lines = [f"# Optimisation walk-forward du seuil « {res['column']} »\n"]
    lines.append(f"## Verdict : **{res['verdict']}**\n")
    lines.append(f"- Grille testée : {res['grid_tested']}")
    lines.append(f"- Seuils retenus par fenêtre : {res['chosen_thresholds']}")
    lines.append(f"- Amplitude des seuils : {res['threshold_spread']} "
                 f"(instabilité {res['threshold_instability']})")
    lines.append(f"- Fenêtres battant la baseline : **{res['folds_beating_baseline']}**\n")
    lines.append("| Fenêtre | Période test | Seuil retenu | Espérance IS | "
                 "Espérance OOS | Baseline OOS | Trades gardés |")
    lines.append("|---|---|---|---|---|---|---|")
    for f in res["folds"]:
        lines.append(f"| {f['fold']} | {f.get('test_period') or '—'} | "
                     f"{f['chosen_threshold']} | {f['in_sample_expectancy']} | "
                     f"{f['out_of_sample_expectancy']} | {f['baseline_out_of_sample']} | "
                     f"{f['n_test_kept']}/{f['n_test_total']} |")
    lines.append(f"\n> {res['note']}")
    return "\n".join(lines)
