# XAUUSD SMC Confluence Signals — Guide d'utilisation

**Indicateur professionnel pour TradingView (Pine Script v6)**
Moteur de décision institutionnel basé sur les Smart Money Concepts.

---

## 1. Présentation

Cet indicateur n'envoie **jamais** un signal sur la base d'un seul critère.
Il calcule un **score de confluence sur 100** à partir de 8 familles de critères
institutionnels, applique des **règles éliminatoires**, puis n'affiche un signal
que si la qualité est suffisante.

Il est conçu pour l'**or (XAU/USD)** mais fonctionne sur toutes les paires et
**toutes les unités de temps** (M1 → W1) : les objectifs et le stop s'adaptent
automatiquement à la volatilité (ATR) du timeframe choisi.

**Ce qu'il fournit à chaque signal :**
- Sens (BUY / SELL)
- Score /100 et note (A+, A, B, C)
- Probabilité estimée
- Entrée, Stop Loss et 3 objectifs dynamiques (TP1, TP2, TP Final)
- Suivi du trade en temps réel (TP atteints, passage au Break Even, clôture)
- La liste des confirmations validées ou manquantes

---

## 2. Installation

1. Ouvre **TradingView** → un graphique **XAUUSD**.
2. Menu **Pine Editor** (en bas de l'écran).
3. Colle l'intégralité du code de l'indicateur.
4. Clique sur **« Ajouter au graphique »**.
5. Recommandé : unité de temps **M5** ou **M15**.

> Après chaque mise à jour du code, **supprime** l'ancienne version du graphique
> puis re-ajoute-la, pour repartir sur des réglages propres.

---

## 3. Le moteur de décision (score /100)

Chaque signal potentiel est noté sur 100 selon ce barème :

| Critère | Points |
|---|---|
| Liquidité (sweep + cassure adossée à la liquidité) | 20 |
| Structure de marché (BOS / CHoCH) | 20 |
| Order Block / Fair Value Gap | 15 |
| Wyckoff (phase + figure) | 15 |
| Tendance HTF (timeframe supérieur) | 10 |
| Volume | 5 |
| VWAP | 5 |
| ATR + Session | 10 |
| **Total** | **100** |

### Règles éliminatoires (aucun signal sans ça)
- **Pas de sweep de liquidité récent → aucun signal.**
- **Pas de confirmation structurelle (BOS/CHoCH) récente → aucun signal.**

### Niveaux de décision
| Score | Résultat |
|---|---|
| **≥ 85** | Signal **validé + alerte** TradingView |
| **80 – 84** | Signal affiché, **sans alerte** |
| **< 80** | Aucun signal |

*(Ces deux seuils sont réglables dans les paramètres du Module 6.)*

### Notes et couleurs (lecture immédiate)
| Score | Couleur | Note |
|---|---|---|
| 90 – 100 | 🟢 vert foncé | A+ |
| 85 – 89 | 🟢 vert | A |
| 80 – 84 | 🟡 jaune | B |
| 70 – 79 | 🟠 orange | C |
| < 70 | 🔴 rouge | Aucun signal |

---

## 4. Le panneau à l'écran

L'indicateur affiche un panneau unique **🎯 TRADE SIGNAL**. Deux modes :

### Mode Simple (par défaut)
Affiche l'essentiel : Sens, Score, Probabilité, HTF, Entry, SL, TP1, TP2,
TP Final, État du trade.

### Mode Expert
Affiche **tout** en plus : Statut, Confiance, Trend, RSI, Mode TP,
Score minimum requis, écart de points, et la **checklist complète** des
confirmations (✔ / ✘) :
Sweep · BOS · CHoCH · Order Block · Fair Value Gap · VWAP · Wyckoff ·
Fibonacci · Discount/Premium · Volume.

**Pour changer de mode :** ⚙️ Réglages → *Interface / Panneaux* →
**« Mode d'interface »** → Simple ou Expert.

### Réglages d'affichage (Interface / Panneaux)
- **Mode d'affichage** : Desktop / Mobile / Auto (Mobile = version compacte).
- **Position du panneau** : haut/bas × gauche/droite/milieu.
- **Taille** : Compact / Normal / Large.
- **Transparence** : 0 à 100 % (75 % conseillé pour voir les bougies).

---

## 5. Lire un signal

Quand un signal est validé :

1. **Sens** — 🟢 BUY ou 🔴 SELL.
2. **Score** — ex. `🟢 92/100 • A+`.
3. **Probabilité** — indicateur de confiance dérivé du score.
4. **Entry / Stop Loss** — niveaux calculés automatiquement.
5. **TP1 / TP2 / TP Final** — objectifs dynamiques avec leur ratio Risque/Rendement.

### Suivi automatique du trade (ligne « 📊 État »)
- **🟢 SL actif · en cours** — trade en cours.
- **✅ TP1 atteint · SL au Break Even** — déplace ton stop à l'entrée.
- **✅ TP2 atteint**.
- **🎯 Trade terminé** — TP Final atteint.
- **❌ Stop Loss touché**.
Les TP atteints deviennent **verts** automatiquement.

---

## 6. Le moteur de Take Profit

Les objectifs ne sont **jamais** des valeurs fixes en points. Ils sont :
1. **Ancrés sur l'ATR** → adaptés au timeframe et à la volatilité.
2. **Calés sur la structure la plus proche** (liquidité EQH/EQL, PDH/PDL,
   PWH/PWL, swings, Order Blocks, FVG).

**Mode TP** (paramètre) :
- **Conservateur** — objectifs plus proches.
- **Équilibré** — par défaut.
- **Agressif** — vise la liquidité plus lointaine.

---

## 7. Créer l'alerte TradingView (à faire une fois)

1. Icône **⏰ Alerte** (ou `Alt+A`).
2. **Condition** → sélectionne l'indicateur.
3. Choisis **« Tout appel de fonction alert() »**.
4. Fréquence : **Une fois par barre à la clôture**.
5. Choisis la notification (pop-up, application mobile, e-mail, webhook).
6. **Créer**.

Seuls les signaux **≥ 85 (A+ / A)** déclenchent une alerte. Le message contient
le sens, le score, la confiance et les niveaux Entry / SL / TP1 / TP2 / TP Final
avec leur R:R.

---

## 8. Réglages recommandés

| Réglage | Conseil |
|---|---|
| Timeframe | M5 ou M15 pour l'exécution, contexte H1 |
| Filtre de session | London + New York (évite la session asiatique) |
| Seuil d'alerte | 85 (montez à 90 pour être plus strict) |
| Mode TP | Équilibré |
| Filtre ATR | activé (évite les marchés trop calmes) |

**Horaires des sessions (heure de Paris) :**
- Londres : 09:00 – 18:00
- New York : 14:00 – 23:00
- Kill zones : 08:00–11:00 et 14:30–17:00

---

## 9. Pourquoi il n'y a pas de signal ?

En mode Expert, la checklist montre en direct ce qui manque :
un critère **✔ vert** est validé, un critère **✘ rouge** manque.
La ligne **« Écart »** indique combien de points il manque pour atteindre le seuil.

Exemple : un score de 68 avec `✘ Sweep`, `✘ Discount`, `✘ Fibonacci` signifie
que le setup se construit mais qu'il manque ces confirmations pour être validé.

---

## 10. Gestion du risque (rappel)

- Risque **fixe** par trade recommandé (ex. 1 % du capital), quelle que soit la
  « qualité » ressentie du setup.
- Taille de position = (Capital × % risque) ÷ (distance au Stop Loss).
- À **tester en démo / backtest** avant tout usage en réel.

---

## 11. Avertissement (Disclaimer)

Cet indicateur est un **outil d'aide à la décision**. Il ne constitue **pas** un
conseil en investissement ni une garantie de résultat. La « probabilité estimée »
est un simple indicateur de confiance dérivé du score, et non une probabilité
réelle de gain. Le trading sur marchés à effet de levier comporte un **risque de
perte en capital** pouvant dépasser le dépôt initial. L'utilisateur reste seul
responsable de ses décisions et de sa gestion du risque. Les performances passées
ne préjugent pas des performances futures.

---

*XAUUSD SMC Confluence Signals — © Wing Master. Tous droits réservés.*
