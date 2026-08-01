#!/usr/bin/env python3
"""Fabrique « L'OR ET LA MACRO » — livre HTML autonome, imprimable en PDF.

Usage :
    pip install markdown
    python3 livre-gold/build.py

Produit livre-gold/or-et-macro.html : aucun fichier externe, aucune police
distante, aucun script tiers. Lisible hors ligne sur téléphone comme sur
ordinateur, et imprimable en PDF (Ctrl+P, A4, marges par défaut).

Conventions des sources Markdown (dossier src/, lues par ordre alphabétique) :

    # Titre        -> ouverture de PARTIE (page pleine à l'impression)
    ## Titre       -> CHAPITRE (nouvelle page à l'impression)
    ### Titre      -> section du chapitre
    #### Titre     -> sous-section

    ::: retenir Titre facultatif
    contenu markdown
    :::
                   -> encadré. Classes : retenir, erreur, astuce, pro,
                      histoire, cas, fiche, danger, memo, chiffre.

    ```schema      -> schéma ASCII encadré
    ```svg         -> SVG inséré tel quel (graphiques explicatifs)
    ```tableau     -> tableau ASCII large (police réduite)
"""

from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover
    sys.exit("Dépendance manquante : pip install markdown")

RACINE = Path(__file__).resolve().parent
SOURCES = RACINE / "src"
SORTIE = RACINE / "or-et-macro.html"

VERSION = "1.0"
TITRE = "L'Or et la Macro"
SOUS_TITRE = "Comprendre les forces qui font bouger le XAUUSD"

CLASSES_ENCADRE = {
    "retenir": "À retenir absolument",
    "erreur": "Erreur fréquente",
    "astuce": "Astuce de pro",
    "pro": "Vu du desk",
    "histoire": "Histoire de marché",
    "cas": "Étude de cas",
    "fiche": "Fiche pratique",
    "danger": "Danger",
    "memo": "Mémo",
    "chiffre": "Le chiffre",
}

RE_OUVERTURE = re.compile(r"^:::[ \t]*([a-z]+)[ \t]*(.*)$")
RE_FERMETURE = re.compile(r"^:::[ \t]*$")
RE_TITRE_SANS_ID = re.compile(r"<h([1-4])(?![^>]*\bid=)>", re.I)


def slug(texte: str) -> str:
    texte = re.sub(r"<[^>]+>", "", texte)
    texte = html.unescape(texte)
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"[^a-zA-Z0-9]+", "-", texte).strip("-").lower()
    return texte or "section"


# --------------------------------------------------------------------------
# Rendu markdown + encadrés
# --------------------------------------------------------------------------

def segmenter(source: str) -> list[tuple]:
    segments: list[tuple] = []
    tampon: list[str] = []
    pile: list[tuple[str, str, list[str]]] = []
    dans_code = False

    for ligne in source.splitlines():
        if ligne.lstrip().startswith("```"):
            dans_code = not dans_code
            (pile[-1][2] if pile else tampon).append(ligne)
            continue

        if not dans_code:
            ouverture = RE_OUVERTURE.match(ligne)
            if ouverture and not RE_FERMETURE.match(ligne):
                classe, titre = ouverture.group(1), ouverture.group(2).strip()
                if not pile:
                    segments.append(("md", "\n".join(tampon)))
                    tampon = []
                pile.append((classe, titre, []))
                continue
            if RE_FERMETURE.match(ligne) and pile:
                classe, titre, contenu = pile.pop()
                rendu = ("box", classe, titre, "\n".join(contenu))
                if pile:
                    pile[-1][2].append(rendre_encadre(*rendu[1:]))
                else:
                    segments.append(rendu)
                continue

        (pile[-1][2] if pile else tampon).append(ligne)

    while pile:
        classe, titre, contenu = pile.pop()
        segments.append(("box", classe, titre, "\n".join(contenu)))
    segments.append(("md", "\n".join(tampon)))
    return segments


def md_vers_html(texte: str) -> str:
    md = markdown.Markdown(
        extensions=["tables", "attr_list", "fenced_code", "sane_lists"],
        output_format="html5",
    )
    return md.convert(texte)


