# Cycle 10 — Recherche d'une source d'alpha indépendante

## Ce qui a pu être testé, et ce qui n'a pas pu l'être

L'environnement de recherche bloque tout accès réseau externe : FRED, Stooq et
Yahoo Finance renvoient tous un refus 403 au niveau du proxy. **Les familles
inter-marchés et macro n'ont donc pas pu être testées** — ce n'est pas un choix
méthodologique, c'est une limite matérielle. Elles restent la piste n°1.

Une seule famille était testable de bout en bout avec les données en main.

## Le spread bid-ask du broker — microstructure réelle

Les exports MT5 contiennent une colonne `<SPREAD>` jamais exploitée : l'écart
bid-ask réel, barre par barre. Médiane 7 points (0,070 $/oz), q90 à 17, max 281.
6,5 % de valeurs nulles (données manquantes) écartées.

**Hypothèse.** Une cassure qui naît pendant une expansion anormale du spread est
produite par un retrait de liquidité, pas par un flux directionnel : elle se
retourne plus souvent.

**Redondance : aucune.** Corrélation maximale avec les modules existants
(ATR normalisé, volume, range, heure) = **0,147**. C'est bien une information
neuve — la première depuis le début de ce travail à passer l'écran aussi nettement.

### Résultat

| Variante | rho | p | rho partiel (temps neutralisé) |
|---|---|---|---|
| spread brut | +0,036 | 0,411 | +0,035 |
| spread relatif | −0,033 | 0,458 | −0,034 |
| spread percentile | −0,011 | 0,805 | −0,012 |
| spread choc | −0,021 | 0,638 | −0,021 |

Benjamini-Hochberg, FDR 10 %, 4 tests : **aucune retenue.**

### Le filtre pratique

Rejeter les cassures nées dans le décile/quintile haut de spread relatif :

| | Gardés | Rejetés | Écart |
|---|---|---|---|
| q80 | n=425 · PF 1,320 · +0,187 R | n=98 · PF 0,946 · **−0,030 R** | +0,217 R · p = 0,136 |
| q90 | n=476 · PF 1,294 · +0,171 R | n=47 · PF 0,819 · **−0,099 R** | +0,270 R · p = 0,126 |

Le groupe rejeté a une espérance nulle ou négative, exactement comme le prédisait
l'hypothèse. Le signe est **le même dans les deux moitiés** (+0,184 et +0,240) et
**dans les quatre années** (+0,236 · +0,054 · +0,230 · +0,343).

**Et pourtant ce n'est pas concluant.** IC95 de l'écart : **[−0,073 ; +0,496]**,
P(écart > 0) = 92,7 %. Surtout : l'effet minimum détectable à cette sélectivité
est de **0,339 R** et l'effet observé vaut **+0,217 R** — il est *structurellement
sous le seuil de détection*. Le test ne peut pas trancher, quelle que soit la
qualité de l'idée.

De plus, les données de spread ne remontent qu'à 2022 : **aucun hors-échantillon
disponible**, dans la fenêtre précisément la plus exploitée.

**Verdict : non significatif, et non tranchable avec cet échantillon.** Ni retenu,
ni réfuté. Il se distingue de l'ADX sur un point : il ne s'inverse nulle part.

## Le vrai goulot d'étranglement n'est pas les idées

| Le filtre garde | Effet minimum détectable |
|---|---|
| 90 % | 0,452 R |
| 70 % | 0,296 R |
| 50 % | **0,272 R** |
| 30 % | 0,297 R |

L'espérance du système vaut **+0,149 R**. Pour être détectable, un filtre gardant
la moitié des trades doit donc **doubler l'espérance du sous-groupe conservé**.

Or un filtre réellement bon, dans la vraie vie, vaut peut-être +0,05 à +0,10 R.
**Ces effets-là sont invisibles dans un échantillon de 827 trades.** Neuf cycles
de recherche n'ont pas échoué faute d'idées : ils ont buté sur un mur de puissance
statistique. Et ce mur explique aussi les faux positifs — quand le seuil de
détection est à 0,27 R, tout ce qui ressort du bruit ressort *par* le bruit.

## La seule façon d'agrandir l'échantillon sans attendre des années

Tester le même système sur **d'autres instruments** : argent, platine, cuivre,
EURUSD, indices. Deux bénéfices, tous deux importants :

1. **Confirmation structurelle.** Si « filtre de tendance journalière + cassure »
   fonctionne aussi ailleurs, l'avantage est structurel et non ajusté à l'or.
   S'il ne fonctionne que sur l'or, c'est un signal d'alerte sérieux.
2. **Puissance.** Cinq instruments donnent ~4 000 trades au lieu de 827. Le seuil
   de détection tombe de 0,27 R à environ **0,12 R** — sous l'espérance du système.
   Les effets modestes deviennent enfin mesurables.

C'est la recommandation prioritaire, avant toute nouvelle famille de concepts.
