# INDEX.md — Banco Curado de Jurisprudência

**Estado da pasta na v5.0:** **populado e operacional**. O banco contém **121 entradas validadas** distribuídas entre TCU (46), TCE-CE (73) e AGU (2). Todas as entradas estão chanceladas pelo Dr. Matheus Nogueira Pereira Lima sob os selos de validação descritos em §4.

**Histórico:**
- **v2.7.0** — pasta estrutural, sem entradas.
- **v2.7.1 → v2.8.0-rc1** (Sessão 1, 11/05/2026) — 34 entradas admitidas (30 TCU + 4 TCE-CE).
- **v2.8.0-rc2** (Sessão 2, 12/05/2026) — 15 entradas adicionais admitidas.
- **v3.0.0** (Sessão 5, 12/05/2026) — admissão de 16 novas entradas TCU + 2 ON-AGU; promoção do selo das entradas TCE-CE para fonte primária qualificada; integração da ADI 6890/STF via `references/fontes-oficiais.md`.
- **v5.0** — consolidação: pasta `stj/` removida (entrada STJ-TEMA-1061 retirada do banco curado); banco TCE-CE expandido para 73 entradas com selo homogêneo de fonte primária qualificada (acórdãos, consultas, resoluções, informativos e súmulas). **Estado atual.**

---

## 1. ESTRUTURA DA PASTA

```
jurisprudencia/
├── INDEX.md                       (este arquivo)
├── GAP_REPORT_SESSAO_1.md         (registro da Sessão 1)
├── GAP_REPORT_SESSAO_2.md         (registro da Sessão 2)
├── GAP_REPORT_SESSAO_5.md         (registro da Sessão 5)
├── tcu/                           (46 entradas — 16 acórdãos/decisões + 30 súmulas)
├── tce-ce/                        (73 entradas — acórdãos, consultas, resoluções, informativos e súmulas)
└── agu/                           (2 entradas — ON-AGU 17/2009 + ON-AGU 87/2024)
```

ADI 6890/STF integrada como referência em `references/fontes-oficiais.md` §3.3.

---

## 2. INVENTÁRIO HISTÓRICO (BASE DA CURADORIA)

> **Nota institucional:** o inventário detalhado abaixo registra o estado das Sessões 1 e 2 (49 entradas iniciais), preservado como documentação histórica. O banco completo da v5.0 (121 entradas) está mapeado nos sub-INDEX por tribunal (`tcu/INDEX.md`, `tce-ce/INDEX.md`, `agu/INDEX.md`).

### 2.1 Padrão de ID

```
[TRIBUNAL]-[INSTRUMENTO]-[NÚMERO]-[ANO]
```

Exemplos: `TCU-SUM-263`, `TCU-AC-1536-2016`, `TCE-CE-CON-05608-2021`, `TCE-CE-INFO-09-2025`.

### 2.2 Pasta `tcu/` — 46 entradas (atualizado v5.0; histórico das 32 iniciais abaixo)

**Súmulas TCU em licitações (30 entradas, todas validadas na Sessão 1):**

