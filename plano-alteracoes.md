# Plano — Alterações do piloto (03/07/2026)

Branch de trabalho: `entrega-cliente`. Prod usa imagem baked → rebuild no deploy.
Numeração espelha as mensagens do Dr. (itens 2 a 6).

## STATUS — IMPLEMENTADO + COMMITADO `8b674ba` (03/07/2026, local no ar; NÃO pushado/deployado)
Todos os 5 itens feitos e validados local: `tsc` 0 erros; backend unit 80/80 + acesso 15/15
(2 testes de "gap" viraram testes de exigência de admin). As 8 falhas do vitest
(`parecerApi.test.ts`/`useParecer.test.ts`, ERR_NETWORK do MSW) são **pré-existentes** (confirmado
por baseline com `git stash`). Migration **0014** aplicada no banco local. Smoke test das anotações
(login→POST→GET→DELETE) e do endpoint de municípios OK.
- **2** IA só-admin: `require_admin` (`app/utils/auth_guard.py`) nos endpoints de IA de `parecer_ia.py`
  + `reprocess` de `parecer.py`; botões de IA/reprocesso escondidos p/ não-admin (`isAdmin`);
  `seeds.py` Matheus=admin + `backend/scripts/promote_matheus_admin.py` (rodar em prod).
- **3** filtro município: `GET /api/parecer-requests/municipios` (distinct, **precisa** `.select_from`)
  + chips no `ParecerFilters` + campo `municipio` no state/tipo/service.
- **4** card "Enviados no mês": `enviados_mes` no overview/schema + 3º card no dashboard.
- **5** title-case display: `utils/formatTitle.ts` (+teste) em ParecerCard/dashboard/editor header.
- **6a** anotações inline: modelo `ParecerAnnotation`+migration 0014, `routers/annotations.py`,
  `services/annotation_colors.py`, extensão `AnnotationHighlight.ts` (decoration), `AnnotationsPanel.tsx`,
  modal "Anotar trecho", integração no `useEditor`/`LegalEditor`/`EditorSidebar`.
- **6b** removido peer review+notificação da UI (botões/modais/`PeerReviewPanel`/`NotificationBell`);
  backend e tabelas `peer_reviews`/`notifications` ficam dormentes (não dropados).

**PENDENTE:** push → backup do banco de prod → deploy
(`docker compose -f docker-compose.prod.yml up -d --build backend frontend`) → aplicar 0014 em prod
→ rodar `promote_matheus_admin.py` em prod. Ver `reference_ione_prod_deploy`.

---


---

## 2. IA só para admin; Matheus e Ione admin

**Regra:** somente `role == admin` pode disparar IA. Ione já é admin; **promover Matheus a admin**.
Flávio/Valéria (advogado) e secretaria seguem sem IA — editam manualmente, pedem revisão, exportam.

### Backend
- Extrair helper de auth para reuso (hoje `_require_admin` existe só em `routers/parecer.py`).
  Criar `app/utils/auth_guard.py` (ou manter em cada router) com `require_admin(credentials)`.
- Gatear com `Depends(bearer)` + `require_admin` os endpoints que chamam a API Anthropic:
  - `routers/parecer_ia.py`: `classify`, `generate`, `preview-correction`, `apply-correction`,
    `correct-selection`.
  - `routers/parecer.py`: `reprocess` (redispara pipeline P1→P3).
  - **NÃO** gatear: `update_version`/`snapshot` (edição manual), peer review (colega revisa sem IA),
    export/approve-and-send, retry-extraction. O pipeline automático do poller não passa por esses
    endpoints — continua gerando na ingestão normalmente.
- `seeds.py`: mudar Matheus para `UserRole.admin` (só afeta banco novo/vazio).

### Migração de dados (prod + local já populados)
- `seeds` não roda com tabela cheia → script idempotente para promover Matheus:
  `UPDATE users SET role='admin' WHERE lower(email)=lower('Matheuspl20@hotmail.com')`.
  Rodar local agora e em prod no deploy (via `docker compose exec ... backend python -`).

### Frontend
- `EditorToolbar.tsx`: esconder botões de IA para não-admin — "Reescrever seções (IA)",
  "Corrigir só a seleção (IA)", e o disparo de geração/reprocesso. Usar `useCurrentUser().role==='admin'`
  (mesmo padrão do botão excluir). Editor de texto e "Realçar trecho" continuam para todos.
