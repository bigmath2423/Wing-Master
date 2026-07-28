"""Étape 2 : traduction condition -> Pine et génération du candidat.

Un code Pine faux serait pire qu'aucun code : il produirait un backtest
trompeur. Ces tests vérifient la traduction ET le refus de traduire quand
l'agent n'est pas sûr.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from backtest_agent.proposals import (
    spec_to_pine, apply_to_template, _render_filter_block,
    generate_candidate_pine, proposals_markdown, _BEGIN, _END,
)

TEMPLATE = Path(__file__).resolve().parent.parent / "tradingview" / "strategy_template.pine"


@pytest.mark.parametrize("spec,attendu", [
    ({"column": "ob", "modality": "True", "direction": "keep"}, "cond_ob"),
    ({"column": "_hour", "modality": "22", "direction": "exclude"},
     "not (hour(time) == 22)"),
    ({"column": "_dow", "modality": "Saturday", "direction": "keep"},
     "dayofweek == dayofweek.saturday"),
    ({"column": "_session", "modality": "Londres", "direction": "keep"},
     "hour(time) >= 7"),
])
def test_traduit_les_conditions_connues(spec, attendu):
    res = spec_to_pine(spec)
    assert res["translatable"] is True
    assert attendu in res["pine"]


def test_exclude_est_bien_la_negation_de_keep():
    keep = spec_to_pine({"column": "_hour", "modality": "9", "direction": "keep"})
    excl = spec_to_pine({"column": "_hour", "modality": "9", "direction": "exclude"})
    assert keep["pine"] == "hour(time) == 9"
    assert excl["pine"] == "not (hour(time) == 9)"


def test_traduit_une_plage_datr():
    res = spec_to_pine({"column": "_atr_bucket", "modality": "(50.4, 157.5]",
                        "direction": "keep"})
    assert res["translatable"] is True
    assert "atr > 50.4" in res["pine"] and "atr <= 157.5" in res["pine"]


def test_traduit_un_seuil_de_confiance():
    res = spec_to_pine({"column": "_conf_bucket", "modality": "75-100%",
                        "direction": "keep"})
    assert res["translatable"] is True
    assert "confidence >= 75" in res["pine"]


def test_refuse_de_traduire_ce_quil_ne_sait_pas_traduire():
    """Mieux vaut un TODO manuel qu'un code Pine faux."""
    res = spec_to_pine({"column": "colonne_exotique", "modality": "X",
                        "direction": "keep"})
    assert res["translatable"] is False
    assert res["pine"] is None


def test_la_direction_nest_pas_traduite_automatiquement():
    """Un biais directionnel est structurant : l'agent doit laisser l'humain décider."""
    res = spec_to_pine({"column": "direction", "modality": "BUY", "direction": "keep"})
    assert res["translatable"] is False


def test_le_bloc_vide_neutralise_les_filtres():
    bloc = _render_filter_block([])
    assert "passFilters = true" in bloc
    assert _BEGIN in bloc and _END in bloc


def test_le_bloc_combine_les_filtres_en_et_logique():
    bloc = _render_filter_block([("cond_ob", "règle A"), ("not (hour(time) == 22)", "règle B")])
    assert "filter1 = cond_ob" in bloc
    assert "filter2 = not (hour(time) == 22)" in bloc
    assert "passFilters = filter1 and filter2" in bloc


def test_le_patch_du_template_est_idempotent():
    """Régénérer deux fois ne doit pas empiler les blocs."""
    original = TEMPLATE.read_text(encoding="utf-8")
    bloc = _render_filter_block([("cond_ob", "r")])
    une_fois = apply_to_template(original, bloc)
    deux_fois = apply_to_template(une_fois, bloc)
    assert une_fois == deux_fois
    assert une_fois.count(_BEGIN) == 1


def test_le_patch_echoue_bruyamment_sans_marqueurs():
    with pytest.raises(ValueError, match="Marqueurs"):
        apply_to_template("strategy('x')\n", _render_filter_block([]))


def test_les_entrees_du_template_sont_bien_gardees_par_passfilters():
    """Sans ça, les filtres générés n'auraient aucun effet sur le backtest."""
    texte = TEMPLATE.read_text(encoding="utf-8")
    assert "longSignal and passFilters" in texte
    assert "shortSignal and passFilters" in texte


def test_genere_un_fichier_candidat(structured_df, tmp_path):
    out = tmp_path / "candidat.pine"
    res = generate_candidate_pine(structured_df, template_path=TEMPLATE, out_path=out)
    if res.get("available"):
        assert out.exists()
        contenu = out.read_text(encoding="utf-8")
        assert _BEGIN in contenu and "passFilters" in contenu


def test_markdown_explicite_quand_rien_nest_proposable():
    md = proposals_markdown({"available": True, "n_proposals": 0,
                             "proposals": [], "pine_filter_block": "",
                             "walk_forward_summary": {
                                 "rules_confirmed": 0, "rules_evaluated": 3,
                                 "n_in_sample": 100, "n_out_of_sample": 40}})
    assert "Aucune modification proposée" in md
    assert "sur-optimiser" in md
