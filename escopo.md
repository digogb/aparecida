# Documento de Escopo — Sistema Ione
**Versão:** 1.1
**Data:** 31 de março de 2026
**Contratante:** [Nome do cliente]
**Contratada:** [Nome da empresa desenvolvedora]

---

## 1. Objetivo

Este documento define o escopo funcional do **Sistema Ione**, plataforma de gestão jurídica com geração de pareceres assistida por inteligência artificial. O objetivo é estabelecer com precisão quais funcionalidades estão incluídas na contratação, servindo como referência vinculante para ambas as partes e prevenindo alterações de escopo não acordadas.

---

## 2. Visão Geral do Sistema

O Sistema Ione é uma aplicação web destinada a escritórios de advocacia e departamentos jurídicos municipais. Ele centraliza:

- **Geração automatizada de pareceres jurídicos** via IA (Anthropic Claude)
- **Dashboard gerencial** com indicadores e alertas em tempo real
- **Gestão de movimentações processuais** (DJE)
- **Gestão de tarefas** em quadro Kanban
- **Controle de usuários** com perfis de acesso distintos

O escopo contratado cobre especificamente os módulos de **Dashboard**, **Geração de Pareceres** e **Integração com Gmail**, detalhados nas seções a seguir.

---

## 3. Módulo 1 — Dashboard

### 3.1 Descrição Geral

O Dashboard é a tela inicial do sistema após o login. Apresenta uma visão consolidada do estado operacional do escritório, com indicadores de desempenho, alertas prioritários e atividades recentes.

### 3.2 Indicadores (KPIs)

O painel exibe os seguintes cartões de métricas em tempo real:

| Indicador | Descrição |
|-----------|-----------|
| **Aguardando Revisão** | Quantidade de pareceres com status `gerado` ou `em_revisao` |
| **Em Revisão** | Quantidade de pareceres ativamente em processo de revisão |
| **Movimentações Não Lidas** | Total de movimentações processuais ainda não visualizadas |
| **Tarefas Urgentes** | Tarefas com prioridade alta em colunas não concluídas |
| **Concluídas na Semana** | Pareceres com status `enviado` nos últimos 7 dias |
| **Enviados (Total)** | Contador histórico de todos os pareceres enviados |

**Escopo inclui:**
- Exibição dos 6 indicadores listados acima
- Atualização dos dados a cada carregamento de página
- Layout responsivo em grade (3 colunas em desktop, 1 coluna em mobile)

**Escopo NÃO inclui:**
- Atualização automática em tempo real sem recarregar a página (exceto via ação do usuário)
- Gráficos históricos ou séries temporais
- Exportação dos indicadores em planilha ou relatório
- Configuração dos indicadores pelo usuário (ex: trocar KPIs exibidos)
- Filtro por período nos KPIs

### 3.3 Painel de Alertas

O sistema identifica e exibe automaticamente situações que requerem atenção imediata:

| Tipo de Alerta | Critério de Disparo |
|---------------|---------------------|
| **Pareceres Atrasados** | Pareceres sem atualização há mais de 48 horas |
| **Intimações Não Lidas** | Movimentações do tipo intimação ainda não marcadas como lidas |
| **Tarefas com Prazo Próximo** | Tarefas com data de vencimento nos próximos 3 dias |

**Escopo inclui:**
- Exibição dos 3 tipos de alerta listados acima
- Máximo de 5 alertas exibidos por categoria
- Ícone e cor distintos por tipo de alerta
- Clique no alerta redireciona para o item correspondente

**Escopo NÃO inclui:**
- Notificações push ou sonoras no navegador
- Envio de alertas por e-mail a partir do dashboard (funcionalidade separada)
- Configuração dos critérios de alerta pelo usuário
- Alertas de vencimento de prazos processuais integrados a sistemas externos

### 3.4 Atividades Recentes

O dashboard exibe dois painéis de atividade recente:

**Últimos Pareceres:**
- Lista dos 5 pareceres mais recentes
- Informações exibidas: assunto, status atual, município
- Clique navega para o editor do parecer

