"""Génère le mode d'emploi PDF de backtest-agent.

    pip install reportlab
    python3 docs/generer_mode_emploi.py

Le PDF est un binaire : sans ce script il serait impossible à mettre à jour.
Pensez à le régénérer quand la version, la liste des commandes ou les seuils
changent — sinon le mode d'emploi donnera des instructions périmées, ce qui est
pire qu'une documentation absente.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether,
)

SORTIE = str(Path(__file__).resolve().parent / "mode-emploi.pdf")

ENCRE = colors.HexColor("#1a1a2e")
ACCENT = colors.HexColor("#2563eb")
GRIS = colors.HexColor("#5b6472")
GRIS_CLAIR = colors.HexColor("#e4e7ec")
FOND_CODE = colors.HexColor("#f5f7fa")
ALERTE = colors.HexColor("#b45309")
FOND_ALERTE = colors.HexColor("#fef6e7")
VERT = colors.HexColor("#047857")
FOND_VERT = colors.HexColor("#ecfdf5")

base = getSampleStyleSheet()

S = {
    "titre": ParagraphStyle(
        "titre", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=26, leading=30, textColor=ENCRE, spaceAfter=4, alignment=TA_LEFT),
    "soustitre": ParagraphStyle(
        "soustitre", parent=base["Normal"], fontName="Helvetica",
        fontSize=11.5, leading=16, textColor=GRIS, spaceAfter=18),
    "h1": ParagraphStyle(
        "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
        fontSize=15, leading=19, textColor=ENCRE, spaceBefore=18, spaceAfter=7),
    "h2": ParagraphStyle(
        "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
        fontSize=11.5, leading=15, textColor=ACCENT, spaceBefore=12, spaceAfter=5),
    "p": ParagraphStyle(
        "p", parent=base["Normal"], fontName="Helvetica",
        fontSize=9.8, leading=14.5, textColor=ENCRE, spaceAfter=7),
    "puce": ParagraphStyle(
        "puce", parent=base["Normal"], fontName="Helvetica",
        fontSize=9.8, leading=14.5, textColor=ENCRE,
        leftIndent=11, bulletIndent=2, spaceAfter=3.5),
    "code": ParagraphStyle(
        "code", parent=base["Code"], fontName="Courier-Bold",
        fontSize=9, leading=13.5, textColor=ENCRE, spaceAfter=0, spaceBefore=0),
    "sortie": ParagraphStyle(
        "sortie", parent=base["Code"], fontName="Courier",
        fontSize=8.2, leading=11.5, textColor=GRIS, spaceAfter=0, spaceBefore=0),
    "cellule": ParagraphStyle(
        "cellule", parent=base["Normal"], fontName="Helvetica",
        fontSize=8.8, leading=12, textColor=ENCRE),
    "cellule_g": ParagraphStyle(
        "cellule_g", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=8.8, leading=12, textColor=ENCRE),
    "cellule_code": ParagraphStyle(
        "cellule_code", parent=base["Normal"], fontName="Courier-Bold",
        fontSize=8.5, leading=12, textColor=ACCENT),
    "entete": ParagraphStyle(
        "entete", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=8.8, leading=12, textColor=colors.white),
    "note": ParagraphStyle(
        "note", parent=base["Normal"], fontName="Helvetica",
        fontSize=9.2, leading=13.5, textColor=ENCRE),
}


def p(txt, style="p"):
    return Paragraph(txt, S[style])


def puces(items):
    return [Paragraph(t, S["puce"], bulletText="•") for t in items]


def bloc_code(lignes, sortie=False):
    """Bloc de code sur fond gris, non cassable."""
    style = "sortie" if sortie else "code"
    contenu = [[Paragraph(l.replace(" ", "&nbsp;") or "&nbsp;", S[style])]
               for l in lignes]
    t = Table(contenu, colWidths=[163 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FOND_CODE),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT if not sortie else GRIS_CLAIR),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 9)]


def encadre(titre, texte, ton="alerte"):
    fond, bord = (FOND_ALERTE, ALERTE) if ton == "alerte" else (FOND_VERT, VERT)
    corps = f"<b>{titre}</b><br/>{texte}"
    t = Table([[Paragraph(corps, S["note"])]], colWidths=[163 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fond),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, bord),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 3), t, Spacer(1, 10)]


def tableau(entetes, lignes, largeurs, styles_col=None):
    styles_col = styles_col or ["cellule"] * len(entetes)
    data = [[Paragraph(h, S["entete"]) for h in entetes]]
    for ligne in lignes:
        data.append([Paragraph(c, S[styles_col[i]]) for i, c in enumerate(ligne)])
    t = Table(data, colWidths=largeurs, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ENCRE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FOND_CODE]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRIS_CLAIR),
        ("BOX", (0, 0), (-1, -1), 0.5, GRIS_CLAIR),
    ]))
    return [Spacer(1, 3), t, Spacer(1, 11)]


# --------------------------------------------------------------------------
# Contenu
# --------------------------------------------------------------------------
story = []

story.append(p("Backtest Analysis Agent", "titre"))
story.append(p("Mode d'emploi — installation et utilisation<br/>"
               "Agent d'analyse quantitative de backtests de trading", "soustitre"))

story.append(p("1. Ce dont vous avez besoin", "h1"))
story.append(p(
    "L'agent est un outil en ligne de commande écrit en Python. Il analyse un "
    "fichier de résultats de backtest et produit des rapports. Il "
    "<b>fonctionne entièrement hors ligne</b> : aucune clé API n'est nécessaire.", "p"))
story.extend(puces([
    "<b>Python 3.10 ou plus récent</b> — vérifiez avec <font face='Courier-Bold'>python3 --version</font>",
    "<b>Git</b>, pour récupérer le dépôt",
    "Environ 100 Mo d'espace disque (pandas et numpy compris)",
]))
story.append(Spacer(1, 6))

story.append(p("2. Installation en trois commandes", "h1"))
story.extend(bloc_code([
    "git clone https://github.com/bigmath2423/Wing-Master.git",
    "cd Wing-Master/backtest-agent",
    "pip install -e .",
]))
story.append(p(
    "La dernière commande installe la commande <font face='Courier-Bold'>backtest-agent</font> "
    "sur votre système. Vérifiez que tout est en place :", "p"))
story.extend(bloc_code([
    "backtest-agent --version",
    "# → backtest-agent 0.5.0",
]))

story.append(p("Si vous préférez ne rien installer", "h2"))
story.append(p(
    "Installez seulement les deux dépendances de calcul, puis appelez le module "
    "directement depuis le dossier <font face='Courier-Bold'>backtest-agent/</font> :", "p"))
story.extend(bloc_code([
    "pip install pandas numpy",
    "python3 -m backtest_agent.cli --help",
]))

story.append(p("Options supplémentaires (facultatives)", "h2"))
story.extend(tableau(
    ["Commande", "Ce que ça ajoute"],
    [["pip install -e \".[llm]\"",
      "La couche d'interprétation « analyste » par Claude. Sans elle, l'agent "
      "produit un rapport complet mais sans commentaire rédigé."],
     ["pip install -e \".[webhook]\"",
      "Le récepteur d'alertes TradingView en temps réel (suivi forward)."],
     ["pip install -e \".[dev]\"",
      "pytest, pour lancer la suite de tests."]],
    [58 * mm, 105 * mm],
    ["cellule_code", "cellule"]))


# KeepTogether : sans cela le titre peut rester orphelin en bas de page,
# séparé du texte qu'il annonce.
story.append(KeepTogether([
    p("Mettre à jour plus tard", "h2"),
    p("L'installation en mode <font face='Courier-Bold'>-e</font> pointe vers votre "
      "copie du dépôt : une mise à jour se résume à récupérer les nouveautés. "
      "Relancez <font face='Courier-Bold'>pip install -e .</font> seulement si les "
      "dépendances ont changé.", "p"),
    *bloc_code([
        "git pull",
        "backtest-agent --version",
    ]),
]))

story.append(p("Vérifier que l'installation fonctionne", "h2"))
story.append(p(
    "Cette commande génère un jeu de démonstration puis lance l'analyse complète. "
    "Si elle aboutit, tout est opérationnel :", "p"))
story.extend(bloc_code([
    "python3 examples/generate_sample.py -n 300",
    "backtest-agent pipeline examples/sample_trades.csv -o reports/",
]))
story.append(p(
    "Avec l'extra <font face='Courier-Bold'>[dev]</font>, vous pouvez aussi lancer "
    "la suite de tests : <font face='Courier-Bold'>pytest</font>.", "p"))

# ---------------------------------------------------------------- page 2
story.append(p("3. Préparer vos données", "h1"))
story.append(p(
    "L'agent lit un fichier <b>CSV ou JSON</b> contenant une ligne par trade. "
    "Le plus simple est d'exporter depuis TradingView : onglet "
    "<b>Strategy Tester</b> → <b>List of Trades</b> → <b>Export CSV</b>.", "p"))
story.append(p(
    "Les noms de colonnes sont reconnus automatiquement, en français comme en "
    "anglais. Vous n'avez rien à renommer.", "p"))

story.extend(tableau(
    ["Colonne", "Exemple", "Nécessaire ?"],
    [["date / heure", "2025-01-02 14:30", "recommandé"],
     ["actif", "BTCUSDT", "recommandé"],
     ["timeframe", "15m", "recommandé"],
     ["direction", "BUY / SELL", "recommandé"],
     ["prix d'entrée, stop, take profit, sortie", "chiffres", "pour calculer le R"],
     ["résultat", "WIN / LOSS", "déduit du gain si absent"],
     ["gain / perte", "+1.8", "<b>au moins un des deux</b>"],
     ["durée, score de confiance", "45 min, 0.72", "facultatif"],
     ["conditions de marché", "OB, FVG, sweep, VWAP, ATR…", "facultatif"]],
    [56 * mm, 52 * mm, 55 * mm]))

story.append(p(
    "<b>Toute colonne supplémentaire est traitée comme une condition de marché</b> "
    "et entre automatiquement dans l'analyse. Vous pouvez donc ajouter vos propres "
    "indicateurs sans rien configurer.", "p"))

story.append(p("4. Les commandes", "h1"))
story.append(p(
    "Une seule suffit pour commencer — <font face='Courier-Bold'>pipeline</font> "
    "enchaîne tout le cycle et écrit les rapports dans le dossier indiqué :", "p"))
story.extend(bloc_code([
    "backtest-agent pipeline mon_export.csv -o reports/",
]))
story.extend(bloc_code([
    "  Trades analysés           : 400",
    "  Règles confirmées (OOS)   : 2",
    "  Propositions générées     : 2",
    "  Règles robustes (glissant): 0",
    "  Verdict final             : REJETER",
], sortie=True))

story.append(p("Ou étape par étape", "h2"))
story.extend(tableau(
    ["Commande", "Ce qu'elle fait"],
    [["analyze",
      "Le rapport principal : taux de réussite, profit factor, drawdown, analyse "
      "des pertes, meilleurs setups, suggestions et tests A/B."],
     ["walkforward",
      "Vérifie chaque règle sur des données jamais vues (découpe 70 / 30)."],
     ["propose",
      "Traduit les règles validées en <b>code Pine</b> et génère une stratégie "
      "candidate à re-tester sur TradingView."],
     ["validate",
      "Teste la <b>pile de filtres complète</b>, la cohérence entre actifs et "
      "périodes, et la robustesse du drawdown (Monte-Carlo)."],
     ["rolling",
      "Walk-forward <b>glissant</b> : rejoue la validation sur plusieurs fenêtres "
      "successives. La vérification la plus sévère."],
     ["compare",
      "Compare deux exports réels : votre backtest d'origine contre le candidat."],
     ["view",
      "Affiche un rapport <font face='Courier'>.md</font> en page HTML dans le "
      "navigateur — plus lisible que le Bloc-notes (titres, tableaux, gras)."],
     ["pipeline",
      "Enchaîne tout ce qui précède en une seule commande."]],
    [30 * mm, 133 * mm],
    ["cellule_code", "cellule"]))

story.append(p(
    "Chaque commande accepte <font face='Courier-Bold'>-o fichier.md</font> pour "
    "écrire le rapport, <font face='Courier-Bold'>--json fichier.json</font> pour "
    "les données brutes, et <font face='Courier-Bold'>--help</font> pour le détail "
    "des options.", "p"))

story.append(p("5. Activer le commentaire d'analyste (facultatif)", "h1"))
story.append(p(
    "Par défaut, l'agent calcule tout lui-même et rédige un rapport factuel. Avec "
    "une clé API Claude, il ajoute par-dessus une lecture d'analyste rédigée. "
    "<b>Les chiffres restent calculés par le code</b> — l'IA les commente, elle ne "
    "les invente jamais.", "p"))
story.extend(bloc_code([
    "pip install -e \".[llm]\"",
    "export ANTHROPIC_API_KEY=sk-...",
    "backtest-agent analyze mon_export.csv -o rapport.md",
]))

story.append(p("6. Ce qu'il faut comprendre avant de vous en servir", "h1"))
story.append(p(
    "Cet agent est conçu pour se comporter comme un chercheur, pas comme un outil "
    "qui cherche à vous faire plaisir. Trois conséquences concrètes :", "p"))

story.extend(puces([
    "<b>Il peut vous répondre « ne changez rien ».</b> Si aucune règle ne résiste "
    "à la validation, il le dit et ne propose rien. Ce n'est pas une panne : c'est "
    "la bonne réponse quand les données ne contiennent pas de signal fiable.",
    "<b>Il refuse les améliorations trompeuses.</b> Une règle qui fait grimper les "
    "chiffres en supprimant 87 % de vos trades est rejetée, même si le profit "
    "factor paraît excellent.",
    "<b>Il ne modifie jamais votre indicateur.</b> Il génère un fichier "
    "<i>candidat</i> que vous devez re-tester vous-même sur TradingView avant "
    "d'adopter quoi que ce soit.",
]))

story.extend(encadre(
    "La seule étape que l'agent ne peut pas faire à votre place",
    "TradingView est une plateforme fermée : le code Pine ne peut pas être exécuté "
    "localement. Après <font face='Courier'>propose</font>, vous devez copier la "
    "stratégie candidate dans TradingView, relancer le Strategy Tester, exporter le "
    "résultat, puis le comparer :<br/><br/>"
    "<font face='Courier-Bold'>backtest-agent compare origine.csv candidat.csv</font>"
    "<br/><br/>C'est cette comparaison — et elle seule — qui tranche vraiment.",
    ton="ok"))

story.append(p("7. En cas de problème", "h1"))
story.extend(tableau(
    ["Message", "Que faire"],
    [["Fichier introuvable",
      "Vérifiez le chemin. Les chemins relatifs partent du dossier courant."],
     ["Format non supporté",
      "Seuls .csv, .tsv, .txt et .json sont acceptés. Exportez votre fichier "
      "Excel en CSV."],
     ["Fichier de backtest vide",
      "Le fichier ne contient que des en-têtes, sans aucune ligne de trade."],
     ["Impossible de déterminer le résultat",
      "Il manque à la fois la colonne de résultat et celle de gain / perte. "
      "L'agent a besoin d'au moins l'une des deux."],
     ["Pas assez de trades",
      "Les validations exigent un minimum de données : environ 60 trades pour "
      "<font face='Courier'>walkforward</font>, environ 120 pour "
      "<font face='Courier'>rolling</font>."],
     ["commande introuvable",
      "L'installation n'a pas abouti, ou le dossier des scripts n'est pas dans "
      "votre PATH. Utilisez <font face='Courier'>python3 -m backtest_agent.cli</font>."]],
    [50 * mm, 113 * mm],
    ["cellule_g", "cellule"]))

story.append(p(
    "Toutes les erreurs affichent un message explicite et renvoient le code de "
    "sortie 2 — jamais une trace technique.", "p"))

story.append(p("Pour aller plus loin", "h1"))
story.append(p(
    "Le fichier <font face='Courier-Bold'>README.md</font> du dossier "
    "<font face='Courier-Bold'>backtest-agent/</font> détaille l'architecture, le "
    "branchement TradingView (export et webhook), la méthode de validation "
    "walk-forward et la logique anti-sur-optimisation.", "p"))


# --------------------------------------------------------------------------
# Mise en page : pied de page numéroté
# --------------------------------------------------------------------------
def pied_de_page(canvas, doc):
    canvas.saveState()
    largeur, _ = A4
    canvas.setStrokeColor(GRIS_CLAIR)
    canvas.setLineWidth(0.5)
    canvas.line(23 * mm, 15 * mm, largeur - 23 * mm, 15 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRIS)
    canvas.drawString(23 * mm, 10.5 * mm, "Backtest Analysis Agent — mode d'emploi")
    canvas.drawRightString(largeur - 23 * mm, 10.5 * mm, f"page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    SORTIE, pagesize=A4,
    leftMargin=23 * mm, rightMargin=23 * mm,
    topMargin=20 * mm, bottomMargin=22 * mm,
    title="Backtest Analysis Agent — mode d'emploi",
    author="Backtest Analysis Agent",
    subject="Installation et utilisation")

cadre = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="corps")
doc.addPageTemplates([PageTemplate(id="std", frames=[cadre], onPage=pied_de_page)])
doc.build(story)
print(f"PDF écrit : {SORTIE}")
