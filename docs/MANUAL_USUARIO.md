# Manual do Usuário — Sistema Ione

**Ione Advogados & Associados — Assessoria Jurídica em Direito Público Municipal**

Este manual descreve, passo a passo, como usar o sistema Ione para receber consultas
jurídicas, gerar pareceres com apoio de inteligência artificial, revisar, aprovar e
enviar o parecer ao cliente.

> **Para quem é este manual:** advogados e secretaria do escritório. Não é necessário
> nenhum conhecimento técnico.

---

## Sumário

1. [Primeiro acesso e login](#1-primeiro-acesso-e-login)
2. [Recuperar / trocar senha](#2-recuperar--trocar-senha)
3. [Visão geral das telas](#3-visão-geral-das-telas)
4. [Como uma consulta chega ao sistema](#4-como-uma-consulta-chega-ao-sistema)
5. [A lista de Pareceres](#5-a-lista-de-pareceres)
6. [Gerando o parecer com a IA](#6-gerando-o-parecer-com-a-ia)
7. [Editando o parecer](#7-editando-o-parecer)
8. [Revisão pela IA (correções)](#8-revisão-pela-ia-correções)
9. [Revisão por um colega (peer review)](#9-revisão-por-um-colega-peer-review)
10. [Aprovar e enviar ao cliente](#10-aprovar-e-enviar-ao-cliente)
11. [Exportar em DOCX ou PDF](#11-exportar-em-docx-ou-pdf)
12. [Notificações](#12-notificações)
13. [Significado de cada status](#13-significado-de-cada-status)
14. [Perguntas frequentes e cuidados importantes](#14-perguntas-frequentes-e-cuidados-importantes)

---

## 1. Primeiro acesso e login

1. Abra o endereço do sistema no navegador: **https://app.ioneadvogados.com.br**
2. Informe seu **e-mail** e sua **senha**.
3. Clique em **Entrar**.

Se o e-mail ou a senha estiverem errados, aparece a mensagem *"Email ou senha inválidos"*.

> No primeiro acesso, sua senha pode ser uma senha provisória fornecida pelo
> administrador. Recomendamos trocá-la (veja a seção seguinte).

---

## 2. Recuperar / trocar senha

**Esqueci minha senha:**

1. Na tela de login, clique em **Esqueci minha senha**.
2. Digite seu e-mail e clique em **Enviar link de redefinição**.
3. Você receberá um e-mail com um link. Abra-o e defina uma nova senha
   (mínimo de **8 caracteres**), confirmando-a no segundo campo.

**Trocar a senha estando logado:**

1. No topo da tela, clique no seu nome/avatar.
2. Escolha a opção de **trocar senha** e siga as instruções.

---

## 3. Visão geral das telas

O menu lateral tem duas áreas principais:

- **Dashboard** (página inicial) — um resumo do andamento dos pareceres: total em
  aberto, concluídos na semana, distribuição por etapa, por município e por advogado,
  e os pareceres mais antigos ainda em aberto.
- **Pareceres** — a lista de todas as consultas/pareceres, onde você trabalha o dia a dia.

No canto superior direito ficam o **sino de notificações** e o seu perfil.

---

## 4. Como uma consulta chega ao sistema

Há duas formas de uma consulta entrar:

### a) Por e-mail (automático)

As prefeituras enviam a consulta para o e-mail oficial do escritório
(**consultas.ioneadvogados@gmail.com**). O sistema verifica essa caixa
**a cada 5 minutos** e cria automaticamente um novo parecer com o texto do e-mail e
os anexos (contratos, editais, etc.). Não é preciso fazer nada — a consulta aparece
sozinha na lista de Pareceres.

### b) Importação manual (arquivo .eml)

Se você tiver o e-mail salvo como arquivo `.eml`:

1. Vá em **Pareceres**.
2. Clique em **Importar Consulta** (canto superior direito).
3. Escolha o arquivo `.eml`. O sistema lê o conteúdo e abre o parecer recém-criado.

---

## 5. A lista de Pareceres

Na tela **Pareceres** você vê, no topo, quatro indicadores: **Total**,
**Aguardando revisão**, **Em correção** e **Enviados na semana**.

Abaixo há **filtros** (por status, por tema e por remetente) e a lista de pareceres.
Cada item mostra o assunto, o remetente, o tema e o **status** atual (veja a
[seção 13](#13-significado-de-cada-status)).

Clique em um parecer para abri-lo no editor.

> A lista se atualiza sozinha enquanto um parecer está sendo processado pela IA.

---

## 6. Gerando o parecer com a IA

Ao abrir uma consulta recém-chegada, o sistema já fez a leitura do e-mail e dos anexos.
O processo da IA tem etapas automáticas (classificação do tema/município e geração do
texto). Em geral:

1. Abra a consulta na lista.
2. Se o parecer ainda não foi gerado, use a ação **Enviar para IA** para iniciar a
   geração do texto.
3. Aguarde alguns instantes. Enquanto a IA trabalha, o status fica como *processando* e
   a tela se atualiza automaticamente. Ao final, o texto do parecer aparece no editor e
   o status passa para **Aguardando revisão**.

> A IA usa como base a legislação (Lei 14.133/21 e legislação municipal pertinente),
> jurisprudência (TCU, TCE-CE) e os modelos de escrita do escritório.

---

## 7. Editando o parecer

O parecer abre num **editor de texto** semelhante ao Word, em uma folha branca.
Você pode:

- Editar livremente o texto (negrito, itálico, etc. na barra de ferramentas).
- Navegar pelas seções: **EMENTA**, **I — RELATÓRIO**, **II — FUNDAMENTOS**,
  **III — CONCLUSÃO**.
- Ver, na lateral, os dados da consulta (remetente, data, município, tema, status),
  os anexos e o **fluxo de revisão**.

Clique em **Salvar** para guardar suas alterações. Cada salvamento cria uma nova
**versão**, então você nunca perde o histórico — é possível consultar e restaurar
versões anteriores pela lateral.

> O cabeçalho (título, consulente), o bloco de assinaturas e a data são montados
> automaticamente no documento final — você não precisa digitá-los no corpo do texto.

---

## 8. Revisão pela IA (correções)

Quando quiser que a IA reveja e proponha melhorias:

1. No editor, use **Revisar parecer**.
2. A IA analisa o texto e devolve um **preview das correções** propostas, seção por seção.
3. Você decide o que **aceitar** ou **descartar**. Só o que for aceito é aplicado, criando
   uma nova versão. O status fica como **Em correção** durante esse processo.

Nada é alterado sem a sua confirmação.

---

## 9. Revisão por um colega (peer review)

Para pedir que outro advogado revise trechos do parecer:

1. No editor, use **Enviar para colega**.
2. Escolha o colega revisor e os trechos/observações.
3. O colega recebe uma **notificação** (sino) e poderá abrir o parecer, revisar e devolver.
4. Quando a revisão é concluída, **você** recebe uma notificação de volta.

Esse fluxo é opcional e serve para uma segunda opinião antes da aprovação.

---

## 10. Aprovar e enviar ao cliente

Quando o parecer estiver pronto:

- **Aprovar** — marca o parecer como **Aprovado** (pronto para envio), sem enviar ainda.
- **Aprovar e enviar** — aprova e, em seguida, **envia o parecer por e-mail** ao
  remetente original (a prefeitura), como **resposta na mesma conversa de e-mail**, com o
  **PDF do parecer em anexo**. O status passa para **Enviado**.

O e-mail de resposta usa um texto formal padrão do escritório, com a assinatura
institucional.

> Se precisar devolver o parecer para ajustes (em vez de aprovar), use a opção de
> **devolver**, informando o motivo. O status passa para **Devolvido**.

---

## 11. Exportar em DOCX ou PDF

No editor é possível **baixar** o parecer:

- **DOCX** — para abrir/editar no Word.
- **PDF** — versão final para impressão ou arquivo.

O arquivo é baixado com o número do parecer no nome (ex.: `PAR-2026-0007.pdf`).

> **Atenção aos marcadores de revisão:** se o texto ainda contiver marcações como
> **`[REVISAR—...]`** ou **`[!VERIFICAR:...!]`**, o sistema **avisa antes de exportar**.
> Essas marcas indicam pontos que a IA pediu para um humano conferir (por exemplo, a
> citação exata de um julgado). **Confira e resolva esses pontos antes de enviar o
> parecer ao cliente.**

---

## 12. Notificações

O **sino** no canto superior direito mostra as notificações **não lidas** — atualmente,
os pedidos de **revisão de colega** (peer review). Clique em uma notificação para abrir
o parecer correspondente; ela é marcada como lida automaticamente.

---

## 13. Significado de cada status

| Status (na lista)      | O que significa                                                        |
|------------------------|-----------------------------------------------------------------------|
| **Pendente**           | Consulta recebida; ainda não teve o parecer gerado.                   |
| **Aguardando revisão** | A IA gerou o texto; aguardando a leitura/revisão do advogado.         |
| **Em correção**        | Em processo de revisão/correção (pela IA ou ajustes).                 |
| **Devolvido**          | Foi devolvido para ajustes, com um motivo registrado.                |
| **Aprovado**           | Aprovado pelo advogado; pronto para envio.                            |
| **Enviado**            | Enviado por e-mail ao cliente (resposta na conversa original).       |
| **Erro**               | Ocorreu uma falha no processamento — tente novamente ou contate o suporte. |

---

## 14. Perguntas frequentes e cuidados importantes

**A consulta não apareceu na lista. E agora?**
O sistema verifica o e-mail a cada 5 minutos — aguarde alguns minutos. Confirme se a
prefeitura enviou para **consultas.ioneadvogados@gmail.com**. Em último caso, importe o
e-mail manualmente como `.eml` (seção 4b).

**O parecer gerado pela IA pode ser enviado direto ao cliente?**
**Não sem revisão humana.** A IA é uma assistente: o advogado é sempre responsável por
ler, conferir e validar o conteúdo — em especial citações de leis, súmulas e julgados —
antes de aprovar e enviar. Resolva todos os marcadores `[REVISAR—]` / `[!VERIFICAR:!]`.

**Perdi uma alteração. Como recupero?**
Cada salvamento cria uma versão. Use o painel de **versões** na lateral do editor para
consultar e **restaurar** uma versão anterior.

**Quem recebe a resposta quando eu clico em "Aprovar e enviar"?**
O remetente original da consulta (a prefeitura), como resposta na mesma conversa de
e-mail, com o PDF do parecer anexado.

**Esqueci minha senha.**
Use **Esqueci minha senha** na tela de login (seção 2).

---

*Em caso de dúvidas ou problemas técnicos, contate o administrador do sistema.*
