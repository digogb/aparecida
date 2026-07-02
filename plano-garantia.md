# Plano — Correções da auditoria cobertas pela GARANTIA (9 itens)

## STATUS DE IMPLEMENTAÇÃO (2026-07-02) — todos os grupos implementados, NÃO commitado
- **Grupo A (prompts 2.1/2.2/3.1/3.2/3.3/3.4 + salvaguarda D):** feito nos 2 prompts P2
  (`p2_parecer_lei_14133.txt` regras: citação literal, anti-inversão de teor, conectivo "Há" no ★2,
  art×conteúdo, ausência de documento, **IRR-6** calibragem de zelo; `p2_parecer_municipal_geral.txt`:
  ZT-1b/ZT-2b/ZT-2c + **IRR-5** calibragem de zelo + ★2). Fecho "É o parecer." em TODAS as camadas:
  `docx_generator.py:579`, prompts, `SignatureBlock.ts` (FECHO + `docHasFecho` cobre novo+legado),
  skills/*.md, examples_*.md, tests. "Avancemos"→"Avançando" em prompts+skills.
- **Grupo B (Erro 3 — correção por trecho):** endpoint `POST /parecer-requests/{id}/correct-selection`
  (`routers/parecer_ia.py`), `parecer_engine.correct_selection`, `parecer_ai_service.correct_selection`
  (P3-trecho, max_tokens=2000, sem web_search); frontend: `editorApi.correctSelection`, botão "Corrigir
  seleção" na `EditorToolbar` (desabilitado sem seleção), `SelectionCorrectionModal` + handlers no
  `LegalEditor` que substituem SÓ o range via `insertContentAt({from,to}, corrigido)`.
- **Grupo C (item D — confirmação de envio):** `SendConfirmModal` no `LegalEditor`, botão "Aprovar e
  enviar"/"Enviar" abre o diálogo (destinatário/assunto/resumo) antes do `approve-and-send`.
- **Grupo D (2.3):** já estava resolvido pelo caps raise; adicionada a salvaguarda de prompt (Passo 2)
  dentro do Grupo A.
- **Verificação:** backend `pytest tests/` = 372 passed, mesmas 5 falhas pré-existentes (zero regressão);
  frontend `tsc --noEmit` OK + 18 vitest OK; prompts carregam com as regras novas e o fecho novo.
  Endpoint correct-selection validado end-to-end no container (só bloqueou no **saldo de créditos da
  conta Anthropic esgotado** — billing, não é código).
- **PENDENTE:** (a) recarregar créditos Anthropic e **regenerar 2-3 casos reais** p/ validar visualmente
  a calibragem do Grupo A (ausência de "Há" repetido, `[REVISAR]`/`[!VERIFICAR]` no lugar de citação não
  confirmada, sem crítica à Comissão, fecho novo); (b) smoke manual do editor (Corrigir seleção) e do
  envio (confirmação); (c) **commit + push + deploy** (backend usa imagem baked em prod → rebuild).

## Context
O cliente (Dr. Matheus) enviou o **Relatório de Auditoria** (`Relatorio_Auditoria_Pareceres.pdf`,
19 pontos). A resposta contratual (`resposta_auditoria_ione.docx`) classificou cada ponto contra o
escopo do **Contrato nº 02/04/2026** e a **garantia de 30 dias (Cláusula 6ª)**: **9 são correção
coberta** (bug/calibragem dentro do escopo) e **10 são funcionalidade nova (Fase 2, orçamento à
parte)**. Este plano cobre **apenas os 9 itens de garantia** — os de Fase 2 (exclusão por perfil,
relatório mensal/exportação, controle de acesso por perfil, reconhecimento de thread¹, anotações
colaborativas persistentes, OCR, filtro/paginação/busca, painel de tokens) **ficam fora**.

> ¹ Nota: o "reconhecimento de resposta em thread" (Erro 4) foi classificado como Fase 2 pelo
> escritório, mas o dedup por thread **já foi implementado** nesta base (commit `22d3a8b`,
> ver `plano-thread.md`). Não faz parte deste plano.

Marcadores neutros `[REVISAR — ...]` já existem e são **aceitos** pelo auditor mecânico
(`auditor_mecanico.py` só reprova os de "parte adversa"). Os itens de conteúdo/redação são
**calibragem sobre mecanismo existente** — sem mudança no gate.

## Os 9 itens (referência: Seção 2 / TABELA 2 da resposta)

| Ref | Item | Tipo | Grupo |
|---|---|---|---|
| 2.1 | Citação literal de lei inventada entre aspas (art. 107, 14.133) | prompt | A |
| 2.2 | Jurisprudência atribuída errada (teor do acórdão) | prompt | A |
| 3.1 | Repetição de "Há" no início de frases | prompt | A |
| 3.2 | Fecho → "É o parecer." | prompt+código | A |
| 3.3 | Excesso de zelo: minuta de aditivo / crítica à Comissão | prompt | A |
| 3.4 | Ajustes pontuais + conferência artigo×conteúdo | prompt | A |
| Erro 3 | Correção IA apaga edições → por trecho selecionado | bug editor | B |
| D | Falta confirmação antes de enviar email | bug UX | C |
| 2.3 | Documento dado como ausente que estava no processo | bug pipeline | D |

---

## GRUPO A — Calibragem dos prompts P2 (itens 2.1, 2.2, 3.1, 3.2, 3.3, 3.4)
Editar **ambos** os prompts (a IA usa um ou outro conforme a vertente):
`backend/prompts/p2_parecer_lei_14133.txt` e `backend/prompts/p2_parecer_municipal_geral.txt`.
Reforço de regras já existentes; nenhuma mudança de gate.

- **2.1 (lei inventada entre aspas):** endurecer a regra da L178 (`p2_lei`). Regra dura: **nunca**
  colocar texto de artigo entre aspas/`> blockquote` como transcrição literal sem confirmação de
  fonte; na dúvida, **parafrasear** OU marcar `[REVISAR — TEXTO LITERAL DO ART. X DA LEI Y NÃO
  CONFIRMADO. CONFERIR REDAÇÃO OFICIAL ANTES DA ASSINATURA.]`. Deixar explícito que citar número de
  artigo real com redação inventada é o pior caso (aparência de autenticidade).
- **2.2 (teor de jurisprudência):** estender a regra de ancoragem (L180-182). Hoje o `[REVISAR]` cobre
  *existência* do acórdão; passar a cobrir **teor/tese**: ao citar acórdão com número, a tese atribuída
  deve corresponder ao efetivamente decidido (confirmar via `web_search`); sem confirmação do teor →
  `[REVISAR — TEOR ATRIBUÍDO AO ACÓRDÃO X/Y NÃO CONFIRMADO. VERIFICAR SE O JULGADO FIRMOU ESTA TESE.]`.
- **3.1 (repetição de "Há"):** instrução de estilo — diversificar conectivos de abertura de período;
  evitar iniciar frases com "Há"/"Há, contudo,"; oferecer alternativas ("Com efeito", "Cumpre observar",
  "Deve-se ponderar que", "Nesse passo"). Encaixa no bloco de conectivos (★2, L133).
- **3.2 (fecho):** trocar `"É o parecer, submetido à superior consideração."` por `"É o parecer."`
  em: (a) prompts L124 e L280 (ambos os P2); (b) **`docx_generator.py:579`** `_adicionar_fecho` (é o
  gerador que imprime o fecho fixo); (c) referências nos `skills/**/*.md` (consistência — a IA lê skills);
  (d) `tests/test_docx_generator.py` e `tests/test_auditor_mecanico.py`. Conferir `export_service.py:119`
  (`conclusao_dispositivo` fallback) — alinhar redação se necessário.
- **3.3 (excesso de zelo):** dois padrões estruturais — (a) tratar **minuta de prorrogação/aditivo com
  campos em branco** (datas, valor, dotação) como **naturalmente incompleta** (o parecer antecede a
  assinatura) — não gerar parágrafos de alerta tratando como vício formal; (b) **conter críticas a
  fundamentos/julgados trazidos pela própria Comissão/Administração consulente** — o parecer é
  consultivo, não adversarial. Adicionar como regra IRR próxima às existentes (IRR-3/IRR-4).
- **3.4 (pontuais):** "Avancemos para" → "Avançando para"; reforçar **verificação de correspondência
  artigo × conteúdo nas citações do PRÓPRIO parecer** (não só da parte adversa — a IRR-3 cobre adversa),
  ex.: art. 42 da LC 101/2000 grifado como "não corresponde". Se não conferir, parafrasear ou `[REVISAR]`.

**Verificação Grupo A:** regenerar 2-3 casos reais de prod local (usar a receita de injeção do
`plano-thread.md` / memória `project_poller_thread_dedup`) e conferir: fecho novo, ausência de "Há"
repetido, marcadores `[REVISAR]` no lugar de citações não confirmadas, ausência de crítica à Comissão.
`pytest tests/test_auditor_mecanico.py tests/test_docx_generator.py`.

---

## GRUPO B — Correção IA por trecho selecionado (Erro 3)
**Sintoma:** "Solicitar correção para IA" / "Corrigir" descarta as edições anteriores (reescreve o
documento/seções inteiras). **Alvo (pedido do cliente):** corrigir **apenas o trecho selecionado**,
preservando o resto.

Fluxo atual: `parecer_ia.py` `preview_correction`/`apply_correction` → `parecer_engine.py:640/701`
(correção por **seção**, `secoes_aprovadas`) → nova versão a partir do P3. O que sobrescreve edições
manuais.

- **Backend:** novo endpoint `POST /parecer-requests/{id}/correct-selection` em `routers/parecer_ia.py`
  recebendo `{ trecho: str, instrucao: str }` e retornando **só o trecho corrigido** (`{ corrigido: str }`).
  Nova função em `parecer_engine.py` (ex.: `correct_selection`) que chama a IA (`parecer_ai_service`)
  com um prompt curto de **correção pontual** — recebe o trecho + instrução, devolve o trecho reescrito,
  sem tocar no resto do documento. Reusa `MODEL_P2_P3` (sem web_search por padrão; barato).
- **Frontend** (`components/editor/LegalEditor.tsx` + `EditorToolbar.tsx`): o botão "Corrigir" passa a
  operar sobre a **seleção atual** do TipTap. Envia `state.doc.textBetween(from,to)` + a instrução;
  ao receber, substitui **apenas o range selecionado** por transação TipTap (`chain().insertContentAt`
  / `replaceRange`) — **não recarrega o documento**, preservando edições manuais e demais trechos.
  `content_tiptap` continua canônico ([[project_editor_display_layer]]).
- Manter o fluxo por seção existente (P3) como opção; o **default** do botão vira o modo por trecho.
- Persistência: após aplicar, salvar via `update_version` (PUT já existente) para criar/atualizar a versão
  — garante que a edição incremental não se perde.

**Fora do escopo aqui:** restringir o botão a Matheus/Ione (controle de acesso por perfil = Fase 2, item
3.3 da resposta). Só o **bug** (por trecho, sem reescrever tudo) é garantia.

**Verificação Grupo B:** no editor local, editar manualmente um parágrafo, selecionar outro trecho,
pedir correção → só o trecho muda; a edição manual permanece; versão salva.

---

## GRUPO C — Confirmação antes de enviar por email (D)
**Sintoma:** `approve_and_send` (`routers/export.py:157`) dispara o email ao clicar "Enviar", sem
confirmação. Ação irreversível.

- **Frontend:** antes de chamar `approve-and-send`, abrir **diálogo de confirmação** mostrando:
  **destinatário** (`sender_email` do request), **assunto** e **resumo** (nº do PAR + município + tema).
  Só chama o endpoint após "Confirmar envio". Onde: no componente que hoje dispara o envio
  (`EditorSidebar.tsx` / `EditorToolbar.tsx` — o botão "Enviar"/"Solicitar correção" está nesses).
- **Backend (opcional):** endpoint leve `GET /parecer-requests/{id}/send-preview` retornando
  `{ destinatario, assunto, resumo }` para popular o diálogo; ou o frontend monta com dados já
  disponíveis no `ParecerRequest`. Preferir o frontend se os dados já estão carregados.

**Verificação Grupo C:** clicar "Enviar" → diálogo com destinatário/assunto/resumo → cancelar não
envia; confirmar envia (checar via mock/log do `email_sender`).

---

## GRUPO D — Documento dado como ausente / 2.3 (JÁ RESOLVIDO por truncamento — revisado)
**Sintoma:** parecer da Banda "Desejo de Menina" (PAR-2026-0035) declarou ausentes minuta/TR/instrumento
de exclusividade que **estavam** no processo.

**Diagnóstico feito em prod (2026-07-02) — causa confirmada = TRUNCAMENTO, não thread nem OCR:**
- A consulta é **1 e-mail com 1 único anexo** (thread `19ef0bd8930483a7`, 2 msgs: consulta + resposta do
  escritório). **NÃO houve resposta em thread trazendo documentos** → o fix de dedup/irmão (`22d3a8b`)
  **não** era o caminho aqui.
- O anexo `INEX Nº 009...DESEJO DE MENINA.pdf` (14,6 MB) foi extraído com `extraction_status=success` e
  **343.173 chars** (≈172 págs × 2k — o processo inteiro, **legível/digital**). **OCR não é necessário**
  (Achado A/Fase 2 não se aplica a este caso).
- PAR-2026-0035 foi gerado em 23/jun, quando `MAX_USER_CONTENT_CHARS = 180.000` valia p/ o P2 → o PDF de
  343k foi **cortado a 180k**, perdendo as **últimas páginas** (onde estavam minuta/TR/exclusividade — o
  revisor anotou "veio nas últimas páginas"). Truncamento clássico.

**Já corrigido (nesta base) — pelo fix de caps, não pelo de threads:** o P2 agora usa
`MAX_P2_USER_CONTENT_CHARS = 1.500.000` (Sonnet 5, commit **`655ada6`**; ver
[[project_limites_contexto_anexos]] + water-filling [[project_anexos_truncados_prompt]]). Agora
343k << 1,5M → o PDF inteiro entra, incluindo as últimas páginas. **Portanto o 2.3 já está tratado no
código atual — falta só validar e (opcional) endurecer o prompt.**

- **Passo 1 — VALIDAR (recomendado):** reprocessar o caso Banda local (buscar o anexo via prod, injetar
  com a receita da memória `project_poller_thread_dedup`) com o código atual e conferir que a IA
  reconhece a minuta/TR/exclusividade (ou ao menos não afirma ausência).
- **Passo 2 — salvaguarda de prompt (baixo esforço, garantia):** instruir a IA a **não afirmar ausência
  de documento** quando o parecer se apoiar em anexos volumosos — na dúvida, usar
  `[REVISAR — CONFERIR SE O DOCUMENTO X CONSTA NOS ANEXOS; A LEITURA PODE TER SIDO PARCIAL.]` em vez de
  concluir pela ausência (mesma filosofia de 2.1/2.2). Rede de segurança para futuros PDFs > 1,5M chars.
- **Fora de escopo (Fase 2):** OCR de PDFs escaneados (Achado A / item 3.6) — não se aplicou a este caso,
  mas segue como Fase 2 para consultas efetivamente digitalizadas/ilegíveis.

**Resumo:** o Grupo D deixa de ter trabalho estrutural de garantia (o bug já foi corrigido pelo caps
raise). Resta **validar** o caso Banda e, opcionalmente, o **Passo 2** (salvaguarda de prompt, que na
prática entra no Grupo A). Não confundir com o fix de threads (Erro 4), que é outro caminho.

---

## Ordem sugerida e esforço
1. **Grupo A** (prompts) — maior impacto jurídico, menor risco técnico; edições de texto + tests.
2. **Grupo C** (confirmação de envio) — pequeno, alto valor, frontend.
3. **Grupo B** (correção por trecho) — médio; backend endpoint + editor TipTap.
4. **Grupo D** (anexos) — diagnóstico primeiro; parte pode ser Fase 2 (OCR).

## Fora de escopo (Fase 2 — NÃO implementar aqui)
Erros 1, 2, 5 e Achados A(OCR), B, C, F, H; controle de acesso por perfil (parte do Erro 1 e 3);
reconhecimento de thread (Erro 4, já feito à parte). Cada um vira proposta comercial própria.

## Verificação global
- Backend: `pytest tests/` (baseline atual tem 5 falhas pré-existentes não relacionadas — ver
  `project_poller_thread_dedup`).
- Regenerar casos reais de prod local (Araripe/Salitre/Banda) e conferir os itens de A e D na tela.
- Frontend: `npx tsc --noEmit` + `npx vitest run`; smoke manual do editor (B) e do envio (C).
