"""CLI de bout en bout : chaque commande doit produire un fichier exploitable,
et échouer proprement (message clair, pas de traceback) sur entrée invalide.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from backtest_agent.cli import main


def test_analyze_produit_un_rapport_et_un_json_valide(structured_csv, tmp_path):
    md, js = tmp_path / "r.md", tmp_path / "r.json"
    code = main(["analyze", structured_csv, "--no-llm", "-o", str(md), "--json", str(js)])
    assert code == 0
    assert "Analyse globale" in md.read_text(encoding="utf-8")
    # Le JSON doit être relisible par un parseur STRICT (pas de NaN/Infinity).
    data = json.loads(js.read_text(encoding="utf-8"),
                      parse_constant=lambda c: pytest.fail(f"non-JSON: {c}"))
    assert data["global_metrics"]["n_trades"] > 0


def test_walkforward_produit_un_rapport(structured_csv, tmp_path):
    out = tmp_path / "wf.md"
    assert main(["walkforward", structured_csv, "-o", str(out)]) == 0
    assert "walk-forward" in out.read_text(encoding="utf-8").lower()


def test_propose_genere_un_candidat_pine(structured_csv, tmp_path):
    md, pine = tmp_path / "p.md", tmp_path / "c.pine"
    assert main(["propose", structured_csv, "-o", str(md),
                 "--candidate", str(pine)]) == 0
    assert md.exists()
    if pine.exists():
        assert "passFilters" in pine.read_text(encoding="utf-8")


def test_validate_produit_un_verdict(structured_csv, tmp_path):
    out = tmp_path / "v.md"
    assert main(["validate", structured_csv, "-o", str(out), "--sims", "100"]) == 0
    assert "Verdict" in out.read_text(encoding="utf-8")


def test_view_convertit_un_rapport_en_html_sans_ouvrir_de_navigateur(
        structured_csv, tmp_path):
    md = tmp_path / "r.md"
    assert main(["analyze", structured_csv, "--no-llm", "-o", str(md)]) == 0
    assert main(["view", str(md), "--no-open"]) == 0
    html = md.with_suffix(".html")
    assert html.exists()
    assert "<h1>" in html.read_text(encoding="utf-8")


def test_view_sur_fichier_introuvable_est_propre(capsys):
    code = main(["view", "/chemin/inexistant.md", "--no-open"])
    assert code == 2
    assert "introuvable" in capsys.readouterr().err.lower()


def test_compare_produit_un_tableau(structured_csv, tmp_path):
    out = tmp_path / "c.md"
    assert main(["compare", structured_csv, structured_csv, "-o", str(out)]) == 0
    texte = out.read_text(encoding="utf-8")
    assert "Baseline" in texte and "Candidat" in texte


def test_pipeline_produit_les_quatre_rapports(structured_csv, tmp_path):
    outdir = tmp_path / "out"
    assert main(["pipeline", structured_csv, "-o", str(outdir),
                 "--no-llm", "--sims", "100"]) == 0
    for nom in ["1_analyse.md", "2_walkforward.md", "3_propositions.md",
                "4_validation.md"]:
        assert (outdir / nom).exists(), f"{nom} manquant"


def test_fichier_introuvable_donne_un_message_clair_sans_traceback(capsys):
    code = main(["analyze", "/chemin/qui/nexiste/pas.csv", "--no-llm"])
    assert code == 2
    assert "introuvable" in capsys.readouterr().err.lower()


def test_format_non_supporte_donne_un_message_clair(tmp_path, capsys):
    mauvais = tmp_path / "data.xlsx"
    mauvais.write_text("pas un csv", encoding="utf-8")
    code = main(["analyze", str(mauvais), "--no-llm"])
    assert code == 2
    assert "format non supporté" in capsys.readouterr().err.lower()


def test_fichier_vide_donne_un_message_clair(tmp_path, capsys):
    vide = tmp_path / "vide.csv"
    vide.write_text("datetime,side,profit\n", encoding="utf-8")
    code = main(["analyze", str(vide), "--no-llm"])
    assert code == 2
    assert "vide" in capsys.readouterr().err.lower()


def test_les_donnees_dexemple_du_depot_sont_analysables(tmp_path):
    """Le CSV livré dans le dépôt doit rester exploitable (garde anti-régression)."""
    exemple = Path(__file__).resolve().parent.parent / "examples" / "sample_trades.csv"
    if not exemple.exists():
        pytest.skip("jeu d'exemple absent")
    assert main(["analyze", str(exemple), "--no-llm", "-o",
                 str(tmp_path / "r.md")]) == 0
