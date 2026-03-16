from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ionde:ionde_dev_2026@db:5432/ionde"
    JWT_SECRET: str = "troque-isso-em-producao"
    ANTHROPIC_API_KEY: str = ""
    GMAIL_CREDENTIALS_PATH: str = "/app/credentials/gmail_service_account.json"
    ENV: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
