# execucao-fiscal-lef.md

> **Reference da skill:** `parecer-tributario-financeiro`
> **Vertente:** Tributária — execução fiscal
> **Recorte EXCLUSIVO:** vertente do **MUNICÍPIO EXEQUENTE.** Defesa do executado (embargos, EPE, impugnação) → `defesa-acoes-de-execucao`

---

## Gatilhos de carregamento

- Execução fiscal sob ótica do município exequente
- CDA — requisitos, vícios, substituição (Súmula 392/STJ)
- Inscrição em dívida ativa
- Citação, penhora, BACENJUD/SISBAJUD, RENAJUD
- Redirecionamento ao sócio (Súmula 435/STJ; Tema 962/STJ; Tema 981/STJ)
- IDPJ na execução fiscal (Tema 962/STJ)
- Prescrição intercorrente (carregar `prescricao-decadencia-tributaria.md`)
- Bem de família (Lei 8.009 art. 3º, IV)
- Suspensão da execução por parcelamento
- Habilitação de crédito em falência

---

## 1. Núcleo da disciplina

A execução fiscal é o instrumento processual pelo qual a Fazenda municipal cobra **judicialmente** o crédito tributário e o não-tributário. Disciplinada pela **Lei 6.830/80 (LEF)** e supletivamente pelo CPC, é a peça-chave da capacidade arrecadatória.

Para municípios pequenos: simultaneamente principal instrumento de coação e maior fonte de frustração — taxa de êxito modesta, contencioso massivo, custo operacional elevado.

Contencioso dominado por dois eixos:
1. **Vícios formais da CDA** (Súmula 392/STJ — substituição até a sentença, mas não convalida vícios essenciais)
2. **Redirecionamento ao sócio-gerente** em dissolução irregular (Súmula 435/STJ + Tema 962/STJ + Tema 981/STJ)

Três decisões-chave do parecerista exequente:
1. **Garantir higidez da CDA** antes do ajuizamento — checklist do art. 2º LEF
2. **Manejar constrição patrimonial com agilidade** — BACENJUD/SISBAJUD imediato; RENAJUD; busca cartorial
3. **Proteger o crédito da prescrição intercorrente** (Tema 566/STJ)

---

## 2. Marco normativo

### LEF (Lei 6.830/80)
- **Art. 2º** — dívida ativa; requisitos da CDA
- **Art. 3º** — presunção de certeza e liquidez da CDA
- **Art. 6º** — petição inicial
- **Art. 7º** — citação
- **Art. 8º** — modalidades de citação
- **Art. 11** — ordem de penhora
- **Art. 16** — embargos do executado
- **Art. 40** — prescrição intercorrente

### CTN
- **Art. 201** — dívida ativa
- **Art. 202** — termo de inscrição
- **Art. 203** — vício na inscrição
- **Art. 204** — presunção de certeza e liquidez
- **Arts. 184-193** — garantias e privilégios

### CPC (aplicação supletiva)
- **Arts. 824 e ss.** — penhora
- **Arts. 854 e ss.** — penhora online (BACENJUD/SISBAJUD)
- **Arts. 133 e ss.** — IDPJ

### Lei 8.009/1990
- **Art. 3º, IV** — exceção do bem de família: o crédito tributário relativo ao próprio imóvel (IPTU, contribuição de melhoria) afasta a impenhorabilidade

### Súmulas STJ
- **Súmula 392** — substituição da CDA até a sentença, vedada modificação do sujeito passivo
- **Súmula 435** — dissolução irregular gera responsabilidade pessoal do sócio-gerente
- **Súmula 393** — exceção de pré-executividade admitida para matérias conhecíveis de ofício sem dilação probatória (ótica do executado)
- **Súmula 451** — legitimidade do MP para o ajuizamento (não aplicável a tributo municipal)
- **Súmula 559** — encargo legal do art. 1º do DL 1.025/69 não se aplica a Estados e Municípios

🔒 EXIGE pesquisa-jurisprudencial.

Fonte: <https://www.planalto.gov.br/ccivil_03/leis/l6830.htm>

---

## 3. CDA e inicial da execução

### Requisitos da CDA (LEF art. 2º + CTN art. 202)
- Nome do devedor e, sendo o caso, dos co-responsáveis
- Quantia devida, modo de calcular (juros e correção)
- Origem, natureza e fundamento legal
- Data da inscrição
- Número do processo administrativo (quando houver)

### Presunção de certeza e liquidez (LEF art. 3º; CTN art. 204)
**Relativa.** Pode ser ilidida por prova inequívoca produzida pelo executado ou por terceiro.

