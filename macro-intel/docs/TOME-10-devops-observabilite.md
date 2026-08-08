# Tome 10 — DevOps, Observabilité & Déploiement

> **Statut : ✅ Rédigé** · Code : `Dockerfile`, `docker-compose.yml`, `Makefile`, `.github/workflows/ci.yml`.

---

## 1. Intégration continue
GitHub Actions sur tout push touchant `macro-intel/` :
`ruff check` → `ruff format --check` → `pytest`.
Localement identique via `make check`. Ajout recommandé : `mypy app` en CI
(déjà sans erreur sur 40 fichiers).

## 2. Conteneurisation
Image `python:3.11-slim`, dépendances en couche séparée (cache Docker),
**utilisateur non-root** (uid 10001), `HEALTHCHECK` sur `/health`,
`.dockerignore` excluant venv/caches/tests/secrets.
`docker compose up --build` suffit à démarrer ; service PostgreSQL prêt à
décommenter pour la production.

## 3. Déploiement recommandé (trader individuel)
VPS 1 vCPU / 1 Go suffisant. Reverse-proxy **Caddy** (HTTPS automatique) devant
Uvicorn. Variables d'environnement injectées par le gestionnaire de secrets de
l'hébergeur. Redémarrage `unless-stopped`.

Pour le webhook TradingView (URL HTTPS publique requise) : domaine + Caddy, ou
tunnel (`cloudflared`) en usage domestique.

## 4. Ordonnancement en production
APScheduler in-process (cycle configurable, `coalesce`, `max_instances=1`).
Passage à Celery/RQ + Redis **seulement si** le parallélisme des connecteurs le
justifie — non requis à l'échelle d'un utilisateur (ADR-004).

## 5. Observabilité
- **Logs structurés** par domaine (`macro.pipeline`, `macro.platform`,
  `macro.providers.*`, `macro.ai.*`) avec cause des replis.
- **Santé** : `/health` (statut, environnement, IA, version).
- **Qualité des données** : bloc `data_quality` dans `/v1/dashboard`
  (dégradation, sources actives, volumes) — observabilité exposée au produit.
- À ajouter : métriques Prometheus par connecteur (durée, succès, fraîcheur) et
  endpoint `/health/ingestion` détaillé (Tome 2 §9).

## 6. Sauvegarde
SQLite : copie du fichier. PostgreSQL : `pg_dump` quotidien + snapshot de volume.
Les agrégats continus Timescale sont reconstructibles. Restauration à tester
périodiquement.

## 7. Montée en charge (si un jour nécessaire)
1. Basculer `DATABASE_URL` vers PostgreSQL + Timescale (aucun changement de code).
2. Ajouter Redis (cache + pub/sub) derrière l'interface prévue.
3. Extraire la couche IA en service si son coût de calcul le justifie
   (frontières de modules déjà posées, Tome 1).

## 8. Definition of Done
- [x] CI verte (lint, format, tests) sur chaque push.
- [x] Image durcie, healthcheck, compose prêt.
- [x] Logs exploitables, santé et qualité des données exposées.
- [ ] À planifier : métriques Prometheus, mypy en CI, test de restauration.
