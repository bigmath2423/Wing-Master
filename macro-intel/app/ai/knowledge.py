"""Base de connaissances macroéconomique (mécanismes de transmission).

Sert de socle **déterministe** à la couche IA : même sans clé LLM, la plateforme
sait expliquer *pourquoi* un événement compte, *quels marchés* il touche et
*par quel mécanisme*. Le LLM, lorsqu'il est disponible, enrichit et nuance ces
explications (il ne les remplace pas).

Chaque thème décrit :
  - `mechanism`  : la chaîne causale économique ;
  - `markets`    : marchés concernés, avec le sens d'impact **historique** ;
  - `scenarios`  : issues possibles, formulées de façon descriptive ;
  - `why`        : pourquoi le sujet est important pour un trader macro.

⚠️ Aucune formulation prescriptive ici : on décrit des régularités observées,
jamais une action à entreprendre.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Topic:
    key: str
    label: str
    why: str
    mechanism: str
    markets: dict[str, str] = field(default_factory=dict)  # marché -> effet historique
    scenarios: list[str] = field(default_factory=list)
    keywords: tuple[str, ...] = ()


# ── Thèmes macro couverts ───────────────────────────────────────
TOPICS: dict[str, Topic] = {
    "inflation": Topic(
        key="inflation",
        label="Inflation (CPI / PCE / PPI)",
        why=(
            "L'inflation détermine la trajectoire des taux directeurs, donc le coût "
            "de l'argent et la valorisation de tous les actifs."
        ),
        mechanism=(
            "Inflation plus forte que prévu → anticipations de politique monétaire "
            "plus restrictive → hausse des rendements nominaux et souvent des taux "
            "réels → soutien du dollar, pression sur les actifs longue duration."
        ),
        markets={
            "or": "ambigu : couverture contre l'inflation, mais pénalisé si les taux réels montent",
            "dollar": "haussier si cela renforce les anticipations de resserrement",
            "obligations": "baissier sur les prix (hausse des rendements)",
            "indices": "baissier, surtout sur les valeurs de croissance",
            "crypto": "baissier à court terme (liquidité plus rare)",
        },
        scenarios=[
            "Publication au-dessus du consensus : anticipations de resserrement renforcées, "
            "taux réels et dollar orientés à la hausse.",
            "Publication conforme au consensus : réaction limitée, l'attention se déplace "
            "vers la composante sous-jacente (cœur) et les services.",
            "Publication en dessous du consensus : anticipations d'assouplissement, "
            "détente des taux réels, contexte historiquement porteur pour les actifs longs.",
        ],
        keywords=("cpi", "inflation", "pce", "ppi", "prix à la consommation", "core"),
    ),
    "rates": Topic(
        key="rates",
        label="Taux directeurs & politique monétaire",
        why=(
            "Le taux directeur est le prix de référence de la liquidité mondiale : il "
            "irrigue toutes les classes d'actifs."
        ),
        mechanism=(
            "Décision ou discours plus restrictif (hawkish) → hausse des taux réels → "
            "coût d'opportunité accru pour les actifs sans rendement → dollar soutenu. "
            "Plus accommodant (dovish) → mécanisme inverse."
        ),
        markets={
            "or": "baissier si les taux réels montent, haussier s'ils se détendent",
            "dollar": "haussier si restrictif, baissier si accommodant",
            "indices": "haussier si accommodant (valorisations soutenues)",
            "crypto": "très sensible à la liquidité : haussier si accommodant",
        },
        scenarios=[
            "Ton plus restrictif qu'attendu : taux réels en hausse, dollar soutenu, "
            "pression sur les actifs sans rendement.",
            "Ton conforme aux attentes : la réaction dépend surtout des projections "
            "et de la conférence de presse.",
            "Ton plus accommodant qu'attendu : détente des taux réels, contexte "
            "historiquement favorable aux actifs de duration et à l'or.",
        ],
        keywords=(
            "fomc",
            "fed",
            "bce",
            "ecb",
            "taux directeur",
            "hawkish",
            "dovish",
            "rate hike",
            "rate cut",
            "minutes",
            "powell",
            "lagarde",
        ),
    ),
    "employment": Topic(
        key="employment",
        label="Emploi (NFP, chômage, salaires)",
        why=(
            "Le marché du travail conditionne la consommation et les salaires, donc "
            "l'inflation future et la marge de manœuvre des banques centrales."
        ),
        mechanism=(
            "Emploi robuste → pressions salariales → inflation persistante → "
            "politique monétaire restrictive plus longtemps. Emploi qui se dégrade → "
            "anticipations d'assouplissement, mais risque de ralentissement."
        ),
        markets={
            "dollar": "haussier si l'emploi surprend positivement",
            "or": "baissier à court terme si les taux réels montent",
            "indices": "ambigu : bonne nouvelle économique, mauvaise nouvelle pour les taux",
        },
        scenarios=[
            "Créations d'emplois nettement supérieures au consensus : anticipations de "
            "taux plus élevés plus longtemps.",
            "Publication proche du consensus : attention portée au taux de chômage et au salaire horaire.",
            "Nette décélération : anticipations d'assouplissement, mais vigilance sur "
            "le scénario de ralentissement.",
        ],
        keywords=("nfp", "nonfarm", "emploi", "chômage", "unemployment", "payroll", "jobless", "salaire"),
    ),
    "growth": Topic(
        key="growth",
        label="Croissance (PIB, PMI)",
        why="La croissance détermine les bénéfices, la demande de matières premières et l'appétit pour le risque.",
        mechanism=(
            "Activité qui accélère → demande de matières premières et appétit pour le "
            "risque en hausse. Activité qui ralentit → recherche d'actifs défensifs."
        ),
        markets={
            "indices": "haussier si la croissance surprend positivement",
            "pétrole": "haussier (demande industrielle)",
            "or": "haussier en cas de crainte de récession (valeur refuge)",
        },
        scenarios=[
            "Activité au-dessus des attentes : contexte de type risk-on, matières "
            "premières industrielles soutenues.",
            "Activité en ligne : consolidation, l'attention reste sur l'inflation.",
            "Contraction : rotation vers les actifs défensifs, anticipations d'assouplissement monétaire.",
        ],
        keywords=("pib", "gdp", "pmi", "ism", "croissance", "récession", "recession"),
    ),
    "geopolitics": Topic(
        key="geopolitics",
        label="Géopolitique (conflits, sanctions, crises)",
        why=(
            "Les chocs géopolitiques créent une prime de risque immédiate et peuvent "
            "perturber l'offre d'énergie et de métaux."
        ),
        mechanism=(
            "Montée des tensions → demande d'actifs refuges (or, dollar, obligations "
            "d'État) et prime de risque sur l'énergie → hausse de la volatilité (VIX)."
        ),
        markets={
            "or": "haussier (valeur refuge historique)",
            "pétrole": "haussier si l'offre est menacée",
            "indices": "baissier (aversion au risque)",
            "vix": "haussier (prime de volatilité)",
        },
        scenarios=[
            "Escalade : prime de risque durable, or et énergie soutenus, volatilité élevée.",
            "Statu quo tendu : la prime de risque s'érode progressivement.",
            "Désescalade : reflux de la prime de risque, retour de l'appétit pour le risque.",
        ],
        keywords=(
            "guerre",
            "war",
            "conflit",
            "conflict",
            "sanction",
            "attaque",
            "attack",
            "invasion",
            "crise",
            "crisis",
            "militaire",
            "géopolitique",
        ),
    ),
    "energy": Topic(
        key="energy",
        label="Énergie (OPEP, stocks de pétrole)",
        why="L'énergie est un intrant de l'inflation : elle relie matières premières et politique monétaire.",
        mechanism=(
            "Offre restreinte (quotas OPEP, stocks en baisse) → hausse du brut → "
            "inflation importée → contrainte supplémentaire pour les banques centrales."
        ),
        markets={
            "pétrole": "haussier si les stocks baissent ou si l'OPEP réduit sa production",
            "inflation": "haussier (effet de second tour)",
            "indices": "baissier si le choc énergétique est marqué",
        },
        scenarios=[
            "Stocks en forte baisse / réduction de production : tension sur les prix "
            "de l'énergie et pression inflationniste.",
            "Stocks stables : marché équilibré, faible impact macro.",
            "Stocks en hausse / production accrue : détente des prix, effet désinflationniste.",
        ],
        keywords=("opep", "opec", "pétrole", "oil", "crude", "brent", "wti", "stocks", "inventories", "gaz"),
    ),
    "risk_sentiment": Topic(
        key="risk_sentiment",
        label="Appétit pour le risque (VIX, flux)",
        why="Le régime de risque conditionne la corrélation entre les actifs et l'ampleur des mouvements.",
        mechanism=(
            "Hausse de l'aversion au risque → liquidation des actifs risqués, demande "
            "de liquidité en dollar et d'obligations d'État → hausse du VIX."
        ),
        markets={
            "vix": "haussier en phase d'aversion au risque",
            "indices": "baissier",
            "or": "haussier, sauf en cas de crise de liquidité aiguë",
            "crypto": "baissier (actif de risque à bêta élevé)",
        },
        scenarios=[
            "Aversion au risque marquée : corrélations qui convergent, volatilité élevée.",
            "Régime neutre : les facteurs spécifiques dominent.",
            "Appétit pour le risque : actifs cycliques et crypto soutenus.",
        ],
        keywords=(
            "vix",
            "volatilité",
            "volatility",
            "risk-off",
            "risk-on",
            "selloff",
            "krach",
            "panique",
            "rally",
        ),
    ),
    "positioning": Topic(
        key="positioning",
        label="Positionnement (COT, flux)",
        why="Un positionnement extrême rend le marché vulnérable à un dénouement rapide.",
        mechanism=(
            "Positionnement spéculatif très étiré dans un sens → sensibilité accrue aux "
            "nouvelles contraires (effet de débouclage)."
        ),
        markets={
            "or": "un positionnement net long extrême a historiquement précédé des phases de consolidation",
            "dollar": "idem, sensibilité accrue aux surprises",
        },
        scenarios=[
            "Positionnement extrême maintenu : vulnérabilité aux surprises contraires.",
            "Normalisation progressive : réduction de la fragilité technique.",
            "Débouclage rapide : amplification des mouvements.",
        ],
        keywords=(
            "cot",
            "positionnement",
            "positioning",
            "net long",
            "net short",
            "spéculateurs",
            "commitments of traders",
        ),
    ),
    "currency": Topic(
        key="currency",
        label="Dollar & devises (DXY)",
        why="Le dollar est l'unité de compte des matières premières et le baromètre de la liquidité mondiale.",
        mechanism=(
            "Dollar plus fort → matières premières cotées en dollars mécaniquement plus "
            "chères pour les autres devises → pression sur la demande et sur les prix."
        ),
        markets={
            "or": "baissier (relation inverse historique)",
            "matières premières": "baissier",
            "actions émergentes": "baissier (coût de financement en dollars)",
        },
        scenarios=[
            "Dollar qui s'apprécie : pression sur les matières premières et les actifs émergents.",
            "Dollar stable : les facteurs propres à chaque actif reprennent le dessus.",
            "Dollar qui se déprécie : contexte historiquement porteur pour les matières premières.",
        ],
        keywords=("dxy", "dollar", "devise", "currency", "euro", "yen", "forex"),
    ),
    "bonds": Topic(
        key="bonds",
        label="Obligations & courbe des taux",
        why="La courbe des taux résume les anticipations de croissance, d'inflation et de politique monétaire.",
        mechanism=(
            "Courbe qui s'inverse (2 ans au-dessus du 10 ans) → anticipations de "
            "ralentissement. Re-pentification depuis l'inversion → souvent associée aux "
            "phases de transition du cycle."
        ),
        markets={
            "indices": "sensible au niveau des taux longs",
            "or": "piloté par les taux réels plutôt que nominaux",
            "banques": "sensible à la pente (marge d'intermédiation)",
        },
        scenarios=[
            "Aplatissement / inversion : anticipations de ralentissement renforcées.",
            "Pente stable : régime de taux lisible.",
            "Re-pentification : anticipations de croissance ou de prime d'inflation.",
        ],
        keywords=(
            "obligation",
            "bond",
            "yield",
            "rendement",
            "courbe",
            "curve",
            "treasury",
            "10y",
            "2y",
            "inversion",
        ),
    ),
}


def detect_topics(text: str, limit: int = 3) -> list[Topic]:
    """Identifie les thèmes macro évoqués par un texte, par score de mots-clés."""
    lowered = text.lower()
    scored: list[tuple[int, Topic]] = []
    for topic in TOPICS.values():
        hits = sum(1 for kw in topic.keywords if kw in lowered)
        if hits:
            scored.append((hits, topic))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [topic for _, topic in scored[:limit]]


def topic_for_category(category: str) -> Topic:
    """Thème de repli lorsqu'aucun mot-clé ne ressort, d'après la catégorie."""
    mapping = {
        "geopolitics": "geopolitics",
        "central_bank": "rates",
        "release": "inflation",
        "markets": "risk_sentiment",
    }
    return TOPICS[mapping.get(category, "risk_sentiment")]
