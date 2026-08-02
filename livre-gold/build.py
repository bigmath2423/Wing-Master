#!/usr/bin/env python3
"""Fabrique GOLD MACRO — manuel professionnel, HTML autonome et imprimable.

Usage :
    pip install markdown
    python3 livre-gold/build.py

Produit livre-gold/gold-macro.html : aucun fichier externe, aucune police
distante, aucun script tiers. Lisible hors ligne sur téléphone, tablette et
ordinateur, imprimable en PDF (Ctrl+P, A4, marges par défaut, arrière-plans
activés).

CONVENTIONS DES SOURCES (dossier src/, lues par ordre alphabétique)
───────────────────────────────────────────────────────────────────
    # Titre                 ouverture de PARTIE (page pleine à l'impression)
    ## Titre                CHAPITRE (nouvelle page)
    ## Titre {: .fiche }    FICHE (numérotation séparée)
    ## Titre {: .libre }    page spéciale, sans numéro
    ### Titre               section
    #### Titre              sous-section

    ::: classe Titre facultatif
    contenu markdown
    :::

    Classes disponibles :
      retenir      À retenir absolument
      erreur       Erreur des débutants
      institutions Ce que font les institutions
      detail       Le détail que 90 % des traders ignorent
      xau          Application directe sur XAUUSD
      fiche        Fiche pratique
      cas          Étude de cas
      histoire     Histoire de marché
      astuce       Astuce
      danger       Danger
      memo         Mémo
      resume       Résumé
      niveaux      trois niveaux d'explication (liste de 3 puces)
      cartes       grille de cartes (liste à puces)
      cle          phrase forte, en grand
      respiration  page de respiration (saut de page avant et après)

    ```schema     schéma ASCII encadré
    ```svg        SVG inséré tel quel (s'adapte au thème)
    ```tableau    tableau ASCII large
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
SORTIE = RACINE / "gold-macro.html"

VERSION = "2.0"
TITRE = "GOLD MACRO"
SOUS_TITRE = "Le manuel de référence du trader XAUUSD"

CLASSES_ENCADRE = {
    "retenir": "À retenir absolument",
    "erreur": "Erreur des débutants",
    "institutions": "Ce que font les institutions",
    "detail": "Le détail que 90 % des traders ignorent",
    "xau": "Application directe sur XAUUSD",
    "fiche": "Fiche pratique",
    "cas": "Étude de cas",
    "histoire": "Histoire de marché",
    "astuce": "Astuce",
    "danger": "Danger",
    "memo": "Mémo",
    "resume": "Résumé",
    "niveaux": "",
    "cartes": "",
    "cle": "",
    "respiration": "",
}

RE_OUVERTURE = re.compile(r"^:::[ \t]*([a-z]+)[ \t]*(.*)$")
RE_FERMETURE = re.compile(r"^:::[ \t]*$")


def slug(texte: str) -> str:
    texte = re.sub(r"<[^>]+>", "", texte)
    texte = html.unescape(texte)
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"[^a-zA-Z0-9]+", "-", texte).strip("-").lower()
    return texte or "section"


# --------------------------------------------------------------------------
# Rendu markdown et encadrés
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
                bloc = ("box", classe, titre, "\n".join(contenu))
                if pile:
                    pile[-1][2].append(rendre_encadre(*bloc[1:]))
                else:
                    segments.append(bloc)
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
    libelle = titre if titre else CLASSES_ENCADRE.get(classe, "")
    entete = f'<p class="bloc-titre">{html.escape(libelle)}</p>' if libelle else ""
    balise = "section" if classe == "respiration" else "aside"
    return (
        f'<{balise} class="bloc bloc--{html.escape(classe)}">'
        f"{entete}{md_vers_html(contenu)}</{balise}>"
    )


def liberer_svg(corps: str) -> str:
    def remplacer(m: re.Match) -> str:
        return f'<figure class="figure">{html.unescape(m.group(1))}</figure>'

    return re.sub(
        r'<pre><code class="language-svg">(.*?)</code></pre>', remplacer, corps, flags=re.S
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
    corps = corps.replace('<pre><code class="language-schema">', '<pre class="schema"><code>')
    corps = corps.replace(
        '<pre><code class="language-tableau">', '<pre class="schema schema--large"><code>'
    )
    corps = corps.replace("<table>", '<div class="tab"><table>').replace(
        "</table>", "</table></div>"
    )
    return liberer_svg(corps)


# --------------------------------------------------------------------------
# Ancres, numérotation, plan
# --------------------------------------------------------------------------

def attribut(attrs: str, nom: str) -> str | None:
    m = re.search(rf'{nom}="([^"]*)"', attrs)
    return m.group(1) if m else None


def ancrer(corps: str) -> tuple[str, list[dict]]:
    vus: dict[str, int] = {}
    plan: list[dict] = []

    def traiter(m: re.Match) -> str:
        niveau, attrs, texte = int(m.group(1)), m.group(2) or "", m.group(3)
        brut = html.unescape(re.sub(r"<[^>]+>", "", texte)).strip()
        ident = attribut(attrs, "id")
        if not ident:
            base = slug(brut)
            vus[base] = vus.get(base, 0) + 1
            ident = base if vus[base] == 1 else f"{base}-{vus[base]}"
            attrs = f'{attrs} id="{ident}"'
        classe = attribut(attrs, "class") or ""
        plan.append({"n": niveau, "id": ident, "t": brut, "c": classe})
        return f"<h{niveau}{attrs}>{texte}</h{niveau}>"

    corps = re.sub(r"<h([1-4])([^>]*)>(.*?)</h\1>", traiter, corps, flags=re.I | re.S)
    return corps, plan


def numeroter(corps: str, plan: list[dict]) -> tuple[str, dict]:
    partie = [0]
    chapitre = [0]
    fiche = [0]
    etiquettes: dict[str, str] = {}

    def h1(m: re.Match) -> str:
        attrs, texte = m.group(1) or "", m.group(2)
        brut = re.sub(r"<[^>]+>", "", texte)
        if "libre" in (attribut(attrs, "class") or ""):
            etiquette = ""
        else:
            partie[0] += 1
            etiquette = f"Partie {partie[0]}"
        ident = attribut(attrs, "id") or ""
        etiquettes[ident] = etiquette
        sup = f' data-eyebrow="{html.escape(etiquette)}"' if etiquette else ""
        return f"<h1{attrs}{sup}>{texte}</h1>"

    def h2(m: re.Match) -> str:
        attrs, texte = m.group(1) or "", m.group(2)
        classe = attribut(attrs, "class") or ""
        if "libre" in classe:
            etiquette = ""
        elif "fiche" in classe:
            fiche[0] += 1
            etiquette = f"Fiche {fiche[0]:02d}"
        else:
            chapitre[0] += 1
            etiquette = f"Chapitre {chapitre[0]:02d}"
        ident = attribut(attrs, "id") or ""
        etiquettes[ident] = etiquette
        sup = f' data-eyebrow="{html.escape(etiquette)}"' if etiquette else ""
        return f"<h2{attrs}{sup}>{texte}</h2>"

    corps = re.sub(r"<h1([^>]*)>(.*?)</h1>", h1, corps, flags=re.S)
    corps = re.sub(r"<h2([^>]*)>(.*?)</h2>", h2, corps, flags=re.S)
    return corps, etiquettes


def construire_nav(plan: list[dict]) -> str:
    lignes = ['<ul class="nav-racine">']
    for e in plan:
        if e["n"] == 1:
            lignes.append(f'<li class="nav-partie"><a href="#{e["id"]}">{html.escape(e["t"])}</a></li>')
        elif e["n"] == 2:
            lignes.append(f'<li class="nav-chapitre"><a href="#{e["id"]}">{html.escape(e["t"])}</a></li>')
    lignes.append("</ul>")
    return "\n".join(lignes)


def construire_sommaire(plan: list[dict], etiquettes: dict) -> str:
    lignes = ['<section class="sommaire"><p class="sommaire-sur">Sommaire</p>']
    ouvert = False
    for e in plan:
        if e["n"] == 1:
            if ouvert:
                lignes.append("</ol>")
            eti = etiquettes.get(e["id"], "")
            lignes.append(
                f'<h3 class="s-partie"><span>{html.escape(eti)}</span>'
                f'<a href="#{e["id"]}">{html.escape(e["t"])}</a></h3><ol>'
            )
            ouvert = True
        elif e["n"] == 2:
            eti = etiquettes.get(e["id"], "")
            num = eti.split()[-1] if eti else "·"
            lignes.append(
                f'<li class="s-chap"><span class="s-num">{html.escape(num)}</span>'
                f'<a href="#{e["id"]}">{html.escape(e["t"])}</a></li>'
            )
    if ouvert:
        lignes.append("</ol>")
    lignes.append("</section>")
    return "\n".join(lignes)


# --------------------------------------------------------------------------
# Habillage
# --------------------------------------------------------------------------

CSS = r"""
:root{
  --fond:#0c1016; --fond-2:#141a23; --fond-3:#1c2430; --fond-4:#232d3b;
  --encre:#eef1f6; --encre-2:#b4bdc9; --encre-3:#7c8797;
  --trait:#212a36; --trait-2:#303c4c;
  --or:#e0ae4a; --or-clair:#f6d68c; --or-fonce:#9c7420;
  --vert:#45bd86; --rouge:#ec5f6a; --bleu:#5aa5ea; --violet:#ab8bee; --cyan:#45bece;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:"SFMono-Regular",Menlo,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace;
  --mesure:38rem;
}
html[data-theme="light"]{
  --fond:#fffdf9; --fond-2:#f6f2ea; --fond-3:#efe9dd; --fond-4:#e6dfd0;
  --encre:#15181d; --encre-2:#474e5a; --encre-3:#78818f;
  --trait:#e3dccd; --trait-2:#cdc4b1;
  --or:#8f6410; --or-clair:#74510b; --or-fonce:#74510b;
  --vert:#17795a; --rouge:#b02b36; --bleu:#1a659f; --violet:#5b3fa8; --cyan:#0e6c76;
}
@media (prefers-color-scheme: light){
  html:not([data-theme]){
    --fond:#fffdf9; --fond-2:#f6f2ea; --fond-3:#efe9dd; --fond-4:#e6dfd0;
    --encre:#15181d; --encre-2:#474e5a; --encre-3:#78818f;
    --trait:#e3dccd; --trait-2:#cdc4b1;
    --or:#8f6410; --or-clair:#74510b; --or-fonce:#74510b;
    --vert:#17795a; --rouge:#b02b36; --bleu:#1a659f; --violet:#5b3fa8; --cyan:#0e6c76;
  }
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--fond); color:var(--encre);
  font-family:var(--serif); font-size:19px; line-height:1.78;
  -webkit-font-smoothing:antialiased; -webkit-text-size-adjust:100%;
  text-rendering:optimizeLegibility;
}

