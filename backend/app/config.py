from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ione:ione_dev_2026@db:5432/ione"
    JWT_SECRET: str = "troque-isso-em-producao"
    ANTHROPIC_API_KEY: str = ""
    GMAIL_CREDENTIALS_PATH: str = "/app/credentials/gmail_service_account.json"
    GMAIL_SENDER_EMAIL: str = ""
    # OAuth2 (para teste / Gmail pessoal)
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REFRESH_TOKEN: str = ""
    GMAIL_TEST_RECIPIENT: str = ""  # se definido, todos os emails vão para este endereço (teste)
    ENV: str = "development"
    # Origens permitidas para CORS — separadas por vírgula. Vazio = fallback dev (localhost:5173)
    CORS_ORIGINS: str = ""
    # URL pública da app — usada para montar o link de redefinição de senha enviado por email.
    # Ex (prod): https://app.ioneadvogados.com.br ; (dev) http://localhost:5173
    APP_BASE_URL: str = "http://localhost:5173"

    # DJE search — configure via .env
    # Ex: DJE_NOME_ADVOGADO="JOSE ANTONIO SOUZA"
    # Ex: DJE_NUMERO_OAB="12345/SP"
    DJE_NOME_ADVOGADO: str = ""
    DJE_NUMERO_OAB: str = ""
    DJE_SIGLA_TRIBUNAL: str = ""

    # Camada 6 — verificação web via tool use (web_search server tool da Anthropic).
    # Quando True, o P2 pode chamar web_search para verificar normas, julgados e valores
    # antes de gerar um marcador [REVISAR—] ou [!VERIFICAR:!]. Custo extra de 0,01 USD por busca.
    WEB_SEARCH_ENABLED: bool = True
    WEB_SEARCH_MAX_USES_CONSULTIVO: int = 8       # parecer comum
    WEB_SEARCH_MAX_USES_QUASE_PROCESSUAL: int = 20  # impugnação/recurso/defesa em TCE

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