### Substituição da CDA (LEF art. 2º, §8º; Súmula 392/STJ)
- **Até a sentença** dos embargos
- **Não convalida vício essencial** (ausência de elementos que comprometem a defesa do executado)
- **Não pode modificar o sujeito passivo** (Súmula 392)

### Petição inicial (LEF art. 6º)
- Juiz competente
- Requerimento de citação
- Requerimento da medida cautelar fiscal (se cabível)
- Pedido de penhora
- Indicação de bens à penhora (se conhecidos)

---

## 4. Citação e constrição patrimonial

### Modalidades de citação (LEF art. 8º)
- Carta com AR (regra)
- Oficial de Justiça (se a carta retornar negativa)
- Edital (se não localizado em qualquer outra modalidade)

### Citação por edital — cuidados
**Tema 1.144/STJ** (🔒 verificar) — citação por edital deve ser precedida de tentativa real, com diligência efetiva.

### Penhora — ordem (LEF art. 11)
1. Dinheiro
2. Títulos da dívida pública e títulos de crédito com cotação em bolsa
3. Pedras e metais preciosos
4. Imóveis
5. Navios e aeronaves
6. Veículos
7. Móveis e semoventes
8. Direitos e ações

### BACENJUD/SISBAJUD
**Sistema integrado** que permite penhora online de ativos financeiros. Após CPC/2015 e jurisprudência consolidada, **não exige esgotamento prévio** de outras formas de penhora — é instrumento ordinário.

### RENAJUD
Sistema integrado para penhora de veículos. Solicitação automática.

### Bem de família — exceção do IPTU
Lei 8.009 art. 3º, IV: o bem de família **não** é impenhorável quando o crédito tributário decorre do próprio imóvel — IPTU, contribuição de melhoria, taxas vinculadas ao imóvel. Aplicação direta em execuções fiscais municipais.

🔒 verificar redação do inciso IV.

---

## 5. Redirecionamento — TEMA SENSÍVEL

### Súmula 435/STJ
**Dissolução irregular** (presumida pela ausência da empresa no endereço cadastrado, sem comunicação aos órgãos competentes) **gera responsabilidade pessoal do sócio-gerente** (CTN art. 135, III).

### Tema 962/STJ — IDPJ na execução fiscal
**Tese:** "O incidente de desconsideração da personalidade jurídica (IDPJ) é dispensável para o redirecionamento da execução fiscal nos casos em que a dissolução irregular configura a hipótese da Súmula 435/STJ ou em outras hipóteses do art. 135 do CTN, sendo aplicável quando se pretende redirecionamento por outras hipóteses." 🔒 verificar redação completa

**Implicação:** Em dissolução irregular (Súmula 435), o redirecionamento é direto, sem IDPJ. Para outras hipóteses de responsabilização não cobertas pelo art. 135 do CTN, IDPJ é obrigatório.

### Tema 981/STJ — prazo para redirecionar
**Tese:** o redirecionamento ao sócio-gerente em dissolução irregular **deve ocorrer dentro de 5 anos da diligência que constatou a dissolução**. 🔒 verificar redação.

**Implicação:** o município tem **5 anos do AR negativo** (que constatou a ausência da empresa) para pedir o redirecionamento. Após, ocorre prescrição.

### Procedimento
1. Requerer ao juízo a expedição de mandado para certificação da situação da empresa
2. Constatada dissolução irregular, requerer redirecionamento (Súmula 435)
3. Em outras hipóteses de responsabilidade, requerer IDPJ (Tema 962)
4. Aguardar a manifestação do sócio (contraditório)
5. Decisão do juízo

---

## 6. Suspensão, parcelamento e habilitação

### Suspensão da execução
- Parcelamento ativo do executado (CTN art. 151, VI)
- Depósito integral (CTN art. 151, II)
- Liminar/tutela em ação anulatória (CTN art. 151, IV/V)

### Após rescisão de parcelamento
Retomar a execução com pedido de prosseguimento.

### Habilitação em falência
Crédito tributário tem privilégio (CTN art. 186) — preferência sobre demais créditos, salvo trabalhistas até 150 salários mínimos por credor.

---

## 7. Armadilhas técnicas

