"""Application configuration — env-driven, Docker-friendly."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Audira.run API"
    app_version: str = "0.4.0-phase1"
    environment: str = "development"
    debug: bool = False

    # Auth (FR-E17-1)
    auth_mode: str = "development"  # development | workos
    jwt_secret: str = "dev-jwt-secret-change-in-production-min-32-chars"
    jwt_expiry_hours: int = 24
    web_app_url: str = "http://localhost:3000"

    # Database (Render Postgres + pgvector in production)
    database_url: str = "postgresql+asyncpg://audira:audira@localhost:5432/audira"

    # Redis (cache + Arq job queue)
    redis_url: str = "redis://localhost:6379/0"

    # Object storage (Cloudflare R2 / S3)
    object_storage_endpoint: str = ""
    object_storage_bucket: str = "audira-artifacts"
    object_storage_access_key: str = ""
    object_storage_secret_key: str = ""

    # GPU inference tier (Modal / Replicate / Baseten — decoupled)
    inference_base_url: str = ""
    inference_api_key: str = ""
    inference_monthly_cost_cap_usd: float = 500.0

    # Direct social OAuth (users authenticate straight with each provider)
    # Callback URL registered with each provider must point here:
    oauth_redirect_uri: str = "http://localhost:8000/auth/callback"

    # Google OAuth (console.cloud.google.com → Credentials → OAuth client ID)
    google_client_id: str = ""
    google_client_secret: str = ""

    # GitHub OAuth (github.com/settings/developers → OAuth Apps)
    github_client_id: str = ""
    github_client_secret: str = ""

    # LinkedIn OAuth (linkedin.com/developers → Apps → Auth)
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""

    # Sign in with Apple (developer.apple.com → Certificates, Identifiers & Profiles)
    apple_client_id: str = ""  # Services ID, e.g. run.audira.web
    apple_team_id: str = ""
    apple_key_id: str = ""
    apple_private_key: str = ""  # contents of the .p8 key (PEM)

    # WorkOS Directory Sync / SCIM (optional — enterprise provisioning only)
    workos_api_key: str = ""
    workos_client_id: str = ""
    workos_redirect_uri: str = "http://localhost:8000/auth/callback"
    workos_webhook_secret: str = ""

    # Observability
    sentry_dsn: str = ""
    otel_exporter_otlp_endpoint: str = ""

    # CORS — Vercel frontend
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
