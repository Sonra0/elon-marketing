from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = Field(default="dev", alias="ELON_ENV")
    log_level: str = Field(default="INFO", alias="ELON_LOG_LEVEL")
    base_url: str = Field(default="http://localhost:8000", alias="ELON_BASE_URL")

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "elon"
    postgres_user: str = "elon"
    postgres_password: str = "change_me"

    redis_url: str = "redis://redis:6379/0"

    s3_endpoint_url: str = "http://minio:9000"
    s3_region: str = "us-east-1"
    s3_access_key: str = "elonminio"
    s3_secret_key: str = "change_me_minio"
    s3_bucket: str = "elon"

    secret_box_key: str = ""
    jwt_secret: str = "change_me_jwt"
    jwt_alg: str = "HS256"
    jwt_ttl_hours: int = 72

    anthropic_api_key: str = ""
    anthropic_model_default: str = "claude-sonnet-4-6"
    anthropic_model_planner: str = "claude-opus-4-7"

    telegram_bot_token: str = ""
    telegram_webhook_secret: str = "change_me_tg_secret"

    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_oauth_redirect: str = "/oauth/meta/callback"
    whatsapp_verify_token: str = "change_me_wa_verify"

    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_oauth_redirect: str = "/oauth/tiktok/callback"

    tavily_api_key: str = ""
    serpapi_api_key: str = ""

    tenant_monthly_budget_usd: float = 50.0
    budget_alert_thresholds: str = "0.8,1.0"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def alert_thresholds(self) -> list[float]:
        return [float(x.strip()) for x in self.budget_alert_thresholds.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
