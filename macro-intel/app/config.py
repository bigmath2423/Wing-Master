"""Configuration centralisée (12-factor : tout vient de l'environnement)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Général
    app_env: str = "development"
    log_level: str = "INFO"
    api_shared_secret: str = "change-me-please"

    # Base de données
    database_url: str = "sqlite:///./macro_intel.db"

    # Fréquences de rafraîchissement (secondes)
    refresh_market_seconds: int = 300
    refresh_news_seconds: int = 600
    refresh_calendar_seconds: int = 3600

    # Clés API (toutes optionnelles)
    fred_api_key: str = ""
    finnhub_api_key: str = ""
    newsapi_key: str = ""
    fmp_api_key: str = ""
    trading_economics_key: str = ""

    # IA
    anthropic_api_key: str = ""
    ai_model: str = "claude-opus-4-8"

    # Notifications
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""

    @property
    def ai_enabled(self) -> bool:
        return bool(self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