**Últimas Movimentações:**
- Lista das 5 movimentações processuais mais recentes
- Informações exibidas: tipo de documento, número do processo, data de publicação
- Clique navega para o detalhe da movimentação

**Escopo inclui:**
- Exibição das últimas 5 entradas em cada lista
- Navegação por clique para o item

**Escopo NÃO inclui:**
- Paginação ou "ver mais" na seção de atividades recentes
- Filtros nas seções de atividades recentes

### 3.5 Interface Visual

- Paleta de cores em tons bege/marrom com estética de escritório jurídico tradicional
- Tipografia com serifa nos títulos
- Cores de status padronizadas: dourado (pendente), cinza (aguardando), laranja (em correção), vermelho (devolvido), verde (aprovado)

---

## 4. Módulo 2 — Geração de Pareceres

### 4.1 Descrição Geral

O módulo de pareceres cobre o ciclo completo de vida de um parecer jurídico: desde a ingestão do pedido via e-mail até o envio do documento final ao cliente. O processo é apoiado por IA em três etapas principais: classificação, geração e revisão.

### 4.2 Fluxo de Status

```
pendente → classificado → gerado → em_correção / em_revisão → aprovado → enviado
                                           ↓
                                      devolvido
                                           ↓
                                        erro
```

Cada transição de status é registrada com data, hora e usuário responsável (trilha de auditoria).

### 4.3 Ingestão de Pedidos

O sistema suporta duas formas de entrada de pedidos de parecer:

#### 4.3.1 Upload Manual de E-mail

- Upload de arquivos `.eml` (e-mail exportado) diretamente pela interface web
- Útil para pedidos avulsos ou retroativos

#### 4.3.2 Integração Automática com Gmail (Webhook)

O sistema monitora automaticamente a caixa de entrada do Gmail do escritório e cria pareceres a partir de e-mails recebidos, sem intervenção manual.

**Fluxo de funcionamento:**
1. Cliente (município) envia e-mail com pedido de parecer para o endereço do escritório
2. Gmail notifica o sistema via Google Cloud Pub/Sub (webhook)
3. Sistema recebe a notificação, extrai os dados do e-mail e cria automaticamente um novo pedido de parecer com status `pendente`
4. Pipeline de classificação (P1) e geração (P2) é disparado em segundo plano
5. Deduplicação automática: e-mails já processados não geram pedidos duplicados

**Dados capturados automaticamente:**
- ID da thread e ID da mensagem do Gmail (para deduplicação)
- E-mail do remetente
- Corpo e assunto do e-mail
- Anexos (PDF, DOCX, imagens)

**Processamento de anexos:**
- Extração de texto dos formatos: PDF, DOCX, imagens digitalizadas (OCR)
- Fallback automático entre métodos de extração (pdfplumber → python-docx → tesseract → libreoffice)
- Armazenamento dos arquivos para fins de auditoria

**Escopo inclui:**
- Upload manual via interface web de arquivos `.eml`
- Integração automática com Gmail via Google Cloud Pub/Sub (webhook)
- Deduplicação de pedidos por thread do Gmail
- Extração de texto dos formatos: PDF, DOCX, imagens digitalizadas (OCR)
- Armazenamento dos arquivos anexados
- Disparo automático do pipeline de IA ao receber novo e-mail

**Escopo NÃO inclui:**
- Integração com outros provedores de e-mail (Outlook, Yahoo, IMAP/POP3 genérico)
- Suporte a outros formatos de arquivo além dos listados (ex: ODS, XLS, HTML)
- Reconhecimento de handwriting (escrita à mão) em documentos digitalizados
- Configuração da conta Gmail pelo próprio usuário na interface (requer configuração técnica no servidor)

### 4.4 Classificação Automática (P1)

Após a ingestão, o sistema realiza a classificação automática do pedido utilizando IA (Claude Haiku):