def rendre_encadre(classe: str, titre: str, contenu: str) -> str:
    libelle = titre or CLASSES_ENCADRE.get(classe, "")
    entete = f'<p class="bloc-titre">{html.escape(libelle)}</p>' if libelle else ""
    return (
        f'<aside class="bloc bloc--{html.escape(classe)}">'
        f"{entete}{md_vers_html(contenu)}</aside>"
    )


def liberer_svg(corps: str) -> str:
    """Réinjecte les blocs ```svg comme SVG véritables."""

    def remplacer(m: re.Match) -> str:
        return f'<figure class="figure">{html.unescape(m.group(1))}</figure>'

    return re.sub(
        r'<pre><code class="language-svg">(.*?)</code></pre>',
        remplacer,
        corps,
        flags=re.S,
    )


def rendre(source: str) -> str:
    morceaux = []
    for segment in segmenter(source):
        if segment[0] == "md":
            if segment[1].strip():
                morceaux.append(md_vers_html(segment[1]))
        else:
            morceaux.append(rendre_encadre(*segment[1:]))
    corps = "\n".join(morceaux)
    corps = corps.replace(
        '<pre><code class="language-schema">', '<pre class="schema"><code>'
    )
    corps = corps.replace(
        '<pre><code class="language-tableau">',
        '<pre class="schema schema--large"><code>',
    )
    return liberer_svg(corps)


# --------------------------------------------------------------------------
# Ancres et plan
# --------------------------------------------------------------------------

def ancrer(corps: str) -> tuple[str, list[dict]]:
    vus: dict[str, int] = {}
    corps = RE_TITRE_SANS_ID.sub(lambda m: f"<h{m.group(1)} data-auto>", corps)
    plan: list[dict] = []

    def traiter(m: re.Match) -> str:
        niveau, ident, texte = int(m.group(1)), m.group(2), m.group(3)
        brut = html.unescape(re.sub(r"<[^>]+>", "", texte)).strip()
        if not ident:
            base = slug(brut)
            vus[base] = vus.get(base, 0) + 1
            ident = base if vus[base] == 1 else f"{base}-{vus[base]}"
        plan.append({"n": niveau, "id": ident, "t": brut})
        return f'<h{niveau} id="{ident}">{texte}</h{niveau}>'

    corps = re.sub(
        r'<h([1-4])(?:\s+data-auto)?(?:\s+id="([^"]+)")?>(.*?)</h\1>',
        traiter,
        corps,
        flags=re.I | re.S,
    )
    return corps, plan


def numeroter(corps: str, plan: list[dict]) -> str:
    """Exergue « PARTIE N » sur les h1 et « CHAPITRE N » sur les h2."""
    partie = [0]
    chapitre = [0]

    def h1(m: re.Match) -> str:
        brut = re.sub(r"<[^>]+>", "", m.group(2))
        if re.match(r"\s*(Avant|Introduction|Conclusion|Annexe|Comment)", brut, re.I):
            etiquette = brut.split("—")[0].strip()
        else:
            partie[0] += 1
            etiquette = f"Partie {partie[0]}"
        return f'<h1 id="{m.group(1)}" data-eyebrow="{html.escape(etiquette)}">{m.group(2)}</h1>'

    def h2(m: re.Match) -> str:
        brut = re.sub(r"<[^>]+>", "", m.group(2))
        if re.match(r"\s*(Annexe|Sommaire|Avertissement|Comment lire|Glossaire|Index|Ce que vous savez|Le mot de la fin)", brut, re.I):
            etiquette = ""
        else:
            chapitre[0] += 1
            etiquette = f"Chapitre {chapitre[0]}"
        attr = f' data-eyebrow="{html.escape(etiquette)}"' if etiquette else ""
        return f'<h2 id="{m.group(1)}"{attr}>{m.group(2)}</h2>'

    corps = re.sub(r'<h1 id="([^"]+)">(.*?)</h1>', h1, corps, flags=re.S)
    corps = re.sub(r'<h2 id="([^"]+)">(.*?)</h2>', h2, corps, flags=re.S)
    return corps


