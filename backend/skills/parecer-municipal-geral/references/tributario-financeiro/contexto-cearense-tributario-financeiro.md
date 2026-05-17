# contexto-cearense-tributario-financeiro.md

> **Reference da skill:** `parecer-tributario-financeiro`
> **Função:** consolidação central das particularidades regionais cearenses em matéria tributária e financeira municipal
> **Recorte:** TCE-CE, TJCE, prática regional de municípios cearenses (especial atenção a municípios assessorados pelo escritório — Araripe, Salitre, Potengi, Saboeiro)

---

## Gatilhos de carregamento

- Município cearense identificado no caso
- Consulta envolve fiscalização do TCE-CE em curso ou potencial
- Jurisprudência do TJCE pode ser relevante (retenção de cota-parte ICMS, ações entre municípios e Estado)
- Particularidades de municípios pequenos do interior (DTP, falta de capacidade técnica em Fazenda, renúncia local)
- Programa "Transição Responsável" do TCE-CE acionado (fim de mandato, sucessor)

Carregamento adicional ao reference de matéria — **não substitui** os references temáticos. Em consulta sobre IPTU em Araripe, carregar `iptu.md` + este reference.

---

## 1. Mapa institucional do controle externo cearense

### TCE-CE — Tribunal de Contas do Estado do Ceará

Competente para fiscalizar a totalidade dos 184 municípios cearenses. Estrutura relevante para esta skill:

- **PCG (Contas de Governo do Prefeito)** — apreciação anual da gestão financeira global. Parecer prévio do TCE-CE submetido à Câmara Municipal para julgamento político (CF art. 31 §2º).
- **PCA (Contas de Gestão do Ordenador)** — julgamento direto pelo TCE-CE (CF art. 71, II). Engloba secretários municipais, ordenadores de despesa, gestores de fundos.
- **Representações** — ferramenta de provocação por cidadão, MP, vereador, partido político.
- **Inspeções e auditorias** — programadas ou em razão de denúncia.

**Glosas frequentes em matéria desta skill (consolidação observacional):**
- DTP (despesa total com pessoal) acima do limite prudencial (95% = 57%) sem plano de recondução
- Descumprimento do art. 42 da LRF — assumir despesa sem cobertura financeira nos últimos oito meses do mandato
- Concessão de benefícios fiscais (REFIS, isenção genérica) em fim de mandato sem estimativa de impacto (LRF art. 14)
- Inscrição irregular em Restos a Pagar não-processados (RPNP) sem disponibilidade de caixa
- Ausência ou insuficiência de procedimento prévio para cobrança da dívida ativa (lavratura, inscrição em CDA, impulso da execução fiscal)
- Não publicação tempestiva de RREO e RGF (LRF art. 52 e 55)

**Iniciativa "Transição Responsável"** (transicaoresponsavel.tce.ce.gov.br) — programa estruturado pelo TCE-CE para orientar transição entre gestões municipais. Particularmente relevante em pareceres sobre assunção de gestão por sucessor em janeiro de ano par.

🔒 **EXIGE pesquisa-jurisprudencial** para qualquer Acórdão TCE-CE concretamente citado em parecer. Acórdãos paradigmáticos não são citados de memória.

### TJCE — Tribunal de Justiça do Ceará

Competente para ações judiciais em que a controvérsia tributária ou financeira não foi pacificada por instância superior. Cenários típicos:

- **Retenção de cota-parte ICMS pelo Estado do Ceará** — ação de obrigação de fazer + cobrança movida pelo município contra o Estado. Tema 1.135/STF orienta o cabimento (a retenção deve obedecer à reserva de lei).
- **Mandado de segurança** contra Secretaria da Fazenda do Estado por bloqueio de FPM ou cota-parte sem fundamento legal estrito.
- **Discussão sobre Plano Diretor e IPTU progressivo no tempo** — embora o aspecto urbanístico vá para `parecer-administrativo-geral`, eventual discussão do tributo em si pode passar pelo TJCE.

🔒 **EXIGE pesquisa-jurisprudencial** para ementas e julgados específicos do TJCE.

---

## 2. Particularidades dos municípios cearenses pequenos e médios

A maioria dos municípios assessorados pelo escritório enfrenta um conjunto recorrente de fragilidades estruturais que afetam diretamente a produção de pareceres tributários e financeiros:

### 2.1 Tributário