**Dados extraídos na classificação:**
- Município solicitante
- Área jurídica: `licitação` ou `administrativo`
- Grau de urgência
- Grau de confiança da classificação
- Modelo de parecer aplicável

**Escopo inclui:**
- Classificação automática nas duas áreas suportadas (licitação e administrativo)
- Exibição dos dados de classificação na interface
- Possibilidade de o advogado corrigir a classificação manualmente

**Escopo NÃO inclui:**
- Suporte a áreas jurídicas além de licitação e administrativo (ex: tributário, ambiental, trabalhista)
- Treinamento ou customização do modelo de classificação
- Adição de novos modelos de parecer sem novo desenvolvimento

### 4.5 Geração do Parecer (P2)

A partir da classificação, o sistema gera automaticamente o parecer completo utilizando IA (Claude Sonnet):

**Estrutura gerada:**
1. **Ementa** — resumo do parecer
2. **I — Relatório** — descrição dos fatos e histórico
3. **III — Fundamentos** — fundamentação jurídica
4. **IV — Conclusão** — conclusão e recomendação

**Características da geração:**
- Conteúdo gerado em linguagem jurídica formal
- Editor de texto rico (TipTap) para edição posterior pelo advogado
- Suporte a formatação: negrito, itálico, sublinhado, títulos, listas, citações em bloco
- Histórico de versões: cada geração ou edição cria uma nova versão salva
- Numeração automática do parecer

**Escopo inclui:**
- Geração automática das 4 seções listadas
- Editor de texto rico com as formatações listadas
- Controle de versões com possibilidade de restaurar versão anterior
- Numeração automática sequencial de pareceres

**Escopo NÃO inclui:**
- Verificação automática de citações legais em bases de dados externas (ex: JusBrasil, Planalto)
- Geração de pareceres em língua estrangeira
- Templates customizáveis de parecer pelo usuário final (sem novo desenvolvimento)
- Assinatura digital integrada a certificados ICP-Brasil
- Integração com sistemas de protocolo eletrônico

### 4.6 Revisão e Correção por IA (P3)

O advogado pode solicitar correções pontuais ao parecer gerado:

**Fluxo de revisão:**
1. Advogado seleciona trechos problemáticos no texto e adiciona observações
2. Sistema gera preview das alterações sugeridas por seção
3. Advogado aprova ou rejeita cada seção individualmente
4. Apenas as seções aprovadas são aplicadas, gerando nova versão

**Escopo inclui:**
- Seleção de trechos para revisão com campo de observação
- Preview das alterações antes de aplicar
- Aprovação/rejeição por seção
- Geração de nova versão ao aplicar correções

**Escopo NÃO inclui:**
- Revisão automática de gramática/ortografia
- Sugestões automáticas de melhoria sem solicitação do usuário
- Comparação lado a lado de versões no histórico (apenas versão atual vs. prévia de correção)

### 4.7 Revisão por Pares (Peer Review)

O sistema suporta revisão colaborativa entre advogados:

**Fluxo:**
1. Advogado responsável solicita revisão de colega disponível
2. Revisor visualiza o parecer, marca trechos problemáticos e registra observações
3. Sistema notifica o solicitante com o resultado da revisão
4. Solicitante pode aceitar sugestões do revisor, gerando nova versão

**Escopo inclui:**
- Solicitação de revisão para outro usuário advogado cadastrado
- Marcação de trechos e observações pelo revisor
- Notificação ao solicitante ao concluir revisão
- Geração de nova versão a partir das sugestões aceitas

**Escopo NÃO inclui:**
- Revisão por usuários externos ao sistema (sem login)
- Comentários em tempo real / chat durante a revisão

### 4.8 Exportação de Documentos

O parecer aprovado pode ser exportado nos formatos:

| Formato | Conteúdo |
|---------|----------|
| **DOCX** | Documento Word formatado com cabeçalho do escritório, corpo do parecer, assinatura e rodapé com dados de contato |
| **PDF** | Versão PDF do mesmo documento DOCX |

