"""Convertisseur Markdown -> HTML minimal, sans dépendance externe.

Ce n'est PAS un parseur Markdown complet : il couvre exactement le
sous-ensemble de syntaxe que les modules de ce paquet utilisent pour produire
leurs rapports (titres, gras, italique, code en ligne, citations, listes à
puces, tableaux, blocs de code ```clôturés```, et les rares fragments HTML
bruts insérés par report.py). Un vrai parseur (le paquet `markdown`) resterait
une dépendance de plus pour un simple confort de lecture — celui-ci n'en
ajoute aucune : seule la bibliothèque standard est utilisée.
"""

from __future__ import annotations

import html
import re
import webbrowser
from pathlib import Path

_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\w)_([^_]+)_(?!\w)")
_HEADER = re.compile(r"^(#{1,3})\s+(.*)$")

CSS = """
body { font-family: "Segoe UI", Arial, sans-serif; max-width: 900px; margin: 40px auto;
       padding: 0 20px; line-height: 1.6; color: #1a1a2e; }
h1, h2, h3 { color: #1a1a2e; }
h1 { border-bottom: 2px solid #1a1a2e; padding-bottom: 8px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background: #1a1a2e; color: white; }
tr:nth-child(even) { background: #f5f7fa; }
code { background: #f5f7fa; padding: 2px 6px; border-radius: 4px;
       font-family: Consolas, monospace; }
pre { background: #f5f7fa; padding: 12px; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }
blockquote { border-left: 3px solid #2563eb; margin: 0; padding: 4px 16px;
             color: #5b6472; background: #f5f7fa; }
ul { padding-left: 24px; }
hr { border: none; border-top: 1px solid #ddd; margin: 24px 0; }
"""


def _inline(text: str) -> str:
    """Applique le formatage en ligne (gras, italique, code) après échappement HTML."""
    text = html.escape(text)
    text = _INLINE_CODE.sub(r"<code>\1</code>", text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    return text


def _is_table_row(line: str) -> bool:
    return line.startswith("|") and line.endswith("|") and len(line) > 1


def _is_separator_row(line: str) -> bool:
    cellules = [c.strip() for c in line.strip("|").split("|")]
    return bool(cellules) and all(re.fullmatch(r":?-+:?", c) for c in cellules)


def _table_to_html(rows: list[str]) -> str:
    entete = [c.strip() for c in rows[0].strip("|").split("|")]
    corps = rows[2:] if len(rows) > 1 and _is_separator_row(rows[1]) else rows[1:]
    out = ["<table>",
           "<tr>" + "".join(f"<th>{_inline(c)}</th>" for c in entete) + "</tr>"]
    for r in corps:
        cellules = [c.strip() for c in r.strip("|").split("|")]
        out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cellules) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def markdown_to_html(text: str) -> str:
    """Convertit le sous-ensemble de Markdown produit par ce paquet en HTML."""
    lines = text.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)

    while i < n:
        stripped = lines[i].strip()

        if not stripped:
            i += 1
            continue

        # Fragment HTML brut (ex: <details>, <summary>) : recopié tel quel.
        if stripped.startswith("<"):
            out.append(stripped)
            i += 1
            continue

        # Bloc de code ```...```
        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # saute la clôture ```
            out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
            continue

        # Séparateur horizontal
        if stripped in ("---", "***"):
            out.append("<hr>")
            i += 1
            continue

        # Titres
        m = _HEADER.match(stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # Tableau : bloc contigu de lignes |...|
        if _is_table_row(stripped):
            rows = []
            while i < n and _is_table_row(lines[i].strip()):
                rows.append(lines[i].strip())
                i += 1
            out.append(_table_to_html(rows))
            continue

        # Citation : bloc contigu de lignes "> ..."
        if stripped.startswith(">"):
            morceaux = []
            while i < n and lines[i].strip().startswith(">"):
                morceaux.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            out.append("<blockquote><p>" + _inline(" ".join(morceaux)) + "</p></blockquote>")
            continue

        # Liste à puces : bloc contigu de lignes "- ..."
        if stripped.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ul>")
            continue

        # Paragraphe : accumule les lignes jusqu'au prochain bloc ou ligne vide.
        para = [stripped]
        i += 1
        while i < n and lines[i].strip() and not (
                lines[i].strip().startswith(("#", "```", "|", ">", "- "))
                or lines[i].strip() in ("---", "***")):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + _inline(" ".join(para)) + "</p>")

    return "\n".join(out)


def wrap_html(body: str, title: str) -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
            f"<body>{body}</body></html>")


def render_report(md_path: Path, open_browser: bool = True) -> Path:
    """Convertit un rapport .md en .html à côté, et l'ouvre dans le navigateur."""
    texte = Path(md_path).read_text(encoding="utf-8")
    body = markdown_to_html(texte)
    html_out = wrap_html(body, Path(md_path).stem)
    html_path = Path(md_path).with_suffix(".html")
    html_path.write_text(html_out, encoding="utf-8")
    if open_browser:
        webbrowser.open(html_path.resolve().as_uri())
    return html_path