| ID | Categoria (Pinheiro/Mansur 2023) | Selo |
|---|---|---|
| TCU-SUM-39 | Contratação Direta | Pinheiro/Mansur + 2 fontes secundárias |
| TCU-SUM-177 | TR/Projeto Básico | Pinheiro/Mansur |
| TCU-SUM-185 | Obras e Engenharia | Pinheiro/Mansur |
| TCU-SUM-191 | Contrato Administrativo | Pinheiro/Mansur |
| TCU-SUM-205 | Contrato Administrativo | Pinheiro/Mansur |
| TCU-SUM-222 | **Transversal** | Pinheiro/Mansur + portal TCU + secundárias **[entrada-piloto]** |
| TCU-SUM-247 | Parcelamento | Pinheiro/Mansur + portal TCU + Acórdão 5301/2013 |
| TCU-SUM-248 | Modalidade Convite | Pinheiro/Mansur (aplicabilidade transicional) |
| TCU-SUM-250 | Contratação Direta | Pinheiro/Mansur + Acórdãos 2669/2016 e 2392/2018 |
| TCU-SUM-252 | Contratação Direta | CNJ + Pinheiro/Mansur + jurisprudência TCU **[entrada-piloto]** |
| TCU-SUM-253 | Obras e Engenharia | Pinheiro/Mansur |
| TCU-SUM-254 | Orçamento Estimativo | Pinheiro/Mansur |
| TCU-SUM-255 | Contratação Direta | Pinheiro/Mansur |
| TCU-SUM-257 | Obras e Engenharia | CNJ + Pinheiro/Mansur + ConJur + Acórdãos 505/2018 e 713/2019 **[entrada-piloto]** |
| TCU-SUM-258 | Obras e Engenharia | Pinheiro/Mansur |
| TCU-SUM-259 | Obras e Engenharia | Pinheiro/Mansur |
| TCU-SUM-260 | Obras e Engenharia | Pinheiro/Mansur |
| TCU-SUM-261 | TR/Projeto Básico | Pinheiro/Mansur |
| TCU-SUM-262 | Habilitação/Proposta | Pinheiro/Mansur + Acórdão 2.198/2023-Pl |
| TCU-SUM-263 | Habilitação/Proposta | Portal oficial TCU + Pinheiro/Mansur + 5 secundárias **[entrada-piloto]** |
| TCU-SUM-265 | Contratação Direta | Pinheiro/Mansur |
| TCU-SUM-269 | Bens e Serviços de Informática | Pinheiro/Mansur + RGV&L + Jusbrasil + tele.síntese **[entrada-piloto]** |
| TCU-SUM-270 | Indicação de Marca | Pinheiro/Mansur |
| TCU-SUM-272 | Habilitação/Proposta | Pinheiro/Mansur + Jurishand |
| TCU-SUM-274 | Habilitação/Proposta | Pinheiro/Mansur |
| TCU-SUM-275 | Habilitação/Proposta | Pinheiro/Mansur |
| TCU-SUM-281 | Cooperativa | Pinheiro/Mansur |
| TCU-SUM-283 | Habilitação/Proposta | Pinheiro/Mansur |
| TCU-SUM-287 | Contratação Direta | Pinheiro/Mansur + Acórdão 3094/2014 |
| TCU-SUM-289 | Habilitação/Proposta | Pinheiro/Mansur |

**Acórdãos do TCU (2 entradas, admitidas na Sessão 2 — Frente A):**

| ID | Tema | Selo |
|---|---|---|
| TCU-AC-1536-2016 | Vedação à compensação entre acréscimos e supressões em aditivos (leading-case da regra geral; substitui pseudo-Súmula 244 descartada) | Convergência alta — Portal TCU + Zênite + Observatório NLL + Enunciado 4 do Manual TCU (5ª ed., 2024) |
| TCU-AC-1176-2021 | Vedação à restrição geográfica em editais (substitui Súmula 245 descartada por estar fora de escopo) | Convergência alta — texto literal em duas fontes técnicas + reforço por TCU-AC-949-2025 sob Lei 14.133/2021 |

### 2.3 Pasta `tce-ce/` — 16 entradas iniciais (Sessões 1 e 2); 73 entradas no estado v5.0

**Sessão 1 (4 entradas):**

| ID | Tema | Selo |
|---|---|---|
| TCE-CE-CON-05608-2021 | Dispensa por valor — unidade gestora autônoma (Meruoca) | Fonte secundária única — primária pendente |
| TCE-CE-SUM-2 | Restrição — parcelas de menor relevância | **Fonte primária** (PDF oficial) |
| TCE-CE-SUM-3 | Restrição — quadro permanente | Transmitida pelo Dr. Matheus + TCU convergente — PDF intranet inacessível |
| TCE-CE-SUM-4 | Restrição — visita técnica única | Transmitida pelo Dr. Matheus + TCU/TCE-SP convergentes — PDF intranet inacessível |

**Sessão 2 — Rodada B1 (Blocos D1+D2, 5 entradas):**

