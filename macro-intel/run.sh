#!/usr/bin/env bash
# Démarrage rapide en développement.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "→ Création de l'environnement virtuel..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "→ Installation des dépendances..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  echo "→ Aucun .env, copie depuis .env.example (fonctionne sans clé API)."
  cp .env.example .env
fi

echo "→ Lancement de l'API sur http://localhost:8000  (dashboard: /, docs: /docs)"
exec uvicorn app.main:app --reload --port 8000
