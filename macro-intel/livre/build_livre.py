#!/usr/bin/env python3
"""Assemble les chapitres Markdown en un livre HTML unique, prêt pour le PDF.

Usage :
    python build_livre.py            # génère livre.html
    python build_livre.py --out X    # chemin de sortie personnalisé

Le fichier produit est autonome (aucune ressource externe) et contient une
feuille de style d'impression : ouvrez-le dans un navigateur puis
« Imprimer → Enregistrer au format PDF ».

Le rendu Markdown est volontairement minimal et sans dépendance : le corpus
n'utilise qu'un sous-ensemble maîtrisé de la syntaxe (titres, tableaux, listes,
code, gras, italique, citations).
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent

CHAPITRES = [
    "00-introduction.md",
    "01-bases-economie.md",
    "02-indicateurs.md",
    "03-banques-centrales.md",
    "04-taux-obligations.md",
    "05-dollar-forex.md",
    "06-matieres-premieres.md",
    "07-geopolitique.md",
    "08-calendrier.md",
    "09-biais-macro.md",
    "10-fondamental-technique.md",
    "11-smc.md",
    "12-methode-macro-smc.md",
    "13-psychologie.md",
    "14-glossaire.md",
    "15-annexes.md",
]

TITRE = (
    "Maîtriser la Macroéconomie, l'Analyse Fondamentale et le Trading Institutionnel"
)
SOUS_TITRE = "De Débutant à Trader Macro-SMC"


# ── Rendu Markdown minimal ──────────────────────────────────────
def _inline(texte: str) -> str:
    """Formatage en ligne : code, gras, italique, liens."""
    texte = html.escape(texte, quote=False)
    texte = re.sub(r"`([^`]+)`", r"<code>\1</code>", texte)
    texte = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", texte)
    texte = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", texte)
    texte = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', texte)
    return texte


def _table(lignes: list[str]) -> str:
    """Convertit un tableau Markdown (avec ligne de séparation) en HTML."""
    if len(lignes) < 2:
        return ""
    cellules = [c.strip() for c in lignes[0].strip().strip("|").split("|")]
    corps = lignes[2:]  # on ignore la ligne d'alignement
    out = ["<table><thead><tr>"]
    out += [f"<th>{_inline(c)}</th>" for c in cellules]
    out.append("</tr></thead><tbody>")
    for ligne in corps:
        valeurs = [c.strip() for c in ligne.strip().strip("|").split("|")]
        out.append("<tr>" + "".join(f"<td>{_inline(v)}</td>" for v in valeurs) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def rendre(markdown: str) -> str:
    """Transforme un chapitre Markdown en HTML."""
    lignes = markdown.split("\n")
    out: list[str] = []
    i = 0
    liste_ouverte: str | None = None

    def fermer_liste() -> None:
        nonlocal liste_ouverte
        if liste_ouverte:
            out.append(f"</{liste_ouverte}>")
            liste_ouverte = None

    while i < len(lignes):
        ligne = lignes[i]

        # Blocs de code (y compris diagrammes Mermaid, rendus tels quels)
        if ligne.startswith("```"):
            fermer_liste()
            langue = ligne[3:].strip()
            bloc: list[str] = []
            i += 1
            while i < len(lignes) and not lignes[i].startswith("```"):
                bloc.append(lignes[i])
                i += 1
            contenu = html.escape("\n".join(bloc))
            classe = " class=\"diagramme\"" if langue == "mermaid" else ""
            out.append(f"<pre{classe}><code>{contenu}</code></pre>")
            i += 1
            continue

        # Tableaux
        if ligne.strip().startswith("|") and i + 1 < len(lignes) and "---" in lignes[i + 1]:
            fermer_liste()
            bloc = []
            while i < len(lignes) and lignes[i].strip().startswith("|"):
                bloc.append(lignes[i])
                i += 1
            out.append(_table(bloc))
            continue

        # Titres
        if ligne.startswith("#"):
            fermer_liste()
            niveau = len(ligne) - len(ligne.lstrip("#"))
            texte = ligne[niveau:].strip()
            ancre = re.sub(r"[^a-z0-9]+", "-", texte.lower()).strip("-")[:60]
            out.append(f'<h{niveau} id="{ancre}">{_inline(texte)}</h{niveau}>')
            i += 1
            continue

        # Citations
        if ligne.startswith(">"):
            fermer_liste()
            bloc = []
            while i < len(lignes) and lignes[i].startswith(">"):
                bloc.append(lignes[i].lstrip(">").strip())
                i += 1
            contenu = "<br>".join(_inline(x) for x in bloc if x)
            out.append(f"<blockquote>{contenu}</blockquote>")
            continue

        # Séparateurs
        if ligne.strip() in {"---", "***", "___"}:
            fermer_liste()
            out.append("<hr>")
            i += 1
            continue

        # Listes (avec gestion des items s'étendant sur plusieurs lignes)
        puce = re.match(r"^(\s*)[-*]\s+(.*)", ligne)
        numerotee = re.match(r"^(\s*)\d+\.\s+(.*)", ligne)
        if puce or numerotee:
            correspondance = puce or numerotee
            balise = "ul" if puce else "ol"
            if liste_ouverte != balise:
                fermer_liste()
                out.append(f"<{balise}>")
                liste_ouverte = balise

            # Un item peut se poursuivre sur les lignes indentées suivantes :
            # sans cela, la continuation deviendrait un paragraphe et couperait
            # la liste en deux.
            morceaux = [correspondance.group(2)]
            i += 1
            while (
                i < len(lignes)
                and lignes[i].strip()
                and lignes[i][:1] in {" ", "\t"}
                and not re.match(r"^\s*([-*]|\d+\.)\s+", lignes[i])
            ):
                morceaux.append(lignes[i].strip())
                i += 1
            out.append(f"<li>{_inline(' '.join(morceaux))}</li>")
            continue

        # Paragraphes
        if ligne.strip():
            fermer_liste()
            bloc = []
            while i < len(lignes) and lignes[i].strip() and not lignes[i].startswith(
                ("#", ">", "|", "```", "---")
            ) and not re.match(r"^(\s*)([-*]|\d+\.)\s+", lignes[i]):
                bloc.append(lignes[i].strip())
                i += 1
            out.append(f"<p>{_inline(' '.join(bloc))}</p>")
            continue

        fermer_liste()
        i += 1

    fermer_liste()
    return "\n".join(out)


# ── Feuille de style ────────────────────────────────────────────
STYLE = """
:root {
  --encre: #1a1a1a; --texte2: #4a4a4a; --doux: #767676;
  --accent: #1f5673; --trait: #d8d8d8; --fond2: #f6f7f8;
  --serif: Georgia, "Times New Roman", serif;
  --sans: "Segoe UI", system-ui, -apple-system, sans-serif;
  --mono: "SF Mono", Consolas, "Courier New", monospace;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: #fff; color: var(--encre);
  font-family: var(--serif); font-size: 11.5pt; line-height: 1.65;
}
.page { max-width: 780px; margin: 0 auto; padding: 40px 32px 80px; }