/* ═══════════ barre latérale ═══════════ */
#barre{
  position:fixed; inset:0 auto 0 0; width:20rem; z-index:20;
  background:var(--fond-2); border-right:1px solid var(--trait);
  display:flex; flex-direction:column; transition:transform .2s ease;
}
#barre header{padding:1.15rem 1.15rem .85rem; border-bottom:1px solid var(--trait)}
#barre .marque{
  font-family:var(--sans); font-size:.68rem; letter-spacing:.3em;
  text-transform:uppercase; color:var(--or); font-weight:800; margin:0;
}
#barre .marque span{color:var(--encre-3); letter-spacing:.14em}
#recherche{
  width:100%; margin-top:.75rem; padding:.58rem .7rem; border-radius:9px;
  border:1px solid var(--trait-2); background:var(--fond); color:var(--encre);
  font-family:var(--sans); font-size:.85rem;
}
#recherche:focus{outline:2px solid var(--or); outline-offset:1px}
#indice{font-family:var(--sans); font-size:.66rem; color:var(--encre-3); margin:.45rem 0 0}
#plan{overflow-y:auto; padding:.75rem .55rem 3rem; flex:1}
#plan ul{list-style:none; margin:0; padding:0}
#plan a{
  display:block; padding:.34rem .62rem; border-radius:7px; text-decoration:none;
  color:var(--encre-2); font-family:var(--sans); font-size:.82rem; line-height:1.38;
}
#plan a:hover{background:var(--fond-3); color:var(--encre)}
#plan .nav-partie{margin-top:1rem}
#plan .nav-partie > a{
  color:var(--or); font-weight:800; font-size:.72rem; letter-spacing:.1em;
  text-transform:uppercase;
}
#plan .nav-chapitre > a{padding-left:1.05rem; border-left:1px solid var(--trait)}
#plan a.actif{background:var(--fond-3); color:var(--or-clair); font-weight:700}
html[data-theme="light"] #plan a.actif{color:var(--or)}