def construire_nav(plan: list[dict]) -> str:
    lignes = ['<ul class="nav-racine">']
    for e in plan:
        if e["n"] == 1:
            lignes.append(f'<li class="nav-partie"><a href="#{e["id"]}">{html.escape(e["t"])}</a></li>')
        elif e["n"] == 2:
            lignes.append(f'<li class="nav-chapitre"><a href="#{e["id"]}">{html.escape(e["t"])}</a></li>')
    lignes.append("</ul>")
    return "\n".join(lignes)


def construire_sommaire(plan: list[dict]) -> str:
    lignes = ['<section class="sommaire"><h2 class="sommaire-titre">Sommaire</h2><ol>']
    n = 0
    for e in plan:
        if e["n"] == 1:
            lignes.append(
                f'<li class="s-partie"><a href="#{e["id"]}">{html.escape(e["t"])}</a></li>'
            )
        elif e["n"] == 2:
            brut = e["t"]
            if not re.match(r"\s*(Annexe|Sommaire|Avertissement|Comment lire|Glossaire|Index|Ce que vous savez|Le mot de la fin)", brut, re.I):
                n += 1
                num = f'<span class="s-num">{n}</span>'
            else:
                num = '<span class="s-num s-num--vide"></span>'
            lignes.append(
                f'<li class="s-chap">{num}<a href="#{e["id"]}">{html.escape(brut)}</a></li>'
            )
    lignes.append("</ol></section>")
    return "\n".join(lignes)


# --------------------------------------------------------------------------
# Habillage
# --------------------------------------------------------------------------

