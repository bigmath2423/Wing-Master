# 📚 Documentation de la plateforme — MacroLens

> **MacroLens** est la plateforme d'analyse macroéconomique assistée par IA
> décrite dans le cahier des charges maître (Tome 0). Elle **assiste** le trader ;
> elle ne décide jamais à sa place.

Cette documentation est organisée en **tomes**. Chaque tome est une spécification
professionnelle autonome, suffisamment détaillée pour être implémentée sans zone
d'ombre. **Aucun tome ne casse un module défini précédemment.**

## Les tomes

| Tome | Titre | Statut | Rôle |
|:----:|-------|:------:|------|
| **0** | [Cahier des charges & Vision](TOME-00-cahier-des-charges.md) | ✅ | Principes, périmètre, garde-fous, glossaire — le contrat maître |
| **1** | [Architecture globale & Fondations](TOME-01-architecture.md) | ✅ | Macro-architecture, stack comparée, modules, migration |
| **2** | [Ingestion & Sources de données](TOME-02-ingestion-sources.md) | ✅ | Catalogue des sources, contrat de connecteur, résilience, coûts |
| **3** | [Modèle de données & Stockage](TOME-03-modele-donnees-stockage.md) | ✅ | Schéma, TimescaleDB, pgvector, migrations, rétention |
| **4** | [Analyse macro & Corrélations](TOME-04-analyse-correlations.md) | ✅ 🛠 | Régimes, courbe des taux, corrélations, scoring |
| **5** | [Couche Intelligence Artificielle](TOME-05-couche-ia.md) | ✅ 🛠 | Explication, scénarios, confiance, **garde-fous anti-signal** |
| **6** | [API & Services backend](TOME-06-api-backend.md) | ✅ 🛠 | Surface `/v1`, temps réel, validation, qualité des données |
| **7** | [Frontend & Design system](TOME-07-frontend-design.md) | ✅ 🛠 | Interface sombre, 6 onglets, responsive, accessibilité |
| **8** | [Intégration TradingView](TOME-08-integration-tradingview.md) | ✅ 🛠 | Indépendance stricte, fusion bornée, webhook |
| **9** | [Sécurité & Conformité](TOME-09-securite-conformite.md) | ✅ | Modèle de menace, secrets, RGPD, avertissements |
| **10** | [DevOps & Observabilité](TOME-10-devops-observabilite.md) | ✅ | CI/CD, Docker durci, logs, déploiement, montée en charge |
| **11** | [Qualité & Tests](TOME-11-qualite-tests.md) | ✅ 🛠 | 79 tests, validation de l'analyse, calibration |
| **12** | [Roadmap & évolutions](TOME-12-roadmap.md) | ✅ | Priorités, registre ADR complet, bilan |

Légende : ✅ rédigé · 🛠 implémenté dans le code.

## Conventions
- **Langue** : français (identifiants techniques en anglais).
- **Diagrammes** : Mermaid (rendu natif sur GitHub).
- **Décisions structurantes** : tracées en ADR (contexte → options comparées →
  décision → justification). Registre complet dans le [Tome 12](TOME-12-roadmap.md#4-registre-complet-des-décisions-adr).

## Principe intangible (rappelé dans chaque tome)

> La plateforme **centralise, analyse, explique et met en scénarios**.
> Elle **ne donne jamais** d'ordre d'achat/vente et **n'exécute jamais** de position.
> La décision finale appartient **toujours** au trader.
>
> Ce n'est pas qu'une mention légale : c'est une contrainte **technique**,
> implémentée (`app/ai/guardrails.py`) et **testée** (`tests/test_guardrails.py`).
