# INDEX.md — Banco Curado de Manuais Oficiais do TCU

**Estado da pasta na v5.0:** **populado e operacional**. Conforme decisões metodológicas consolidadas na Sessão 3 (12/05/2026), o banco contém **13 entradas validadas** do Manual TCU 5ª ed. (2025), distribuídas em **6 blocos temáticos** que cobrem o núcleo doutrinário institucional da Lei 14.133/2021. Todas as entradas estão chanceladas pelo Dr. Matheus Nogueira Pereira Lima sob o **selo único "validado por fonte primária oficial TCU"**.

**Substituição metodológica registrada na Sessão 3:** esta pasta substitui integralmente a antiga `doutrina/` (que estaria preenchida com citações de Justen Filho, Niebuhr, Coelho Motta, Di Pietro). A decisão de substituição se fundamenta em três razões consolidadas:

- **Peso institucional superior** — citar "Manual TCU, *Licitações & Contratos*, 5. ed., 2025, p. X" em parecer dirigido ao TCE-CE ou ao próprio TCU é citar a Corte contra ela mesma; nenhuma doutrina privada alcança esse peso institucional.
- **Atualização integral à Lei 14.133/2021** — o Manual TCU 5ª ed. (2025) nasce sob o regime da Lei nova, sem necessidade de transposição interpretativa da Lei 8.666/93.
- **Salvaguarda metodológica resolvida em raiz** — com publicação oficial estática e paginação fixa, dispensa-se a estrutura de dupla referência qualificada que seria necessária para doutrina privada.

**Histórico:**
- **v2.7.0–v2.8.0-rc2** — pasta `doutrina/` apenas estrutural (INDEX), sem entradas.
- **v2.9.0** (Sessão 3, 12/05/2026) — substituição executada; 13 entradas admitidas. **Estado atual.**

---

## 1. ESTRUTURA DA PASTA

```
manuais-tcu/
├── INDEX.md                         (este arquivo)
├── GAP_REPORT_SESSAO_3.md           (registro da Sessão 3)
└── tcu-manual-2025/                 (13 entradas — Manual TCU 5ª ed. (2025))
    ├── MANUAL-TCU-2.1-INTEGRIDADE-001.md
    ├── MANUAL-TCU-2.6-AUDITORIA-INTERNA-001.md
    ├── MANUAL-TCU-3.2-PRINCIPIOS-001.md
    ├── MANUAL-TCU-4.7-PARECER-001.md
    ├── MANUAL-TCU-4.7-PARECER-002.md
    ├── MANUAL-TCU-5.9.1-CREDENCIAMENTO-001.md
    ├── MANUAL-TCU-5.10-CONTRATACAO-DIRETA-001.md
    ├── MANUAL-TCU-5.10.1.3-NOTORIA-001.md
    ├── MANUAL-TCU-5.10.1.3-NOTORIA-002.md
    ├── MANUAL-TCU-5.10.1.3-NOTORIA-003.md
    ├── MANUAL-TCU-5.10.2.1-DISPENSA-VALOR-001.md
    ├── MANUAL-TCU-6.2-ADITIVOS-001.md
    └── MANUAL-TCU-6.2-ADITIVOS-002.md
```

---

## 2. INVENTÁRIO DAS 13 ENTRADAS POR BLOCO TEMÁTICO

### 2.1 Padrão de ID

```
MANUAL-TCU-[SECAO]-[TEMA]-[NUM-SEQUENCIAL]
```

Exemplos: `MANUAL-TCU-5.10.1.3-NOTORIA-001`, `MANUAL-TCU-4.7-PARECER-001`, `MANUAL-TCU-6.2-ADITIVOS-002`.

### 2.2 Bloco D1 — Inexigibilidade e Notória Especialização — Seção 5.10.1.3 (3 entradas)

| ID | Eixo argumentativo | Páginas do Manual |
|---|---|---|
| `MANUAL-TCU-5.10.1.3-NOTORIA-001` | Os três requisitos cumulativos da inexigibilidade do art. 74, III, e a supressão da singularidade como requisito autônomo (reforma Lei 8.666/93 → Lei 14.133/2021) | 705-706 |
| `MANUAL-TCU-5.10.1.3-NOTORIA-002` | Comprovação objetiva da notória especialização — os sete vetores do art. 6º, XIX (desempenho anterior, estudos, experiência, publicações, organização, aparelhamento, equipe técnica) | 707-709 |
| `MANUAL-TCU-5.10.1.3-NOTORIA-003` | Inviabilidade qualitativa de competição como impossibilidade de critério objetivo, não como ausência de pluralidade de prestadores — distinção art. 74, III × art. 74, I | 706-707, 710 |

### 2.3 Bloco D2 — Análise jurídica da contratação (parecer art. 53) — Seção 4.7 (2 entradas)