CSS = r"""
:root{
  --fond:#0d1117; --fond-2:#141a22; --fond-3:#1b2430;
  --encre:#e9ecf1; --encre-2:#aab3c0; --encre-3:#6f7a8a;
  --trait:#232c38; --trait-2:#313d4d;
  --or:#d8a63c; --or-clair:#f0c96f; --or-fonce:#a97c1e;
  --vert:#3fb07d; --rouge:#e2565f; --bleu:#4f9ae2; --violet:#a184e6; --cyan:#3fb2be;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:"SFMono-Regular",Menlo,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace;
  --largeur:44rem;
}
html[data-theme="light"]{
  --fond:#fdfcf9; --fond-2:#f4f1ea; --fond-3:#ebe6db;
  --encre:#191c21; --encre-2:#4b515c; --encre-3:#7b8391;
  --trait:#ded8c9; --trait-2:#c9c1ad;
  --or:#9c6f14; --or-clair:#7d5810; --or-fonce:#7d5810;
  --vert:#1c7a55; --rouge:#b32e39; --bleu:#1e6aab; --violet:#5f45ad; --cyan:#116f79;
}
@media (prefers-color-scheme: light){
  html:not([data-theme]){
    --fond:#fdfcf9; --fond-2:#f4f1ea; --fond-3:#ebe6db;
    --encre:#191c21; --encre-2:#4b515c; --encre-3:#7b8391;
    --trait:#ded8c9; --trait-2:#c9c1ad;
    --or:#9c6f14; --or-clair:#7d5810; --or-fonce:#7d5810;
    --vert:#1c7a55; --rouge:#b32e39; --bleu:#1e6aab; --violet:#5f45ad; --cyan:#116f79;
  }
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--fond); color:var(--encre);
  font-family:var(--serif); font-size:17px; line-height:1.7;
  -webkit-font-smoothing:antialiased; -webkit-text-size-adjust:100%;
}

/* ---------- barre latérale ---------- */
#barre{
  position:fixed; inset:0 auto 0 0; width:19rem; z-index:20;
  background:var(--fond-2); border-right:1px solid var(--trait);
  display:flex; flex-direction:column; transition:transform .18s ease;
}
#barre header{padding:1rem 1.05rem .75rem; border-bottom:1px solid var(--trait)}
#barre .marque{
  font-family:var(--sans); font-size:.64rem; letter-spacing:.24em;
  text-transform:uppercase; color:var(--or); font-weight:700; margin:0;
}
#barre .marque span{color:var(--encre-3)}
#recherche{
  width:100%; margin-top:.65rem; padding:.5rem .65rem; border-radius:8px;
  border:1px solid var(--trait-2); background:var(--fond); color:var(--encre);
  font-family:var(--sans); font-size:.82rem;
}
#recherche:focus{outline:2px solid var(--or); outline-offset:1px}
#indice{font-family:var(--sans); font-size:.64rem; color:var(--encre-3); margin:.4rem 0 0}
#plan{overflow-y:auto; padding:.7rem .55rem 3rem; flex:1}
#plan ul{list-style:none; margin:0; padding:0}
#plan a{
  display:block; padding:.3rem .6rem; border-radius:6px; text-decoration:none;
  color:var(--encre-2); font-family:var(--sans); font-size:.79rem; line-height:1.35;
}
#plan a:hover{background:var(--fond-3); color:var(--encre)}
#plan .nav-partie{margin-top:.9rem}
#plan .nav-partie > a{
  color:var(--or); font-weight:700; font-size:.71rem; letter-spacing:.09em;
  text-transform:uppercase;
}
#plan .nav-chapitre > a{padding-left:1rem; border-left:1px solid var(--trait)}
#plan a.actif{background:var(--fond-3); color:var(--or-clair); font-weight:600}
html[data-theme="light"] #plan a.actif{color:var(--or)}

/* ---------- commandes ---------- */
.commandes{position:fixed; right:1rem; top:1rem; z-index:30; display:flex; gap:.4rem}
.commandes button{
  font-family:var(--sans); font-size:.72rem; font-weight:600; cursor:pointer;
  background:var(--fond-2); color:var(--encre-2); border:1px solid var(--trait-2);
  border-radius:8px; padding:.42rem .62rem;
}
.commandes button:hover{color:var(--or); border-color:var(--or)}
#haut{
  position:fixed; right:1rem; bottom:1rem; z-index:30; opacity:0; pointer-events:none;
  transition:opacity .2s; width:2.4rem; height:2.4rem; border-radius:50%; cursor:pointer;
  background:var(--fond-2); color:var(--encre-2); border:1px solid var(--trait-2);
  font-size:.9rem;
}
#haut.visible{opacity:1; pointer-events:auto}

/* ---------- corps ---------- */
main{margin-left:19rem; padding:0 2.5rem 8rem; transition:margin .18s ease}
.page{max-width:var(--largeur); margin:0 auto}
body.plein #barre{transform:translateX(-100%)}
body.plein main{margin-left:0}

/* ---------- couverture ---------- */
.couverture{
  min-height:100vh; display:flex; flex-direction:column; justify-content:center;
  align-items:center; text-align:center; padding:3rem 1.5rem;
  background:
    radial-gradient(circle at 50% 32%, color-mix(in srgb,var(--or) 16%,transparent), transparent 62%),
    var(--fond);
  border-bottom:1px solid var(--trait);
}
.medaille{
  width:126px; height:126px; border-radius:50%; margin-bottom:2.2rem;
  background:linear-gradient(145deg,#f4d27a,#d8a63c 45%,#8c6414);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  box-shadow:0 14px 40px rgba(0,0,0,.35), inset 0 2px 6px rgba(255,255,255,.55);
  color:#3a2a06; font-family:var(--sans);
}
.medaille b{font-size:2.5rem; line-height:1; font-weight:800; letter-spacing:-.02em}
.medaille span{font-size:.6rem; letter-spacing:.3em; margin-top:.25rem; font-weight:700}
.couverture .surtitre{
  font-family:var(--sans); font-size:.7rem; letter-spacing:.34em; text-transform:uppercase;
  color:var(--or); margin:0 0 1.4rem; font-weight:700;
}
.couverture h1{
  font-family:var(--sans); font-size:clamp(2.6rem,8vw,4.4rem); line-height:1.02;
  margin:0 0 1rem; letter-spacing:-.03em; border:0; padding:0; font-weight:800;
}
.couverture h1::before{content:none}
.couverture .accroche{
  color:var(--encre-2); font-size:1.05rem; max-width:32rem; margin:0 auto 1.6rem;
}
.couverture .filet{width:70px; height:3px; background:var(--or); margin:0 auto 1.6rem}
.couverture .public{
  font-family:var(--sans); font-size:.82rem; color:var(--encre-3); max-width:30rem;
  margin:0 auto; line-height:1.6;
}
.couverture .meta{
  font-family:var(--sans); font-size:.66rem; color:var(--encre-3); margin-top:3rem;
  letter-spacing:.16em; text-transform:uppercase;
}

/* ---------- sommaire ---------- */
.sommaire{max-width:var(--largeur); margin:0 auto; padding:3.5rem 0 2rem}
.sommaire-titre{
  font-family:var(--sans); font-size:.72rem; letter-spacing:.3em; text-transform:uppercase;
  color:var(--or); border:0; margin:0 0 1.8rem; padding:0;
}
.sommaire ol{list-style:none; margin:0; padding:0}
.sommaire .s-partie{margin:1.7rem 0 .5rem}
.sommaire .s-partie a{
  font-family:var(--sans); font-weight:800; font-size:.8rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--or); text-decoration:none; display:block;
  border-bottom:1px solid var(--trait); padding-bottom:.35rem;
}
.sommaire .s-chap{display:flex; gap:.7rem; align-items:baseline; padding:.16rem 0}
.sommaire .s-num{
  font-family:var(--sans); font-size:.68rem; color:var(--encre-3); min-width:1.4rem;
  text-align:right; font-weight:700;
}
.sommaire .s-chap a{
  font-family:var(--sans); font-size:.85rem; color:var(--encre-2); text-decoration:none;
}
.sommaire a:hover{color:var(--or)}

/* ---------- titres ---------- */
h1,h2,h3,h4{font-family:var(--sans); line-height:1.18; letter-spacing:-.015em}
h1{
  font-size:2.3rem; margin:5rem 0 2rem; padding-top:3rem; position:relative;
  border-top:3px solid var(--or); scroll-margin-top:1rem; font-weight:800;
}
h1::before{
  content:attr(data-eyebrow); position:absolute; top:1.3rem; left:0;
  font-size:.66rem; letter-spacing:.3em; text-transform:uppercase; color:var(--or);
  font-weight:800;
}
h2{
  font-size:1.65rem; margin:3.6rem 0 1.2rem; padding-top:1.7rem; position:relative;
  scroll-margin-top:1rem; font-weight:800;
}
h2[data-eyebrow]::before{
  content:attr(data-eyebrow); position:absolute; top:0; left:0;
  font-family:var(--sans); font-size:.64rem; letter-spacing:.24em; text-transform:uppercase;
  color:var(--or); font-weight:800;
}
h3{
  font-size:1.02rem; margin:2.4rem 0 .7rem; padding-left:.75rem;
  border-left:3px solid var(--or); scroll-margin-top:1rem; font-weight:700;
}
h4{
  font-size:.78rem; text-transform:uppercase; letter-spacing:.14em;
  margin:1.8rem 0 .5rem; color:var(--encre-3); font-weight:700;
}
p{margin:.8rem 0}
a{color:var(--bleu)}
a:hover{color:var(--or)}
hr{border:0; border-top:1px solid var(--trait); margin:2.6rem 0}
strong{color:var(--encre)}
em{color:var(--encre-2)}

/* chapô sous un titre de chapitre */
h2 + p em:only-child{
  display:block; font-size:1.02rem; color:var(--encre-2); font-style:italic;
  border-left:2px solid var(--or); padding-left:.9rem; margin:.4rem 0 1.4rem;
}

/* ---------- listes ---------- */
ul,ol{margin:.75rem 0; padding-left:1.3rem}
li{margin:.34rem 0}
li > strong:first-child{
  font-family:var(--sans); font-size:.72rem; letter-spacing:.06em; text-transform:uppercase;
  color:var(--or); font-weight:800;
}
.bloc li > strong:first-child{color:inherit; letter-spacing:.04em}

/* ---------- encadrés ---------- */
.bloc{
  margin:1.4rem 0; padding:.95rem 1.15rem; border-radius:11px;
  border:1px solid var(--trait-2); border-left-width:4px; background:var(--fond-2);
  font-size:.96rem;
}
.bloc > :first-child{margin-top:0}
.bloc > :last-child{margin-bottom:0}
.bloc-titre{
  font-family:var(--sans); font-size:.67rem; font-weight:800; letter-spacing:.16em;
  text-transform:uppercase; margin:0 0 .5rem !important;
}
.bloc--retenir{border-left-color:var(--or); background:color-mix(in srgb,var(--or) 10%,var(--fond-2))}
.bloc--retenir .bloc-titre{color:var(--or)}
.bloc--erreur{border-left-color:var(--rouge)}
.bloc--erreur .bloc-titre{color:var(--rouge)}
.bloc--danger{border-left-color:var(--rouge); background:color-mix(in srgb,var(--rouge) 10%,var(--fond-2))}
.bloc--danger .bloc-titre{color:var(--rouge)}
.bloc--astuce{border-left-color:var(--bleu)}
.bloc--astuce .bloc-titre{color:var(--bleu)}
.bloc--pro{border-left-color:var(--cyan)}
.bloc--pro .bloc-titre{color:var(--cyan)}
.bloc--histoire{border-left-color:var(--violet)}
.bloc--histoire .bloc-titre{color:var(--violet)}
.bloc--cas{border-left-color:var(--vert)}
.bloc--cas .bloc-titre{color:var(--vert)}
.bloc--fiche{border-left-color:var(--vert); background:color-mix(in srgb,var(--vert) 8%,var(--fond-2))}
.bloc--fiche .bloc-titre{color:var(--vert)}
.bloc--memo{border-left-color:var(--violet); background:color-mix(in srgb,var(--violet) 8%,var(--fond-2))}
.bloc--memo .bloc-titre{color:var(--violet)}
.bloc--memo p{font-family:var(--sans); font-size:.92rem}
.bloc--chiffre{border-left-color:var(--or); text-align:center}
.bloc--chiffre .bloc-titre{color:var(--or)}
.bloc--chiffre strong{font-size:1.5rem; font-family:var(--sans)}

/* ---------- tableaux ---------- */
.tableau-enveloppe{overflow-x:auto; margin:1.3rem 0}
table{
  width:100%; border-collapse:collapse; font-family:var(--sans); font-size:.83rem;
  display:block; overflow-x:auto; margin:1.3rem 0;
}
th,td{border:1px solid var(--trait); padding:.48rem .62rem; text-align:left; vertical-align:top}
th{
  background:var(--fond-3); font-size:.66rem; letter-spacing:.11em; text-transform:uppercase;
  color:var(--encre-2); font-weight:800; white-space:nowrap;
}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--fond-2) 60%,transparent)}

/* ---------- code, schémas, figures ---------- */
code{
  font-family:var(--mono); font-size:.86em; background:var(--fond-3);
  padding:.1em .36em; border-radius:5px; color:var(--or-clair);
}
html[data-theme="light"] code{color:var(--or)}
pre.schema{
  font-family:var(--mono); background:var(--fond-2); border:1px solid var(--trait);
  border-radius:11px; padding:1rem 1.1rem; overflow-x:auto; margin:1.3rem 0;
  font-size:.76rem; line-height:1.45; color:var(--encre-2);
}
pre.schema code{background:none; padding:0; color:inherit; font-size:inherit}
pre.schema--large{font-size:.69rem}
.figure{margin:1.6rem 0; text-align:center}
.figure svg{max-width:100%; height:auto}
.figure figcaption{
  font-family:var(--sans); font-size:.72rem; color:var(--encre-3); margin-top:.5rem;
}
blockquote{
  margin:1.3rem 0; padding:.2rem 0 .2rem 1.1rem; border-left:3px solid var(--or);
  color:var(--encre-2); font-style:italic;
}

/* ---------- responsive ---------- */
@media (max-width:1080px){
  body{font-size:16.5px}
  #barre{transform:translateX(-100%); box-shadow:0 0 40px rgba(0,0,0,.45)}
  body.menu #barre{transform:translateX(0)}
  main{margin-left:0; padding:0 1.05rem 6rem}
  .commandes{top:.55rem; right:.55rem}
  h1{font-size:1.9rem}
  h2{font-size:1.35rem}
}

/* ---------- impression ---------- */
@media print{
  :root{
    --fond:#fff; --fond-2:#fff; --fond-3:#f2f0ec;
    --encre:#000; --encre-2:#2f2f2f; --encre-3:#666;
    --trait:#bbb; --trait-2:#9a9a9a; --or:#8a6209; --or-clair:#8a6209;
  }
  body{font-size:10.5pt; background:#fff; color:#000}
  #barre,.commandes,#haut{display:none !important}
  main{margin:0; padding:0}
  .page,.couverture,.sommaire{max-width:none}
  .couverture{
    min-height:0; padding:44mm 0 0; border:0; background:none; page-break-after:always;
  }
  .couverture h1{font-size:34pt; page-break-before:avoid}
  .couverture .accroche{font-size:11pt}
  .medaille{box-shadow:none; width:96px; height:96px}
  .sommaire{page-break-before:always; padding:0}
  h1{page-break-before:always; page-break-after:avoid; padding-top:2.4rem}
  h2{page-break-before:always; page-break-after:avoid}
  h3,h4{page-break-after:avoid}
  .bloc,pre.schema,table,li,.figure{page-break-inside:avoid}
  a{color:#000; text-decoration:none}
  @page{margin:16mm 15mm}
}
"""

