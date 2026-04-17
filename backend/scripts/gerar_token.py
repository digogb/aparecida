import os

# Permite que o Google retorne um subconjunto dos escopos pedidos sem erro
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)

# open_browser=False — imprime a URL em vez de tentar abrir o browser
creds = flow.run_local_server(port=9753, open_browser=False)

print("\nGMAIL_REFRESH_TOKEN =", creds.refresh_token)
print("GMAIL_CLIENT_ID     =", creds.client_id)
print("GMAIL_CLIENT_SECRET =", creds.client_secret)
print("\nEscopos concedidos:", creds.scopes)
