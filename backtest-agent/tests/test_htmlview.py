"""Convertisseur Markdown -> HTML : couvre exactement la syntaxe que les
rapports du paquet produisent, pas Markdown en général.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from backtest_agent.htmlview import markdown_to_html, render_report, wrap_html
from backtest_agent.report import build_report
from backtest_agent.validate import validate_candidate, validation_markdown


def test_titres_h1_h2_h3():
    html = markdown_to_html("# Un\n## Deux\n### Trois\n")
    assert "<h1>Un</h1>" in html
    assert "<h2>Deux</h2>" in html
    assert "<h3>Trois</h3>" in html


def test_gras_italique_code_en_ligne():
    html = markdown_to_html("Voici **gras**, _italique_ et `code`.")
    assert "<strong>gras</strong>" in html
    assert "<em>italique</em>" in html
    assert "<code>code</code>" in html


def test_echappement_html_dans_le_texte():
    """Un signe < dans les données (ex: un delta) ne doit jamais casser la page."""
    html = markdown_to_html("Comparaison a < b et x & y")
    assert "&lt;" in html and "&amp;" in html
    assert "a < b" not in html  # pas de < brut qui casserait le HTML


def test_tableau_avec_ligne_de_separation():
    md = "| Col A | Col B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n"
    html = markdown_to_html(md)
    assert "<table>" in html
    assert "<th>Col A</th>" in html and "<th>Col B</th>" in html
    assert "<td>1</td>" in html and "<td>4</td>" in html
    # La ligne de séparation ne doit pas apparaître comme une ligne de données.
    assert "<td>---</td>" not in html


def test_citation_blockquote():
    html = markdown_to_html("> Attention à ceci.\n> Suite de la citation.")
    assert "<blockquote>" in html
    assert "Attention à ceci." in html and "Suite de la citation." in html


def test_liste_a_puces():
    html = markdown_to_html("- premier\n- deuxième\n- troisième\n")
    assert html.count("<li>") == 3
    assert "<li>premier</li>" in html


def test_bloc_de_code_est_echappe():
    md = '```json\n{"a": 1, "b": "<x>"}\n```\n'
    html = markdown_to_html(md)
    assert "<pre><code>" in html
    assert "&lt;x&gt;" in html  # le contenu du bloc reste échappé


def test_fragment_html_brut_recopie_tel_quel():
    """Les <details> insérés par report.py doivent traverser sans être échappés."""
    html = markdown_to_html("<details><summary>Détails</summary>\n")
    assert "<details><summary>Détails</summary>" in html


def test_separateur_horizontal():
    assert "<hr>" in markdown_to_html("Avant\n\n---\n\nAprès")


def test_wrap_html_inclut_le_titre_et_le_style():
    page = wrap_html("<p>corps</p>", "Mon titre")
    assert "<title>Mon titre</title>" in page
    assert "<p>corps</p>" in page
    assert "<style>" in page


def test_render_report_ecrit_un_fichier_html_sans_ouvrir_de_navigateur(tmp_path):
    md = tmp_path / "rapport.md"
    md.write_text("# Titre\n\nUn paragraphe avec **gras**.\n", encoding="utf-8")
    html_path = render_report(md, open_browser=False)
    assert html_path == md.with_suffix(".html")
    assert html_path.exists()
    contenu = html_path.read_text(encoding="utf-8")
    assert "<h1>Titre</h1>" in contenu
    assert "<strong>gras</strong>" in contenu


def test_convertit_le_rapport_principal_sans_planter(structured_df):
    """Le rapport principal (build_report) utilise titres, listes et citations."""
    rapport = build_report(structured_df, use_llm=False)
    html = markdown_to_html(rapport["markdown"])
    assert "<h1>" in html and "<h2>" in html
    assert "<li>" in html          # les sections sont rédigées en listes à puces
    assert "<blockquote>" in html  # les notes méthodologiques sont des citations


def test_convertit_un_rapport_a_tableaux_sans_planter(structured_df):
    """validate/rolling/walkforward utilisent des tableaux Markdown : à vérifier séparément."""
    resultat = validate_candidate(structured_df, n_sims=100)
    html = markdown_to_html(validation_markdown(resultat))
    assert "<h1>" in html
    # Que le verdict soit calculable ou non, la page ne doit jamais planter ni
    # rester vide.
    assert len(html) > 20
