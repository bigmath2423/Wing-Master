#!/usr/bin/env python3
"""Fabrique le Manuel de Trading Personnel (HTML autonome, imprimable en PDF).

Usage :
    pip install markdown
    python3 manuel-trading/build.py

Le fichier produit — manuel-trading/manuel-de-trading.html — est autonome :
aucune police, aucune image, aucun script externe. Il s'ouvre hors ligne et
s'imprime en PDF (Ctrl+P, « Enregistrer au format PDF », marges par défaut).

Conventions d'écriture des sources Markdown (dossier src/, lues dans l'ordre
alphabétique des noms de fichiers) :

    # Titre            -> ouverture de tome (page pleine à l'impression)
    ## Titre           -> chapitre
    ### Titre          -> entrée de dictionnaire / sous-section
    #### Titre         -> sous-sous-section

    ::: retenir À retenir absolument
    contenu markdown
    :::
                       -> encadré. Classes : retenir, erreur, piege, memo,
                          astuce, pro, resume, danger.

    ```schema
    ASCII art
    ```
                       -> schéma ASCII encadré.

    {#ancre}           -> ancre explicite sur un titre (extension attr_list).
"""

from __future__ import annotations

import html
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover - dépendance déclarée dans le README
    sys.exit("Dépendance manquante : pip install markdown")

RACINE = Path(__file__).resolve().parent
SOURCES = RACINE / "src"
SORTIE = RACINE / "manuel-de-trading.html"

VERSION = "1.0"

CLASSES_ENCADRE = {
    "retenir": "À retenir absolument",
    "erreur": "Les erreurs",
    "piege": "Piège",
    "memo": "Mémo",
    "astuce": "Astuce",
    "pro": "Vu du côté institutionnel",
    "resume": "Résumé en une page",
    "danger": "Danger",
}

RE_OUVERTURE = re.compile(r"^:::[ \t]*([a-z]+)[ \t]*(.*)$")
RE_FERMETURE = re.compile(r"^:::[ \t]*$")
RE_TITRE = re.compile(r"<h([1-4])(?![^>]*\bid=)>", re.I)
RE_TITRE_TOUS = re.compile(r'<h([1-4])(?:\s+id="([^"]+)")?>(.*?)</h\1>', re.I | re.S)


def slug(texte: str) -> str:
    """Identifiant d'ancre stable, sans accent, utilisable dans une URL."""
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"<[^>]+>", "", texte)
    texte = html.unescape(texte)
    texte = re.sub(r"[^a-zA-Z0-9]+", "-", texte).strip("-").lower()
    return texte or "section"


# --------------------------------------------------------------------------
# Découpage des encadrés ::: ... :::
# --------------------------------------------------------------------------

def segmenter(source: str) -> list[tuple]:
    """Découpe le markdown en segments ('md', texte) et ('box', classe, titre, texte)."""
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

    while pile:  # encadré non refermé : on ferme proprement
        classe, titre, contenu = pile.pop()
        segments.append(("box", classe, titre, "\n".join(contenu)))
    segments.append(("md", "\n".join(tampon)))
    return segments


def convertisseur() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=["tables", "attr_list", "fenced_code", "sane_lists", "footnotes"],
        output_format="html5",
    )


def md_vers_html(texte: str) -> str:
    md = convertisseur()
    return md.convert(texte)


