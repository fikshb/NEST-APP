from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://nestapp:nestapp_dev_password@db:5432/nestapp"
    api_secret_key: str = "change-me-in-production"
    storage_root: str = "/app/storage"
    openclaw_service_token: str = "dev-bot-token-change-in-prod"
    resend_api_key: str = "stub"
    email_from: str = "onboarding@resend.dev"
    finance_email: str = "finance@example.com"
    initial_asset_path: str = "/app/initial_asset"
    admin_user: str = "adminnest"
    admin_password: str = "@adm1nNest!!"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
