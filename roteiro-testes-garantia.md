# Roteiro de Testes — Correções da Garantia (auditoria)

> Ambiente local: **http://localhost:5173** (frontend) · backend :8000 · Postgres :5432.
> Se algo não subir: `docker compose up -d` na pasta `ione/`.
>
> **Login:** qualquer usuário com senha **`123456`**.
> Admin: **harvey@pearsonhardman.com** · Advogado: mike@pearsonhardman.com · Secretaria: donna@pearsonhardman.com
>
> **Pareceres disponíveis** (status `gerado` = abrem no editor):
> PAR-2026-0004 e 0005 (Araripe/Locação — 0005 é o irmão com o laudo) ·
> PAR-2026-0006 e 0007 (Salitre/Arbitragem — 0007 é o irmão com Nota Técnica) ·
> PAR-2026-0001, 0003.
>
> **Legenda:** 🟢 = testável sem consumir API · 🔴 = precisa de **crédito Anthropic** (recarregado ✅).

---

## BLOCO 0 — Pré-requisitos
- [ ] Abrir http://localhost:5173, fazer login (harvey@pearsonhardman.com / 123456).
- [ ] A lista de Pareceres carrega e mostra os PAR-2026-000x.
- [ ] (Regressão do fix anterior) PAR-0004/0005 e PAR-0006/0007 aparecem com o badge **"rodada 1/2" / "2/2"** (mesma thread).

---

## BLOCO 1 — Grupo A: Fecho "É o parecer." 🟢

### 1.1 — Fecho no editor
- [ ] Abrir **PAR-2026-0004** (ou qualquer `gerado`).
- [ ] Rolar até o fim da Conclusão, antes do bloco de assinaturas.
- [ ] **Esperado:** o fecho exibido é **"É o parecer."** (curto), **não** "É o parecer, submetido à superior consideração.".
- [ ] **Não pode** aparecer o fecho duplicado (uma vez no texto + uma vez no bloco de assinatura).

### 1.2 — Fecho no DOCX exportado
- [ ] No editor, exportar em **DOCX**.
- [ ] Abrir o arquivo. **Esperado:** o parágrafo de fecho é **"É o parecer."**, seguido das assinaturas.

### 1.3 — Fecho no PDF exportado
- [ ] Exportar em **PDF**. **Esperado:** mesmo fecho **"É o parecer."**.

> Observação: pareceres **antigos** (gerados antes da mudança) têm o texto longo salvo no conteúdo;
> o editor esconde o fecho legado para não duplicar. O importante é: **nada duplicado** e, em pareceres
> novos, o fecho curto. Se algum antigo mostrar o fecho longo no corpo, é esperado (é o conteúdo salvo).

---

## BLOCO 2 — Grupo A: Calibragem de conteúdo 🔴 (crédito recarregado ✅)
> Só aparece ao **gerar/regenerar** um parecer. Já validado no **PAR-2026-0002** (regenerado): fecho novo,
> 0 "Há", 0 "Avancemos", marcador `[!VERIFICAR:]` de cautela, sem excesso de zelo. Para revalidar, abra o
> PAR-2026-0002 ou regenere Araripe/Salitre (receita na memória / plano-thread).

- [ ] **3.1 (conectivo):** o parecer **não** inicia frases repetidamente com "Há" / "Há, contudo,".
- [ ] **2.1 (lei):** nenhuma redação de artigo entre aspas sem confirmação — quando incerto, vem
      parafraseado ou com marcador `[REVISAR — ...]` / `[!VERIFICAR: ... !]`.
- [ ] **2.2 (jurisprudência):** acórdão citado com número → a tese atribuída confere; sem confirmação
      do teor, vem marcador em vez de afirmação categórica.
- [ ] **3.3 (zelo):** parecer de aditivo/prorrogação **não** trata campos em branco da minuta como vício;
      **não** critica fundamentos/julgados trazidos pela própria Comissão/consulente.
- [ ] **3.4:** usa "Avançando para..." (não "Avancemos para..."); artigos citados correspondem ao conteúdo.
- [ ] **2.3 (anexo):** com anexo volumoso, se um documento não for localizado, vem `[REVISAR]` em vez de
      afirmar categoricamente que "não foi juntado".

---

## BLOCO 3 — Grupo B: Correção por trecho selecionado (Erro 3)

> **Onde ficam os botões (após reorganização):** na **toolbar** existe só **"Realçar trecho"**
> (realça trecho, não corrige). No **rodapé** ficam as duas ações que chamam IA, lado a lado:
> **"Reescrever seções (IA)"** (correção ampla: reescreve seções inteiras) e **"Corrigir só a seleção (IA)"**
> (reescreve só a seleção). Ver comparação no BLOCO 6.