- **CTM desatualizado.** Muitos municípios mantêm Códigos Tributários Municipais que não foram revisados desde a década de 1990. Dispositivos sobre prescrição, lançamento, base de cálculo do IPTU e alíquotas de ISS frequentemente colidem com a CF/88 redacionada por ECs posteriores e com a LC 116/2003. **Implicação:** parecer baseado no CTM municipal sem confronto com a moldura federal pode validar regime ilegal.
- **Planta Genérica de Valores (PGV) defasada.** Em vez de instituir PGV nova por lei (com observância da anterioridade), há recurso recorrente a "atualização por decreto" acima do índice oficial — vedação cristalizada na Súmula 160/STJ.
- **Cobrança de IPTU por destinação econômica versus localização formal.** Municípios cearenses do interior frequentemente lançam IPTU sobre imóveis com destinação rural produtiva, ignorando a regra do CTN art. 32 §1º e a jurisprudência do STJ sobre prevalência da destinação efetiva. Conflito ITR (federal) × IPTU (municipal) é recorrente.
- **ISS de cartórios extrajudiciais.** Enquadramento controvertido localmente, embora pacificado pela LC 116 (item 21 da lista anexa).
- **REFIS de IPTU a cada três ou quatro anos.** Prática comum, mas frequentemente conduzida sem estimativa de impacto e sem lei específica nos termos do art. 150 §6º da CF — gerando responsabilização posterior do gestor.

### 2.2 Financeiro

- **DTP com folga frágil.** Historicamente perto do limite global (60%), com prudencial estourado em vários quadrimestres. Decisão de aumento de pessoal exige cenário fiscal individualizado.
- **Cálculo deficiente da RCL.** Falta de capacidade técnica em pequenas Secretarias de Fazenda. A RCL é apurada de forma inconsistente entre Tesouro, Contabilidade e Controle Interno, gerando distorção do percentual da DTP.
- **Geração de despesa em fim de mandato.** Recorrente, com responsabilização frequente — concessão de reajuste, contratação de pessoal, criação de cargos, abertura de créditos especiais.
- **RPPS local com autossuficiência discutível.** Vários municípios cearenses operam Institutos Próprios de Previdência. Tratamento de inativos no cômputo da DTP depende de autossuficiência atuarial — muitos institutos operam em desequilíbrio sem o reconhecimento formal disso.
- **Servidores cedidos com ônus para o cessionário.** Prática comum em consórcios públicos (saúde, resíduos sólidos) e cessões para o Estado. O ônus financeiro entra na DTP do cessionário (LRF art. 18).
- **Ofício Circular nº 63/2025 do TCE-CE** sobre prazo de retorno ao limite de despesa de pessoal — 🔒 verificar destinatários e exigências exatas via `pesquisa-jurisprudencial` antes de citar em parecer.

### 2.3 Repasses constitucionais

- **FPM cearense.** Muitos municípios pequenos têm o FPM como mais de 70% da receita total. Retenção indevida pela União (CAUC, exigência fiscal sem base legal) gera pleito administrativo com fundamento no Tema 1.135/STF.
- **Cota-parte ICMS — IPM.** Distribuição calculada anualmente com base em índices. Pleitos administrativos de revisão do IPM (Índice de Participação dos Municípios) são via inicial; o judicial vem apenas após esgotamento.
- **Câmara Municipal — limite de 6%.** CF art. 29-A. Vedações próprias (§2º). Frequentemente desrespeitado em municípios pequenos com Câmara superdimensionada.

---

## 3. Matriz de referência cruzada por matéria

Para cada subtema desta skill, a camada cearense relevante está nos seguintes pontos:

| Subtema (reference principal) | Pontos cearenses relevantes |
|---|---|
| `iptu.md` | CTM desatualizado · PGV defasada · destinação econômica × localização formal · "atualização por decreto" |
| `iss-lc-116.md` | ISS de cartórios · ISS de empresas optantes do Simples · alíquota mínima (LC 157/2016) |
| `itbi.md` | Adoção do Tema 1.124/STF tardia em municípios pequenos · base de cálculo (Tema 1.113) |
| `taxas-municipais.md` | CIP — Contribuição de Iluminação Pública (CF art. 149-A) · base de cálculo questionada |
| `beneficios-fiscais.md` | REFIS frequente sem estimativa · IPTU social sem lei específica |
| `prescricao-decadencia-tributaria.md` | Inscrição em CDA com vícios · prescrição intercorrente em execuções paradas há mais de 5 anos (Tema 566/STJ) |
| `execucao-fiscal-lef.md` | Execuções paradas · falta de impulso · redirecionamento ao sócio incipiente |
| `lrf-limites-fiscais.md` | DTP perto do prudencial · cálculo deficiente da RCL · Iniciativa "Transição Responsável" · Of. Circ. 63/2025 |
| `planejamento-orcamentario.md` | LDO e LOA com defasagem técnica · Anexo de Metas Fiscais formal |
| `reparticao-receitas.md` | Retenção FPM · revisão do IPM · Tema 1.135/STF · TJCE |
| `despesa-publica-4320.md` | Empenho global irregular · liquidação sem ateste · ordem cronológica frequentemente desrespeitada |
| `restos-a-pagar.md` | RPNP em fim de mandato · art. 42 LRF · CP 359-C · pivô recorrente em PCG/PCA |