def rendre_encadre(classe: str, titre: str, contenu: str) -> str:
    libelle = titre or CLASSES_ENCADRE.get(classe, "")
    entete = f'<p class="encadre-titre">{html.escape(libelle)}</p>' if libelle else ""
    return (
        f'<aside class="encadre encadre--{html.escape(classe)}">'
        f"{entete}{md_vers_html(contenu)}</aside>"
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
    # Schémas ASCII : ```schema -> <pre class="schema">
    corps = corps.replace(
        '<pre><code class="language-schema">', '<pre class="schema"><code>'
    )
    corps = corps.replace(
        '<pre><code class="language-tableau">', '<pre class="schema schema--large"><code>'
    )
    return corps


# --------------------------------------------------------------------------
# Ancres, table des matières, index de recherche
# --------------------------------------------------------------------------

def ancrer(corps: str) -> tuple[str, list[dict]]:
    """Ajoute un id à chaque titre sans id, puis extrait le plan du document."""
    vus: dict[str, int] = {}

    def ajouter_id(m: re.Match) -> str:
        return f"<h{m.group(1)} data-auto>"

    corps = RE_TITRE.sub(ajouter_id, corps)

    plan: list[dict] = []

    def traiter(m: re.Match) -> str:
        niveau, ident, texte = int(m.group(1)), m.group(2), m.group(3)
        brut = re.sub(r"<[^>]+>", "", texte)
        brut = html.unescape(brut).strip()
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


def construire_nav(plan: list[dict]) -> str:
    lignes = ['<ul class="nav-racine">']
    for entree in plan:
        if entree["n"] > 2:
            continue
        classe = "nav-tome" if entree["n"] == 1 else "nav-chapitre"
        lignes.append(
            f'<li class="{classe}"><a href="#{entree["id"]}">'
            f'{html.escape(entree["t"])}</a></li>'
        )
    lignes.append("</ul>")
    return "\n".join(lignes)


def construire_sommaire(plan: list[dict]) -> str:
    """Table des matières visible dans le corps du livre (indispensable en PDF)."""
    lignes = ['<div class="sommaire"><h2>Sommaire</h2><ol>']
    for entree in plan:
        if entree["n"] == 1:
            lignes.append(
                f'<li class="s-tome"><a href="#{entree["id"]}">'
                f'{html.escape(entree["t"])}</a></li>'
            )
        elif entree["n"] == 2:
            lignes.append(
                f'<li class="s-chap"><a href="#{entree["id"]}">'
                f'{html.escape(entree["t"])}</a></li>'
            )
    lignes.append("</ol></div>")
    return "\n".join(lignes)


def index_js(plan: list[dict]) -> str:
    import json

    allege = [{"i": e["id"], "t": e["t"], "n": e["n"]} for e in plan]
    return json.dumps(allege, ensure_ascii=False, separators=(",", ":"))


# --------------------------------------------------------------------------
# Gabarit
# --------------------------------------------------------------------------

CSS = r"""
:root{
  --fond:#0f1115; --fond-2:#151922; --fond-3:#1b2029;
  --encre:#e7e9ee; --encre-2:#a9b0bd; --encre-3:#6f7787;
  --trait:#262c38; --trait-2:#333b4a;
  --or:#d8a13a; --or-clair:#f0c56b;
  --vert:#3fb27f; --rouge:#e0525f; --orange:#e08a3c;
  --violet:#9b7ce0; --bleu:#4c9ae0; --cyan:#3fb6c0;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:"SFMono-Regular",Menlo,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace;
  --largeur:46rem;
}
html[data-theme="light"]{
  --fond:#fbfaf7; --fond-2:#f3f1ec; --fond-3:#ebe8e1;
  --encre:#1b1d22; --encre-2:#4c525e; --encre-3:#7c8492;
  --trait:#ddd8cd; --trait-2:#c8c2b4;
  --or:#9a6d12; --or-clair:#7a5610;
  --vert:#1f7a52; --rouge:#b32d3a; --orange:#a45c12;
  --violet:#6a49b8; --bleu:#1f6bab; --cyan:#12707a;
}
@media (prefers-color-scheme: light){
  html:not([data-theme]){
    --fond:#fbfaf7; --fond-2:#f3f1ec; --fond-3:#ebe8e1;
    --encre:#1b1d22; --encre-2:#4c525e; --encre-3:#7c8492;
    --trait:#ddd8cd; --trait-2:#c8c2b4;
    --or:#9a6d12; --or-clair:#7a5610;
    --vert:#1f7a52; --rouge:#b32d3a; --orange:#a45c12;
    --violet:#6a49b8; --bleu:#1f6bab; --cyan:#12707a;
  }
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--fond); color:var(--encre);
  font-family:var(--serif); font-size:17px; line-height:1.68;
  -webkit-font-smoothing:antialiased;
}

/* ---------- barre latérale ---------- */
#barre{
  position:fixed; inset:0 auto 0 0; width:19rem; z-index:20;
  background:var(--fond-2); border-right:1px solid var(--trait);
  display:flex; flex-direction:column; transform:translateX(0);
  transition:transform .18s ease;
}
#barre header{padding:1.1rem 1.1rem .7rem; border-bottom:1px solid var(--trait)}
#barre .marque{
  font-family:var(--sans); font-size:.66rem; letter-spacing:.22em;
  text-transform:uppercase; color:var(--or); font-weight:700;
}
#barre .marque span{color:var(--encre-3)}
#recherche{
  width:100%; margin-top:.7rem; padding:.5rem .65rem; border-radius:7px;
  border:1px solid var(--trait-2); background:var(--fond); color:var(--encre);
  font-family:var(--sans); font-size:.82rem;
}
#recherche:focus{outline:2px solid var(--or); outline-offset:1px}
#indice{font-family:var(--sans); font-size:.66rem; color:var(--encre-3); margin:.45rem 0 0}
#plan{overflow-y:auto; padding:.8rem .6rem 3rem; flex:1}
#plan ul{list-style:none; margin:0; padding:0}
#plan a{
  display:block; padding:.3rem .6rem; border-radius:6px; text-decoration:none;
  color:var(--encre-2); font-family:var(--sans); font-size:.8rem; line-height:1.35;
}
#plan a:hover{background:var(--fond-3); color:var(--encre)}
#plan .nav-tome{margin-top:.85rem}
#plan .nav-tome > a{
  color:var(--or); font-weight:700; font-size:.74rem; letter-spacing:.07em;
  text-transform:uppercase;
}
#plan .nav-chapitre > a{padding-left:1.1rem; border-left:1px solid var(--trait)}
#plan a.actif{background:var(--fond-3); color:var(--or-clair); font-weight:600}
.resultat-niveau-3 a{padding-left:1.1rem !important}

/* ---------- sommaire imprimé ---------- */
.sommaire{
  max-width:var(--largeur); margin:0 auto; padding:3rem 0 1rem;
  border-bottom:1px solid var(--trait);
}
.sommaire h2{
  font-size:.72rem; letter-spacing:.28em; text-transform:uppercase; color:var(--or);
  border:0; margin:0 0 1.6rem; padding:0;
}
.sommaire ol{list-style:none; margin:0; padding:0; counter-reset:tome}
.sommaire .s-tome{margin:1.5rem 0 .4rem}
.sommaire .s-tome a{
  font-family:var(--sans); font-weight:700; font-size:.95rem; color:var(--encre);
  text-decoration:none; display:block; border-bottom:1px solid var(--trait);
  padding-bottom:.3rem;
}
.sommaire .s-chap a{
  font-family:var(--sans); font-size:.82rem; color:var(--encre-2); text-decoration:none;
  display:block; padding:.12rem 0 .12rem 1.1rem;
}
.sommaire a:hover{color:var(--or)}

/* ---------- boutons flottants ---------- */
.commandes{
  position:fixed; right:1rem; top:1rem; z-index:30; display:flex; gap:.4rem;
}
.commandes button{
  font-family:var(--sans); font-size:.72rem; font-weight:600; cursor:pointer;
  background:var(--fond-2); color:var(--encre-2); border:1px solid var(--trait-2);
  border-radius:7px; padding:.42rem .6rem;
}
.commandes button:hover{color:var(--or); border-color:var(--or)}
#haut{position:fixed; right:1rem; bottom:1rem; z-index:30; opacity:0; pointer-events:none;
  transition:opacity .2s; font-family:var(--sans); font-size:.9rem; cursor:pointer;
  background:var(--fond-2); color:var(--encre-2); border:1px solid var(--trait-2);
  border-radius:50%; width:2.4rem; height:2.4rem}
#haut.visible:hover{color:var(--or); border-color:var(--or)}
#haut.visible{opacity:1; pointer-events:auto}

/* ---------- corps ---------- */
main{margin-left:19rem; padding:0 2.5rem 8rem; transition:margin .18s ease}
.page{max-width:var(--largeur); margin:0 auto}
body.plein #barre{transform:translateX(-100%)}
body.plein main{margin-left:0}

/* ---------- couverture ---------- */
.couverture{
  max-width:var(--largeur); margin:0 auto; padding:5rem 0 4rem; text-align:center;
  border-bottom:1px solid var(--trait);
}
.couverture .filet{
  width:64px; height:3px; background:var(--or); margin:0 auto 2rem;
}
.couverture h1{
  font-size:clamp(2.4rem,6vw,3.6rem); line-height:1.08; margin:0 0 .6rem;
  border:0; padding:0; letter-spacing:-.01em;
}
.couverture h1::before{content:none}
.couverture .sous{
  font-family:var(--sans); font-size:.78rem; letter-spacing:.28em;
  text-transform:uppercase; color:var(--or); margin:0 0 2.2rem;
}
.couverture .accroche{color:var(--encre-2); font-size:1.02rem; max-width:34rem; margin:0 auto}
.couverture .meta{
  font-family:var(--sans); font-size:.7rem; color:var(--encre-3);
  margin-top:2.6rem; letter-spacing:.1em; text-transform:uppercase;
}

/* ---------- titres ---------- */
h1,h2,h3,h4{font-family:var(--sans); line-height:1.2; letter-spacing:-.01em}
h1{
  font-size:2.1rem; margin:4.5rem 0 1.6rem; padding-top:2.6rem;
  border-top:3px solid var(--or); position:relative; scroll-margin-top:1rem;
}
h1::before{
  content:attr(data-tome); position:absolute; top:1.1rem; left:0;
  font-size:.68rem; letter-spacing:.28em; text-transform:uppercase; color:var(--or);
  font-weight:700;
}
h2{
  font-size:1.42rem; margin:3.2rem 0 1rem; padding-bottom:.4rem;
  border-bottom:1px solid var(--trait); scroll-margin-top:1rem;
}
h3{font-size:1.06rem; margin:2.3rem 0 .6rem; color:var(--or-clair); scroll-margin-top:1rem}
html[data-theme="light"] h3{color:var(--or)}
h4{
  font-size:.82rem; text-transform:uppercase; letter-spacing:.13em;
  margin:1.7rem 0 .5rem; color:var(--encre-3);
}
p{margin:.75rem 0}
a{color:var(--bleu)}
a:hover{color:var(--or)}
hr{border:0; border-top:1px solid var(--trait); margin:2.6rem 0}
strong{color:var(--encre)}
em{color:var(--encre-2)}

/* accroche en italique sous une entrée de dictionnaire */
h3 + p em:only-child{
  display:block; color:var(--encre-2); font-size:.95rem; border-left:2px solid var(--or);
  padding-left:.8rem; margin:.2rem 0 .9rem;
}

/* ---------- listes à étiquettes ---------- */
ul,ol{margin:.7rem 0; padding-left:1.25rem}
li{margin:.32rem 0}
li > strong:first-child{
  font-family:var(--sans); font-size:.7rem; letter-spacing:.09em; text-transform:uppercase;
  color:var(--or); font-weight:700;
}
.encadre li > strong:first-child{color:inherit; letter-spacing:.06em}

/* ---------- encadrés ---------- */
.encadre{
  margin:1.3rem 0; padding:.85rem 1.1rem; border-radius:9px;
  border:1px solid var(--trait-2); border-left-width:4px; background:var(--fond-2);
  font-size:.95rem;
}
.encadre > :first-child{margin-top:0}
.encadre > :last-child{margin-bottom:0}
.encadre-titre{
  font-family:var(--sans); font-size:.68rem; font-weight:700; letter-spacing:.15em;
  text-transform:uppercase; margin:0 0 .45rem !important;
}
.encadre--retenir{border-left-color:var(--vert)}
.encadre--retenir .encadre-titre{color:var(--vert)}
.encadre--erreur{border-left-color:var(--rouge)}
.encadre--erreur .encadre-titre{color:var(--rouge)}
.encadre--danger{border-left-color:var(--rouge); background:color-mix(in srgb,var(--rouge) 9%,var(--fond-2))}
.encadre--danger .encadre-titre{color:var(--rouge)}
.encadre--piege{border-left-color:var(--orange)}
.encadre--piege .encadre-titre{color:var(--orange)}
.encadre--memo{border-left-color:var(--violet); background:color-mix(in srgb,var(--violet) 8%,var(--fond-2))}
.encadre--memo .encadre-titre{color:var(--violet)}
.encadre--memo p{font-family:var(--sans); font-size:.9rem}
.encadre--astuce{border-left-color:var(--bleu)}
.encadre--astuce .encadre-titre{color:var(--bleu)}
.encadre--pro{border-left-color:var(--cyan)}
.encadre--pro .encadre-titre{color:var(--cyan)}
.encadre--resume{border-left-color:var(--or); background:color-mix(in srgb,var(--or) 8%,var(--fond-2))}
.encadre--resume .encadre-titre{color:var(--or)}

/* ---------- tableaux ---------- */
table{
  width:100%; border-collapse:collapse; margin:1.2rem 0; font-family:var(--sans);
  font-size:.83rem; display:block; overflow-x:auto;
}
th,td{border:1px solid var(--trait); padding:.45rem .6rem; text-align:left; vertical-align:top}
th{
  background:var(--fond-3); font-size:.68rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--encre-2); font-weight:700; white-space:nowrap;
}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--fond-2) 60%,transparent)}

/* ---------- code et schémas ---------- */
code{
  font-family:var(--mono); font-size:.86em; background:var(--fond-3);
  padding:.1em .35em; border-radius:4px; color:var(--or-clair);
}
html[data-theme="light"] code{color:var(--or)}
pre.schema{
  font-family:var(--mono); background:var(--fond-2); border:1px solid var(--trait);
  border-radius:9px; padding:.9rem 1rem; overflow-x:auto; margin:1.2rem 0;
  font-size:.76rem; line-height:1.42; color:var(--encre-2);
}
pre.schema code{background:none; padding:0; color:inherit; font-size:inherit}
pre.schema--large{font-size:.7rem}

blockquote{
  margin:1.2rem 0; padding:.2rem 0 .2rem 1.1rem; border-left:3px solid var(--or);
  color:var(--encre-2); font-style:italic;
}

/* ---------- responsive ---------- */
@media (max-width:1080px){
  #barre{transform:translateX(-100%); box-shadow:0 0 40px rgba(0,0,0,.4)}
  body.menu #barre{transform:translateX(0)}
  main{margin-left:0; padding:0 1.1rem 6rem}
  .commandes{top:.6rem; right:.6rem}
}

/* ---------- impression ---------- */
@media print{
  :root{
    --fond:#fff; --fond-2:#fff; --fond-3:#f2f2f2;
    --encre:#000; --encre-2:#333; --encre-3:#666;
    --trait:#bbb; --trait-2:#999; --or:#8a6000;
  }
  body{font-size:10.5pt; background:#fff; color:#000}
  #barre,.commandes,#haut{display:none !important}
  main{margin:0; padding:0}
  .page,.couverture{max-width:none}
  .couverture{padding:38mm 0 0; border:0; page-break-after:always}
  .couverture h1{font-size:30pt; page-break-before:avoid}
  .couverture .accroche{font-size:11pt}
  h1{page-break-before:always; page-break-after:avoid}
  .sommaire{page-break-before:always}
  .sommaire + main h1:first-of-type{page-break-before:always}
  h2,h3,h4{page-break-after:avoid}
  .encadre,pre.schema,table,li{page-break-inside:avoid}
  a{color:#000; text-decoration:none}
  @page{margin:16mm 14mm}
}
"""

JS = r"""
(function(){
  var plan = document.getElementById('plan');
  var champ = document.getElementById('recherche');
  var indice = document.getElementById('indice');
  var navOriginal = plan.innerHTML;
  var INDEX = window.__INDEX__ || [];

  function sansAccent(s){
    return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  }

  function chercher(q){
    if(!q.trim()){ plan.innerHTML = navOriginal; indice.textContent = REPERE; brancher(); return; }
    var mots = sansAccent(q).split(/\s+/).filter(Boolean);
    var trouves = INDEX.filter(function(e){
      var t = sansAccent(e.t);
      return mots.every(function(m){ return t.indexOf(m) !== -1; });
    }).slice(0,120);
    if(!trouves.length){
      plan.innerHTML = '<p style="font-family:var(--sans);font-size:.78rem;color:var(--encre-3);padding:.6rem">Aucun terme trouvé.</p>';
      indice.textContent = '0 résultat';
      return;
    }
    plan.innerHTML = '<ul class="nav-racine">' + trouves.map(function(e){
      return '<li class="resultat-niveau-' + e.n + '"><a href="#' + e.i + '">' +
             e.t.replace(/&/g,'&amp;').replace(/</g,'&lt;') + '</a></li>';
    }).join('') + '</ul>';
    indice.textContent = trouves.length + ' résultat' + (trouves.length>1?'s':'');
    brancher();
  }

  var REPERE = INDEX.length + ' entrées indexées';
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

  // thème
  var btnTheme = document.getElementById('theme');
  var memo = localStorage.getItem('manuel-theme');
  if(memo){ document.documentElement.setAttribute('data-theme', memo); }
  btnTheme.addEventListener('click', function(){
    var actuel = document.documentElement.getAttribute('data-theme');
    if(!actuel){
      actuel = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }
    var suivant = actuel === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', suivant);
    localStorage.setItem('manuel-theme', suivant);
  });

  document.getElementById('plein').addEventListener('click', function(){
    if(window.innerWidth <= 1080){ document.body.classList.toggle('menu'); }
    else { document.body.classList.toggle('plein'); }
  });

  // position de lecture + titre actif
  var titres = Array.prototype.slice.call(document.querySelectorAll('main h1, main h2'));
  var haut = document.getElementById('haut');
  function surDefilement(){
    haut.classList.toggle('visible', window.scrollY > 900);
    if(champ.value.trim()) return;
    var courant = null;
    for(var i=0;i<titres.length;i++){
      if(titres[i].getBoundingClientRect().top < 120){ courant = titres[i]; } else { break; }
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
    localStorage.setItem('manuel-position', String(window.scrollY));
  }
  window.addEventListener('scroll', surDefilement, {passive:true});
  surDefilement();

  haut.addEventListener('click', function(){ window.scrollTo({top:0,behavior:'smooth'}); });

  // reprise de lecture (sauf si une ancre est demandée)
  if(!location.hash){
    var pos = parseInt(localStorage.getItem('manuel-position') || '0', 10);
    if(pos > 400){ window.scrollTo(0, pos); }
  }
})();
"""

GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manuel de Trading Personnel</title>
<meta name="description" content="Manuel de référence : dictionnaire, concepts, macroéconomie, checklists, règles d'or, erreurs, aide-mémoire et antisèche.">
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
    <p class="marque">Manuel de trading <span>· personnel</span></p>
    <input id="recherche" type="search" placeholder="Chercher un terme… (touche /)" autocomplete="off">
    <p id="indice"></p>
  </header>
  <nav id="plan">{nav}</nav>
</aside>

<div class="couverture">
  <div class="filet"></div>
  <p class="sous">Référence permanente</p>
  <h1>Manuel de Trading Personnel</h1>
  <p class="accroche">Dictionnaire, concepts, macroéconomie, checklists, règles d'or,
  erreurs, aide-mémoire et antisèche. Huit tomes, un seul livre : celui qu'on relit
  avant d'ouvrir une position.</p>
  <p class="meta">Version {version} · {date} · {entrees} entrées indexées</p>
</div>

{sommaire}

<main><div class="page">
{corps}
</div></main>

<script>window.__INDEX__ = {index};</script>
<script>{js}</script>
</body>
</html>
"""


def numeroter_tomes(corps: str, plan: list[dict]) -> str:
    """Ajoute l'exergue « TOME N » au-dessus de chaque h1."""
    compteur = [0]

    def traiter(m: re.Match) -> str:
        titre = m.group(2)
        brut = re.sub(r"<[^>]+>", "", titre)
        if re.match(r"\s*(Tome|Préface|Avant|Index|Comment)", brut, re.I):
            etiquette = brut.split("—")[0].strip()
        else:
            compteur[0] += 1
            etiquette = f"Tome {compteur[0]}"
        return f'<h1 id="{m.group(1)}" data-tome="{html.escape(etiquette)}">{titre}</h1>'

    return re.sub(r'<h1 id="([^"]+)">(.*?)</h1>', traiter, corps, flags=re.S)


def main() -> int:
    fichiers = sorted(SOURCES.glob("*.md"))
    if not fichiers:
        sys.exit(f"Aucune source trouvée dans {SOURCES}")

    source = "\n\n".join(f.read_text(encoding="utf-8") for f in fichiers)
    corps = rendre(source)
    corps, plan = ancrer(corps)
    corps = numeroter_tomes(corps, plan)

    page = GABARIT.format(
        css=CSS,
        js=JS,
        nav=construire_nav(plan),
        sommaire=construire_sommaire(plan),
        corps=corps,
        index=index_js(plan),
        version=VERSION,
        date=date.today().strftime("%d/%m/%Y"),
        entrees=len(plan),
    )
    SORTIE.write_text(page, encoding="utf-8")

    tomes = sum(1 for e in plan if e["n"] == 1)
    chapitres = sum(1 for e in plan if e["n"] == 2)
    termes = sum(1 for e in plan if e["n"] == 3)
    mots = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", corps)))
    print(f"{SORTIE.relative_to(RACINE.parent)} — {SORTIE.stat().st_size/1024:.0f} Ko")
    print(f"{len(fichiers)} sources · {tomes} tomes · {chapitres} chapitres · "
          f"{termes} entrées · ~{mots} mots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
