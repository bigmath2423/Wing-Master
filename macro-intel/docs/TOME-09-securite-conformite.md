# Tome 9 — Sécurité & Conformité

> **Statut : ✅ Rédigé** · Mesures en place + trajectoire de durcissement.

---

## 1. Modèle de menace (usage individuel, service exposé)

| Menace | Impact | Mitigation en place |
|--------|--------|---------------------|
| Webhook appelé par un tiers | injection de faux signaux | secret partagé, comparaison à temps constant |
| Fuite de clés API | usage frauduleux des quotas | secrets en variables d'environnement, `.env` gitignoré, jamais journalisés |
| Endpoint de test exposé en production | contournement d'authentification | `/tradingview/simulate` refusé hors `development` (403) |
| Secret par défaut oublié | webhook ouvert | avertissement au démarrage hors développement |
| Entrées malformées | erreurs, comportements imprévus | validation Pydantic stricte (types, bornes, `Literal`) |
| Escalade via conteneur | compromission hôte | conteneur **non-root** (uid 10001), `HEALTHCHECK` |
| Injection HTML dans l'UI | XSS | échappement systématique de tout contenu dynamique |
| Dépendances vulnérables | compromission | versions épinglées, audit à planifier (`pip-audit`) |

## 2. Gestion des secrets
Aucun secret dans le code ni dans Git. Configuration 12-factor (`config.py` +
`.env`). En production : gestionnaire de secrets de la plateforme d'hébergement.
Rotation recommandée du `API_SHARED_SECRET` (valeur longue et aléatoire).

## 3. Transport & exposition
HTTPS obligatoire en production (reverse-proxy Caddy/Nginx ou tunnel).
CORS actuellement permissif (`*`) pour le développement → **à restreindre** à
l'origine du frontend en production. Aucune donnée sensible en query string
hors contexte de développement.

## 4. Authentification (trajectoire)
V1 mono-utilisateur : accès protégé par jeton partagé au niveau du reverse-proxy
ou du webhook. V2 multi-utilisateur : OAuth2/OIDC, table `user`, portées par
endpoint. La structure d'API (`/v1`) est prête pour l'ajout d'une dépendance
d'authentification sans rupture.

## 5. Conformité & responsabilité

**Positionnement réglementaire** : MacroLens est un **outil d'information et
d'aide à l'analyse**. Elle ne fournit pas de recommandation personnalisée
d'investissement, n'exécute aucun ordre et ne gère aucun capital.

Mesures :
- Avertissement permanent dans l'UI (pied de page), dans la licence et dans les
  réponses d'API (champ `disclaimer`).
- **Garde-fous anti-signal** techniques (Tome 5) : le produit est structurellement
  incapable d'émettre un ordre — ce n'est pas qu'une mention légale.
- Traçabilité des sources et de la fraîcheur (`data_quality`, `source`).

**RGPD** : seules des données de marché publiques sont stockées. Aucune donnée
personnelle de tiers. La configuration utilisateur se limite à des jetons
techniques. Pas de traceur, pas d'analytique tierce, aucune ressource externe
chargée par l'interface.

## 6. Journalisation
Logs structurés, niveau configurable. **Aucun secret journalisé.** Les échecs de
sources sont journalisés en `WARNING` avec la cause, sans divulguer de clé.

## 7. Definition of Done
- [x] Secrets externalisés et absents du dépôt.
- [x] Webhook authentifié, entrées validées, endpoint de test restreint.
- [x] Conteneur non-root, échappement UI, aucune ressource externe.
- [x] Avertissements et garde-fous techniques en place.
- [ ] À planifier : audit de dépendances automatisé, restriction CORS en prod.
