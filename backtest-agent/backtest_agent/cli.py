"""Interface en ligne de commande de l'agent.

Exemples :
    python -m backtest_agent.cli analyze examples/sample_trades.csv
    python -m backtest_agent.cli analyze trades.csv --no-llm --json out.json
    python -m backtest_agent.cli analyze trades.csv -o reports/rapport.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ingest import load_trades
from .report import build_report
from .walkforward import walk_forward, walkforward_markdown
from .proposals import (
    build_proposals, generate_candidate_pine, proposals_markdown,
)
from . import llm

_DEFAULT_TEMPLATE = str(
    Path(__file__).resolve().parent.parent / "tradingview" / "strategy_template.pine")


def _cmd_analyze(args: argparse.Namespace) -> int:
    df = load_trades(args.input)
    result = build_report(df, use_llm=not args.no_llm, model=args.model)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result["markdown"], encoding="utf-8")
        print(f"[ok] Rapport écrit dans {args.output}")
    else:
        print(result["markdown"])

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(
            json.dumps(result["payload"], indent=2, ensure_ascii=False, default=str),
            encoding="utf-8")
        print(f"[ok] Statistiques JSON écrites dans {args.json}", file=sys.stderr)

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
    md = walkforward_markdown(wf)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"[ok] Rapport walk-forward écrit dans {args.output}")
    else:
        print(md)
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(
            json.dumps(wf, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8")
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
    md = proposals_markdown(result)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"[ok] Propositions écrites dans {args.output}")
    else:
        print(md)
    if result.get("candidate_path"):
        print(f"[ok] Stratégie candidate générée : {result['candidate_path']}")
    if result.get("available"):
        print(f"[info] {result['n_proposals']} proposition(s) issue(s) de règles "
              "validées hors échantillon.", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="backtest-agent",
        description="Agent d'analyse quantitative de backtests de trading.")
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
    pr.add_argument("--candidate",
                    help="Chemin de sortie d'une stratégie .pine candidate.")
    pr.add_argument("--template", default=_DEFAULT_TEMPLATE,
                    help="Template .pine source (défaut : strategy_template.pine).")
    pr.add_argument("--split", type=float, default=0.7,
                    help="Part in-sample pour la validation (défaut 0.7).")
    pr.add_argument("--min-oos", type=int, default=10,
                    help="Nb min de trades OOS pour valider une règle (défaut 10).")
    pr.set_defaults(func=_cmd_propose)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