| ID | Eixo argumentativo | Páginas do Manual |
|---|---|---|
| `MANUAL-TCU-4.7-PARECER-001` | Qualidade técnica do parecer — três vetores do art. 53, § 1º, II (completude, efetividade, clareza); extensão objetiva do § 4º (alcança aditivos, convênios, adesões); exigência de conclusividade (Acórdão 521/2013-Plenário) | 490-495 |
| `MANUAL-TCU-4.7-PARECER-002` | Segunda linha de defesa (art. 169, II) e proteção do agente público pelo art. 10 — direito à representação judicial; preservação após desligamento (§ 2º); exceção restrita ao dolo provado (§ 1º, II) | 491-492 |

### 2.4 Bloco D3 — Alteração contratual / aditivos — Seção 6.2 (2 entradas)

| ID | Eixo argumentativo | Páginas do Manual |
|---|---|---|
| `MANUAL-TCU-6.2-ADITIVOS-001` | Limites do art. 125 (25%/50%) — cálculo isolado sobre acréscimos e supressões; vedação à compensação entre itens distintos; três regimes de base (item/lote/global); exceção do restabelecimento de item suprimido | 935-940 |
| `MANUAL-TCU-6.2-ADITIVOS-002` | Alterações consensuais sujeitas aos mesmos limites (art. 124, II) + extrapolação excepcionalíssima com os seis pressupostos cumulativos da Decisão 215/1999-TCU-Plenário | 943-946 |

### 2.5 Bloco D4 — Dispensa e Credenciamento — Seções 5.10, 5.10.2.1 e 5.9.1 (3 entradas)

| ID | Eixo argumentativo | Páginas do Manual |
|---|---|---|
| `MANUAL-TCU-5.10-CONTRATACAO-DIRETA-001` | Estrutura procedimental do art. 72 — simetria com processo licitatório; planejamento obrigatório; pesquisa de preços como teste de viabilidade da inexigibilidade (IN-Seges/ME 65/2021, art. 7º, § 3º); checklist instrutório de oito elementos | 682-687 |
| `MANUAL-TCU-5.10.2.1-DISPENSA-VALOR-001` | Tridimensionalidade da base do art. 75, § 1º (unidade gestora + ramo de atividade + exercício); critério da autonomia orçamentária e financeira efetiva; duplicação para consórcios; cálculo plurianual (ON-AGU 87/2024) | 720-724 |
| `MANUAL-TCU-5.9.1-CREDENCIAMENTO-001` | Três hipóteses do art. 79 — paralela e não excludente, seleção a critério de terceiros, mercados fluidos; arquitetura tripartite (licitação × inexigibilidade III × credenciamento); roteiro completo para saúde municipal cearense | 644-647 |

### 2.6 Bloco D5 — Governança e Controle — Seção 2 (2 entradas)

| ID | Eixo argumentativo | Páginas do Manual |
|---|---|---|
| `MANUAL-TCU-2.1-INTEGRIDADE-001` | Promoção da integridade como dever da alta administração (art. 11, parágrafo único) — três planos sobrepostos de vedação ao conflito de interesses (arts. 7º, III; 9º, §§ 1º e 2º; 14, IV); segregação de funções; programa de integridade em grande vulto; arquitetura das três linhas de defesa (art. 169) | 13-24 |
| `MANUAL-TCU-2.6-AUDITORIA-INTERNA-001` | Auditoria interna como terceira linha de defesa (art. 169, III) — três modalidades (avaliação/consultoria/apuração); art. 170 como vinculação cogente do controle externo aos critérios de oportunidade, materialidade, relevância e risco; art. 171, II como vedação a interpretações tendenciosas | 111-129 |

### 2.7 Bloco D6 — Transversal — Princípios e Critérios — Seções 3.2 e 3.4 (1 entrada consolidada)

| ID | Eixo argumentativo | Páginas do Manual |
|---|---|---|
| `MANUAL-TCU-3.2-PRINCIPIOS-001` | Economicidade como relação custo-benefício (não menor preço) — princípio do art. 5º; arquitetura plural de critérios do art. 33; critério de maior retorno econômico (art. 33, VI c/c art. 39 — contratos de eficiência); vantajosidade global × vantajosidade momentânea | 149-157, 172-175, 192-196 |

---

## 3. ESTRUTURA PADRÃO DAS ENTRADAS

Cada entrada `.md` segue o seguinte padrão consolidado (modelo da Sessão 3):

