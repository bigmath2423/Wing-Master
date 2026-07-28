"""Interface en ligne de commande de l'agent.

Exemples :
    python -m backtest_agent.cli analyze examples/sample_trades.csv
    python -m backtest_agent.cli analyze trades.csv --no-llm --json out.json
    python -m backtest_agent.cli analyze trades.csv -o reports/rapport.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ingest import load_trades
from .report import build_report
from .walkforward import walk_forward, walkforward_markdown
from .proposals import (
    build_proposals, generate_candidate_pine, proposals_markdown,
)
from .validate import (
    validate_candidate, compare_backtests, validation_markdown, comparison_markdown,
)
from .rolling import (
    rolling_walk_forward, optimize_threshold, rolling_markdown, threshold_markdown,
)
from . import llm, jsonutil

_DEFAULT_TEMPLATE = str(
    Path(__file__).resolve().parent.parent / "tradingview" / "strategy_template.pine")


def _write(path: str | None, text: str, label: str) -> None:
    """Écrit un rapport Markdown, ou l'affiche si aucun chemin n'est donné."""
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8")
        print(f"[ok] {label} écrit dans {path}")
    else:
        print(text)


def _write_json(path: str | None, obj: object, label: str = "JSON") -> None:
    if not path:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(jsonutil.dumps(obj), encoding="utf-8")
    print(f"[ok] {label} écrit dans {path}", file=sys.stderr)


def _cmd_analyze(args: argparse.Namespace) -> int:
    df = load_trades(args.input)
    result = build_report(df, use_llm=not args.no_llm, model=args.model)

    _write(args.output, result["markdown"], "Rapport")
    _write_json(args.json, result["payload"], "Statistiques JSON")

    mode = "LLM (analyste)" if result["llm_used"] else "déterministe"
    print(f"[info] Mode d'analyse : {mode}", file=sys.stderr)
    if not result["llm_used"] and not args.no_llm:
        if not llm.is_available():
            print("[info] Astuce : définissez ANTHROPIC_API_KEY pour activer "
                  "la couche d'interprétation analyste.", file=sys.stderr)
    return 0


def _cmd_walkforward(args: argparse.Namespace) -> int:
    df = load_trades(args.input)
    wf = walk_forward(df, split=args.split, min_oos_trades=args.min_oos)
    _write(args.output, walkforward_markdown(wf), "Rapport walk-forward")
    _write_json(args.json, wf)
    if wf.get("available"):
        print(f"[info] {wf['rules_confirmed']}/{wf['rules_evaluated']} règles "
              "confirmées hors échantillon.", file=sys.stderr)
    return 0


def _cmd_propose(args: argparse.Namespace) -> int:
    df = load_trades(args.input)
    if args.candidate:
        result = generate_candidate_pine(
            df, template_path=args.template, out_path=args.candidate,
            split=args.split, min_oos_trades=args.min_oos)
    else:
        result = build_proposals(df, split=args.split, min_oos_trades=args.min_oos)
    _write(args.output, proposals_markdown(result), "Propositions")
    _write_json(getattr(args, "json", None), result)
    if result.get("candidate_path"):
        print(f"[ok] Stratégie candidate générée : {result['candidate_path']}")
    if result.get("available"):
        print(f"[info] {result['n_proposals']} proposition(s) issue(s) de règles "
              "validées hors échantillon.", file=sys.stderr)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    df = load_trades(args.input)
    res = validate_candidate(df, split=args.split, min_oos_trades=args.min_oos,
                             n_sims=args.sims, n_periods=args.periods)
    _write(args.output, validation_markdown(res), "Rapport de validation")
    _write_json(args.json, res)
    if res.get("verdict"):
        print(f"[info] Verdict : {res['verdict']['verdict']}", file=sys.stderr)
    return 0


def _cmd_compare(args: argparse.Namespace) -> int:
    baseline = load_trades(args.baseline)
    candidate = load_trades(args.candidate)
    res = compare_backtests(baseline, candidate)
    _write(args.output, comparison_markdown(res), "Rapport de comparaison")
    _write_json(args.json, res)
    print(f"[info] Verdict : {res['verdict']['verdict']}", file=sys.stderr)
    return 0


def _cmd_rolling(args: argparse.Namespace) -> int:
    df = load_trades(args.input)
    if args.threshold:
        res = optimize_threshold(df, column=args.threshold, n_folds=args.folds,
                                 train_window=args.train_window,
                                 anchored=args.anchored)
        _write(args.output, threshold_markdown(res), "Optimisation de seuil")
    else:
        res = rolling_walk_forward(df, n_folds=args.folds,
                                   train_window=args.train_window,
                                   anchored=args.anchored)
        _write(args.output, rolling_markdown(res), "Walk-forward glissant")
    _write_json(args.json, res)
    if res.get("available"):
        if args.threshold:
            print(f"[info] Verdict : {res['verdict']}", file=sys.stderr)
        else:
            print(f"[info] {len(res['robust_rules'])} règle(s) robuste(s) sur "
                  f"{res['n_folds_usable']} fenêtres.", file=sys.stderr)
    return 0


def _cmd_pipeline(args: argparse.Namespace) -> int:
    """Cycle complet : analyse → walk-forward → propositions → validation
    combinée → walk-forward glissant."""
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = load_trades(args.input)

    print(f"[1/5] Analyse de {len(df)} trades…", file=sys.stderr)
    report = build_report(df, use_llm=not args.no_llm, model=args.model)
    _write(str(outdir / "1_analyse.md"), report["markdown"], "Analyse")
    _write_json(str(outdir / "1_analyse.json"), report["payload"])

    print("[2/5] Validation walk-forward…", file=sys.stderr)
    wf = walk_forward(df, split=args.split, min_oos_trades=args.min_oos)
    _write(str(outdir / "2_walkforward.md"), walkforward_markdown(wf), "Walk-forward")

    print("[3/5] Propositions de modification…", file=sys.stderr)
    candidate = str(outdir / "strategy_candidate.pine")
    proposals = generate_candidate_pine(
        df, template_path=args.template, out_path=candidate,
        split=args.split, min_oos_trades=args.min_oos)
    _write(str(outdir / "3_propositions.md"), proposals_markdown(proposals),
           "Propositions")

    print("[4/5] Validation de la pile combinée…", file=sys.stderr)
    validation = validate_candidate(df, split=args.split, min_oos_trades=args.min_oos,
                                    n_sims=args.sims, n_periods=args.periods)
    _write(str(outdir / "4_validation.md"), validation_markdown(validation),
           "Validation")

    print("[5/5] Walk-forward glissant…", file=sys.stderr)
    rolling = rolling_walk_forward(df, n_folds=args.folds,
                                   train_window=args.train_window)
    _write(str(outdir / "5_walkforward_glissant.md"), rolling_markdown(rolling),
           "Walk-forward glissant")

    verdict = validation.get("verdict", {}).get("verdict", "INDÉTERMINÉ")
    n_conf = wf.get("rules_confirmed", 0) if wf.get("available") else 0
    n_robustes = len(rolling.get("robust_rules", [])) if rolling.get("available") else "—"
    summary = [
        "",
        "=" * 62,
        f"  Trades analysés          : {len(df)}",
        f"  Règles confirmées (OOS)  : {n_conf}",
        f"  Propositions générées    : {proposals.get('n_proposals', 0)}",
        f"  Règles robustes (glissant): {n_robustes}",
        f"  Verdict final            : {verdict}",
        "=" * 62,
        f"  Rapports : {outdir}/",
        "",
        "  Prochaine étape : re-backtester strategy_candidate.pine sur",
        "  TradingView, exporter, puis :",
        f"    backtest-agent compare {args.input} <export_candidat.csv>",
        "",
    ]
    print("\n".join(summary), file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    from . import __version__
    parser = argparse.ArgumentParser(
        prog="backtest-agent",
        description="Agent d'analyse quantitative de backtests de trading.")
    parser.add_argument("--version", action="version",
                        version=f"backtest-agent {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("analyze", help="Analyser un fichier de backtest.")
    p.add_argument("input", help="Chemin du fichier de backtest (CSV/JSON).")
    p.add_argument("-o", "--output", help="Chemin de sortie du rapport Markdown.")
    p.add_argument("--json", help="Chemin de sortie des statistiques JSON.")
    p.add_argument("--no-llm", action="store_true",
                   help="Forcer le mode déterministe (pas d'appel LLM).")
    p.add_argument("--model", help="Modèle Claude à utiliser (override).")
    p.set_defaults(func=_cmd_analyze)

    w = sub.add_parser("walkforward",
                       help="Valider les filtres hors échantillon (in/out-of-sample).")
    w.add_argument("input", help="Chemin du fichier de backtest (CSV/JSON).")
    w.add_argument("-o", "--output", help="Chemin de sortie du rapport Markdown.")
    w.add_argument("--json", help="Chemin de sortie du détail JSON.")
    w.add_argument("--split", type=float, default=0.7,
                   help="Part in-sample (défaut 0.7 = 70%%).")
    w.add_argument("--min-oos", type=int, default=10,
                   help="Nb min de trades OOS pour juger une règle (défaut 10).")
    w.set_defaults(func=_cmd_walkforward)

    pr = sub.add_parser(
        "propose",
        help="ÉTAPE 2 : proposer des modifs d'indicateur (règles validées seulement).")
    pr.add_argument("input", help="Chemin du fichier de backtest (CSV/JSON).")
    pr.add_argument("-o", "--output", help="Rapport de propositions (Markdown).")
    pr.add_argument("--json", help="Détail JSON.")
    pr.add_argument("--candidate",
                    help="Chemin de sortie d'une stratégie .pine candidate.")
    pr.add_argument("--template", default=_DEFAULT_TEMPLATE,
                    help="Template .pine source (défaut : strategy_template.pine).")
    pr.add_argument("--split", type=float, default=0.7,
                    help="Part in-sample pour la validation (défaut 0.7).")
    pr.add_argument("--min-oos", type=int, default=10,
                    help="Nb min de trades OOS pour valider une règle (défaut 10).")
    pr.set_defaults(func=_cmd_propose)

    v = sub.add_parser(
        "validate",
        help="ÉTAPE 3 : valider la pile de filtres combinée (multi-actifs, "
             "multi-périodes, Monte-Carlo).")
    v.add_argument("input", help="Chemin du fichier de backtest (CSV/JSON).")
    v.add_argument("-o", "--output", help="Rapport de validation (Markdown).")
    v.add_argument("--json", help="Détail JSON.")
    v.add_argument("--split", type=float, default=0.7,
                   help="Part in-sample pour dériver les règles (défaut 0.7).")
    v.add_argument("--min-oos", type=int, default=10,
                   help="Nb min de trades OOS pour valider une règle (défaut 10).")
    v.add_argument("--sims", type=int, default=2000,
                   help="Nb de simulations Monte-Carlo (défaut 2000).")
    v.add_argument("--periods", type=int, default=4,
                   help="Nb de tranches chronologiques testées (défaut 4).")
    v.set_defaults(func=_cmd_validate)

    c = sub.add_parser(
        "compare",
        help="ÉTAPE 3 : comparer deux re-backtests réels (baseline vs candidat).")
    c.add_argument("baseline", help="Export du backtest de référence.")
    c.add_argument("candidate", help="Export du backtest de la stratégie candidate.")
    c.add_argument("-o", "--output", help="Rapport de comparaison (Markdown).")
    c.add_argument("--json", help="Détail JSON.")
    c.set_defaults(func=_cmd_compare)

    rl = sub.add_parser(
        "rolling",
        help="Walk-forward GLISSANT : rejoue chercher/vérifier sur plusieurs "
             "fenêtres successives (validation la plus sévère).")
    rl.add_argument("input", help="Chemin du fichier de backtest (CSV/JSON).")
    rl.add_argument("-o", "--output", help="Rapport Markdown.")
    rl.add_argument("--json", help="Détail JSON.")
    rl.add_argument("--folds", type=int, default=5,
                    help="Nombre de fenêtres de test (défaut 5).")
    rl.add_argument("--train-window", type=int, default=3,
                    help="Nombre de tranches d'apprentissage (défaut 3).")
    rl.add_argument("--anchored", action="store_true",
                    help="Fenêtre d'apprentissage qui grandit au lieu de glisser.")
    rl.add_argument("--threshold", metavar="COLONNE",
                    help="Optimiser un seuil numérique (ex: confidence, atr) "
                         "en walk-forward au lieu d'évaluer les règles.")
    rl.set_defaults(func=_cmd_rolling)

    pl = sub.add_parser(
        "pipeline",
        help="Cycle complet : analyse → walk-forward → propositions → validation.")
    pl.add_argument("input", help="Chemin du fichier de backtest (CSV/JSON).")
    pl.add_argument("-o", "--outdir", default="reports",
                    help="Dossier de sortie (défaut : reports/).")
    pl.add_argument("--template", default=_DEFAULT_TEMPLATE,
                    help="Template .pine source.")
    pl.add_argument("--split", type=float, default=0.7)
    pl.add_argument("--min-oos", type=int, default=10)
    pl.add_argument("--sims", type=int, default=2000)
    pl.add_argument("--periods", type=int, default=4)
    pl.add_argument("--folds", type=int, default=5,
                    help="Fenêtres du walk-forward glissant (défaut 5).")
    pl.add_argument("--train-window", type=int, default=3,
                    help="Tranches d'apprentissage du glissant (défaut 3).")
    pl.add_argument("--no-llm", action="store_true",
                    help="Forcer le mode déterministe.")
    pl.add_argument("--model", help="Modèle Claude à utiliser (override).")
    pl.set_defaults(func=_cmd_pipeline)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"[erreur] Fichier introuvable : {exc.filename}", file=sys.stderr)
        return 2
    except ValueError as exc:
        # Erreurs métier attendues (format inconnu, colonnes manquantes, fichier vide).
        print(f"[erreur] {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\n[interrompu]", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
