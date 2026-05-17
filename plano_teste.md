Plano de testes — Ione Advogados
Princípios
Pirâmide de testes: muitos unitários, alguns de integração, poucos E2E.
Tudo automatizado em CI — nenhum teste é opcional num PR.
Feedback rápido: unitários em < 10s, integração < 2min, E2E < 10min.
Cobertura é guia, não meta: foco em caminhos críticos (auth, pipeline de parecer, editor, permissões).
Testes falham por motivo claro: nada de expect(x).toBe(true) genérico.
1. Backend — Python (FastAPI + pytest)
1.1. O que já existe
test_access_control, test_api_contracts, test_auth_security, test_classifier, test_export, test_extractor, test_pipeline_stability, test_routers_parecer, test_upload_security. Já cobrem os fluxos principais.

1.2. O que adicionar
Unitários (pytest, mocks):

app/services/* — cada service isolado, sem DB real. Mockar dependências externas (LLM, DJe search, storage).
app/models/* — validação de constraints, relações, defaults.
app/schemas/* — serialização/deserialização Pydantic, validações custom.
Utilitários de template (templates/) — renderização pura, sem IO.
Integração (pytest + TestClient + DB de teste):

Fluxo completo por router: criar → classificar → gerar → revisar → aprovar → exportar um parecer.
Multi-tenant: usuário A não vê parecer do usuário B.
WebSocket de notificações DJe — usar httpx.AsyncClient + websockets.
Migrations Alembic — teste que sobe DB do zero com alembic upgrade head em cada run.
Contratos (schemathesis ou pytest + OpenAPI):

Gera casos de teste automáticos a partir do OpenAPI do FastAPI.
Comando: schemathesis run http://localhost:8000/openapi.json --checks all.
Detecta discrepâncias entre schema e comportamento real.
Segurança:

test_upload_security.py e test_auth_security.py já existem — expandir com:
SQL injection nos filtros de lista.
JWT expirado/tampered/sem assinatura.
Path traversal no export.
Rate limit.
Ferramentas:

pytest-cov — meta de 80% em app/services, 90% em app/routers.
pytest-xdist — paralelização.
pytest-asyncio — rotas async.
factory-boy ou pytest-factoryboy — fixtures de dados sem boilerplate.
freezegun — testes dependentes de data/tempo.
respx ou httpx-mock — mock de HTTP externo.
Estrutura proposta:

backend/tests/
  unit/              ← rápido, sem DB
    services/
    schemas/
    utils/
  integration/       ← DB de teste, TestClient
    routers/
    flows/           ← fluxos ponta-a-ponta no backend
    websockets/
  contract/          ← schemathesis
  security/          ← pentest automatizado
  conftest.py        ← fixtures compartilhadas
2. Frontend — Unitários e de componente
2.1. Setup
npm i -D vitest @testing-library/react @testing-library/user-event \
         @testing-library/jest-dom jsdom msw @vitest/coverage-v8
vitest.config.ts com jsdom, setup file que carrega @testing-library/jest-dom e MSW server.

2.2. Unitários — o que testar
Hooks (src/hooks/):

useMediaQuery — mudanças de viewport, cleanup de listener.
useAuth — login, logout, refresh de token, expiração.
Hooks de React Query — estados de loading/error/success com MSW.
Utils/Services puros (src/services/):

Normalização de payloads API.
Formatação de datas, moedas, status.
Validação de formulários (se houver lógica custom).
Components de UI isolados (@testing-library/react):

Sidebar — rotas ativas, destaque visual.
StatusBadge — cada status renderiza cor correta.
ParecerCard — props → render; click → callback.
MobileDrawer (novo) — abre/fecha por prop, ESC fecha, click no backdrop fecha, foco fica preso dentro.
EditorToolbar — cada botão dispara comando correto no mock do editor.
Modais — abrir, fechar, submit, cancelar.
Regras:

Nunca testar implementação (estado interno, classes CSS). Testar comportamento visível ao usuário: "quando clico em salvar, o callback é chamado com o valor do input".
user-event > fireEvent.
MSW para qualquer chamada HTTP — nunca mockar fetch/axios direto.
2.3. Integração de componentes (ainda Vitest + RTL)
Fluxos dentro de uma página, sem subir o app inteiro:

Login: usuário digita credenciais → MSW responde token → redireciona para dashboard (mock do useNavigate).
ParecerList: renderiza lista da API, aplica filtro, vê contagem mudar.
Editor: carrega parecer, digita texto, clica salvar → PATCH correto é enviado.
Kanban: arrasta card de coluna A para B → PATCH /tasks/:id com novo status.
PeerReview: submete revisão → modal fecha e lista atualiza (invalidation do React Query).
Estrutura:

frontend/src/
  components/
    parecer/
      ParecerCard.tsx
      ParecerCard.test.tsx      ← ao lado do componente
  hooks/
    useAuth.ts
    useAuth.test.ts
  __tests__/
    flows/                      ← integração multi-componente
    fixtures/                   ← dados mockados
    msw/
      handlers.ts
      server.ts
Meta de cobertura: 70% linhas no total, 85% em hooks/ e services/. Não exigir cobertura de components/ puramente visuais.

3. Testes E2E / funcionais — Playwright
3.1. Setup
npm i -D @playwright/test
npx playwright install --with-deps chromium firefox webkit
3.2. Escopo — fluxos de negócio ponta a ponta
Cada teste roda contra o stack real (docker-compose de teste com DB seedado):

Autenticação

Login sucesso → dashboard.
Login inválido → mensagem de erro.
Logout → volta pro login.
Sessão expirada → redireciona.
Parecer (fluxo principal)

Criar parecer → upload PDF → classificação → geração → revisão por pares → aprovação → export Word.
Cada etapa em um teste separado + um teste "happy path completo".
Devolução no meio do fluxo: reviewer devolve → autor recebe alerta → corrige → reenvia.
Dashboard

Métricas batem com dados seedados.
Clicar num card filtra a lista.
Alertas aparecem e desaparecem após ação.
Kanban

Criar tarefa → aparece na coluna correta.
Arrastar entre colunas → persiste.
Editar tarefa → atualização reflete no card.
DJe

Nova movimentação chega via WebSocket → sino pisca.
Marcar como lida → contador decrementa.
Permissões

Usuário advogado não vê pareceres de outro advogado.
Usuário comum não acessa tela admin.
Tentativa de URL direta a recurso alheio → 403.
Regras Playwright:

Seletores por getByRole, getByLabel, getByText — nunca CSS classes.
test.step() para legibilidade.
trace: 'on-first-retry' e video: 'retain-on-failure' no CI.
Fixture de login autenticado (cookie/storage state salvo uma vez, reutilizado).
Dados via API de seed, não via UI (mais rápido e estável).
3.3. Cross-browser
Chromium (principal) + Firefox + WebKit, em 3 viewports: 375px (mobile), 768px (tablet), 1280px (desktop). Só rodar o conjunto completo em main e releases; PRs rodam só Chromium desktop.

4. Testes de interface — regressão visual e responsividade
4.1. Regressão visual (Playwright toHaveScreenshot)
Captura screenshot de cada rota principal em 375/768/1280.
Compara pixel a pixel contra baseline versionada.
Qualquer diff pede revisão humana (aprovação cria nova baseline).
Ignorar áreas voláteis (datas, avatares) com mask.
4.2. Responsividade (testes explícitos)
Testes dedicados a comportamento mobile:

Em 375px: sidebar não aparece, hamburger aparece, click abre drawer, click em item fecha drawer e navega.
Em 1280px: sidebar visível, hamburger escondido.
Em 375px no editor: split-view vira abas; toggle alterna "Original" ↔ "Editado".
Modais ocupam ~95vw em mobile.
Forms não têm scroll horizontal em 360px (assert scrollWidth === clientWidth no container).
4.3. Acessibilidade
npm i -D @axe-core/playwright
Em todo smoke test: await expect(page).toPassAxeTests().
Regras: WCAG 2.1 AA, touch-target-size ≥ 44px.
eslint-plugin-jsx-a11y ativo no eslint.config.js.
4.4. Performance (Lighthouse CI)
npm i -D @lhci/cli
Budgets:

Mobile Performance ≥ 80.
Accessibility ≥ 95.
Best Practices ≥ 90.
First Contentful Paint < 2s, Total Blocking Time < 300ms.
Roda nas rotas /, /pareceres, /pareceres/:id, /login.

5. Testes de contrato API ↔ frontend
Evita drift entre backend e frontend sem E2E caro.

Opção A (recomendada): gerar tipos TypeScript do OpenAPI do FastAPI.

npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
Rodar em pre-commit ou no CI; commit diff se houver mudança.
tsc vai pegar qualquer quebra de schema no frontend.
Opção B: Pact (consumer-driven contracts) — só se o time crescer. Complexo demais para agora.

6. Testes de carga e resiliência (backend)
Menos prioritário, mas importante antes de produção pesada:

k6 ou Locust — simular N usuários concorrentes criando/lendo pareceres.
Metas: p95 < 500ms nos endpoints de listagem, < 2s em upload de PDF 10MB.
Teste de soak (30min carga moderada) para detectar vazamento de memória.
Teste de spike (0 → 100 usuários em 10s).
7. CI — GitHub Actions
Pipeline proposto (.github/workflows/ci.yml):

on: [pull_request, push]
jobs:
  lint:              ← 1min     — eslint, ruff, tsc
  backend-unit:      ← 2min     — pytest unit/
  backend-integration: ← 5min   — pytest integration/ com Postgres em serviço
  frontend-unit:     ← 2min     — vitest
  frontend-build:    ← 2min     — tsc + vite build
  e2e:               ← 8min     — Playwright Chromium em docker-compose
  visual:            ← 3min     — Playwright screenshots
  a11y:              ← roda junto com e2e
  lighthouse:        ← 4min     — só em push para main
  security:          ← paralelo — npm audit, pip-audit, trivy na imagem
Regras:

PR não faz merge se qualquer job falhar.
Artefatos (trace do Playwright, coverage HTML) sobem como artifacts de 7 dias.
Cache agressivo de node_modules e .venv.
Testes de performance/soak em workflow separado, agendado (noturno).
8. Dados de teste
Backend:

Fixtures pytest com factory-boy — UserFactory, ParecerFactory, TaskFactory.
Banco de teste: SQLite em memória para unit, Postgres em container para integration.
Seed determinístico (seed=42) para reprodutibilidade.
Frontend:

MSW handlers centralizados em __tests__/msw/handlers.ts.
Fixtures de dados em JSON versionado, gerados uma vez via backend real (snapshot).
E2E:

API de seed (POST /api/testing/seed) disponível só em ENV=test, limpa e repopula DB.
Cada teste é isolado — beforeEach resetar estado.
9. Convenções
Nomenclatura: describe('ComponentName') > it('does X when Y'). Teste lido sem abrir código.
Arrange-Act-Assert explícito com linhas em branco.
Um assert principal por teste (pode ter auxiliares).
Zero sleep/waitForTimeout fixos — sempre waitFor com condição.
Sem flakiness tolerada — teste que falha intermitente vira issue, é consertado ou deletado.
Mock no limite do sistema, nunca no meio. Mock HTTP (MSW), não o hook que chama HTTP.
10. Cronograma sugerido
Semana	Entrega
1	Setup Vitest + RTL + MSW; 10 testes unitários de hooks e services. Setup Playwright + 8 smokes. CI com lint + unit + build.
2	Integração de componentes (login, ParecerList, Editor). Baseline visual das 4 rotas. Axe nos smokes.
3	E2E dos 3 fluxos críticos (parecer end-to-end, kanban, DJe WebSocket). openapi-typescript em pre-commit.
4	Responsividade: testes mobile explícitos, viewport matrix. Lighthouse CI com budgets.
5	Backend: expandir contract tests (schemathesis), preencher lacunas de cobertura em services.
6	k6 load test + soak. Documentação do README de testes. Consolidação do plano e revisão.