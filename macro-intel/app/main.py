"""Point d'entrée FastAPI : assemble routes, DB, scheduler et dashboard.

Lancer en dev :
    uvicorn app.main:app --reload --port 8000

Docs interactives : http://localhost:8000/docs
Dashboard        : http://localhost:8000/
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api import routes_macro, routes_tradingview, routes_v1
from app.config import settings
from app.db import init_db
from app.pipeline import run_pipeline
from app.platform_state import refresh_platform
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("macro.main")

_DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"
_APP = _DASHBOARD_DIR / "app.html"  # application MacroLens
_SIMULATOR = _DASHBOARD_DIR / "index.html"  # simulateur d'impact (conservé)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage Macro-Intel (env=%s, IA=%s)...", settings.app_env, settings.ai_enabled)
    if settings.app_env != "development" and settings.api_shared_secret == "change-me-please":
        logger.warning(
            "⚠️  SÉCURITÉ : API_SHARED_SECRET utilise la valeur par défaut en "
            "environnement '%s'. Définissez un secret aléatoire dans .env avant "
            "d'exposer le webhook publiquement.",
            settings.app_env,
        )
    init_db()
    try:
        run_pipeline()  # premier cycle synchrone pour avoir des données au boot
    except Exception as exc:
        logger.warning("Premier cycle incomplet : %s", exc)
    try:
        refresh_platform()  # régime, analyses IA, corrélations, prix
    except Exception as exc:
        logger.warning("Première consolidation plateforme incomplète : %s", exc)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="MacroLens",
    description=(
        "Plateforme d'analyse macroéconomique assistée par IA. Centralise, analyse, "
        "explique et met en scénarios le contexte macro et géopolitique. "
        "**N'émet jamais de signal d'achat ou de vente** : la décision appartient au lecteur."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restreindre en production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_v1.router)
app.include_router(routes_macro.router)
app.include_router(routes_tradingview.router)


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "env": settings.app_env,
        "ai": settings.ai_enabled,
        "version": app.version,
    }


@app.get("/", include_in_schema=False)
def home():
    """Application MacroLens (poste d'analyse macro)."""
    if _APP.exists():
        return FileResponse(_APP)
    return {"message": "MacroLens opérationnel. Voir /docs"}


@app.get("/simulateur", include_in_schema=False)
def simulator():
    """Simulateur d'impact macro sur l'or (outil pédagogique conservé)."""
    if _SIMULATOR.exists():
        return FileResponse(_SIMULATOR)
    return {"message": "Simulateur indisponible."}
