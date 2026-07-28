"""Cohérence entre le code, la documentation et l'empaquetage.

Ces vérifications existent parce que la dérive est déjà arrivée : `__version__`
affichait 0.1.0 pendant que `pyproject.toml` déclarait 0.3.0, et `rolling`
n'était exporté nulle part alors que toutes les autres briques l'étaient. Une
documentation fausse coûte plus cher qu'une documentation absente.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import backtest_agent
from backtest_agent.cli import main

RACINE = Path(__file__).resolve().parent.parent
README = (RACINE / "README.md").read_text(encoding="utf-8")
PYPROJECT = (RACINE / "pyproject.toml").read_text(encoding="utf-8")
SCHEMA = (RACINE / "config" / "schema.yaml").read_text(encoding="utf-8")


def test_la_version_du_paquet_suit_pyproject():
    """Une seule source de vérité : pyproject. Le paquet la lit, ne la duplique pas."""
    attendue = re.search(r'^version = "([^"]+)"', PYPROJECT, re.M).group(1)
    assert backtest_agent.__version__ == attendue, (
        f"Dérive de version : paquet={backtest_agent.__version__}, "
        f"pyproject={attendue}")


def test_toutes_les_briques_publiques_sont_exportees():
    """Si une capacité existe, elle doit être atteignable depuis le paquet."""
    for nom in ["load_trades", "global_metrics", "build_report", "walk_forward",
                "build_proposals", "validate_candidate", "compare_backtests",
                "rolling_walk_forward", "optimize_threshold"]:
        assert nom in backtest_agent.__all__, f"{nom} absent de __all__"
        assert hasattr(backtest_agent, nom), f"{nom} non importable"


def test_le_readme_documente_toutes_les_commandes(capsys):
    """Une commande non documentée est une commande que personne n'utilisera."""
    with pytest.raises(SystemExit):
        main(["--help"])
    aide = capsys.readouterr().out
    commandes = re.search(r"\{([a-z,]+)\}", aide).group(1).split(",")
    assert len(commandes) >= 7
    for cmd in commandes:
        assert f"backtest-agent {cmd}" in README or f"`{cmd}`" in README, (
            f"La commande « {cmd} » n'apparaît nulle part dans le README.")


def test_les_seuils_documentes_correspondent_au_code():
    """Le schema.yaml sert de référence lisible : il doit dire la vérité."""
    from backtest_agent import rolling, validate
    attendus = {
        "min_chunk": rolling.MIN_CHUNK,
        "min_fold_trades": rolling.MIN_FOLD_TRADES,
        "min_folds_for_claim": rolling.MIN_FOLDS_FOR_CLAIM,
        "min_t_stat": rolling.MIN_T_STAT,
        "min_effect_size": rolling.MIN_EFFECT_SIZE,
        "min_trades_after": validate.MIN_TRADES_AFTER,
        "min_retained": validate.MIN_RETAINED,
        "min_segment_agreement": validate.MIN_SEGMENT_AGREEMENT,
    }
    for cle, valeur in attendus.items():
        motif = rf"^\s*{cle}:\s*([\d.]+)"
        trouve = re.search(motif, SCHEMA, re.M)
        assert trouve, f"« {cle} » n'est pas documenté dans config/schema.yaml"
        assert float(trouve.group(1)) == pytest.approx(float(valeur)), (
            f"« {cle} » : schema.yaml dit {trouve.group(1)}, le code dit {valeur}")


def test_le_nombre_de_tests_annonce_dans_le_readme_est_plausible():
    """Le README chiffre la suite : ce chiffre doit rester crédible."""
    annonce = re.search(r"(\d+)\s+tests", README)
    assert annonce, "Le README doit indiquer le nombre de tests."
    n = int(annonce.group(1))
    reel = sum(len(re.findall(r"^def test_", f.read_text(encoding="utf-8"), re.M))
               for f in (RACINE / "tests").glob("test_*.py"))
    # Les tests paramétrés en produisent plusieurs : on tolère un écart vers le haut.
    assert reel <= n <= reel * 1.3, (
        f"Le README annonce {n} tests, on en compte {reel} définis.")