/* Couverture */
.couverture {
  min-height: 88vh; display: flex; flex-direction: column;
  justify-content: center; text-align: center; page-break-after: always;
}
.couverture .surtitre {
  font-family: var(--sans); font-size: 10pt; letter-spacing: 3px;
  text-transform: uppercase; color: var(--doux); margin-bottom: 24px;
}
.couverture h1 {
  font-size: 27pt; line-height: 1.25; margin: 0 0 16px; border: 0; padding: 0;
}
.couverture .soustitre {
  font-size: 15pt; color: var(--accent); font-style: italic; margin-bottom: 40px;
}
.couverture .filet { width: 70px; height: 2px; background: var(--accent); margin: 0 auto 36px; }
.couverture .note { font-family: var(--sans); font-size: 9.5pt; color: var(--doux); line-height: 1.8; }

/* Sommaire */
.sommaire { page-break-after: always; }
.sommaire ol { list-style: none; padding: 0; counter-reset: partie; }
.sommaire li {
  counter-increment: partie; padding: 9px 0; border-bottom: 1px solid var(--trait);
  font-family: var(--sans); font-size: 10.5pt;
}
.sommaire li::before {
  content: counter(partie) ". "; color: var(--accent); font-weight: 700; margin-right: 8px;
}
.sommaire a { color: var(--encre); text-decoration: none; }

/* Titres */
h1 {
  font-size: 21pt; margin: 0 0 22px; padding-bottom: 12px;
  border-bottom: 3px solid var(--accent); page-break-before: always; page-break-after: avoid;
}
h2 { font-size: 15.5pt; margin: 32px 0 12px; color: var(--accent); page-break-after: avoid; }
h3 { font-size: 12.5pt; margin: 24px 0 10px; page-break-after: avoid; }
h4 { font-size: 11.5pt; margin: 18px 0 8px; font-family: var(--sans); page-break-after: avoid; }
h1:first-of-type { page-break-before: avoid; }

p { margin: 0 0 12px; text-align: justify; }
strong { font-weight: 700; }
a { color: var(--accent); }