**Escopo inclui:**
- Exportação em DOCX e PDF
- Formatação profissional com cabeçalho, corpo e rodapé
- Campo de assinatura do advogado responsável

**Escopo NÃO inclui:**
- Exportação em outros formatos (ex: ODT, HTML, TXT)
- Configuração do template de exportação pelo usuário (sem novo desenvolvimento)
- Envio automático do documento exportado por e-mail a partir do editor

### 4.9 Lista de Pareceres

Tela com a listagem de todos os pareceres do sistema:

**Funcionalidades:**
- Listagem paginada (20 itens por página)
- Cartões de métricas: Total, Aguardando, Em Correção, Enviados na semana
- Filtros: status, área jurídica (tema), e-mail do remetente
- Importação de `.eml` diretamente da listagem
- Clique no parecer abre o editor

**Escopo inclui:**
- Todos os itens listados acima

**Escopo NÃO inclui:**
- Exportação da listagem em planilha
- Busca por texto livre no conteúdo dos pareceres
- Ordenação por colunas na listagem

---

## 5. Funcionalidades de Suporte Incluídas

As funcionalidades abaixo são necessárias para o funcionamento dos módulos de Dashboard e Pareceres e estão incluídas no escopo:

### 5.1 Autenticação e Controle de Acesso

| Perfil | Permissões |
|--------|-----------|
| **Advogado** | Acesso completo ao fluxo de pareceres, revisão por pares, exportação |
| **Secretaria** | Importação de e-mails, visualização, atribuição de pareceres |
| **Administrador** | Acesso completo + gestão de usuários e municípios |

- Login com e-mail e senha
- Sessão mantida via token JWT
- Logout manual

**Escopo NÃO inclui:**
- Login social (Google, Microsoft)
- SSO (Single Sign-On) com sistemas externos
- Autenticação em dois fatores (2FA)
- Controle de acesso por município ou por cliente específico

### 5.2 Gestão de Municípios

- Cadastro de municípios atendidos (nome, UF, domínios de e-mail)
- Ativação/desativação de municípios
- Associação automática de pedidos ao município pelo domínio do e-mail remetente

### 5.3 Trilha de Auditoria

- Registro histórico de todas as transições de status de cada parecer
- Registro de qual usuário realizou cada ação e em qual data/hora
- Visualização do histórico de versões do conteúdo do parecer

---

## 6. Funcionalidades Fora do Escopo

As funcionalidades abaixo **não estão incluídas** nesta contratação e requerem negociação separada caso sejam demandadas:

1. **Módulo de Movimentações Processuais (DJE)** — monitoramento e consulta ao Diário de Justiça Eletrônico
2. **Módulo de Tarefas (Kanban)** — quadro de gestão de tarefas
3. **Integração com outros provedores de e-mail** (Outlook, Yahoo, IMAP/POP3 genérico)
4. **Notificações por e-mail** — envio de alertas e notificações via e-mail
5. **API pública** para integração com sistemas externos
6. **Aplicativo mobile** (iOS/Android)
7. **Múltiplos escritórios** na mesma instalação (multi-tenant)
8. **Relatórios gerenciais** avançados com gráficos históricos
9. **Novas áreas jurídicas** além de licitação e administrativo
10. **Assinatura digital** com certificado ICP-Brasil
11. **Integração com sistemas de protocolo** (ex: e-Saj, PJe, Projudi)

---

## 7. Requisitos Técnicos

### 7.1 Infraestrutura (responsabilidade do contratante)

| Componente | Requisito Mínimo |
|-----------|-----------------|
| Servidor | VPS Linux com 4 vCPUs, 8 GB RAM |
| Armazenamento | 50 GB SSD (arquivos e banco de dados) |
| Banco de dados | PostgreSQL 16 |
| Domínio | Domínio próprio com SSL (HTTPS) |
| Internet | Conexão estável com acesso à internet (chamadas externas à API Anthropic) |

### 7.2 Dependências Externas