JS = r"""
(function(){
  var plan = document.getElementById('plan');
  var champ = document.getElementById('recherche');
  var indice = document.getElementById('indice');
  var navOriginal = plan.innerHTML;
  var INDEX = window.__INDEX__ || [];
  var REPERE = INDEX.length + ' sections indexées';

  function sansAccent(s){ return s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase(); }

  function chercher(q){
    if(!q.trim()){ plan.innerHTML = navOriginal; indice.textContent = REPERE; brancher(); return; }
    var mots = sansAccent(q).split(/\s+/).filter(Boolean);
    var trouves = INDEX.filter(function(e){
      var t = sansAccent(e.t);
      return mots.every(function(m){ return t.indexOf(m) !== -1; });
    }).slice(0,120);
    if(!trouves.length){
      plan.innerHTML = '<p style="font-family:var(--sans);font-size:.78rem;color:var(--encre-3);padding:.6rem">Rien trouvé.</p>';
      indice.textContent = '0 résultat'; return;
    }
    plan.innerHTML = '<ul class="nav-racine">' + trouves.map(function(e){
      return '<li class="nav-chapitre"><a href="#' + e.i + '">' +
             e.t.replace(/&/g,'&amp;').replace(/</g,'&lt;') + '</a></li>';
    }).join('') + '</ul>';
    indice.textContent = trouves.length + ' résultat' + (trouves.length>1?'s':'');
    brancher();
  }

  indice.textContent = REPERE;
  champ.addEventListener('input', function(){ chercher(champ.value); });
  champ.addEventListener('keydown', function(e){
    if(e.key === 'Escape'){ champ.value=''; chercher(''); champ.blur(); }
    if(e.key === 'Enter'){ var a = plan.querySelector('a'); if(a){ a.click(); } }
  });

  function brancher(){
    plan.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){
        if(window.innerWidth <= 1080){ document.body.classList.remove('menu'); }
      });
    });
  }
  brancher();

  document.addEventListener('keydown', function(e){
    if(e.key === '/' && document.activeElement !== champ){ e.preventDefault(); champ.focus(); champ.select(); }
  });

  var btnTheme = document.getElementById('theme');
  var memo = localStorage.getItem('gold-theme');
  if(memo){ document.documentElement.setAttribute('data-theme', memo); }
  btnTheme.addEventListener('click', function(){
    var actuel = document.documentElement.getAttribute('data-theme');
    if(!actuel){ actuel = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'; }
    var suivant = actuel === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', suivant);
    localStorage.setItem('gold-theme', suivant);
  });

  document.getElementById('plein').addEventListener('click', function(){
    if(window.innerWidth <= 1080){ document.body.classList.toggle('menu'); }
    else { document.body.classList.toggle('plein'); }
  });

  var titres = Array.prototype.slice.call(document.querySelectorAll('main h1, main h2'));
  var haut = document.getElementById('haut');
  function surDefilement(){
    haut.classList.toggle('visible', window.scrollY > 900);
    if(champ.value.trim()) return;
    var courant = null;
    for(var i=0;i<titres.length;i++){
      if(titres[i].getBoundingClientRect().top < 130){ courant = titres[i]; } else { break; }
    }
    plan.querySelectorAll('a.actif').forEach(function(a){ a.classList.remove('actif'); });
    if(courant){
      var lien = plan.querySelector('a[href="#' + courant.id + '"]');
      if(lien){
        lien.classList.add('actif');
        var b = lien.getBoundingClientRect(), p = plan.getBoundingClientRect();
        if(b.top < p.top || b.bottom > p.bottom){ lien.scrollIntoView({block:'center'}); }
      }
    }
    localStorage.setItem('gold-position', String(window.scrollY));
  }
  window.addEventListener('scroll', surDefilement, {passive:true});
  surDefilement();
  haut.addEventListener('click', function(){ window.scrollTo({top:0,behavior:'smooth'}); });

  if(!location.hash){
    var pos = parseInt(localStorage.getItem('gold-position') || '0', 10);
    if(pos > 400){ window.scrollTo(0, pos); }
  }
})();
"""

GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre} — {sous_titre}</title>
<meta name="description" content="Livre de macroéconomie appliquée au trading de l'or : dollar, taux réels, inflation, emploi, banques centrales, corrélations et méthode d'analyse complète.">
<style>{css}</style>
</head>
<body>
<div class="commandes">
  <button id="plein" title="Afficher / masquer le sommaire">☰ Sommaire</button>
  <button id="theme" title="Basculer clair / sombre">◐ Thème</button>
</div>
<button id="haut" title="Revenir en haut">↑</button>

<aside id="barre">
  <header>
    <p class="marque">L'Or et la Macro <span>· XAUUSD</span></p>
    <input id="recherche" type="search" placeholder="Chercher… (touche /)" autocomplete="off">
    <p id="indice"></p>
  </header>
  <nav id="plan">{nav}</nav>
</aside>

<header class="couverture">
  <div class="medaille"><b>Au</b><span>79</span></div>
  <p class="surtitre">Macroéconomie appliquée</p>
  <h1>{titre}</h1>
  <div class="filet"></div>
  <p class="accroche">{sous_titre}</p>
  <p class="public">Pour le trader qui maîtrise déjà la structure de marché, la liquidité
  et l'exécution — et à qui il ne manque plus que la lecture des forces qui
  décident de la direction.</p>
  <p class="meta">{chapitres} chapitres · Version {version} · {date}</p>
