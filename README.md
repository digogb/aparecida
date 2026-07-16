# Sistema Ione — Automação de Pareceres Jurídicos

Sistema web do escritório **Ione Advogados & Associados** (Direito Público Municipal) para
recepção de consultas jurídicas de prefeituras por e-mail, geração assistida de pareceres
com IA, edição colaborativa, aprovação e envio da resposta ao consulente — na mesma
conversa de e-mail original.

- **Manual do usuário** (para os advogados e a secretaria): [`docs/MANUAL_USUARIO.md`](docs/MANUAL_USUARIO.md)
- **Guia de deploy** (VM, HTTPS, CI/CD): [`DEPLOY.md`](DEPLOY.md)

## Visão geral do fluxo

```
E-mail da prefeitura (Gmail)
        │  polling periódico
        ▼
Extração de texto (PDF/DOCX, OCR por página quando necessário)
        ▼
Classificação IA (P1: é consulta jurídica? tema? município?)
        ▼
Geração do parecer (P2: Claude + leis municipais + jurisprudência TCE-CE/TCU)
        ▼
Gate mecânico (auditor: ementa, parágrafos, citações literais, marcadores)
        │  reprova → auto-revisão (P3)
        ▼
Editor (TipTap): edição manual, anotações por advogado, correção por trecho (IA)
        ▼
Aprovar e enviar → DOCX gerado e respondido na thread original do Gmail
```

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Alembic · asyncpg |
| Frontend | React 18 · TypeScript · Vite · TailwindCSS · TipTap · React Query |
| Banco | PostgreSQL 16 |
| IA | Claude API (Anthropic) — geração, classificação e revisão |
| E-mail | Gmail API (OAuth2) — leitura da caixa e envio das respostas |
| Export | python-docx (DOCX) |
| Infra | Docker Compose (db + backend + frontend) |

## Como rodar em desenvolvimento

Pré-requisitos: Docker + Docker Compose.

```bash
cp .env.example .env        # preencha ANTHROPIC_API_KEY (e Gmail, se for testar e-mail)
docker compose up -d --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000 (health check em `/health`; docs em `/docs`)
- Postgres: localhost:5432 (usuário `ione`)

As migrations (Alembic) rodam automaticamente na subida do backend, e `app/seeds.py`
popula usuários iniciais **apenas se a tabela estiver vazia** (senha padrão `123456` —
troque no primeiro acesso). O login é feito pelo e-mail do usuário.

Produção usa `docker-compose.prod.yml` (build estático do frontend servido por nginx) —
ver [`DEPLOY.md`](DEPLOY.md).

## Arquitetura — pontos não-óbvios

- **Auto-discovery de routers**: `app/main.py` registra automaticamente qualquer arquivo
  em `app/routers/` que exporte `router = APIRouter()` (e `ws_router` para WebSocket).
  Para criar um endpoint novo, basta criar o arquivo — nunca edite `main.py`.
- **Rotas do frontend**: registradas apenas em `src/routes.tsx`; a Sidebar lê esse
  registro. `App.tsx` e `Sidebar.tsx` não precisam ser editados.
- **Prompts do pipeline**: em `backend/prompts/` (P1 classificação, P1.5 valores
  financeiros, P2 geração — um por modelo de parecer —, P3 revisão). As bases de
  conhecimento ficam em `backend/skills/` (jurisprudência, manuais, regras de escrita)
  e `backend/leis_municipios/` (legislação local por município).
- **Fronteira de confiança**: texto de anexo entra nos prompts envolto em
  `<documento_anexo>` com delimitadores neutralizados (`app/services/prompt_safety.py`) —
  defesa contra prompt injection em documentos recebidos.
- **Auditor mecânico** (`app/services/auditor_mecanico.py`): gate determinístico que
  reprova parecer com ementa fora do padrão, parágrafos longos, citação literal de lei
  não verificada ou marcadores residuais — reprovação dispara a auto-revisão P3.
- **Chrome do editor** (EMENTA destacada, bloco de assinaturas, anotações coloridas) é
  *decoration* do TipTap, nunca conteúdo — o mesmo documento alimenta o DOCX canônico.
- **Ações de IA são restritas a administradores** (`app/utils/auth_guard.py`); os demais
  advogados editam manualmente e colaboram por anotações.

## Testes

Backend (a partir de `backend/`, com as dependências de `requirements.txt`):

```bash
DATABASE_URL=sqlite+aiosqlite:///:memory: ANTHROPIC_API_KEY=dummy ENV=test \
  pytest tests/ --ignore=tests/test_pipeline_stability.py
```

> `test_pipeline_stability.py` exercita o pipeline com chamadas que podem ser lentas;
> os demais arquivos rodam em segundos, sem rede e sem banco externo.
> Não defina `JWT_SECRET` ao rodar os testes localmente — o conftest usa o default.

Frontend (a partir de `frontend/`):

```bash
npm ci
npx tsc --noEmit   # checagem de tipos
npx vitest run     # testes unitários
npm run test:e2e   # Playwright (requer a stack docker no ar)
```

O CI (`.github/workflows/ci.yml`) roda lint (ruff + tsc), testes de backend (unit e
integração com Postgres), vitest, build do frontend, E2E e auditorias de dependências.

## Estrutura do repositório

```
backend/
  app/
    routers/          # endpoints (auto-descobertos)
    services/         # pipeline, extração, auditor, Gmail, DOCX, e-mail
    models/ schemas/  # SQLAlchemy / Pydantic
  prompts/            # prompts P1/P1.5/P2/P3
  skills/             # bases de conhecimento jurídico (jurisprudência, manuais)
  leis_municipios/    # legislação local por município
  alembic/            # migrations
  tests/
frontend/
  src/
    components/       # editor, dashboard, lista de pareceres, layout
    hooks/ services/  # React Query + clientes da API
docs/MANUAL_USUARIO.md
DEPLOY.md
docker-compose.yml / docker-compose.prod.yml
```