/* Listes */
ul, ol { margin: 0 0 14px; padding-left: 24px; }
li { margin-bottom: 5px; }

/* Tableaux */
table {
  width: 100%; border-collapse: collapse; margin: 16px 0;
  font-family: var(--sans); font-size: 9.5pt; page-break-inside: avoid;
}
th {
  background: var(--accent); color: #fff; text-align: left;
  padding: 8px 10px; font-weight: 600;
}
td { padding: 7px 10px; border-bottom: 1px solid var(--trait); vertical-align: top; }
tbody tr:nth-child(even) { background: var(--fond2); }

/* Citations */
blockquote {
  margin: 16px 0; padding: 12px 18px; background: var(--fond2);
  border-left: 4px solid var(--accent); font-size: 10.5pt; page-break-inside: avoid;
}

/* Code et schémas */
pre {
  background: var(--fond2); border: 1px solid var(--trait); border-radius: 4px;
  padding: 12px 14px; overflow-x: auto; font-family: var(--mono);
  font-size: 8.5pt; line-height: 1.5; page-break-inside: avoid;
}
code { font-family: var(--mono); font-size: 9pt; background: var(--fond2); padding: 1px 4px; border-radius: 3px; }
pre code { background: none; padding: 0; font-size: inherit; }
pre.diagramme { background: #fff; border-style: dashed; }

hr { border: 0; border-top: 1px solid var(--trait); margin: 26px 0; }

/* Impression */
@media print {
  @page { size: A4; margin: 18mm 16mm; }
  body { font-size: 10.5pt; }
  .page { max-width: none; padding: 0; }
  .couverture { min-height: 92vh; }
  h1 { page-break-before: always; }
  h1:first-of-type { page-break-before: avoid; }
  table, pre, blockquote { page-break-inside: avoid; }
  h1, h2, h3, h4 { page-break-after: avoid; }
  a { color: var(--encre); text-decoration: none; }
  .no-print { display: none; }
}

/* Aide écran */
.aide {
  position: fixed; bottom: 16px; right: 16px; background: var(--accent); color: #fff;
  font-family: var(--sans); font-size: 9pt; padding: 9px 14px; border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0,0,0,.2);
}
"""


def construire(sortie: Path) -> tuple[int, int]:
    """Assemble le livre. Renvoie (nombre de chapitres, taille en Ko)."""
    corps: list[str] = []
    titres: list[str] = []

    for nom in CHAPITRES:
        chemin = RACINE / nom
        if not chemin.exists():
            print(f"  ⚠ chapitre introuvable, ignoré : {nom}")
            continue
        texte = chemin.read_text(encoding="utf-8")
        premiere = next((x for x in texte.split("\n") if x.startswith("# ")), nom)
        titres.append(premiere.lstrip("# ").strip())
        corps.append(f'<section class="chapitre">{rendre(texte)}</section>')

    sommaire = "\n".join(
        f'<li><a href="#{re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]}">{html.escape(t)}</a></li>'
        for t in titres
    )

    document = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITRE)}</title>
<style>{STYLE}</style>
</head>
<body>
<div class="page">

  <div class="couverture">
    <div class="surtitre">Manuel de formation professionnelle</div>
    <h1>{html.escape(TITRE)}</h1>
    <div class="soustitre">{html.escape(SOUS_TITRE)}</div>
    <div class="filet"></div>
    <div class="note">
      15 parties · Économie · Analyse fondamentale · Smart Money Concepts<br>
      Résumés · Fiches de révision · Exercices corrigés · Études de cas<br><br>
      <strong>Ouvrage pédagogique.</strong> Ne constitue pas un conseil en investissement.<br>
      Le trading comporte un risque de perte en capital.
    </div>
  </div>

  <div class="sommaire">
    <h1 style="page-break-before:avoid">Sommaire</h1>
    <ol>{sommaire}</ol>
  </div>

  {"".join(corps)}

</div>
<div class="aide no-print">Imprimer → Enregistrer au format PDF</div>
</body>
</html>"""

    sortie.write_text(document, encoding="utf-8")
    return len(titres), len(document.encode("utf-8")) // 1024


def main() -> None:
    parseur = argparse.ArgumentParser(description="Génère le livre HTML.")
    parseur.add_argument("--out", default=str(RACINE / "livre.html"), help="Fichier de sortie")
    args = parseur.parse_args()

    chemin = Path(args.out)
    nb, taille = construire(chemin)
    print(f"✓ Livre généré : {chemin}")
    print(f"  {nb} chapitres · {taille} Ko")
    print("  Ouvrez le fichier puis « Imprimer → Enregistrer au format PDF ».")


if __name__ == "__main__":
    main()