| Serviço | Finalidade | Responsabilidade |
|---------|-----------|-----------------|
| **Anthropic Claude API** | Geração de pareceres por IA | Contratante fornece chave de API |
| **Google Cloud Pub/Sub** | Notificações de novos e-mails do Gmail | Contratante fornece projeto GCP e credenciais de serviço |
| **Gmail (conta do escritório)** | Recebimento de pedidos de parecer | Contratante fornece conta Gmail e autoriza integração |
| **Navegador moderno** | Acesso à aplicação | Chrome/Firefox/Edge (versões dos últimos 2 anos) |

### 7.3 Observação sobre Custos de IA

O custo de uso da API da Anthropic (Claude) é cobrado diretamente à conta da Anthropic do contratante, com base no volume de tokens processados. **Este custo não está incluído no valor desta contratação** e é de responsabilidade exclusiva do contratante.

---

## 8. Limitações e Premissas

1. **Volume:** O sistema foi projetado para o volume típico de um escritório de médio porte. Cargas excepcionais (ex: centenas de pareceres simultâneos) podem requerer ajustes de infraestrutura.
2. **Qualidade da IA:** O conteúdo gerado pela IA é uma sugestão que requer revisão humana pelo advogado. A responsabilidade pelo conteúdo final do parecer é do profissional que o assina.
3. **Formatos de arquivo:** Documentos escaneados com baixa resolução podem resultar em extração de texto incompleta via OCR.
4. **Disponibilidade:** A disponibilidade do sistema depende da disponibilidade da API da Anthropic e da infraestrutura contratada.
5. **Legislação:** O sistema não realiza atualização automática de referências legais. Cabe ao advogado verificar a atualidade das normas citadas.
6. **Integração Gmail:** O funcionamento da integração depende da configuração de um projeto no Google Cloud Platform (GCP) com a API Gmail e um tópico Pub/Sub habilitados. A configuração inicial do GCP é de responsabilidade da contratada, mas as credenciais e a conta Gmail são de responsabilidade do contratante.

---

## 9. Critérios de Aceite

O sistema será considerado entregue e aceito quando:

- [ ] Login e logout funcionando para os 3 perfis (advogado, secretaria, administrador)
- [ ] Dashboard exibindo os 6 KPIs, alertas e atividades recentes conforme seção 3
- [ ] Upload de `.eml` com extração automática de texto (PDF, DOCX, imagem)
- [ ] Classificação automática por IA retornando área jurídica e município
- [ ] Geração de parecer com as 4 seções (ementa, relatório, fundamentos, conclusão)
- [ ] Editor de texto rico funcionando com todas as formatações listadas
- [ ] Revisão por IA (P3) com preview e aprovação por seção
- [ ] Revisão por pares com notificação ao solicitante
- [ ] Exportação em DOCX e PDF com formatação profissional
- [ ] Histórico de versões com possibilidade de restauração
- [ ] Trilha de auditoria de status e ações
- [ ] Integração com Gmail: e-mail recebido no Gmail do escritório gera automaticamente um parecer pendente no sistema
- [ ] Deduplicação: reenvio do mesmo e-mail não cria pedido duplicado

---

## 10. Processo de Solicitação de Mudanças

Qualquer funcionalidade não descrita neste documento é considerada fora do escopo. Solicitações de novas funcionalidades ou alterações no comportamento descrito devem seguir o processo:

1. Solicitação formal por escrito (e-mail ou sistema de tickets)
2. Análise de impacto pela equipe de desenvolvimento
3. Apresentação de proposta de custo e prazo adicional
4. Aprovação formal pelo contratante antes do início do desenvolvimento

**Nenhuma alteração de escopo será implementada sem aprovação formal prévia.**

---

## 11. Assinaturas

Este documento define o escopo acordado entre as partes.

| | Contratante | Contratada |
|--|------------|-----------|
| **Nome** | | |
| **Cargo** | | |
| **Data** | | |
| **Assinatura** | | |

---

*Documento gerado em 31 de março de 2026.*