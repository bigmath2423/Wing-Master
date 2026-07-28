## Chapitre 9 — Premium / Discount

Le filtre le plus simple du manuel, et celui qui supprime le plus grand nombre
de mauvais trades.

### Le principe

Tout mouvement s'inscrit dans un **dealing range** : du dernier creux
significatif au dernier sommet significatif. Le point médian sépare la zone
chère (premium) de la zone bon marché (discount).

```schema
   1,0900 ──────────────────────  haut du dealing range
          ░░░░░░ PREMIUM ░░░░░░   ← ventes uniquement
   1,0850 ══════ ÉQUILIBRE ══════ ← zone morte, aucun trade
          ▓▓▓▓▓▓ DISCOUNT ▓▓▓▓▓▓  ← achats uniquement
   1,0800 ──────────────────────  bas du dealing range
```

### Comment tracer le range correctement

1. Repérez le dernier extrême qui a **pris de la liquidité** (une purge, pas
   n'importe quel creux).
2. Reliez-le à l'extrême opposé qui a également pris de la liquidité.
3. Tracez le 50 %.
4. Redessinez dès qu'un nouvel extrême est atteint.

L'erreur la plus fréquente n'est pas dans la règle mais dans le tracé : un range
mal défini rend le filtre inutile.

### Le tableau de décision

| Position du prix | Achat | Vente |
|---|---|---|
| Discount profond (0,70–1,0) | ★★★ | ✘ |
| Discount (0,50–0,70) | ★★ | ✘ |
| Équilibre (0,45–0,55) | ✘ | ✘ |
| Premium (0,30–0,50 depuis le haut) | ✘ | ★★ |
| Premium profond (0,0–0,30) | ✘ | ★★★ |

### Le cas de la tendance forte

En tendance puissante, le prix ne revient jamais en discount du range global.
On applique alors le filtre au **range de l'impulsion en cours**, pas au range
global. C'est la seule exception, et elle doit être décidée à l'avance.

::: retenir
- Au-dessus de 50 %, seules les ventes ; en dessous, seuls les achats.
- Le range se trace entre deux extrêmes ayant pris de la liquidité.
- L'équilibre est une zone morte : on n'y entre jamais.
- En tendance forte, on applique le filtre à l'impulsion en cours.
:::

::: erreur
- Acheter un « bel Order Block » situé en premium.
- Tracer le range sur des extrêmes arbitraires.
- Oublier de redessiner après une expansion.
- Utiliser le filtre pour justifier une entrée déjà décidée.
:::

::: resume
**Premium/discount en une page.** Divisez le mouvement en deux par son milieu.
Au-dessus, le prix est cher : on ne fait que vendre. En dessous, il est bon
marché : on ne fait qu'acheter. Autour du milieu, on ne fait rien. Cette règle
binaire, appliquée sans exception, élimine la majorité des entrées médiocres,
parce que l'immense majorité des mauvais trades consiste à acheter haut et à
vendre bas. Le seul travail réel consiste à tracer le range correctement : entre
deux extrêmes ayant effectivement purgé de la liquidité, redessiné à chaque
nouvelle expansion.
:::

## Chapitre 10 — L'Order Block

La zone d'entrée de référence du SMC.

### Définition rigoureuse

Un Order Block est la **dernière bougie de sens opposé avant un déplacement**.
Mais une bougie seule ne suffit pas : trois conditions doivent être réunies.

```schema
   ┌──┐ ← Order Block (dernière bougie baissière)
   │▓▓│         ███
   └──┘     ███ ███  ← 2. déplacement, avec FVG
     ╲   ███
      ▼ 1. prise de liquidité              3. cassure de structure
```

| Condition | Sans elle |
|---|---|
| **1. Prise de liquidité avant** | La zone n'a aucune raison d'exister |
| **2. Déplacement après (avec FVG)** | Aucune preuve d'intention |
| **3. Cassure de structure** | Le contrôle n'a pas changé de camp |

Si les trois ne sont pas réunies, ce n'est pas un Order Block : c'est une
bougie.

### Comment le délimiter

| Marquage | Zone retenue | Usage |
|---|---|---|
| **Complet** | Mèche à mèche | Conservateur, moins d'entrées manquées |
| **Corps seul** | Ouverture → clôture | Précis, meilleur ratio, plus d'entrées ratées |
| **50 % du bloc** | Point médian | Compromis courant |

Choisissez-en **un seul** et gardez-le. Changer de marquage selon le résultat
souhaité détruit toute mesure de performance.

### Règles d'utilisation

- Une seule mitigation : un OB déjà testé a perdu l'essentiel de sa valeur.
- Toujours dans le sens du biais HTF.
- Toujours du bon côté de l'équilibre.
- Stop **au-delà** de la bougie d'origine, jamais à l'intérieur.
- Objectif sur la liquidité opposée.

::: retenir
- Trois conditions obligatoires : liquidité, déplacement, cassure de structure.
- Un OB ne fonctionne qu'une fois.
- Le stop se place au-delà du bloc, pas au milieu.
- Sans biais HTF, un OB n'est qu'un dessin.
:::

::: erreur
- Marquer un OB sur chaque bougie opposée du graphique.
- Réutiliser un OB déjà mitigé.
- Entrer sur un OB contre la structure supérieure.
- Réduire le stop pour « améliorer le ratio » — le ratio se gagne par
  l'entrée, jamais par le stop.
:::

::: resume
**Order Block en une page.** C'est la trace laissée par une exécution
institutionnelle : la dernière bougie opposée avant un mouvement violent. Sa
validité tient à trois conditions — une liquidité prise juste avant, un
déplacement franc juste après (idéalement avec un FVG), et une cassure de
structure. Le prix y revient parce que l'exécution n'a pas pu être complétée
entièrement lors de l'impulsion. On y entre en ordre limite, une seule fois,
dans le sens de la tendance supérieure et du bon côté de l'équilibre, avec un
stop au-delà du bloc et un objectif sur la liquidité opposée.
:::

## Chapitre 11 — Le Breaker Block

L'Order Block qui a échoué, et qui devient une zone dans l'autre sens.

### La mécanique

```schema
             ╱╲ sommet
      OB ▓▓▓╱  ╲          retour sur le breaker
   ╱╲    ╱      ╲     ┌──► ▓▓▓ ← vente
  ╱  ╲  ╱        ╲    │       ╲
 ╱    ╲╱          ╲___│        ╲▼
 ──────── creux cassé (BOS baissier)
```

Séquence : creux → sommet → creux **plus bas que le premier**. L'Order Block
haussier qui a produit le sommet est désormais invalidé : les acheteurs qui s'y
sont positionnés sont en perte.

### Pourquoi c'est puissant

Deux forces convergent au même prix :

1. **Les piégés** — les acheteurs de la zone veulent sortir à l'équilibre. Leur
   sortie est une vente.
2. **Les institutionnels** — la zone reste un niveau d'exécution connu.

C'est cette superposition qui explique la violence des rejets sur un breaker.

### Breaker contre mitigation block

| | Breaker | Mitigation block |
|---|---|---|
| Structure opposée cassée ? | **Oui** | Non |
| Type de trade | Retournement | Continuation |
| Contexte | Après un CHoCH/MSS | En pleine tendance |

C'est la seule différence, et elle est essentielle : confondre les deux revient
à trader un retournement dans une tendance intacte.

::: retenir
- Une zone d'achat cassée devient une zone de vente.
- Il faut impérativement une cassure de structure : sinon c'est un mitigation
  block.
- La force vient des traders piégés qui cherchent la sortie.
- Un breaker traversé sans réaction annonce une continuation violente.
:::

::: erreur
- Utiliser un breaker sans CHoCH préalable.
- Le confondre avec le mitigation block et trader à contre-tendance.
- Placer le stop à l'intérieur du bloc.
- Retester le même breaker trois fois : après le premier test, il s'épuise.
:::

::: resume
**Breaker en une page.** Quand une zone d'achat échoue et que le prix casse la
structure vers le bas, cette zone change de camp : elle devient une zone de
vente. Sa puissance vient de la superposition de deux flux — les acheteurs
piégés qui liquident à l'équilibre, et les vendeurs institutionnels qui
complètent leur position au même prix. La condition non négociable est la
cassure de structure : sans elle, la zone est un simple mitigation block, qui se
trade en continuation et non en retournement.
:::

## Chapitre 12 — Le Mitigation Block

Le bloc où une position mal engagée est ramenée à l'équilibre — sans cassure de
structure.

### La mécanique

```schema
   ▓▓▓ mitigation block (dernier bloc haussier avant la chute)
      ╲
        ╲▼▼▼  impulsion baissière
             ╱  retour dans le bloc ──► vente
                ╲▼▼▼  continuation de la tendance
```

Contrairement au breaker, **la structure opposée n'a jamais été cassée** : la
tendance reste intacte. Le mitigation block est donc une configuration de
**continuation**, la plus confortable qui soit — on trade dans le sens du
courant.

### Quand l'utiliser

- Tendance HTF clairement établie.
- Le prix corrige et revient vers le dernier bloc opposé.
- Aucun CHoCH n'a eu lieu sur l'unité de temps de travail.

C'est typiquement la configuration du retracement en tendance : on ne cherche
pas un retournement, on rejoint le mouvement.

### Le classement des zones par risque

| Zone | Type de trade | Risque relatif |
|---|---|---|
| Mitigation block | Continuation | Le plus faible |
| Order Block avec biais HTF | Continuation | Faible |
| Breaker après CHoCH | Retournement | Moyen |
| Order Block contre la tendance | Retournement | Élevé — à éviter |

::: retenir
- Le mitigation block se trade **en continuation**.
- Aucune cassure de structure opposée : c'est ce qui le distingue du breaker.
- C'est la configuration la plus confortable, car on suit la tendance.
- Un mitigation block traversé signale un vrai changement de contrôle.
:::

::: erreur
- Le confondre avec un breaker et attendre un retournement.
- L'utiliser en range, où il n'y a pas de tendance à rejoindre.
- Entrer sans que le prix ait atteint la zone, par peur de la manquer.
- Ignorer le filtre premium/discount, valable ici aussi.
:::

::: resume
**Mitigation block en une page.** En pleine tendance, le prix revient
régulièrement sur le dernier bloc de sens opposé avant l'impulsion. Ce retour
permet aux positions mal engagées d'être réduites à l'équilibre, ce qui alimente
la reprise de la tendance. C'est une configuration de continuation : on entre
dans le sens du mouvement dominant, avec un stop de l'autre côté du bloc. La
différence avec le breaker tient en un mot : ici, aucune structure opposée n'a
été cassée. Confondre les deux, c'est trader un retournement dans une tendance
parfaitement intacte.
:::