### 3.1 — Fluxo/UI 🟢
- [ ] Abrir um parecer `gerado` no editor.
- [ ] **Sem** nada selecionado: o botão **"Corrigir só a seleção (IA)"** no **rodapé** (verde) está **desabilitado**.
- [ ] **Selecionar** um trecho (uma frase/parágrafo): o botão **habilita**.
- [ ] Clicar em "Corrigir só a seleção (IA)": abre o modal mostrando **o trecho selecionado** + campo de instrução.
- [ ] O botão "Aplicar correção" fica **desabilitado** enquanto a instrução estiver vazia.
- [ ] "Cancelar" fecha sem alterar nada.

### 3.2 — Preservação de edições (o coração do Erro 3) 🔴 (o "Aplicar" chama IA)
- [ ] **Edite manualmente** um parágrafo A (ex.: troque uma palavra). Não salve ainda.
- [ ] Selecione um **outro** trecho B, "Corrigir só a seleção (IA)", escreva uma instrução (ex.: "deixe mais conciso"),
      "Aplicar correção".
- [ ] **Esperado:** **apenas o trecho B** muda; a sua edição manual no parágrafo A **permanece**; o resto do
      documento fica intacto (não recarrega/reescreve tudo). Este é o comportamento que o cliente pediu.
- [ ] Salvar e reabrir: as duas alterações persistem.

> ⚠️ Hoje, ao clicar "Aplicar correção", a chamada de IA **falha por falta de crédito** (mensagem de erro).
> O fluxo/seleção/modal (3.1) você valida agora; a reescrita real (3.2) só com crédito.

---

## BLOCO 4 — Grupo C: Confirmação antes de enviar (item D) 🟢

### 4.1 — Diálogo de confirmação
- [ ] Abrir um parecer e aprovar (se necessário) até ter o botão **"Aprovar e enviar"** / **"Enviar"**.
- [ ] Clicar em "Aprovar e enviar".
- [ ] **Esperado:** abre um **diálogo de confirmação** mostrando **Destinatário** (e-mail do remetente),
      **Assunto** ("Re: ...") e **Resumo** (nº do PAR · município · tema).
- [ ] **"Cancelar"** fecha e **não envia** (nenhum e-mail disparado).

### 4.2 — Destinatário ausente
- [ ] Se o parecer não tiver e-mail de remetente: o diálogo mostra o aviso em vermelho e o botão
      **"Confirmar envio"** fica **desabilitado**.

> Não clicar em "Confirmar envio" em teste, salvo se `GMAIL_TEST_RECIPIENT` estiver configurado —
> senão dispara e-mail real ao remetente.

---

## BLOCO 5 — Regressão (não quebrou nada) 🟢
- [ ] Abrir/editar um parecer, digitar texto, **Salvar** → status "Salvo".
- [ ] Exportar DOCX e PDF → abrem sem erro, com assinaturas e formatação normais.
- [ ] Realçar trecho ("Realçar trecho") + "Reescrever seções (IA)" — fluxo por seção continua existindo.
- [ ] Badge "rodada N/M" segue aparecendo nos irmãos de thread (BLOCO 0).

---

## BLOCO 6 — Os 3 controles de correção (entenda a diferença) 🟢
A diferença entre os dois botões-IA é **quanto** cada um reescreve:
| Controle | Onde | O que faz |
|---|---|---|
| **Realçar trecho** | Toolbar | Só **realça** (amarelo). Não corrige nada sozinho — apenas sinaliza os pontos para o "Reescrever seções". |
| **Reescrever seções (IA)** | Rodapé | Correção **ampla**: reescreve **seções inteiras** (Ementa/Relatório/Fundamentos/Conclusão) que contêm os trechos realçados. Pode mudar texto além do que você marcou — bom p/ revisões grandes. |
| **Corrigir só a seleção (IA)** | Rodapé | Correção **pontual**: reescreve **apenas o trecho selecionado**, preservando todo o resto (inclusive suas edições). É a correção do Erro 3 da auditoria. |

- [ ] Toolbar tem só **"Realçar trecho"** (não há mais botão de correção-IA na toolbar).
- [ ] Rodapé tem os dois botões-IA lado a lado: **"Reescrever seções (IA)"** (amarelo, com contador de
      realces) e **"Corrigir só a seleção (IA)"** (verde, habilita ao selecionar um trecho).

## Resumo do que dá para validar HOJE (sem crédito)
✅ Fecho "É o parecer." (editor + DOCX + PDF) · ✅ UI da correção por seleção (botão, modal, seleção) ·
✅ Diálogo de confirmação de envio · ✅ Regressão (salvar/exportar/badge).

## O que fica para quando recarregar os créditos Anthropic
🔴 Calibragem de conteúdo do Grupo A (regenerar casos) · 🔴 Reescrita real do trecho (Grupo B, "Aplicar").