- `ParecerCard.tsx`: botão verde de reprocessar (status `erro`) → só admin.
- Como o backend valida no servidor (403), esconder no front é UX; a trava real é a do backend.

**Teste:** logar como Flávio (advogado) → botões de IA ausentes; chamada direta ao endpoint → 403.
Logar como Matheus → agora admin, IA disponível.

---

## 3. Filtro por município na lista de pareceres

Backend **já** aceita `?municipio=` (`routers/parecer.py:list_parecer_requests`, ilike em
`classificacao->>'municipio'`). Falta a fonte de opções + UI.

### Backend
- Novo endpoint leve `GET /api/parecer-requests/municipios` → lista distinta de
  `classificacao->>'municipio'` (não-nulo), ordenada. (Município real vem da classificação da IA,
  não da tabela `municipios`, que tem placeholders SP.)

### Frontend
- `types/parecer.ts`: add `municipio: string` em `ParecerFiltersState`; `EMPTY` em `ParecerList.tsx`.
- `services/parecerApi.ts`: incluir `params.municipio` quando setado.
- `ParecerFilters.tsx`: novo bloco "Município" (chips ou select) alimentado pelo endpoint novo
  (`useQuery`). Selecionar/limpar troca o filtro; `handleFiltersChange` já reseta a página.
- `hasActiveFilter` passa a considerar `filters.municipio`.

**Teste:** selecionar Araripe → lista e paginação refletem só Araripe.

---

## 4. Card "Enviados no mês" no dashboard

Definição escolhida: status `enviado`, por `updated_at`, dentro do mês corrente (fuso America/Fortaleza).

### Backend (`routers/dashboard.py` + `schemas/dashboard.py`)
- Calcular janela do mês local: `month_start_local = now_local.replace(day=1, hour=0,...)`,
  `month_end_local` = primeiro dia do mês seguinte; converter p/ UTC (mesmo padrão da janela semanal).
- Query: `count(*) WHERE status='enviado' AND updated_at >= month_start AND < month_end`.
- Add campo `enviados_mes: int` em `PareceresOverview`.

### Frontend (`DashboardPareceresPage.tsx` + `types/dashboard.ts`)
- Seção "Resumo geral" hoje é `grid-cols-2` (Em aberto / Concluídos na semana).
  Add 3º card "Enviados no mês" → `grid-cols-2 md:grid-cols-3` (ou 3 colunas). Cor sóbria (ex. `#142038`).

**Teste:** marcar um parecer como enviado hoje → card incrementa; enviado mês passado não conta.

---

## 5. Ajustar maiúsculas nos nomes dos pareceres

Assuntos chegam em CAIXA ALTA do e-mail (ex.: "SOLICITAÇÃO DE PARECER JURIDICO LOCAÇÃO SDTS").
Correção **só de exibição** — não mutar o banco (o assunto original é dado do e-mail).

### Frontend
- Novo util `utils/formatTitle.ts` → `formatParecerTitle(subject)`:
  - Só transforma quando a string é predominantemente maiúscula (evita mexer em título já correto).
  - Title Case pt-BR: primeira letra de cada palavra maiúscula, preposições/artigos curtos minúsculos
    (`de, da, do, das, dos, e, a, o, para, com, em, no, na`), exceto na 1ª palavra.
  - Preservar tokens claramente siglas/números (ex.: `SDTS`, `nº 3103005/2025`) — heurística:
    palavra sem vogal ou com dígito fica como está.
- Aplicar em: `ParecerCard.tsx` (assunto), `DashboardPareceresPage.tsx` (OldestList), e nos modais
  de revisão onde o assunto aparece. Não aplicar a `numero_parecer`.

**Teste:** card mostra "Solicitação de Parecer Jurídico Locação SDTS".

---

## 6. Anotações inline (SUBSTITUI o fluxo de revisão + notificação)

Decisão do Dr. (03/07): o modelo de "solicitar revisão a um revisor + notificação" não faz sentido
(todos editam o mesmo doc). Substituir por **anotações inline**: um advogado marca um trecho e escreve
um **questionamento**; qualquer advogado que abrir o parecer vê o trecho realçado e, no hint, o
questionamento. **Cor por autor.** Escopo mínimo: **só marca + pergunta** (sem respostas encadeadas,
sem estado de "resolvido"); apagar a anotação para limpar.

