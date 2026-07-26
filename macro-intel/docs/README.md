# 📚 Documentation de la plateforme — MacroLens

> **MacroLens** est le nom de travail de la plateforme d'analyse macroéconomique
> assistée par IA décrite dans le cahier des charges maître (Tome 0). Elle
> **assiste** le trader ; elle ne décide jamais à sa place.

Cette documentation est organisée en **tomes**. Chaque tome est une spécification
professionnelle autonome et complète, suffisamment détaillée pour être
implémentée sans zone d'ombre. Un tome n'est ouvert que lorsque le précédent est
validé, et **aucun tome ne casse un module défini précédemment**.

## Feuille de route des tomes

| Tome | Titre | Statut | Rôle |
|:----:|-------|:------:|------|
| **0** | [Cahier des charges & Vision](TOME-00-cahier-des-charges.md) | ✅ Rédigé | Principes, périmètre, garde-fous, glossaire — le contrat maître |
| **1** | [Architecture globale & Fondations](TOME-01-architecture.md) | ✅ Rédigé | Macro-architecture, stack comparée, découpage en modules, sécurité transversale, migration depuis l'existant |
| **2** | [Ingestion & Sources de données](TOME-02-ingestion-sources.md) | ✅ Rédigé | Connecteurs (FRED, BLS, banques centrales, DXY/VIX/yields/courbe, COT, OPEP/EIA, news, GDELT), contrat, normalisation, planification, résilience, coûts |
| **3** | Modèle de données & Stockage | ⏳ À venir | Schéma détaillé, séries temporelles (TimescaleDB), référentiel d'événements, rétention, versioning |
| **4** | Moteur d'analyse macro & Corrélations | ⏳ À venir | Indicateurs, régimes de marché, courbe des taux, corrélations inter-marchés, nowcasting |
| **5** | Couche Intelligence Artificielle | ⏳ À venir | Résumé/explication/scénarios/confiance/priorisation, RAG, garde-fous anti-signal, évaluation, coûts |
| **6** | API & Services backend | ⏳ À venir | Contrats d'API, authentification, temps réel, quotas |
| **7** | Frontend & Design system (UX/UI) | ⏳ À venir | Dark mode, dashboards, responsive, bibliothèque de composants |
| **8** | Intégration TradingView | ⏳ À venir | Indépendance stricte, contexte macro fourni à l'indicateur |
| **9** | Sécurité & Conformité | ⏳ À venir | Cybersécurité, secrets, RGPD, avertissements réglementaires |
| **10** | DevOps, Observabilité & Déploiement | ⏳ À venir | CI/CD, IaC, monitoring, montée en charge, coûts |
| **11** | Qualité, Tests & Backtesting de l'analyse | ⏳ À venir | Stratégie de tests, validation historique des scores |
| **12** | Roadmap produit & évolutions | ⏳ À venir | Priorisation, jalons, vision long terme |

## Conventions documentaires

- **Langue** : français (le code et les identifiants techniques restent en anglais).
- **Diagrammes** : Mermaid (rendu nativement sur GitHub et dans les artifacts).
- **Décisions techniques** : chaque choix structurant est tracé sous forme d'ADR
  (Architecture Decision Record) — contexte, options comparées, décision, justification.
- **Statuts** : ✅ Rédigé · 🚧 En cours · ⏳ À venir · 🔒 Gelé (validé, non modifiable sans nouvel ADR).

## Principe intangible (rappelé dans chaque tome)

> La plateforme **centralise, analyse, explique et met en scénarios**.
> Elle **ne donne jamais** d'ordre d'achat/vente et **n'exécute jamais** de position.
> La décision finale appartient **toujours** au trader.