/* ═══════════ commandes ═══════════ */
.commandes{position:fixed; right:1.1rem; top:1.1rem; z-index:30; display:flex; gap:.45rem}
.commandes button{
  font-family:var(--sans); font-size:.75rem; font-weight:700; cursor:pointer;
  background:var(--fond-2); color:var(--encre-2); border:1px solid var(--trait-2);
  border-radius:9px; padding:.48rem .7rem;
}
.commandes button:hover{color:var(--or); border-color:var(--or)}
#haut{
  position:fixed; right:1.1rem; bottom:1.1rem; z-index:30; opacity:0; pointer-events:none;
  transition:opacity .2s; width:2.7rem; height:2.7rem; border-radius:50%; cursor:pointer;
  background:var(--fond-2); color:var(--encre-2); border:1px solid var(--trait-2); font-size:1rem;
}
#haut.visible{opacity:1; pointer-events:auto}

/* ═══════════ corps ═══════════ */
main{margin-left:20rem; padding:0 3rem 12rem; transition:margin .2s ease}
.page{max-width:var(--mesure); margin:0 auto}
body.plein #barre{transform:translateX(-100%)}
body.plein main{margin-left:0}

/* ═══════════ couverture ═══════════ */
.couverture{
  min-height:100vh; display:flex; flex-direction:column; justify-content:center;
  align-items:center; text-align:center; padding:4rem 1.5rem;
  background:
    radial-gradient(ellipse at 50% 30%, color-mix(in srgb,var(--or) 20%,transparent), transparent 65%),
    var(--fond);
  border-bottom:1px solid var(--trait);
}
.medaille{
  width:150px; height:150px; border-radius:50%; margin-bottom:2.6rem;
  background:linear-gradient(150deg,#f9e2a4,#e0ae4a 44%,#8a6212);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  box-shadow:0 18px 55px rgba(0,0,0,.4), inset 0 3px 8px rgba(255,255,255,.6);
  color:#3a2905; font-family:var(--sans);
}
.medaille b{font-size:3rem; line-height:1; font-weight:800; letter-spacing:-.03em}
.medaille span{font-size:.66rem; letter-spacing:.34em; margin-top:.3rem; font-weight:800}
.couverture .surtitre{
  font-family:var(--sans); font-size:.74rem; letter-spacing:.4em; text-transform:uppercase;
  color:var(--or); margin:0 0 1.6rem; font-weight:800;
}
.couverture h1{
  font-family:var(--sans); font-size:clamp(3.2rem,11vw,6rem); line-height:.95;
  margin:0 0 1.3rem; letter-spacing:-.045em; border:0; padding:0; font-weight:800;
}
.couverture h1::before{content:none}
.couverture .filet{width:90px; height:4px; background:var(--or); margin:0 auto 1.8rem}
.couverture .accroche{
  font-family:var(--sans); color:var(--encre); font-size:1.25rem; font-weight:600;
  max-width:26rem; margin:0 auto 1.5rem; line-height:1.45;
}
.couverture .public{
  color:var(--encre-3); font-size:1rem; max-width:28rem; margin:0 auto; line-height:1.65;
}
.couverture .meta{
  font-family:var(--sans); font-size:.68rem; color:var(--encre-3); margin-top:3.5rem;
  letter-spacing:.2em; text-transform:uppercase;
}

/* ═══════════ sommaire ═══════════ */
.sommaire{max-width:var(--mesure); margin:0 auto; padding:5rem 0 3rem}
.sommaire-sur{
  font-family:var(--sans); font-size:.74rem; letter-spacing:.36em; text-transform:uppercase;
  color:var(--or); margin:0 0 2.6rem; font-weight:800;
}
.sommaire h3.s-partie{
  font-family:var(--sans); margin:2.6rem 0 .7rem; padding:0 0 .45rem;
  border:0; border-bottom:2px solid var(--trait-2); font-size:1.15rem; font-weight:800;
  display:flex; align-items:baseline; gap:.7rem;
}
.sommaire h3.s-partie span{
  font-size:.62rem; letter-spacing:.2em; text-transform:uppercase; color:var(--or);
  font-weight:800; white-space:nowrap;
}
.sommaire h3.s-partie a{color:var(--encre); text-decoration:none}
.sommaire ol{list-style:none; margin:0; padding:0}
.sommaire .s-chap{display:flex; gap:.85rem; align-items:baseline; padding:.2rem 0}
.sommaire .s-num{
  font-family:var(--sans); font-size:.72rem; color:var(--or); min-width:1.9rem;
  text-align:right; font-weight:800;
}
.sommaire .s-chap a{font-family:var(--sans); font-size:.95rem; color:var(--encre-2); text-decoration:none}
.sommaire a:hover{color:var(--or)}

/* ═══════════ titres ═══════════ */
h1,h2,h3,h4{font-family:var(--sans); line-height:1.14; letter-spacing:-.025em}
h1{
  font-size:clamp(2.6rem,6vw,3.8rem); margin:9rem 0 2.5rem; padding-top:4rem;
  position:relative; scroll-margin-top:1rem; font-weight:800;
}
h1::before{
  content:attr(data-eyebrow); position:absolute; top:1.6rem; left:0;
  font-size:.72rem; letter-spacing:.36em; text-transform:uppercase; color:var(--or);
  font-weight:800;
}
h1::after{
  content:""; display:block; width:76px; height:4px; background:var(--or); margin-top:1.6rem;
}
h2{
  font-size:clamp(1.85rem,4vw,2.5rem); margin:7rem 0 1.6rem; padding-top:2.4rem;
  position:relative; scroll-margin-top:1rem; font-weight:800;
  border-top:1px solid var(--trait);
}
h2[data-eyebrow]::before{
  content:attr(data-eyebrow); position:absolute; top:1.3rem; left:0;
  font-family:var(--sans); font-size:.68rem; letter-spacing:.3em; text-transform:uppercase;
  color:var(--or); font-weight:800;
}
h3{
  font-size:1.32rem; margin:3.4rem 0 1rem; scroll-margin-top:1rem; font-weight:800;
  color:var(--encre);
}
h4{
  font-size:.82rem; text-transform:uppercase; letter-spacing:.17em;
  margin:2.2rem 0 .6rem; color:var(--or); font-weight:800;
}
p{margin:1.15rem 0}
a{color:var(--bleu)}
a:hover{color:var(--or)}
hr{border:0; height:1px; background:var(--trait); margin:3.5rem 0}
strong{color:var(--encre); font-weight:700}
em{color:var(--encre-2)}

/* phrase d'accroche sous un titre de chapitre */
h2 + p em:only-child{
  display:block; font-family:var(--sans); font-size:1.22rem; font-weight:600;
  font-style:normal; color:var(--or); line-height:1.45; margin:.2rem 0 2.2rem;
}

/* paragraphe d'ouverture */
.lead{font-size:1.15rem; color:var(--encre-2); line-height:1.7}

/* ═══════════ listes ═══════════ */
ul,ol{margin:1.15rem 0; padding-left:1.4rem}
li{margin:.5rem 0; padding-left:.2rem}
ul li::marker{color:var(--or)}
ol li::marker{color:var(--or); font-family:var(--sans); font-weight:800; font-size:.9em}
li > strong:first-child{
  font-family:var(--sans); font-size:.76rem; letter-spacing:.07em; text-transform:uppercase;
  color:var(--or); font-weight:800;
}
.bloc li > strong:first-child{color:inherit; letter-spacing:.04em}

/* ═══════════ encadrés ═══════════ */
.bloc{
  margin:2.4rem 0; padding:1.5rem 1.7rem; border-radius:16px;
  border:1px solid var(--trait-2); background:var(--fond-2); font-size:1rem;
  line-height:1.7;
}
.bloc > :first-child{margin-top:0}
.bloc > :last-child{margin-bottom:0}
.bloc-titre{
  font-family:var(--sans); font-size:.7rem; font-weight:800; letter-spacing:.19em;
  text-transform:uppercase; margin:0 0 .9rem !important; display:flex; align-items:center; gap:.5rem;
}
.bloc-titre::before{
  content:""; width:26px; height:2px; background:currentColor; display:inline-block; flex:none;
}
.bloc--retenir{border-color:var(--or); background:color-mix(in srgb,var(--or) 12%,var(--fond-2))}
.bloc--retenir .bloc-titre{color:var(--or)}
.bloc--erreur{border-color:color-mix(in srgb,var(--rouge) 45%,var(--trait-2)); background:color-mix(in srgb,var(--rouge) 7%,var(--fond-2))}
.bloc--erreur .bloc-titre{color:var(--rouge)}
.bloc--danger{border-color:var(--rouge); background:color-mix(in srgb,var(--rouge) 12%,var(--fond-2))}
.bloc--danger .bloc-titre{color:var(--rouge)}
.bloc--institutions{border-color:color-mix(in srgb,var(--cyan) 45%,var(--trait-2)); background:color-mix(in srgb,var(--cyan) 7%,var(--fond-2))}
.bloc--institutions .bloc-titre{color:var(--cyan)}
.bloc--detail{border-color:color-mix(in srgb,var(--violet) 45%,var(--trait-2)); background:color-mix(in srgb,var(--violet) 8%,var(--fond-2))}
.bloc--detail .bloc-titre{color:var(--violet)}
.bloc--xau{border-color:color-mix(in srgb,var(--or) 55%,var(--trait-2)); background:color-mix(in srgb,var(--or) 7%,var(--fond-2))}
.bloc--xau .bloc-titre{color:var(--or)}
.bloc--fiche{border-color:color-mix(in srgb,var(--vert) 50%,var(--trait-2)); background:color-mix(in srgb,var(--vert) 8%,var(--fond-2))}
.bloc--fiche .bloc-titre{color:var(--vert)}
.bloc--cas{border-color:color-mix(in srgb,var(--vert) 40%,var(--trait-2))}
.bloc--cas .bloc-titre{color:var(--vert)}
.bloc--histoire{border-color:color-mix(in srgb,var(--violet) 40%,var(--trait-2))}
.bloc--histoire .bloc-titre{color:var(--violet)}
.bloc--astuce{border-color:color-mix(in srgb,var(--bleu) 45%,var(--trait-2))}
.bloc--astuce .bloc-titre{color:var(--bleu)}
.bloc--memo{border-color:var(--trait-2); background:var(--fond-3)}
.bloc--memo .bloc-titre{color:var(--encre-3)}
.bloc--memo p{font-family:var(--sans); font-size:1rem; font-weight:600}
.bloc--resume{border-color:var(--or); background:color-mix(in srgb,var(--or) 8%,var(--fond-2))}
.bloc--resume .bloc-titre{color:var(--or)}

/* phrase forte */
.bloc--cle{
  border:0; border-left:5px solid var(--or); border-radius:0; background:none;
  padding:.6rem 0 .6rem 1.8rem; margin:3rem 0;
}
.bloc--cle p{
  font-family:var(--sans); font-size:1.45rem; line-height:1.35; font-weight:700;
  color:var(--encre); letter-spacing:-.02em; margin:.3rem 0;
}

/* trois niveaux */
.bloc--niveaux{background:none; border:0; padding:0; margin:2.2rem 0}
.bloc--niveaux ul{list-style:none; margin:0; padding:0; display:grid; gap:.9rem}
.bloc--niveaux li{
  margin:0; padding:1.05rem 1.25rem; border-radius:14px; background:var(--fond-2);
  border:1px solid var(--trait); border-left:4px solid var(--encre-3); font-size:1rem;
}
.bloc--niveaux li:nth-child(1){border-left-color:var(--vert)}
.bloc--niveaux li:nth-child(2){border-left-color:var(--cyan)}
.bloc--niveaux li:nth-child(3){border-left-color:var(--or)}
.bloc--niveaux li > strong:first-child{
  display:block; margin-bottom:.3rem; font-size:.68rem; letter-spacing:.18em;
}
.bloc--niveaux li:nth-child(1) > strong:first-child{color:var(--vert)}
.bloc--niveaux li:nth-child(2) > strong:first-child{color:var(--cyan)}
.bloc--niveaux li:nth-child(3) > strong:first-child{color:var(--or)}

/* grille de cartes */
.bloc--cartes{background:none; border:0; padding:0; margin:2.2rem 0}
.bloc--cartes ul{
  list-style:none; margin:0; padding:0; display:grid; gap:.85rem;
  grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));
}
.bloc--cartes li{
  margin:0; padding:1.05rem 1.2rem; border-radius:14px; background:var(--fond-2);
  border:1px solid var(--trait); font-size:.96rem; line-height:1.6;
}
.bloc--cartes li > strong:first-child{
  display:block; margin-bottom:.35rem; color:var(--or); font-size:.72rem; letter-spacing:.14em;
}