```markdown
# [ID] — [Título descritivo do eixo argumentativo]

**Fonte:** Tribunal de Contas da União
**Obra:** Licitações & Contratos: Orientações e Jurisprudência do TCU
**Edição:** 5. ed., Brasília: TCU, Secretaria-Geral da Presidência, 2025. 1.017 p.
**Seção:** [Capítulo e subseção do Manual]
**Página(s):** [intervalo]
**Apresentação:** Ministro Bruno Dantas, Presidente do TCU
**Status:** validado por fonte primária oficial TCU
**Validado em:** [data] (chancelado por Dr. Matheus)
**Última verificação:** [data]

## Proposição central (paráfrase funcional)
## Desenvolvimento (transcrição literal — Manual TCU 2025, p. X)
## Tema da skill / Aplicação típica
## Cross-refs com banco jurisprudencial
## Cross-refs internos à pasta `manuais-tcu/`
## Nota operacional (fórmula de citação em parecer)
## Notas críticas (articulações com cluster operacional, recomendações específicas para o escritório)
```

---

## 4. SELO DE VALIDAÇÃO — ÚNICO

### Selo "validado por fonte primária oficial TCU"

Todas as 13 entradas estão sob este selo único. Citação direta segura em parecer, sem necessidade de upgrade prévio ou verificação adicional. Caráter da obra (Manual oficial editado pelo próprio TCU, sob apresentação do Ministro Bruno Dantas) elimina a necessidade das três salvaguardas que seriam aplicáveis a doutrina privada (upgrade priority; restrição a fontes qualificadas; nota operacional reforçada).