1. **CDA com vício essencial.** Substituição não cura.
2. **Modificar sujeito passivo na substituição da CDA.** Súmula 392.
3. **Não pedir BACENJUD/SISBAJUD logo no início.** Tema 566/STJ — diligência útil interrompe prescrição intercorrente.
4. **Pedir IDPJ em dissolução irregular.** Tema 962/STJ — desnecessário.
5. **Redirecionar após 5 anos da constatação da dissolução.** Tema 981/STJ — preclusão.
6. **Não cobrar IPTU sobre bem de família.** Lei 8.009 art. 3º, IV.
7. **Citação por edital sem tentativa real prévia.** Vício formal.
8. **Não retomar execução após rescisão de parcelamento.** Inércia gera prescrição intercorrente.
9. **Penhora fora da ordem do art. 11 LEF sem fundamento.** Possível impugnação.
10. **Habilitar crédito em falência sem documentar privilégio.** CTN art. 186.
11. **Não monitorar a Fazenda em data de tomada de ciência.** Tema 566/STJ — automaticidade do prazo.
12. **Inscrever em dívida ativa crédito viciado.** Quando há vício, retorna à origem para correção.
13. **Não fundamentar lança de citação.** AR negativo + tentativa de oficial de justiça antes do edital.

---

## 8. Checklist de triagem

| # | Pergunta |
|---|----------|
| 1 | A CDA atende aos requisitos do art. 2º LEF + art. 202 CTN? |
| 2 | A inscrição em dívida ativa foi precedida de constituição definitiva do crédito? |
| 3 | Há vício essencial na CDA? |
| 4 | A petição inicial atende ao art. 6º LEF? |
| 5 | A citação foi tentada por carta antes do edital? |
| 6 | BACENJUD/SISBAJUD foi pedido no início? |
| 7 | RENAJUD foi pedido para veículos? |
| 8 | A ordem de penhora do art. 11 LEF está sendo observada? |
| 9 | Em IPTU sobre imóvel: o bem de família foi corretamente afastado (Lei 8.009 art. 3º, IV)? |
| 10 | Em dissolução irregular: redirecionamento dentro de 5 anos do AR negativo? |
| 11 | Em outras hipóteses de responsabilização: IDPJ foi pedido (Tema 962)? |
| 12 | A Fazenda tomou ciência em data certa, para fins do Tema 566/STJ? |
| 13 | Em parcelamento: a execução está suspensa formalmente? |
| 14 | Em falência: crédito habilitado com privilégio (CTN art. 186)? |
| 15 | A prescrição intercorrente está sendo monitorada (carregar `prescricao-decadencia-tributaria.md`)? |

---

## 9. Camada cearense

- **TJCE — varas da Fazenda em Fortaleza:** especializadas em execução fiscal. Padrão decisório alinhado ao Tema 566/STJ.
- **Municípios pequenos sem comarca:** execuções tramitam na comarca-sede, com lentidão. Mobilização para diligências cartoriais é decisiva.
- **TCE-CE:** glosa em PCAs por baixa eficácia da execução fiscal. Município com taxa de êxito ínfima recebe determinação de plano de ação.
- **Cobrança de IPTU em loteamentos clandestinos:** prática comum no Ceará — execução com base em possuidor identificável (Súmula 399/STJ).
- **Procuradoria do município com baixa estrutura:** problema crônico em municípios pequenos. Recomenda-se contratação de assessoria especializada ou consórcio.

🔒 EXIGE pesquisa-jurisprudencial em e-SAJ TJCE para acórdãos paradigma.

---

## 10. Bloqueios e alertas

🔒 **JURISPRUDÊNCIA NÃO CONFIRMADA — EXIGE pesquisa-jurisprudencial:**
- Súmula 392/STJ (substituição CDA)
- Súmula 435/STJ (dissolução irregular)
- Tema 962/STJ (IDPJ)
- Tema 981/STJ (5 anos para redirecionar)
- Tema 1.144/STJ (citação por edital)
- Lei 8.009 art. 3º, IV (redação atual)

🔒 **PRESCRIÇÃO INTERCORRENTE EM CURSO:** sempre verificar via `prescricao-decadencia-tributaria.md`.

🔒 **CDA VICIADA:** parecer pode demandar retorno à origem para correção antes da inscrição.

---

## 11. Doutrina

- THEODORO JÚNIOR, Humberto. *Lei de Execução Fiscal*
- PAULSEN, Leandro. *Direito Tributário* (cap. execução fiscal)
- MARINS, James. *Direito Processual Tributário*
- HARADA, Kiyoshi. *Direito Financeiro e Tributário*
- COSTA, Regina Helena. *Curso de Direito Tributário*

---

## 12. References cruzados

- `credito-tributario.md` — constituição definitiva
- `prescricao-decadencia-tributaria.md` — Tema 566/STJ
- `iptu.md` — bem de família (Lei 8.009 art. 3º, IV)
- `competencia-tributaria-municipal.md` — imunidade recíproca
- **Skill irmã:** `defesa-acoes-de-execucao` (vertente do executado)

---

*Reference operacional. Validação humana das marcações 🔒 obrigatória antes de uso em parecer real.*