/* page de respiration */
.bloc--respiration{
  background:var(--fond-2); border:1px solid var(--trait-2); border-radius:20px;
  padding:2.6rem 2rem; margin:3.5rem 0;
}
.bloc--respiration h3{margin-top:2.2rem}
.bloc--respiration h3:first-child{margin-top:0}

/* ═══════════ tableaux ═══════════ */
.tab{overflow-x:auto; margin:2rem 0; border-radius:14px; border:1px solid var(--trait)}
.tab table{margin:0; border:0; width:100%}
table{
  width:100%; border-collapse:collapse; font-family:var(--sans); font-size:.92rem;
  line-height:1.5;
}
th,td{border-bottom:1px solid var(--trait); padding:.72rem .9rem; text-align:left; vertical-align:top}
th{
  background:var(--fond-3); font-size:.68rem; letter-spacing:.13em; text-transform:uppercase;
  color:var(--encre-2); font-weight:800; white-space:nowrap;
}
tbody tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--fond-2) 55%,transparent)}
td strong{color:var(--encre)}

/* ═══════════ code, schémas, figures ═══════════ */
code{
  font-family:var(--mono); font-size:.85em; background:var(--fond-3);
  padding:.12em .4em; border-radius:6px; color:var(--or-clair);
}
html[data-theme="light"] code{color:var(--or)}
pre.schema{
  font-family:var(--mono); background:var(--fond-2); border:1px solid var(--trait);
  border-radius:14px; padding:1.3rem 1.4rem; overflow-x:auto; margin:2rem 0;
  font-size:.8rem; line-height:1.55; color:var(--encre-2);
}
pre.schema code{background:none; padding:0; color:inherit; font-size:inherit}
pre.schema--large{font-size:.72rem}
.figure{margin:2.4rem 0; text-align:center}
.figure svg{max-width:100%; height:auto}
blockquote{
  margin:2rem 0; padding:.3rem 0 .3rem 1.4rem; border-left:4px solid var(--or);
  color:var(--encre-2); font-style:italic; font-size:1.05rem;
}