| ID | Tema | Selo |
|---|---|---|
| TCE-CE-AC-924-2026 | Inexigibilidade advocatícia sem singularidade — **modulação temporal** (cluster D1, caso menos grave) | Informativo oficial — transcrição reconstruída |
| TCE-CE-AC-2090-2025 | Contratação direta sem formalização + Fundeb (cluster D1, caso mais grave) | Informativo oficial — transcrição reconstruída |
| TCE-CE-AC-186-2018 | Tauá — acórdão fundante histórico (cluster D1, marco temporal) | Informativo oficial — transcrição reconstruída |
| TCE-CE-RES-304-2009 | Fracionamento ilegal — três elementos cumulativos (par tese/antípoda com CON-05608-2021) | Informativo oficial — transcrição reconstruída |
| TCE-CE-AC-1898-2023 | Salitre — burla à LRF + licitação para admissão de profissionais de saúde | Informativo oficial — transcrição reconstruída |

**Sessão 2 — Rodada B2 (Blocos D3+D4+D5, 7 entradas):**

| ID | Tema | Selo |
|---|---|---|
| TCE-CE-AC-559-2025 | Vedação à análise subjetiva de atestados sob Lei 14.133/2021 | Informativo oficial — transcrição reconstruída |
| TCE-CE-AC-833-2026 | Conselho impertinente + vedação a consórcios sob Lei 14.133/2021 | Informativo oficial — transcrição reconstruída |
| TCE-CE-INFO-09-2025 | Desconto global obrigatório aos preços unitários de aditivos | Informativo oficial — transcrição reconstruída |
| TCE-CE-AC-479-2024 | Prorrogação de assessoria pontual + terceirização do controle interno | Informativo oficial — transcrição reconstruída |
| TCE-CE-INFO-08-2024 | Prorrogação exige pesquisa de preços + duas exceções | Informativo oficial — transcrição reconstruída |
| TCE-CE-AC-2001-2019 | Credenciamento como caminho regular (marco histórico) | Informativo oficial — transcrição reconstruída |
| TCE-CE-AC-459-2026 + AC-1902-2026 | Cooperativas e credenciamento na saúde sob Lei 14.133/2021 (entrada consolidada) | Informativo oficial — transcrição reconstruída |

---

## 3. ESTRUTURA PADRÃO DA ENTRADA

Cada arquivo `.md` da pasta contém: ID + cabeçalho com status/validação/fonte/última verificação; ementa oficial ou tese consolidada; síntese da decisão; aplicação típica; reference relacionado; notas críticas.

---

## 4. POLÍTICA DE VALIDAÇÃO — TRÊS SELOS CONSOLIDADOS

### Selo "validado por fonte primária"
Texto oficial recuperado em domínio do TCU, TCE-CE, STF ou STJ. **Citação direta segura em parecer**.

### Selo "validado por convergência alta"
Pinheiro/Mansur 2023 + 2 ou mais fontes secundárias independentes; OU Pinheiro/Mansur + portal oficial não-textual; OU para entradas TCE-CE da Sessão 2: informativo oficial do TCE-CE + transcrição reconstruída a partir do resumo. **Citação segura em parecer com cuidado redacional de atribuição da fonte**.

### Selo "validado por fonte secundária única"
Apenas uma fonte qualificada. Marcado com transparência e **pedido de confirmação futura em fonte primária** (Sessão 5). Citação em parecer formal **exige cautela redacional** e idealmente confirmação prévia.

### Selo específico da Sessão 2 — TCE-CE
"Validado por informativo oficial TCE-CE com transcrição reconstruída a partir do resumo" — toda entrada com este selo traz nota crítica explícita: "*A ementa oficial não foi acessada nesta validação; o conteúdo da decisão repousa sobre resumo do Informativo TCE-CE nº [X]. Antes de citar em parecer formal, recomenda-se confirmação contra inteiro teor no portal do TCE-CE.*"

---

## 5. ANOMALIAS CONSIGNADAS E CORRIGIDAS

### 5.1 Súmulas TCU descartadas

