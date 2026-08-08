# Tome 11 — Qualité, Tests & Validation de l'analyse

> **Statut : ✅ Rédigé & implémenté** · 79 tests, lint et typage sans erreur.

---

## 1. Stratégie de tests

| Niveau | Portée | Fichiers |
|--------|--------|----------|
| **Unitaire — moteur** | scoring, biais, fusion | `test_scoring.py`, `test_bias.py`, `test_fusion.py` |
| **Unitaire — analyse** | régimes, courbe, corrélations | `test_analysis.py` |
| **Unitaire — IA** | analyste, base de mécanismes, priorité, confiance | `test_analyst.py` |
| **Sécurité produit** | garde-fous anti-signal | `test_guardrails.py` |
| **Intégration API** | `/v1`, legacy, validation, non-régression | `test_api_v1.py`, `test_api.py` |
| **Robustesse** | providers hors-ligne, mapping symboles | `test_pipeline.py` |

**79 tests** au total (29 avant la plateforme). Exécution : ~5 s.

## 2. Tests de sécurité produit (les plus importants)
La règle « jamais de signal de trading » est **testée**, pas seulement
documentée :
- 10 formulations prescriptives paramétrées doivent être neutralisées ;
- les niveaux de trading (SL/TP/entrée) doivent être retirés ;
- le texte purement descriptif doit être **préservé intact** (pas de sur-filtrage) ;
- aucune analyse générée ne doit contenir de verbe d'ordre ;
- le briefing exposé par l'API est vérifié de bout en bout.

## 3. Qualité de code
- **ruff** : lint + format (config `pyproject.toml`, règles E/F/I/UP/B/C4/DTZ/SIM).
  Exceptions assumées et documentées : `BLE001` (les providers ne doivent jamais
  lever), `E501` (formules denses), `B008` (idiomes FastAPI).
- **mypy** : 0 erreur sur 40 fichiers.
- **Vérification visuelle réelle** : rendu Chromium desktop + mobile, contrôle des
  erreurs JavaScript et de l'absence de débordement horizontal.

## 4. Validation de l'analyse (au-delà des tests logiciels)

Un score peut être « correct » techniquement et faux économiquement. Deux
niveaux de validation :

1. **Cohérence économique testée** : les relations structurantes sont assertées —
   dollar fort → or pénalisé ; taux réels ↑ → or pénalisé ; risque géopolitique ↑
   → or soutenu ; inflation anticipée ↑ → or soutenu.
2. **Validation historique (à venir)** : les snapshots historisés
   (`macro_snapshot`, Tome 3) permettent de rejouer les scores passés et de
   mesurer leur cohérence avec les mouvements observés — **pour calibrer les
   pondérations**, jamais pour construire une stratégie d'exécution.

> Distinction assumée : on valide la **qualité descriptive** du contexte, pas une
> performance de trading. Mesurer un « taux de réussite » reviendrait à traiter
> la macro comme un signal — ce que le produit refuse par conception.

## 5. Calibration
Les pondérations sont **transparentes et centralisées** (`_CAPS` dans
`scoring.py`, seuils dans `regime.py`, `bias.py`, `fusion.py`), documentées
inline avec leur justification économique, et modifiables sans toucher à
l'architecture.

## 6. Definition of Done
- [x] Couverture des moteurs, de l'IA, de l'API et de la robustesse hors-ligne.
- [x] Règle anti-signal testée à plusieurs niveaux.
- [x] Lint, format et typage sans erreur ; rendu UI vérifié réellement.
- [ ] À planifier : validation historique sur snapshots accumulés.
