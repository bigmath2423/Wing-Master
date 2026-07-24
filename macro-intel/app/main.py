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

from app.api import routes_macro, routes_tradingview
from app.config import settings
from app.db import init_db
from app.pipeline import run_pipeline
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
logger = logging.getLogger("macro.main")

_DASHBOARD = Path(__file__).resolve().parent.parent / "dashboard" / "index.html"


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
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Macro-Intel",
    description="Couche d'intelligence macro pour indicateur TradingView (XAUUSD, BTC, matières premières).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restreindre en production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_macro.router)
app.include_router(routes_tradingview.router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "env": settings.app_env, "ai": settings.ai_enabled}


@app.get("/", include_in_schema=False)
def dashboard():
    if _DASHBOARD.exists():
        return FileResponse(_DASHBOARD)
    return {"message": "Macro-Intel opérationnel. Voir /docs"}