- **Súmula TCU 244** — **não existe sobre licitações**. **Substituída** pelo **TCU-AC-1536-2016-Plenário**. Nota dura em `armadilhas-tce-ce.md`.
- **Súmula TCU 245** — **existe, mas trata de aposentadoria estatutária**. **Substituída** pelo **TCU-AC-1176-2021-Plenário**. Nota dura em `armadilhas-tce-ce.md`.

### 5.2 Framing corrigido — Consulta TCE-CE Meruoca

Admitida com ID temático preciso e par tese/antípoda construído na Sessão 2 com TCE-CE-RES-304-2009.

### 5.3 Súmulas TCE-CE fora do escopo desta skill

Súmulas TCE-CE nº 1, 5, 6 e 7 não integram esta skill. Replicação seletiva sugerida para `defensor-tce-ce`, `embargos-de-declaracao` e skills futuras de direito financeiro.

---

## 6. CATEGORIAS TEMÁTICAS — MAPA DE NAVEGAÇÃO

### 6.1 Categoria "transversal"
Entradas que articulam estruturalmente o regime, sem se prender a subtipo isolado:
- **TCU-SUM-222** — aplicabilidade da jurisprudência federal às contratações municipais.

### 6.2 Clusters operacionais consolidados

**Cluster "inexigibilidade advocatícia"** (Bloco D1 — Sessão 2): TCE-CE-AC-186-2018 → TCE-CE-AC-2090-2025 → TCE-CE-AC-924-2026 + TCU-SUM-252. Curva temporal e de severidade.

**Cluster "fracionamento × descentralização"** (par tese/antípoda): TCE-CE-RES-304-2009 ↔ TCE-CE-CON-05608-2021. Critério estruturante: autonomia orçamentária e financeira efetiva.

**Cluster "preservação do equilíbrio em aditivos"**: TCU-AC-1536-2016 (limite quantitativo) + TCE-CE-INFO-09-2025 (desconto global). Cobertura federal-local.

**Cluster "prorrogação irregular"** (Bloco D4): TCE-CE-AC-479-2024 (vício material) + TCE-CE-INFO-08-2024 (vício procedimental) + cluster do IPCA.

**Cluster "saúde municipal — caminho correto"**: TCE-CE-AC-2001-2019 → TCE-CE-AC-1898-2023 (caminho errado, Salitre) → TCE-CE-AC-459-2026 + AC-1902-2026. Sete anos de jurisprudência estável.

**Cluster "objetividade na habilitação"**: TCU-SUM-263 + TCE-CE-SUM-2 + TCE-CE-AC-559-2025. Regra numérica federal + regra qualitativa local.

**Cluster "restrições editalícias indevidas"**: TCU-AC-1176-2021 + TCE-CE-AC-833-2026 + TCU-SUM-272.

### 6.3 Padrão jurisprudencial cearense — modulação temporal
Identificado em TCE-CE-AC-924-2026, TCE-CE-AC-1898-2023, Resolução TCE-CE nº 4764/2023. Estrutura: irregularidade reconhecida + circunstância atenuante (déficit estrutural; orientação em transição; boa-fé documentada). Dialoga com art. 22 da LINDB.

---

## 7. AÇÕES PENDENTES PARA FECHAMENTO DO CICLO

### Sessão 3 — Doutrina (próxima)
Caminho metodológico (b) — validação por dupla referência qualificada. 10-15 entradas iniciais de Justen Filho e Niebuhr com cross-refs antecipados.

### Sessão 4 — Casos paradigmáticos
5-7 casos do histórico do escritório. Caso candidato natural: Salitre 1898/2023 (com autorização integral consignada).

### Sessão 5 — Complemento de jurisprudência
Confirmar inteiro teor dos 12 acórdãos/informativos TCE-CE da Sessão 2 + Consulta Meruoca + PDFs intranet Súmulas 3 e 4.

### Fechamento — skill v2.8.0 ou v3.0.0
Substituir marcadores `[VERIFICAR — ...]` nos references por IDs do banco curado. Atualizar SKILL.md. Bumpar evals.json. Decisão de versão final.

---

## FIM DO INDEX