Para o ponto cearense específico de cada matéria, consultar a seção "Camada cearense" do reference correspondente — esta consolidação aqui é mapa, não substituto.

---

## 4. Cuidados redobrados em parecer para municípios cearenses

### 4.1 Verificação institucional prévia

Antes de redigir parecer para município cearense, verificar:
- Há PCG ou PCA em julgamento ou recente julgada com glosa relacionada ao tema?
- Há representação ou inspeção do TCE-CE em curso?
- Há ação no TJCE envolvendo o município (cobrança de cota-parte, retenção de FPM, discussão de tributo)?
- Há Ofício Circular do TCE-CE recente sobre o tema?

### 4.2 Linguagem do parecer

Em parecer voltado a município cearense, preferir:
- Citação a Acórdãos do TCE-CE (validados via `pesquisa-jurisprudencial`) — peso institucional regional
- Referência ao programa "Transição Responsável" quando o caso envolver fim de mandato
- Conexão entre o ato consultado e o histórico de glosas conhecidas em municípios da mesma faixa (sem citar nominalmente outros municípios)

### 4.3 Cuidados específicos por município assessorado

Os municípios assessorados pelo escritório (Araripe, Salitre, Potengi, Saboeiro) têm históricos próprios de processos no TCE-CE e contextos fiscais distintos. Sempre que possível, **consultar histórico recente** antes de produzir parecer — isso evita contradição com posições defendidas em representações em curso.

🔒 **EXIGE consulta ao histórico do escritório** antes de assumir posição em parecer que possa ser usado em defesa pendente.

---

## 5. Doutrina e referências de aprofundamento

A literatura jurídica regional especializada em direito tributário e financeiro municipal cearense é escassa. As referências mais úteis costumam ser:

- **TCE-CE — Estudos da Escola de Contas Públicas** — material de educação fiscal voltado a gestores e advogados municipais cearenses
- **AMUCE — Associação dos Municípios do Estado do Ceará** — informativos sobre repartição de receitas e ações coletivas
- **Manual de Procedimentos — Programa Transição Responsável** do TCE-CE

🔒 **EXIGE validação** antes de citar como referência doutrinária em parecer.

---

## 6. Bloqueios e alertas específicos da camada cearense

🔒 **NUNCA citar Acórdão do TCE-CE** sem `pesquisa-jurisprudencial` — a redação de ementas do TCE-CE é particular e frequentemente memoriza-se mal.

🔒 **NUNCA assumir que o histórico de glosas em municípios pequenos é normalizador** — o gestor tem dever de cumprir a moldura federal, ainda que vizinhos descumpram.

🔒 **NUNCA recomendar prática que tenha sido objeto de glosa do TCE-CE em PCG/PCA do próprio município** sem expressa ressalva e cenário alternativo.

🔒 **EM CASO DE DÚVIDA SOBRE OFÍCIO CIRCULAR DO TCE-CE** (números, anos, destinatários, exigências), marcar com a sintaxe `[!VERIFICAR: NÚMERO E ANO DO OFÍCIO CIRCULAR DO TCE-CE !]` e validar antes de citar (Regra ZT-5 do SKILL.md).

---

## Síntese

A camada cearense é o filtro regional que evita pareceres tecnicamente corretos no plano federal, mas operacionalmente desconectados da realidade do controle externo estadual. O TCE-CE julga PCG/PCA com critérios próprios; o TJCE atende contenciosos específicos; municípios pequenos têm fragilidades estruturais conhecidas. Ignorar essa camada produz parecer elegante e inexequível.

A consolidação central está aqui; o detalhamento por matéria está nos references temáticos respectivos.
