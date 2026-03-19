from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ione:ione_dev_2026@db:5432/ione"
    JWT_SECRET: str = "troque-isso-em-producao"
    ANTHROPIC_API_KEY: str = ""
    GMAIL_CREDENTIALS_PATH: str = "/app/credentials/gmail_service_account.json"
    ENV: str = "development"

    # DJE search — configure via .env
    # Ex: DJE_NOME_ADVOGADO="JOSE ANTONIO SOUZA"
    # Ex: DJE_NUMERO_OAB="12345/SP"
    DJE_NOME_ADVOGADO: str = ""
    DJE_NUMERO_OAB: str = ""
    DJE_SIGLA_TRIBUNAL: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
