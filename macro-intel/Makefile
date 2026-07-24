# Macro-Intel — commandes de développement
.DEFAULT_GOAL := help
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help venv install dev run lint format typecheck test check clean docker

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

venv: ## Crée l'environnement virtuel
	python3 -m venv $(VENV)

install: venv ## Installe les dépendances + outils de dev
	$(PIP) install -q -r requirements.txt ruff mypy

run: ## Lance l'API (dashboard: http://localhost:8000/)
	$(VENV)/bin/uvicorn app.main:app --reload --port 8000

lint: ## Vérifie le style (ruff)
	$(VENV)/bin/ruff check app tests

format: ## Formate le code (ruff)
	$(VENV)/bin/ruff format app tests
	$(VENV)/bin/ruff check app tests --fix

typecheck: ## Analyse de types (mypy)
	$(VENV)/bin/mypy app

test: ## Lance les tests
	$(VENV)/bin/pytest

check: lint test ## Contrôle complet (lint + tests) — comme la CI

docker: ## Build + run via docker compose
	docker compose up --build

clean: ## Supprime caches et base locale
	rm -rf .pytest_cache .ruff_cache **/__pycache__ *.db
