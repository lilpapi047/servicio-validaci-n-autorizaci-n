from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Pydantic v2 configuration
    # ---------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",      # read .env automatically
        extra="ignore",       # ignore unknown env vars instead of raising errors
    )

    # ---------------------------------------------------------
    # Your original config settings
    # ---------------------------------------------------------
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    SECRET_KEY: str = Field("5689", alias="SECRET_KEY")
    resend_api_key: str = Field(..., alias="RESEND_API_KEY")
    frontend_url: str = Field(..., alias="FRONTEND_URL")

    # ---------------------------------------------------------
    # JWT / Auth configuration
    # ---------------------------------------------------------
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # ---------------------------------------------------------
    # App environment / flags
    # ---------------------------------------------------------
    app_name: str = Field(default="Global Cup Ticket API", alias="APP_NAME")
    env: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    pythonunbuffered: int = Field(default=1, alias="PYTHONUNBUFFERED")
    docker_env: bool = Field(default=False, alias="DOCKER_ENV")

    # ---------------------------------------------------------
    # Admin security token
    # ---------------------------------------------------------
    admin_api_token: str = Field(default="supersecret-admin-token", alias="ADMIN_API_TOKEN")

    # ---------------------------------------------------------
    # Raffle / ticket assignment
    # ---------------------------------------------------------
    purchase_base_url: str = Field(
        default="https://tickets.example.com/checkout",
        alias="PURCHASE_BASE_URL",
    )
    assignment_ttl_hours: int = Field(default=72, alias="ASSIGNMENT_TTL_HOURS")
    min_eligibility_age: int = Field(default=18, alias="MIN_ELIGIBILITY_AGE")

    # ---------------------------------------------------------
    # Email configuration
    # ---------------------------------------------------------
    email_from: str = Field(default="no-reply@globalcup.local", alias="EMAIL_FROM")
    email_mode: str = Field(default="resend", alias="EMAIL_MODE")

    smtp_server: Optional[str] = Field(
        default="sandbox.smtp.mailtrap.io",
        alias="SMTP_SERVER",
    )
    smtp_port: Optional[int] = Field(default=2525, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default="smtp-username", alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default="smtp-password", alias="SMTP_PASSWORD")


# ---------------------------------------------------------
# Singleton instance used throughout the app
# ---------------------------------------------------------
settings = Settings()