### Modelo de dados (nova tabela — migration 0014 sobre a 0013)
`parecer_annotations`:
- `id` UUID pk · `request_id` FK→parecer_requests (index) · `author_id` FK→users (index)
- `trecho_texto` Text (texto marcado — usado p/ re-ancorar no editor e listar no painel)
- `questionamento` Text · `created_at`
- SEM `resolvido`/replies (escopo mínimo). Pertence ao **request**, não à versão → persiste entre versões.

**Regra crítica:** a anotação NÃO entra no `content_tiptap` (é o canon do DOCX — vazaria no parecer
exportado). Fica só na tabela e é renderizada como decoration. Mesma regra da camada de exibição
(`project_editor_display_layer`).

### Backend (novo `routers/annotations.py`, auto-discovery)
- `GET  /api/parecer-requests/{id}/annotations` → lista (com `author_name` e `author_color`).
- `POST /api/parecer-requests/{id}/annotations` `{trecho_texto, questionamento}` → autor vem do JWT.
- `DELETE /api/annotations/{annotation_id}` → autor da anotação **ou** admin.
- **Cores (paleta fixa no backend):** módulo `app/services/annotation_colors.py` com mapa por e-mail —
  Ione=amarelo `#FDE68A`, Matheus=azul-claro `#BFDBFE`, Flávio=verde `#BBF7D0`, Valéria=roxo `#DDD6FE`,
  fallback neutro. Retornado em cada anotação (sem alterar schema de `users`).

### Frontend
- Nova extensão **`AnnotationHighlight.ts`** (decoration, nunca marca): recebe as anotações
  `[{trecho, color, hint:"<Autor>: <questionamento>"}]`, casa o texto de forma robusta
  (reusar `buildNormalizedDocMap`/`normalizeForMatch`), desenha `Decoration.inline`
  (fundo = cor do autor, `cursor:help`, `title=hint`). Recalcula a cada `docChanged`.
- `useEditor`: buscar anotações (react-query, key `['annotations', parecerId]`) e alimentar a extensão
  via storage/command (padrão do `setSignatureDataLine`). Invalida ao criar/apagar.
- **Adicionar:** selecionar texto → botão "Adicionar questionamento" na toolbar → modal com o trecho
  selecionado + textarea → `POST`. (Ocupa o lugar do antigo "Solicitar revisão".)
- **Painel `AnnotationsPanel.tsx`** (no lugar de `PeerReviewPanel`/`RevisaoMarkersPanel` de revisão):
  lista as anotações com bolinha da cor do autor + questionamento; clicar rola até o trecho; botão
  apagar (autor/admin). Anotações cujo trecho não casa mais → seção "Trecho não localizado".

### Remoção do fluxo antigo (substituição)
- Frontend: remover botão/modal "Solicitar revisão", `PeerReviewPanel`, `ReviewResponseModal`,
  `CompletedReviewModal`, `NotificationBell` (Topbar) e o uso de `useParecerWebSocket`.
- Backend: parar de registrar notificações de peer review; endpoints de peer review saem do fluxo.
  A tabela `peer_reviews`/`notifications` pode ficar **dormente** (não dropar já — menos risco de
  migration); dropar depois se o Dr. quiser. `ws_manager`/`get_unread_count` são compartilhados —
  conferir antes de remover (ver `project_entrega_cliente_escopo`).

**Teste:** Matheus seleciona um trecho e escreve um questionamento → salvo azul-claro. Dr. Ione abre o
mesmo parecer → vê o trecho azul; hover mostra "Matheus: <questionamento>". Ione anota outro trecho →
amarelo. Editar o texto ao redor mantém o realce ancorado; apagar o trecho manda a anotação p/ o painel.

---

## Testes gerais e deploy
- Backend: `DATABASE_URL=sqlite+aiosqlite:///:memory: ANTHROPIC_API_KEY=dummy ENV=test pytest`
  (baseline tem 5 falhas pré-existentes sem relação — não são regressão).
- Frontend: `tsc` + `vitest`.
- Rebuild local: `docker compose up -d --build` para o Dr. validar.
- Deploy prod (após aprovação): commitar na `entrega-cliente`, push, backup do banco,
  `docker compose -f docker-compose.prod.yml up -d --build backend frontend`, rodar o UPDATE do Matheus.
  Ver `reference_ione_prod_deploy`.

## Ordem sugerida (menor risco → maior)
5 (display) → 4 (card) → 3 (filtro) → 2 (gating IA + Matheus admin) → 6 (marcações/decoração).