</header>

{sommaire}

<main><div class="page">
{corps}
</div></main>

<script>window.__INDEX__ = {index};</script>
<script>{js}</script>
</body>
</html>
"""


def main() -> int:
    fichiers = sorted(SOURCES.glob("*.md"))
    if not fichiers:
        sys.exit(f"Aucune source dans {SOURCES}")

    source = "\n\n".join(f.read_text(encoding="utf-8") for f in fichiers)
    corps = rendre(source)
    corps, plan = ancrer(corps)
    corps = numeroter(corps, plan)

    parties = sum(1 for e in plan if e["n"] == 1)
    chapitres = sum(1 for e in plan if e["n"] == 2)
    sections = sum(1 for e in plan if e["n"] == 3)

    page = GABARIT.format(
        css=CSS,
        js=JS,
        titre=TITRE,
        sous_titre=SOUS_TITRE,
        nav=construire_nav(plan),
        sommaire=construire_sommaire(plan),
        corps=corps,
        index=json.dumps(
            [{"i": e["id"], "t": e["t"]} for e in plan],
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        version=VERSION,
        date=date.today().strftime("%d/%m/%Y"),
        chapitres=chapitres,
    )
    SORTIE.write_text(page, encoding="utf-8")

    mots = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", corps)))
    figures = corps.count('class="figure"')
    print(f"{SORTIE.relative_to(RACINE.parent)} — {SORTIE.stat().st_size/1024:.0f} Ko")
    print(
        f"{len(fichiers)} sources · {parties} parties · {chapitres} chapitres · "
        f"{sections} sections · {figures} figures · ~{mots} mots"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
