"""
JALNETRA Configuration
Loads settings from environment variables with safe demo-mode defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # --- Core ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./jalnetra_demo.db"
    SECRET_KEY: str = "jalnetra-demo-secret-change-in-production"
    DEMO_MODE: bool = True

    # --- Feature Flags ---
    USE_REAL_WEATHER: bool = False
    USE_REAL_IOT: bool = False

    # --- WhatsApp ---
    WHATSAPP_PROVIDER: str = "mock"  # mock | meta | twilio
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_RECIPIENT_NUMBER: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None

    # --- Weather API ---
    WEATHER_API_URL: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None

    # --- Frontend ---
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "info"

    # --- Risk Thresholds (configurable) ---
    RISK_THRESHOLD_AWARENESS: float = 0.15
    RISK_THRESHOLD_WATCH: float = 0.30
    RISK_THRESHOLD_WARNING: float = 0.50
    RISK_THRESHOLD_EVACUATE: float = 0.70
    RISK_THRESHOLD_CRITICAL: float = 0.85

    # --- Safety Buffer ---
    SAFETY_BUFFER_MINUTES: int = 6

    # --- Alert Cooldown ---
    ALERT_COOLDOWN_SECONDS: int = 300  # 5 minutes between duplicate alerts

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL

    @property
    def whatsapp_configured(self) -> bool:
        return (
            self.WHATSAPP_PROVIDER != "mock"
            and self.WHATSAPP_ACCESS_TOKEN is not None
            and self.WHATSAPP_PHONE_NUMBER_ID is not None
        )


settings = Settings()
