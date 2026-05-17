# Release Notes — v0.4 (05/05/2026)

## Editor de Pareceres

### Diff visual por autor
- Ao trocar de versão, o editor destaca palavra-a-palavra as alterações em relação à versão anterior
- Cada autor recebe uma cor única; iniciais aparecem no gutter lateral direito (DiffGutter)
- O diff ignora diferenças de maiúsculas e pontuação nas extremidades dos tokens — "interno." e "interno" não são considerados palavras distintas

### Salvar cria versão
- O botão **Salvar** agora grava um snapshot explícito (versão `manual_edit`) em vez de auto-save com debounce
- Trocar de versão não marca o documento como modificado
- A sidebar de versões lista nome e iniciais coloridas do autor de cada versão

### Peer review
- As sugestões aceitas pelo revisor são aplicadas ao conteúdo da versão `peer_review`, permitindo que o diff identifique exatamente o que mudou e exiba as iniciais do revisor
- Formatação (negrito, itálico) dos trechos substituídos é preservada

---

## Identificação de Município

- A identificação do município de origem passou a ser feita exclusivamente pela IA (passo P1 do pipeline)
- Removida a dependência da tabela `municipios` para classificação automática — o campo `classificacao->>'municipio'` do JSONB é a única fonte
- O filtro da lista de pareceres e os agrupamentos do dashboard usam esse campo diretamente
- Resultado: pareceres de municípios não cadastrados previamente são identificados corretamente

---

## Dashboard

- Cards de **Pareceres por Município** e **Pareceres por Advogado** agora exibem dados reais
- Corrigido erro de agrupamento SQL (JSONB GROUP BY com `literal_column`)
- Lista dos 5 pareceres mais antigos em aberto incluída na aba de visão geral

---

## Importação

- Botão renomeado de "Importar .eml" para **Importar Consulta**
- Cabeçalho (assunto + remetente) sempre prefixado ao texto extraído, garantindo contexto mínimo para a IA mesmo em e-mails encaminhados sem corpo

---

## Infraestrutura

- Deploy padronizado em `docker-compose.prod.yml` (frontend serve build estático via nginx interno na porta 80)
- Nginx usa `resolver 127.0.0.11 valid=30s` e variável de upstream para evitar IP stale após restart de containers