/* ═══════════ responsive ═══════════ */
@media (max-width:1180px){
  body{font-size:18px}
  #barre{transform:translateX(-100%); box-shadow:0 0 50px rgba(0,0,0,.5)}
  body.menu #barre{transform:translateX(0)}
  main{margin-left:0; padding:3.2rem 1.35rem 7rem}
  .commandes{top:.6rem; right:.6rem}
  .commandes button{backdrop-filter:blur(6px)}
  h1,h2,h3{scroll-margin-top:4.2rem}
  #haut{right:.7rem; bottom:.7rem; opacity:.85}
  .bloc{padding:1.25rem 1.3rem; border-radius:14px}
  .bloc--cle p{font-size:1.25rem}
}
@media (max-width:600px){
  body{font-size:17.5px; line-height:1.75}
  h1{margin-top:5rem}
  h2{margin-top:4.5rem}
  .medaille{width:118px; height:118px}
  .medaille b{font-size:2.3rem}
}

/* ═══════════ impression ═══════════ */
@media print{
  :root{
    --fond:#fff; --fond-2:#faf8f4; --fond-3:#f0ece4; --fond-4:#e8e2d6;
    --encre:#000; --encre-2:#2b2b2b; --encre-3:#5f5f5f;
    --trait:#d5cfc2; --trait-2:#b3aa97;
    --or:#8a5f0c; --or-clair:#8a5f0c;
    --mesure:none;
  }
  body{font-size:11.5pt; line-height:1.62; background:#fff; color:#000}
  #barre,.commandes,#haut{display:none !important}
  main{margin:0; padding:0}
  .page{max-width:none}
  .couverture{
    min-height:0; padding:52mm 0 0; border:0; background:none; page-break-after:always;
  }
  .couverture h1{font-size:44pt; page-break-before:avoid}
  .couverture .accroche{font-size:14pt}
  .medaille{box-shadow:none; width:110px; height:110px}
  .sommaire{page-break-before:always; page-break-after:always; padding:0}
  h1{page-break-before:always; page-break-after:avoid; margin:0 0 2rem; padding-top:3rem; font-size:30pt}
  h2{page-break-before:always; page-break-after:avoid; margin:0 0 1.2rem; padding-top:1.8rem; font-size:20pt}
  h3{page-break-after:avoid; font-size:13pt; margin-top:2rem}
  h4{page-break-after:avoid}
  .bloc,pre.schema,table,li,.figure,.tab{page-break-inside:avoid}
  .bloc--respiration{page-break-before:always; page-break-inside:auto}
  a{color:#000; text-decoration:none}
  @page{margin:19mm 17mm}
}
"""

JS = r"""
(function(){
  var plan=document.getElementById('plan'),champ=document.getElementById('recherche'),
      indice=document.getElementById('indice'),navOriginal=plan.innerHTML,
      INDEX=window.__INDEX__||[],REPERE=INDEX.length+' sections indexées';

  function sansAccent(s){return s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();}

  function chercher(q){
    if(!q.trim()){plan.innerHTML=navOriginal;indice.textContent=REPERE;brancher();return;}
    var mots=sansAccent(q).split(/\s+/).filter(Boolean);
    var t=INDEX.filter(function(e){var x=sansAccent(e.t);
      return mots.every(function(m){return x.indexOf(m)!==-1;});}).slice(0,120);
    if(!t.length){
      plan.innerHTML='<p style="font-family:var(--sans);font-size:.8rem;color:var(--encre-3);padding:.7rem">Rien trouvé.</p>';
      indice.textContent='0 résultat';return;
    }
    plan.innerHTML='<ul class="nav-racine">'+t.map(function(e){
      return '<li class="nav-chapitre"><a href="#'+e.i+'">'+
        e.t.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</a></li>';}).join('')+'</ul>';
    indice.textContent=t.length+' résultat'+(t.length>1?'s':'');
    brancher();
  }

  indice.textContent=REPERE;
  champ.addEventListener('input',function(){chercher(champ.value);});
  champ.addEventListener('keydown',function(e){
    if(e.key==='Escape'){champ.value='';chercher('');champ.blur();}
    if(e.key==='Enter'){var a=plan.querySelector('a');if(a){a.click();}}
  });

  function brancher(){
    plan.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click',function(){
        if(window.innerWidth<=1180){document.body.classList.remove('menu');}
      });
    });
  }
  brancher();

  document.addEventListener('keydown',function(e){
    if(e.key==='/'&&document.activeElement!==champ){e.preventDefault();champ.focus();champ.select();}
  });

  var btn=document.getElementById('theme'),memo=localStorage.getItem('gm-theme');
  if(memo){document.documentElement.setAttribute('data-theme',memo);}
  btn.addEventListener('click',function(){
    var a=document.documentElement.getAttribute('data-theme');
    if(!a){a=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';}
    var s=a==='dark'?'light':'dark';
    document.documentElement.setAttribute('data-theme',s);
    localStorage.setItem('gm-theme',s);
  });

  document.getElementById('plein').addEventListener('click',function(){
    if(window.innerWidth<=1180){document.body.classList.toggle('menu');}
    else{document.body.classList.toggle('plein');}
  });

  var titres=Array.prototype.slice.call(document.querySelectorAll('main h1, main h2'));
  var haut=document.getElementById('haut');
  function surDefilement(){
    haut.classList.toggle('visible',window.scrollY>900);
    if(champ.value.trim())return;
    var courant=null;
    for(var i=0;i<titres.length;i++){
      if(titres[i].getBoundingClientRect().top<140){courant=titres[i];}else{break;}
    }
    plan.querySelectorAll('a.actif').forEach(function(a){a.classList.remove('actif');});
    if(courant){
      var l=plan.querySelector('a[href="#'+courant.id+'"]');
      if(l){l.classList.add('actif');
        var b=l.getBoundingClientRect(),p=plan.getBoundingClientRect();
        if(b.top<p.top||b.bottom>p.bottom){l.scrollIntoView({block:'center'});}}
    }
    localStorage.setItem('gm-position',String(window.scrollY));
  }
  window.addEventListener('scroll',surDefilement,{passive:true});
  surDefilement();
  haut.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});

  if(!location.hash){
    var pos=parseInt(localStorage.getItem('gm-position')||'0',10);
    if(pos>400){window.scrollTo(0,pos);}
  }
})();
"""

GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre} — {sous_titre}</title>
<meta name="description" content="Manuel professionnel de macroéconomie appliquée au trading de l'or : fiches indicateurs, Fed, graphiques indispensables, routine quotidienne, scénarios et checklists.">
<meta name="color-scheme" content="dark light">
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
    <p class="marque">Gold Macro <span>· XAUUSD</span></p>
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
  <p class="public">Savoir en dix minutes pourquoi l'or peut monter ou baisser
  aujourd'hui, quoi surveiller, et dans quel sens orienter son biais.</p>
  <p class="meta">{parties} parties · {chapitres} chapitres · {fiches} fiches · v{version}</p>
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
    corps, etiquettes = numeroter(corps, plan)

    parties = sum(1 for v in etiquettes.values() if v.startswith("Partie"))
    chapitres = sum(1 for v in etiquettes.values() if v.startswith("Chapitre"))
    fiches = sum(1 for v in etiquettes.values() if v.startswith("Fiche"))
    sections = sum(1 for e in plan if e["n"] == 3)

    page = GABARIT.format(
        css=CSS,
        js=JS,
        titre=TITRE,
        sous_titre=SOUS_TITRE,
        nav=construire_nav(plan),
        sommaire=construire_sommaire(plan, etiquettes),
        corps=corps,
        index=json.dumps(
            [{"i": e["id"], "t": e["t"]} for e in plan],
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        version=VERSION,
        parties=parties,
        chapitres=chapitres,
        fiches=fiches,
    )
    SORTIE.write_text(page, encoding="utf-8")

    mots = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", corps)))
    figures = corps.count('class="figure"')
    print(f"{SORTIE.relative_to(RACINE.parent)} — {SORTIE.stat().st_size/1024:.0f} Ko")
    print(
        f"{len(fichiers)} sources · {parties} parties · {chapitres} chapitres · "
        f"{fiches} fiches · {sections} sections · {figures} figures · ~{mots} mots"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