**Verificação anual recomendada:** o TCU pode publicar novas edições do Manual. Antes de citar em parecer formal, **confirmar a vigência da 5ª edição** consultando o portal do TCU (https://portal.tcu.gov.br/manuais).

---

## 5. CLUSTERS OPERACIONAIS CONSOLIDADOS — ARTICULAÇÃO COM BANCO JURISPRUDENCIAL

A leitura conjunta das 13 entradas com o banco jurisprudencial (`jurisprudencia/`, 49 entradas) revela **oito articulações operacionais** que estruturam a defesa preventiva e reparadora:

### 5.1 Cluster "inexigibilidade advocatícia" (núcleo do contencioso atual)
**Bloco doutrinário:** `NOTORIA-001` + `NOTORIA-002` + `NOTORIA-003`
**Bloco jurisprudencial:** `TCU-SUM-39` + `TCU-SUM-252` + cluster TCE-CE D1 (AC-186/2018 + AC-2090/2025 + AC-924/2026)
**Cobertura:** Sete anos de jurisprudência consolidada + moldura institucional federal.

### 5.2 Cluster "fracionamento × descentralização" (par tese/antípoda)
**Bloco doutrinário:** `DISPENSA-VALOR-001`
**Bloco jurisprudencial:** `TCE-CE-RES-304-2009` (antifracionamento — três elementos) ↔ `TCE-CE-CON-05608-2021` (Meruoca — autonomia efetiva)
**Cobertura:** Federal-local com base tridimensional explícita.

### 5.3 Cluster "preservação do equilíbrio em aditivos"
**Bloco doutrinário:** `ADITIVOS-001` + `ADITIVOS-002`
**Bloco jurisprudencial:** `TCU-AC-1536-2016` (leading-case federal) + `TCE-CE-INFO-09-2025` (desconto global cearense)
**Cobertura:** Federal-local com vertentes unilateral e consensual.

### 5.4 Cluster "saúde municipal — caminho correto"
**Bloco doutrinário:** `CREDENCIAMENTO-001` + `DISPENSA-VALOR-001` (par contrastivo)
**Bloco jurisprudencial:** `TCE-CE-AC-2001-2019` (marco fundante) → `TCE-CE-AC-1898-2023` (Salitre, contraexemplo) → `TCE-CE-AC-459-2026 + AC-1902-2026` (densificação sob Lei 14.133/2021)
**Cobertura:** Sete anos de jurisprudência cearense estável.

### 5.5 Cluster "parecer prévio e proteção do agente"
**Bloco doutrinário:** `PARECER-001` + `PARECER-002`
**Bloco jurisprudencial:** candidatos a admissão: Acórdão 521/2013-Plenário (conclusividade), Acórdão 873/2011-Plenário, Acórdão 3014/2010-Plenário
**Cobertura:** Qualidade técnica do parecer + arquitetura protetiva do art. 10.

### 5.6 Cluster "governança e integridade"
**Bloco doutrinário:** `INTEGRIDADE-001` + `AUDITORIA-INTERNA-001`
**Bloco jurisprudencial:** articulação direta com `TCU-SUM-222` (transversal); par estrutural com casos de conflito de interesses (caso Araripe — NF MP 01.2026.00007045-1, na carteira ativa).

### 5.7 Cluster "objetividade na habilitação"
**Bloco doutrinário:** referência implícita em todas as entradas (sem entrada autônoma)
**Bloco jurisprudencial:** `TCU-SUM-263` + `TCE-CE-SUM-2` + `TCE-CE-AC-559-2025`
**Cobertura:** Regra numérica federal + regra qualitativa local + densificação sob Lei nova.

### 5.8 Cluster "transversal — economicidade e aplicabilidade"
**Bloco doutrinário:** `PRINCIPIOS-001`
**Bloco jurisprudencial:** `TCU-SUM-222` (par transversal estrutural)
**Cobertura:** Princípios estruturantes + aplicabilidade da jurisprudência federal aos municípios.

---

## 6. ARTICULAÇÃO COM O BRIEFING DE TRANSFERÊNCIA À SKILL `defensor-tce-ce`

Tema deslocado da entrada `PARECER-002` para a skill irmã: **regime de responsabilização do parecerista** (art. 28 LINDB + MS 24.631/STF + standard do erro grosseiro do Manual TCU 2025). O briefing completo (`BRIEFING_DEFENSOR_TCE_CE_responsabilizacao_parecerista.md`) consta da entrega da Sessão 3, **fora desta skill**, para ativação futura na curadoria autônoma da skill `defensor-tce-ce`. Decisão registrada no `GAP_REPORT_SESSAO_3.md`.

---

## 7. CANDIDATOS PRIORITÁRIOS A ADMISSÃO FUTURA NO BANCO JURISPRUDENCIAL

Identificados ao longo da curadoria das Sessões 1-3 (acórdãos e decisões expressamente citados pelo Manual TCU 2025 e pelo banco jurisprudencial, ainda não admitidos):

| ID provisório | Bloco | Tema |
|---|---|---|
| `TCU-AC-521-2013` | D2 | Exigência de parecer conclusivo (aprovação/rejeição explícita) |
| `TCU-AC-873-2011` | D2 | Minuta-padrão previamente aprovada |
| `TCU-AC-3014-2010` | D2 | Aprovação prévia e regime excepcional da minuta-padrão |
| `TCU-DEC-215-1999` | D3 | Leading-case da extrapolação excepcionalíssima (seis pressupostos) |
| `TCU-AC-781-2021` | D3 | Replica os seis pressupostos sob a Lei 8.666/93 |
| `TCU-AC-50-2019` | D3 | Pressupostos sob a Lei 8.666/93 |
| `TCU-AC-66-2021` | D3 | Restabelecimento de item suprimido não é compensação vedada |
| `TCU-AC-3266-2022` | D3 | Confirma cálculo isolado sob a Lei 8.666/93 |
| `TCU-AC-591-2011` | D3 | Determinação clara da regra do cálculo isolado |
| `TCU-AC-349-2014` | D3 | Vedação à compensação de subpreço com sobrepreço |
| `TCU-AC-351-2010` | D4 | Credenciamento paralelo e não excludente (fundante) |
| `TCU-AC-352-2016` | D4 | Credenciamento de serviços médicos e exames laboratoriais |
| `TCU-AC-1094-2021` | D4 | Credenciamento de passagens aéreas (mercados fluidos) |
| `TCU-AC-1171-2017` | D5 | Articulação entre planejamento da auditoria interna e objetivos da gestão |
| `ON-AGU-17/2011` | D1, D4 | Razoabilidade do valor em inexigibilidade |
| `ON-AGU-87/2024` | D4 | Cálculo plurianual em dispensa por valor |

**Total:** 16 candidatos prioritários identificados — sugestão de admissão em sessão complementar (Sessão 5).

---

## 8. AÇÕES PENDENTES PARA FECHAMENTO DO CICLO

### Sessão 4 — Casos paradigmáticos (descontinuada)
A pasta `casos-paradigmaticos/` foi **removida na v2.9.0** por decisão de curadoria. Os casos paradigmáticos do escritório passam a integrar diretamente as notas críticas das entradas dos bancos `jurisprudencia/` e `manuais-tcu/` quando relevantes — modelo já aplicado no cluster D1 (TCE-CE-AC-186/2018 + 2090/2025 + 924/2026) e nas notas críticas das 13 entradas do Manual TCU. Casos específicos da carteira ativa (Salitre, Araripe, Potengi, Saboeiro) ficam registrados em pareceres concretos e em briefings de continuidade, não em arquivo autônomo do banco.

### Sessão 5 — Complemento de jurisprudência
Admissão dos 16 candidatos prioritários identificados na seção 7 acima. Confirmação de inteiro teor das 12 entradas TCE-CE da Sessão 2 (informativos oficiais com transcrição reconstruída). Confirmação dos PDFs intranet das Súmulas TCE-CE 3 e 4.

### Fechamento do ciclo da skill — v3.0.0 (futura)
Substituição completa dos marcadores residuais `[VERIFICAR — ...]` ainda presentes nos references por IDs do banco curado. Atualização do SKILL.md e bump do evals.json com testes que invoquem entradas do banco `manuais-tcu/`. Decisão sobre versão final.

---

## FIM DO INDEX
