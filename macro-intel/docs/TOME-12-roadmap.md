# Tome 12 — Roadmap produit & évolutions

> **Statut : ✅ Rédigé** · Clôture du premier cycle de tomes.

---

## 1. Où en est le produit

**Livré et fonctionnel (V1)** :
plateforme d'analyse macro assistée par IA — ingestion multi-sources avec repli
gracieux, moteur d'analyse (régimes, courbe, corrélations, scores par actif),
couche IA avec garde-fous anti-signal, API `/v1` + temps réel, application
sombre responsive, intégration TradingView indépendante, 79 tests, CI, Docker.

**Socle 100 % gratuit** : fonctionne sans aucune clé API et sans réseau (mode
dégradé honnêtement signalé). Les clés (FRED, EIA, Finnhub, Anthropic) enrichissent
sans être requises.

## 2. Prochaines évolutions, par valeur décroissante

### Priorité 1 — activer les données réelles (effort : minutes)
Renseigner `FRED_API_KEY` (gratuite) transforme immédiatement la profondeur :
CPI, NFP, PIB, chômage, courbe complète, VIX, historiques de corrélation.
Puis `EIA_API_KEY` (énergie) et `FINNHUB_API_KEY` (news).
**C'est le meilleur rapport valeur/effort du projet.**

### Priorité 2 — brancher votre indicateur (effort : ~30 min)
Remplacer les placeholders de `signal_bridge.pine` par vos sorties réelles
(SMC, liquidité, VWAP, structure) et créer l'alerte webhook. Vous recevez alors
les verdicts « renforcé / avertissement » sur vos signaux réels.

### Priorité 3 — persistance de production
Basculer `DATABASE_URL` vers PostgreSQL + TimescaleDB (Tome 3), migrations
Alembic, agrégats continus. Débloque : graphiques historiques, validation
historique des scores, rétention maîtrisée.

### Priorité 4 — enrichissements analytiques
- Minutes du FOMC : parsing + résumé IA (Tome 2 §3.3).
- Nowcasting PIB sur séries FRED (remplace le proxy actuel).
- Matrice de corrélation complète (toutes paires) avec carte de chaleur.
- Alertes de contexte : notification quand le régime **change**.

### Priorité 5 — confort
- Cache Redis des analyses IA (frugalité).
- Briefing quotidien programmé (Telegram/e-mail).
- Migration Next.js si le besoin de composants riches apparaît (ADR-009).

## 3. Ce que le produit ne fera jamais
Par conception, et de façon testée : ouvrir une position, émettre un signal
d'achat ou de vente, donner des niveaux d'entrée/SL/TP, ou se substituer au
jugement du trader. Toute évolution future doit passer les tests de
`test_guardrails.py`.

## 4. Registre complet des décisions (ADR)

| ADR | Décision | Tome |
|-----|----------|------|
| 001 | Monolithe modulaire plutôt que microservices | 1 |
| 002 | PostgreSQL + TimescaleDB + pgvector | 1 / 3 |
| 003 | Next.js (cible V2) | 1 / 7 |
| 004 | Redis cache + pub/sub ; APScheduler d'abord | 1 / 10 |
| 005 | LLM optionnel + repli déterministe | 1 / 5 |
| 006 | FRED comme colonne vertébrale des séries macro | 2 |
| 007 | Résilience : multi-source, staleness, circuit breaker | 2 |
| 008 | Cadence par connecteur + fenêtres de publication | 2 |
| 009 | Application autoportante en V1 (révision de l'ADR-003) | 7 |

## 5. Bilan des tomes

| Tome | Sujet | État |
|:----:|-------|------|
| 0 | Cahier des charges & Vision | ✅ |
| 1 | Architecture & Fondations | ✅ |
| 2 | Ingestion & Sources | ✅ |
| 3 | Modèle de données & Stockage | ✅ spécifié (implémentation V2) |
| 4 | Analyse & Corrélations | ✅ implémenté |
| 5 | Couche IA | ✅ implémenté |
| 6 | API & Backend | ✅ implémenté |
| 7 | Frontend & Design | ✅ implémenté |
| 8 | Intégration TradingView | ✅ implémenté |
| 9 | Sécurité & Conformité | ✅ |
| 10 | DevOps & Observabilité | ✅ |
| 11 | Qualité & Tests | ✅ implémenté |
| 12 | Roadmap | ✅ |
