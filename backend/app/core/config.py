"""Configuración tipada de la aplicación (pydantic-settings).

Todas las rutas se resuelven a partir de `Path(__file__)` para que la app
funcione con cualquier directorio de trabajo (requisito de T1.3).
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "production"] = "development"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_enabled: bool = False
    rafa_context_path: Path | None = None

    # Router LLM (F2)
    llm_providers_order: str = "tower,dell"
    llm_tower_url: str = ""
    llm_tower_model: str = ""
    llm_dell_url: str = ""
    llm_dell_model: str = ""
    llm_connect_timeout_s: float = 1.5
    llm_health_ttl_s: float = 10.0
    llm_first_token_timeout_s: float = 15.0
    llm_max_concurrency: int = 2

    # Seguridad y límites (F4)
    allowed_hosts: str = "*"
    max_body_bytes: int = 16384
    rate_limit_chat: str = "10/minute;60/hour"
    rate_limit_contact: str = "3/hour"
    rate_limit_feedback: str = "20/hour"
    daily_chat_budget: int = 500
    trusted_proxy_ips: str = "127.0.0.1"
    public_contact_allowlist: str = ""
    allowed_output_domains: str = "github.com,linkedin.com"
    daily_contact_budget: int = 50
    contact_to: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_timeout_s: float = 10.0
    turnstile_enabled: bool = False
    turnstile_secret: str = ""

    # RAG (F3)
    vault_path: str = ""
    public_vault_dir: str = "Public"
    embed_url: str = ""
    embed_model: str = "bge-m3"
    chroma_path: str = "./data/chroma"
    data_path: str = "./data"
    rag_top_k: int = 5
    rag_min_score: float = 0.50
    rag_context_prefix: str = "Rafael Castaño"

    email: str = ""
    password_application: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def context_file(self) -> Path | None:
        if self.rafa_context_path is not None:
            return self.rafa_context_path
        dev_copy = BACKEND_DIR / "rafa_context.txt"
        return dev_copy if dev_copy.is_file() else None

    @property
    def chat_enabled(self) -> bool:
        return bool(self.google_api_key) and self.context_file is not None

    @property
    def contact_enabled(self) -> bool:
        return bool(self.email) and bool(self.password_application)

    def missing_required(self) -> list[str]:
        missing: list[str] = []
        if not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        if self.context_file is None:
            missing.append("RAFA_CONTEXT_PATH")
        if not self.email:
            missing.append("EMAIL")
        if not self.password_application:
            missing.append("PASSWORD_APPLICATION")
        return missing


@lru_cache
def get_settings() -> Settings:
    return Settings()
