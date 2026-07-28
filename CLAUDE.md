# Conventions du dépôt

## Fusion des pull requests : en local, jamais via l'API GitHub

Merger via l'interface ou l'API GitHub fait fabriquer le commit de fusion par
GitHub, avec `GitHub <noreply@github.com>` comme committer. Ces commits
apparaissent ensuite comme *Unverified* et ne portent pas la signature
Anthropic.

**Procédure à suivre** une fois la CI verte et la PR approuvée :

```bash
git fetch origin main
git checkout main && git pull --ff-only
git merge --no-ff <branche-de-la-pr> -m "Merge pull request #<n> — <titre>"
git push origin main
```

GitHub détecte le merge et ferme la PR automatiquement. Le commit de fusion
porte alors `Claude <noreply@anthropic.com>`, comme les autres.

`--no-ff` est important : il conserve un commit de fusion explicite même quand
une avance rapide serait possible, ce qui garde l'historique des PR lisible.

### Ne jamais réécrire un commit de fusion déjà poussé

Si un commit de fusion créé par GitHub existe déjà sur `main`, il faut le
laisser tel quel. L'amender exigerait un `push --force` sur `main` : cela
réécrirait l'historique public, casserait le lien avec la PR, et attribuerait à
tort le commit du propriétaire du dépôt. La convention ci-dessus s'applique aux
**prochaines** fusions, pas rétroactivement.

## Identité git

```bash
git config user.name  "Claude"
git config user.email "noreply@anthropic.com"
```

## Projet `backtest-agent/`

Agent d'analyse quantitative de backtests de trading. Voir
`backtest-agent/README.md` pour l'architecture et le mode d'emploi.

- Tests : `cd backtest-agent && pytest` (109 tests)
- CI : `.github/workflows/backtest-agent-tests.yml`, Python 3.10 et 3.12,
  déclenchée sur `pull_request` et sur les push vers `main`
- Le mode d'emploi PDF est généré : après toute modification touchant la
  version, la liste des commandes ou les seuils, régénérer avec
  `python3 docs/generer_mode_emploi.py` — sinon il donnera des instructions
  périmées.
