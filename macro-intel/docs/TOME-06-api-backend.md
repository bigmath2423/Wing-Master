# Tome 6 — API & Services backend

> **Statut : ✅ Rédigé & implémenté** · Code : `app/api/`, `app/main.py`.

---

## 1. Principes de conception
- **Versionnement** : la surface applicative vit sous `/v1` ; l'ancienne surface
  (`/macro`, `/tradingview`) est **conservée** pour non-régression.
- **Lecture instantanée** : les endpoints lisent un état en mémoire rafraîchi par
  le scheduler → latence < 200 ms, aucune requête lourde en ligne.
- **Honnêteté des données** : chaque réponse de tableau de bord porte un bloc
  `data_quality` (source, dégradation, volumes) — l'UI ne présente jamais un
  repli comme une donnée réelle.

## 2. Surface `/v1`

| Méthode | Endpoint | Rôle |
|---------|----------|------|
| GET | `/v1/dashboard` | Charge utile complète de l'application |
| GET | `/v1/regime` | Régime dominant + moteurs + confiance |
| GET | `/v1/briefing` | Synthèse de contexte rédigée |
| GET | `/v1/events?priority=` | Événements analysés (filtrable) |
| GET | `/v1/correlations?window=` | Corrélations glissantes |
| GET | `/v1/calendar?importance=&days=` | Calendrier économique à venir |
| GET | `/v1/topics` | Base de mécanismes documentés |
| POST | `/v1/explain?title=` | Analyse d'un événement à la demande |
| POST | `/v1/refresh` | Force un cycle plateforme |
| GET | `/v1/stream` | Flux temps réel (SSE) |

## 3. Surface historique (conservée)
`/macro/latest`, `/macro/{asset}`, `/macro/{asset}/pine`, `/macro/history/{asset}`,
`/macro/stream/sse`, `/macro/refresh`, `/tradingview/webhook`, `/health`, `/docs`.
Vérifiée par `test_api_v1.py::test_legacy_endpoints_still_work`.

## 4. Temps réel (SSE)
Émission **sur changement** (comparaison de `generated_at`) + battement de cœur
(`: keep-alive`), arrêt propre à la déconnexion client, `retry: 5000` pour la
reconnexion, en-têtes anti-buffering (`X-Accel-Buffering: no`).
Choix de SSE plutôt que WebSocket : flux unidirectionnel, reconnexion native,
compatible reverse-proxy — le besoin bidirectionnel n'existe pas.

## 5. Validation & erreurs
Pydantic v2 : `Literal` pour les énumérations, bornes sur les scores, longueurs
minimales. Codes : `401` (secret invalide), `403` (endpoint dev en prod),
`404` (actif inconnu), `422` (validation), `503` (état pas encore prêt).

## 6. Sécurité (détail au Tome 9)
Secret partagé à temps constant sur le webhook, endpoint `/simulate` restreint au
mode développement, avertissement de démarrage si secret par défaut hors dev,
CORS à restreindre en production.

## 7. Definition of Done
- [x] Surface `/v1` complète et documentée (OpenAPI auto).
- [x] Surface historique préservée et testée.
- [x] Temps réel efficace et robuste.
- [x] Qualité des données exposée aux clients.
