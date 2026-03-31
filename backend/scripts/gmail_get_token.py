"""
Script para gerar o refresh token do Gmail OAuth2.

Uso:
  1. Coloque o oauth_credentials.json (baixado do Google Cloud Console) na pasta credentials/
  2. Execute: python scripts/gmail_get_token.py
  3. Abra o link no navegador, faça login, autorize
  4. Cole o código de autorização no terminal
  5. O script vai exibir o GMAIL_REFRESH_TOKEN — copie para o .env
"""

import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_PATH = Path(__file__).parent.parent / "credentials" / "oauth_credentials.json"


def main():
    if not CREDENTIALS_PATH.exists():
        print(f"Erro: {CREDENTIALS_PATH} não encontrado.")
        print("Baixe o JSON de credenciais OAuth do Google Cloud Console")
        print("e salve em credentials/oauth_credentials.json")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_PATH),
        scopes=SCOPES,
    )

    # Usa o servidor local para capturar o redirect
    creds = flow.run_local_server(port=8090, open_browser=True)

    print("\n" + "=" * 60)
    print("Token gerado com sucesso!")
    print("=" * 60)
    print(f"\nAdicione ao seu .env:\n")
    print(f'GMAIL_REFRESH_TOKEN={creds.refresh_token}')
    print(f'GMAIL_CLIENT_ID={creds.client_id}')
    print(f'GMAIL_CLIENT_SECRET={creds.client_secret}')
    print(f'GMAIL_SENDER_EMAIL=<seu_email@gmail.com>')
    print(f"\n" + "=" * 60)


if __name__ == "__main__":
    main()
