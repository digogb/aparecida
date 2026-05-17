# Bloqueios Obrigatórios

> 11 proibições absolutas que distinguem texto autoral do escritório de texto gerado por IA padrão. Cada bloqueio responde a um vício observado em documentos automáticos. **Bloqueio violado é refazer.**

---

## B1 — Prosa-bloco

**Proibido:** parágrafos longos com 6+ frases ou que carreguem múltiplas ideias entrelaçadas.

**Por quê:** parágrafo-bloco força o leitor a manter na memória curta múltiplos argumentos enquanto processa o atual. Fadiga, perda de foco, esquecimento da tese principal a meio-caminho do parágrafo.

**Como evitar:** ao escrever, perguntar a cada 3 frases — "esta ideia ainda é a mesma do início do parágrafo?". Se a resposta for não, abrir parágrafo novo. Uma ideia, um parágrafo.

**Princípio associado:** ★1.

---

## B2 — Subdivisão numerada da fundamentação

**Proibido:** subdivisão da seção II (Fundamentos) em subseções numeradas (1, 2, 3) ou alfabéticas (a, b, c) ou em algarismos romanos (II.1, II.2). **Em hipótese alguma.**

**Por quê:** este é o bloqueio mais distintivo do estilo do escritório. Subdivisão numerada da fundamentação é convenção legislativa ou acadêmica, não consultiva. Quando aplicada ao parecer, fragmenta o raciocínio jurídico maduro e faz o documento parecer gerado por IA padrão (que tende fortemente a essa fragmentação).

**Como evitar:** após `II — FUNDAMENTOS`, escrever em prosa contínua, usando os conectivos arquiteturais (`conectivos-arquiteturais.md`) para sinalizar transições entre movimentos argumentativos.

**Vício típico a corrigir:**

❌ Errado:
```
II — FUNDAMENTOS

1. Da impossibilidade de redução por decreto

[texto]

2. Da prerrogativa unilateral

[texto]

3. Do equilíbrio econômico-financeiro

[texto]
```

✅ Correto:
```
II — FUNDAMENTOS

[parágrafo de abertura com a tese central]
[parágrafos curtos desenvolvendo a tese]
"Compreendida essa dualidade, é preciso examinar agora..."
[parágrafos sobre a prerrogativa unilateral]
"Resta, portanto, examinar a dimensão constitucional..."
[parágrafos sobre o equilíbrio econômico-financeiro]
```

**Princípio associado:** ★2, ★8.

---

## B3 — Citação solta sem paráfrase funcional

**Proibido:** citar dispositivo legal, súmula ou acórdão e seguir o raciocínio sem paráfrase funcional que traduza o conteúdo em linguagem operacional.

**Por quê:** citação solta é "encher página" — o parecerista demonstra que conhece a norma, mas não demonstra que a *interpreta*. O destinatário do parecer (gestor municipal, secretário) frequentemente não decodifica o dispositivo legal por si só. A paráfrase funcional é serviço ao leitor *e* demonstração de domínio.

**Como evitar:** depois de cada citação literal recuada em bloco, abrir parágrafo iniciado por marcador interpretativo:

- "A leitura do dispositivo, à primeira vista, pode sugerir que..."
- "Em outras palavras, o que o artigo autoriza é..."
- "Convém registrar que esse dispositivo deve ser lido em conjunto com..."
- "A regra prática que decorre dessa norma é..."

**Princípio associado:** ★3.

---

## B4 — Ementa em prosa corrida

**Proibido:** ementa redigida como parágrafo de prosa, com sintaxe completa, em vez de palavras-chave separadas por travessão.

**Por quê:** ementa em prosa corrida atrasa a leitura inicial. O destinatário do parecer varre a ementa em segundos para captar conceitos centrais e a conclusão; se a ementa exige decodificação sintática, ela perde a função.

**Como evitar:** ementa do escritório usa o formato de palavras-chave separadas por travessão `―` (figure dash), com 1 a 2 palavras por bloco, terminando com a conclusão.

**Vício típico a corrigir:**

❌ Errado:
```
EMENTA: Trata-se de parecer consultivo acerca da viabilidade jurídica
de Decreto Municipal que determina redução linear de vinte por cento
no valor de todos os contratos administrativos vigentes, concluindo-se
pela inviabilidade jurídica da medida pela ausência dos requisitos do
art. 125 da Lei 14.133/2021 e pela violação ao princípio do equilíbrio
econômico-financeiro consagrado no art. 37, inciso XXI, da Constituição.
```

✅ Correto:
```
EMENTA: Direito Administrativo ― Contratos administrativos ― Decreto
Municipal ― Redução linear ― Inviabilidade jurídica ― Alteração
unilateral ― Limites do art. 125 da Lei 14.133/2021 ― Motivação
individualizada ― Equilíbrio econômico-financeiro ― Termo aditivo
― Rota legítima em três etapas ― Parecer desfavorável.
```

**Princípio associado:** ★6.

---

## B5 — CAIXA-ALTA dramática

**Proibido:** redigir alertas, advertências ou conclusões em CAIXA-ALTA, em parágrafo inteiro maiúsculo, em negrito agressivo ou em qualquer recurso tipográfico que sinalize "exclamação retórica" no parecer consultivo.

**Por quê:** CAIXA-ALTA dramática tem três custos. Compromete a unidade tipográfica do documento. Sugere que o parecerista grita por não confiar no peso do próprio texto. Empobrece o ethos do parecer ao trocar dignidade institucional por exclamação. Em peças contenciosas a CAIXA-ALTA pode ter função; em parecer consultivo, é vício.

**Como evitar:** alertas e advertências em prosa institucional sóbria, com marcador inicial que sinaliza a função protetiva — "Cumpre, ainda, advertir formalmente o gestor sobre o risco de...", "Vale registrar, por dever de informação...", "Não se ignora, contudo, o risco de...".

A função protetiva do alerta é cumprida pelo *conteúdo* (informar o risco com clareza), não pelo *grafismo* (gritar).

**Princípio associado:** ★7.

---

## B6 — URL inventada de jurisprudência

**Proibido:** inserir hyperlink fictício de jurisprudência. Em hipótese alguma o parecer pode trazer URL não validada apresentada como se fosse fonte real.

**Por quê:** URL inventada é o vício mais letal em documento consultivo. Compromete a confiabilidade do parecer em cascata — cliente que descobre URL falsa passa a desconfiar de todos os pareceres anteriores. Pode caracterizar litigância de má-fé se descoberto em peça processual derivada. Mancha o ethos profissional do escritório.

**Como evitar:** sempre que houver referência jurisprudencial, invocar a skill `pesquisa-jurisprudencial` para validação. Se a invocação não for possível na rodada atual (rascunho inicial, prazo apertado), o texto traz o marcador explícito `[a validar pela pesquisa-jurisprudencial]` no lugar da URL. Marcador é honesto. Invenção é fraude.

**Princípio associado:** ★10.

---

## B7 — Juridiquês arcaico

**Proibido:** uso de "destarte", "outrossim", "data venia", "em sede de", "ad argumentandum tantum", "ipso facto" e demais arcaísmos forenses sem função.

**Por quê:** juridiquês arcaico é a marca mais reconhecível do parecerista despreparado ou do gerador automático. Documento que abusa dessas expressões transparece insegurança disfarçada de erudição. O escritório opera em registro técnico moderno — preciso, denso, mas em português contemporâneo legível.

**Como evitar:** vocabulário técnico jurídico **sim**; arcaísmo sem função **não**. Se o termo arcaico tem equivalente moderno claro, usar o moderno.

**Substituições recomendadas:**

| Evitar | Preferir |
|--------|----------|
| Destarte | Assim, Portanto, Por essa razão |
| Outrossim | Além disso, Adicionalmente, Cumpre registrar |
| Data venia | Com o devido respeito, Respeitosamente |
| Em sede de | Em, No âmbito de |
| Ad argumentandum tantum | Apenas para argumentar, Em hipótese argumentativa |
| Ipso facto | Por isso mesmo, Imediatamente |
| Mui respeitosamente | Respeitosamente |
| Esposar tese | Sustentar tese, Adotar tese |
| Faz-se mister | É necessário, Cabe |

**Termos técnicos preservados** (não são juridiquês, são técnica): "ratio decidendi", "habeas corpus", "obiter dictum", "stare decisis", "leading case", "amicus curiae". Estes têm função técnica precisa e não devem ser substituídos.

---

## B8 — Subdivisão da fundamentação por título em negrito sem numeração

**Proibido:** burlar B2 inserindo títulos em negrito *sem* numeração ("Da impossibilidade", "Da prerrogativa", "Do equilíbrio") como se fossem parágrafos comuns. **É a mesma fragmentação com outra roupagem.**

**Por quê:** o vício é o mesmo — fragmentar a fundamentação em blocos rotulados. Trocar o número por negrito não muda o efeito tipográfico. O leitor ainda *para* a cada título, ainda perde fluxo, e o parecer ainda parece modelo automático.

**Como evitar:** se houver tendência a colocar título em negrito para sinalizar mudança de movimento, *substituí-lo por parágrafo de transição* — exatamente como recomendado em ★2 e detalhado em `conectivos-arquiteturais.md`.

**Princípio associado:** ★2, ★8.

---

## B9 — Elementos visuais (Visual Law) em parecer consultivo

**Proibido:** caixas ASCII, tabelas estruturais, fluxogramas, mapas mentais, ícones decorativos, infográficos textuais ou qualquer elemento de Visual Law no parecer consultivo do escritório.

**Por quê:** elementos visuais competem com a prosa madura em vez de complementá-la. Em parecer com fundamentação bem-construída, o texto *já é* visual law — a estrutura argumentativa é o mapa, a paráfrase funcional é o quadro de enquadramento, a sequência de recomendações é o roteiro. Acrescentar caixa visual é tornar tipograficamente explícito o que a prosa já fazia argumentativamente. Redundância, não complementaridade.

Em monoespaçada justificada (Consolas 12pt) com largura útil de pouco mais de quatorze centímetros, caixas ASCII ainda têm o problema técnico de quebra entre páginas e perda da unidade visual.

**Como evitar:** confiar na prosa. Se houver tentação de inserir caixa para "facilitar a visualização", verificar se a prosa pode ser melhor estruturada para cumprir a mesma função.

**Exceção controlada:** tabela simples (sem bordas elaboradas) pode ser usada em **anexos** ao parecer (cronograma, comparativo de valores, lista de documentos). No corpo da fundamentação, vedação absoluta.

---

## B10 — Tabela comparativa no corpo da fundamentação

**Proibido:** tabela de comparação ("antes vs. depois", "regra vs. exceção", "lei A vs. lei B") como recurso argumentativo no corpo da fundamentação.

**Por quê:** tabela comparativa rompe o fluxo narrativo da fundamentação e tem o mesmo efeito da subdivisão numerada — fragmenta o raciocínio em células ao invés de costurar em prosa. Comparações, no estilo do escritório, são feitas *em prosa*, com paralelismo sintático que evidencia a oposição.

**Vício típico a corrigir:**

❌ Errado: tabela "Lei 8.666/93 | Lei 14.133/2021" comparando dispositivos.

✅ Correto: parágrafo que abre paralelismo — "Sob a Lei 8.666/93, exigia-se [X]. A Lei 14.133/2021 manteve a exigência, mas alterou [Y]."

**Exceção controlada:** mesma do B9 — tabelas em anexos, não no corpo argumentativo.

---

## B11 — Conclusão sem indicação clara de favorável / desfavorável / com ressalvas

**Proibido:** parecer terminar sem explicitar, na primeira frase da seção III (Conclusão), se o parecer é **favorável**, **desfavorável** ou **favorável com ressalvas**.

**Por quê:** o destinatário do parecer precisa, ao chegar à conclusão, saber em uma única leitura qual é a resposta da consulta. Conclusão que se perde em recapitulação antes de explicitar a posição obriga o destinatário a inferir, e parecer não se infere — o parecerista responde.

**Como evitar:** primeira frase da seção III com fórmula consagrada:

- "Diante do exposto, e em resposta à consulta formulada, o parecer é **DESFAVORÁVEL** ao [objeto] na forma em que [editado/proposto/apresentado], por [síntese da razão central]."
- "Pelo exposto, opina-se **FAVORAVELMENTE** à [medida proposta], observados os parâmetros expostos na fundamentação."
- "Diante das considerações acima, o parecer é **FAVORÁVEL COM RESSALVAS**, condicionado às adequações detalhadas a seguir."

A indicação favorável / desfavorável vem em **negrito + maiúsculas** apenas na palavra-chave (única exceção tolerada de CAIXA-ALTA, justamente porque é marcador estrutural, não exclamação retórica).

---

# FAMÍLIAS POR MATÉRIA — específicas da `parecer-municipal-geral`

> Esta seção foi introduzida em **v3.1.0** (Etapa 3 da migração da camada da `parecer-lei-14133`, 15/05/2026). Os bloqueios temáticos a seguir **complementam** — jamais substituem — os onze bloqueios universais (B1 a B11) acima. Cada bloqueio temático foi formado a partir de jurisprudência primária validada via `web_search`, com referência expressa à Súmula, ao Tema ou ao precedente que o sustenta. Bloqueio sem lastro jurisprudencial é pior que ausência de bloqueio: abre flanco à parte adversa e fragiliza o parecer. A densidade de cada família é proporcional à massa jurisprudencial validada disponível.

A finalidade da família é a mesma dos onze bloqueios universais: **identificar pontos sobre os quais o parecer da matéria não pode ser silente**. Em direito municipal substantivo, há temas em que o silêncio é leitura indireta de inexistência — e produz parecer mutilado. A vedação ao silêncio é, em si, uma vedação positiva: o parecer **tem que** enfrentar.

Cada bloqueio temático segue o mesmo template dos onze universais (vedação, fundamentação, procedimento, princípio associado), mas acrescenta um campo: **fonte primária validada**, com data da última conferência.

---

## Família B-SERV — Servidores Públicos Municipais

> Aplicável quando a consulta envolver regime jurídico do servidor, provimento, acumulação, remuneração, vantagens, gratificações, abono, vínculo, PAD, sindicância, concurso, estabilidade, aposentadoria. Vertente A da `parecer-municipal-geral`. Sete bloqueios.

### B-SERV-1 — Silêncio sobre concurso público em ato que cria, transforma ou reenquadra cargo

**Vedação:** parecer que se manifesta sobre criação, transformação, reestruturação, fusão ou reenquadramento de cargo público sem enfrentar **expressamente** a exigência do concurso público (CF art. 37, II) e a vedação ao provimento derivado por ascensão, transposição ou acesso.

**Fundamentação:** Constituição Federal, art. 37, II; **Súmula Vinculante 43 do STF** — "É inconstitucional toda modalidade de provimento que propicie ao servidor investir-se, sem prévia aprovação em concurso público destinado ao seu provimento, em cargo que não integra a carreira na qual anteriormente investido." A Súmula consolidou a antiga Súmula 685 e a tese fixada na ADI 837. Há precedente do STF contra norma do próprio Estado do Ceará na ADI 5.909, em situação de reestruturação de carreira que dissimulava ascensão funcional.

**Procedimento de remediação:** ainda que o ato sob consulta não pareça à primeira vista provimento derivado, o parecer **abre parágrafo dedicado** ao tema, distingue (i) reestruturação legítima com unificação de carreiras iguais, (ii) promoção ordinária dentro da mesma carreira e (iii) ascensão funcional vedada. Quando o ato envolver nível de escolaridade diferente entre cargo de origem e cargo de destino, o parecer **explicita** a vedação.

**Princípio associado:** ★8 (estrutura tripartite com enfrentamento da questão central) e REGRA IRR-3 (verificação ativa quando há parte adversa, como em PAD ou em representação no MPCE).

**Fonte primária validada:** STF, Súmula Vinculante 43; STF, ADI 837/DF, Rel. Min. Moreira Alves, j. 27/08/1998; STF, ADI 5.909/CE, Rel. Min. Cármen Lúcia, j. 2024. Validação em 15/05/2026.

### B-SERV-2 — Silêncio sobre acumulação de cargos quando o caso envolver vínculos múltiplos

**Vedação:** parecer sobre situação funcional do servidor com dois ou mais vínculos que não enfrente expressamente as hipóteses constitucionais excepcionais do art. 37, XVI, da Constituição e os dois requisitos cumulativos pacíficos (compatibilidade de horários e observância do teto remuneratório).

**Fundamentação:** CF art. 37, XVI e XVII; STF, RE 565.453 (Tema 76, repercussão geral, sobre cumulação de funções); jurisprudência pacífica do STF e do STJ no sentido de que a compatibilidade de horários é requisito **material**, não meramente formal, e que o teto do art. 37, XI, opera sobre a **soma** dos vínculos.

**Procedimento de remediação:** quando o consulente narrar duas vinculações ativas, o parecer (i) enquadra a hipótese no inciso correto do art. 37, XVI; (ii) lista os requisitos cumulativos; (iii) sinaliza explicitamente que a compatibilidade de horários, na jurisprudência do STF, não se presume nem se confunde com a soma aritmética de 60 ou 80 horas semanais — exige aferição material, com declaração das chefias e, se for o caso, verificação local.

**Princípio associado:** ★3 (paráfrase funcional do art. 37, XVI, após citação literal) e ★4 (exemplo concreto da soma de vínculos).

**Fonte primária validada:** STF, RE 565.453, Tema 76, repercussão geral. Validação em 15/05/2026.

### B-SERV-3 — Silêncio sobre teto remuneratório constitucional em consulta de pagamento

**Vedação:** parecer que examine pagamento de vantagem, gratificação, abono, indenização ou subsídio sem mencionar o teto remuneratório constitucional (CF art. 37, XI) e, no município, sua expressão pelo subsídio do Prefeito.

**Fundamentação:** CF art. 37, XI; STF, ADI 4.014 e jurisprudência consolidada sobre o teto municipal.

**Procedimento de remediação:** parágrafo dedicado registrando (i) qual é o teto aplicável no município (subsídio do Prefeito como referência); (ii) se a vantagem em exame tem ou não natureza remuneratória sujeita ao teto; (iii) recomendação de aferição em folha pela Secretaria de Administração antes do pagamento.

**Princípio associado:** ★8 (enfrentamento estrutural) e B11 (conclusão clara — não há como concluir favoravelmente sem aferição do teto).

**Fonte primária validada:** STF, ADI 4.014; CF art. 37, XI. Validação em 15/05/2026.

### B-SERV-4 — Silêncio sobre reserva de lei para criação ou majoração de vantagem

**Vedação:** parecer que valide concessão, criação ou majoração de qualquer parcela remuneratória — vencimento, gratificação, abono, adicional, indenização — **sem lei municipal específica** que a institua. Vedação também à invocação do princípio da isonomia como fundamento autossuficiente para estender vantagem a categoria não originalmente contemplada na lei concessiva.

**Fundamentação:** CF art. 37, X e XIII; **Súmula Vinculante 37 do STF** — "Não cabe ao Poder Judiciário, que não tem função legislativa, aumentar vencimentos de servidores públicos sob o fundamento de isonomia." O Tema 315 (RE 592.317) e o Tema 600 (RE 710.293) reforçam que o princípio da isonomia, isoladamente, não autoriza extensão de vantagem por via judicial nem administrativa.

**Procedimento de remediação:** parágrafo enfrentando (i) qual a lei municipal que institui ou pretende instituir a parcela; (ii) ausência da lei = reprovação do ato proposto; (iii) presença de lei = exame da observância dos pressupostos formais (iniciativa adequada do art. 61, §1º, II, "a", CF — competência reservada do chefe do Executivo para servidores do Executivo).

**Princípio associado:** ★8 (enfrentamento da reserva legal) e B11 (conclusão clara sobre a juridicidade do ato).

**Fonte primária validada:** STF, Súmula Vinculante 37; STF, RE 592.317, Tema 315; STF, RE 710.293, Tema 600. Validação em 15/05/2026.

### B-SERV-5 — Silêncio sobre vedação ao nepotismo em consulta sobre nomeação de parente

**Vedação:** parecer sobre nomeação para cargo em comissão, função de confiança ou gratificada com vínculo de parentesco que não enfrente expressamente a Súmula Vinculante 13 e sua distinção entre cargos administrativos e cargos políticos.

**Fundamentação:** CF art. 37, caput (impessoalidade e moralidade); **Súmula Vinculante 13 do STF**; jurisprudência consolidada distinguindo (i) cargos em comissão, função de confiança e função gratificada — alcançados integralmente pela vedação; (ii) cargos políticos (Secretário Municipal, por exemplo) — tradicionalmente fora do alcance da SV 13, ressalvada a hipótese de fraude à lei (ausência manifesta de qualificação técnica ou inidoneidade moral do nomeado). O **Tema 1000 do STF** (RE 1.133.118) ainda está em julgamento e pode estreitar a exceção dos cargos políticos — recomenda-se conferência da última posição do Plenário antes de fechar o parecer.

**Procedimento de remediação:** parecer enfrenta a SV 13, identifica a natureza do cargo em questão (administrativo vs. político), aplica o teste de qualificação técnica e idoneidade moral se for cargo político, e — se houver risco — recomenda parecer prévio formal do Ministério Público local antes da nomeação. Em caso de **nepotismo cruzado** (designações recíprocas entre autoridades distintas), a vedação se aplica inclusive a cargos políticos.

**Princípio associado:** ★8 (enfrentamento da SV) e advertência protetiva sóbria ★7 (alertar o gestor para o risco de responsabilização pessoal).

**Fonte primária validada:** STF, Súmula Vinculante 13; STF, RE 1.133.118, Tema 1000 (em julgamento — conferir status no dia da redação). Validação em 15/05/2026.

### B-SERV-6 — Silêncio sobre vedação à contratação por tempo determinado fora das hipóteses do art. 37, IX

**Vedação:** parecer que valide contratação temporária por excepcional interesse público sem confrontar a hipótese concreta com os pressupostos do art. 37, IX, da Constituição, e sem distinguir contratação temporária genuína de **terceirização disfarçada** ou de **provimento precário substituto do concurso**.

**Fundamentação:** CF art. 37, IX; **Tema 612 do STF** (RE 658.026, com repercussão geral) — "Para que se considere válida a contratação temporária de servidores públicos, é preciso que: a) os casos excepcionais estejam previstos em lei; b) o prazo de contratação seja predeterminado; c) a necessidade seja temporária; d) o interesse público seja excepcional; e) a contratação seja indispensável, sendo vedada para os serviços ordinários permanentes do Estado que estejam sob o espectro das contingências normais da Administração." Conferência recomendada na última versão do informativo do STF antes de fechar o parecer.

**Procedimento de remediação:** parágrafo dedicado aplicando os cinco testes do Tema 612 ao caso concreto: a hipótese está em lei municipal? por quanto tempo? a necessidade é temporária ou permanente? o interesse é excepcional ou ordinário? a atividade é típica de quadro permanente? Se um dos testes falha, o parecer registra a falha e recomenda concurso público ou autorização legal específica.

**Princípio associado:** ★8 (enfrentamento estrutural) e ★3 (paráfrase funcional dos cinco requisitos do Tema 612).

**Fonte primária validada:** STF, RE 658.026, Tema 612, repercussão geral. Validação em 15/05/2026.

### B-SERV-7 — Silêncio sobre devolução de valores em revisão de ato favorável a servidor

**Vedação:** parecer que opine pela revisão ou anulação de ato administrativo gerador de vantagem percebida pelo servidor — abono, gratificação, adicional, progressão — sem enfrentar expressamente a questão da **boa-fé** do servidor e a (não) devolução de valores recebidos.

**Fundamentação:** STF, **Tema 531** (RE 638.115) — "Os valores recebidos de boa-fé pelo servidor público, em virtude de errônea ou inadequada interpretação da lei pela Administração Pública, não estão sujeitos à devolução"; LINDB arts. 22-24 (segurança jurídica e proteção da boa-fé). Atenção: em situações de **má-fé** comprovada ou de **decisão judicial** transitada em julgado contrária ao servidor, a devolução pode ser cabível — o parecer **distingue**.

**Procedimento de remediação:** quando o ato em revisão tiver gerado vantagem pecuniária ao servidor, o parecer aborda (i) o critério da boa-fé objetiva; (ii) o lapso temporal entre o ato originário e a revisão (decadência decenal do art. 54 da Lei 9.784/99, aplicável aos municípios por extensão jurisprudencial); (iii) a recomendação expressa sobre devolução ou não devolução, com indicação do prazo prescricional eventualmente aplicável.

**Princípio associado:** ★8 (enfrentamento estrutural) e ★7 (advertência protetiva — alertar para o risco de cobrança indevida).

**Fonte primária validada:** STF, RE 638.115, Tema 531; Lei 9.784/99, art. 54; LINDB, arts. 22-24. Validação em 15/05/2026.

---

## Família B-TRIB — Tributário Municipal

> Aplicável quando a consulta envolver IPTU, ISS, ITBI, taxas, contribuição de melhoria, crédito tributário, prescrição, decadência, isenção, anistia, remissão, REFIS, capacidade contributiva, repartição de receitas. Vertente B da `parecer-municipal-geral`, dimensão tributária. Seis bloqueios.

### B-TRIB-1 — Silêncio sobre reserva de lei específica em parecer favorável a benefício fiscal

**Vedação:** parecer que valide concessão de isenção, anistia, remissão, redução de base de cálculo, crédito presumido ou subsídio — em IPTU, ISS, ITBI, taxa ou qualquer tributo municipal — sem enfrentar expressamente o **art. 150, § 6º, da Constituição**, com a exigência de **lei específica** que regule exclusivamente a matéria ou o tributo correspondente.

**Fundamentação:** CF art. 150, § 6º; jurisprudência consolidada do STF (Tema 682, ARE 743.480) reafirmando a exigência de lei específica e a impossibilidade de delegação genérica ao Executivo para concessão de benefícios fiscais. Decretos do Executivo que perdoam dívida tributária têm sido sistematicamente declarados inconstitucionais (precedente recente: ADI sobre decreto do Amapá, 2025).

**Procedimento de remediação:** parágrafo enfrentando (i) existência de lei municipal específica; (ii) se a lei é específica em sentido próprio (regula exclusivamente o benefício ou o tributo correspondente, sem ser "lei genérica que autoriza o prefeito a"); (iii) compatibilidade com o art. 14 da LRF (estimativa de impacto + medida de compensação). Sem qualquer dos três, parecer reprova.

**Princípio associado:** ★8 (enfrentamento estrutural) e ★7 (advertência protetiva — risco de representação no TCE-CE).

**Fonte primária validada:** CF art. 150, § 6º; STF, ARE 743.480, Tema 682; STF, ADI 1.247-MC (Rel. Min. Celso de Mello, leading case). Validação em 15/05/2026.

### B-TRIB-2 — Silêncio sobre estimativa de impacto e compensação na LRF art. 14

**Vedação:** parecer favorável a qualquer renúncia de receita tributária (isenção, anistia, remissão, REFIS, redução de base de cálculo) que não enfrente o **art. 14 da Lei de Responsabilidade Fiscal** e seus três pressupostos cumulativos: (i) estimativa do impacto orçamentário-financeiro no exercício em curso e nos dois subsequentes; (ii) demonstração de que a renúncia foi considerada na lei orçamentária; (iii) medida de compensação prevista no inciso II do mesmo artigo.

**Fundamentação:** LC 101/2000 (LRF), art. 14; jurisprudência do STF reconhecendo que o art. 14 da LRF integra o regime constitucional da renúncia de receita (CF art. 165, § 6º). Acórdãos consolidados do TCU e do TCE-CE em representações por descumprimento dos pressupostos.

**Procedimento de remediação:** parágrafo registrando (i) presença ou ausência da estimativa de impacto; (ii) se a renúncia foi considerada na LOA vigente; (iii) qual medida de compensação foi adotada. Se faltar qualquer item, parecer **favorável com ressalva** condicionada à juntada antes da remessa à Câmara, ou **desfavorável** se a remessa for iminente.

**Princípio associado:** ★8 (enfrentamento estrutural) e B11 (conclusão clara — não há como concluir "favorável puro" sem os três pressupostos).

**Fonte primária validada:** LC 101/2000, art. 14; CF art. 165, § 6º. Validação em 15/05/2026.

### B-TRIB-3 — Silêncio sobre majoração disfarçada de base de cálculo de IPTU por decreto

**Vedação:** parecer sobre revisão da Planta Genérica de Valores (PGV) ou atualização do IPTU que não distinga **atualização monetária** (admissível por decreto, limitada aos índices oficiais de inflação) de **majoração da base de cálculo** (exige lei).

**Fundamentação:** CF art. 150, I; CTN art. 97, § 1º; **Súmula 160 do STJ** — "É defeso, ao Município, atualizar o IPTU, mediante decreto, em percentual superior ao índice oficial de correção monetária."

**Procedimento de remediação:** parágrafo enfrentando (i) qual é o índice oficial aplicável (IPCA, INPC ou o índice local da LOA); (ii) qual é o percentual de atualização pretendido; (iii) diferença para mais entre o pretendido e o oficial = majoração disfarçada = exige lei. Em caso de revisão da PGV em si (não apenas atualização de valor venal), o parecer registra que se trata de matéria reservada à lei municipal.

**Princípio associado:** ★3 (paráfrase funcional da Súmula 160 após citação literal) e ★8 (enfrentamento estrutural).

**Fonte primária validada:** STJ, Súmula 160; CF art. 150, I; CTN art. 97, § 1º. Validação em 15/05/2026.

### B-TRIB-4 — Silêncio sobre notificação do lançamento em parecer sobre cobrança ou execução fiscal de IPTU

**Vedação:** parecer subsidiando cobrança administrativa ou execução fiscal de IPTU que não trate da notificação do lançamento ao contribuinte — pelo envio do carnê ao endereço — como pressuposto da constituição definitiva do crédito.

**Fundamentação:** CTN arts. 142 e 145; **Súmula 397 do STJ** — "O contribuinte do IPTU é notificado do lançamento pelo envio do carnê ao seu endereço"; **REsp 1.111.124/PR** (recurso repetitivo, Tema 248 do STJ).

**Procedimento de remediação:** parágrafo registrando (i) que o IPTU é tributo de lançamento de ofício; (ii) que a notificação se opera presumidamente pelo envio do carnê; (iii) que o ônus de demonstrar o não-recebimento é do contribuinte; (iv) que, ausente prova do envio nos autos, a presunção não se forma e a CDA pode ser anulada. Quando o município lança por edital, registrar que essa modalidade é admitida só subsidiariamente.

**Princípio associado:** ★3 (paráfrase funcional após citação literal) e B11 (conclusão clara sobre a regularidade da cobrança).

**Fonte primária validada:** STJ, Súmula 397; STJ, REsp 1.111.124/PR (recurso repetitivo, Tema 248); CTN arts. 142 e 145. Validação em 15/05/2026.

### B-TRIB-5 — Silêncio sobre prescrição e decadência tributárias em consulta sobre crédito antigo

**Vedação:** parecer sobre crédito tributário com mais de cinco anos do fato gerador ou da constituição definitiva que não enfrente expressamente os prazos do **CTN art. 173** (decadência do direito de lançar) e do **CTN art. 174** (prescrição da ação de cobrança), com a distinção precisa entre os dois institutos.

**Fundamentação:** CTN arts. 173 e 174; jurisprudência consolidada do STJ, em particular o **REsp 973.733/SC** (recurso repetitivo, Tema 163, sobre termo inicial da decadência em lançamento por homologação) e o **REsp 1.120.295/SP** (recurso repetitivo, Tema 383, sobre a interrupção do prazo prescricional pela citação válida); **Súmula Vinculante 8 do STF** — declara inconstitucionais dispositivos de lei previdenciária que fixavam prazos de prescrição e decadência diferentes do CTN, reafirmando a reserva de lei complementar (CF art. 146, III, "b").

**Procedimento de remediação:** parágrafo identificando (i) qual instituto se aplica ao caso (decadência se ainda não houve lançamento; prescrição se já houve); (ii) qual é o termo inicial específico (data do fato gerador, primeiro dia do exercício seguinte, ou data da notificação do lançamento, conforme o tributo e a modalidade); (iii) eventos suspensivos ou interruptivos; (iv) conclusão sobre exigibilidade ou não do crédito.

**Princípio associado:** ★8 (enfrentamento estrutural) e ★4 (exemplo concreto da contagem do prazo no caso).

**Fonte primária validada:** STJ, REsp 973.733/SC, Tema 163; STJ, REsp 1.120.295/SP, Tema 383; STF, Súmula Vinculante 8; CTN arts. 173 e 174. Validação em 15/05/2026.

### B-TRIB-6 — Silêncio sobre capacidade contributiva em parecer favorável a alíquota progressiva ou diferenciada

**Vedação:** parecer favorável à instituição ou majoração de alíquota progressiva de IPTU (CF art. 156, § 1º, I e II) ou de alíquotas diferenciadas de ISS sem enfrentar o princípio da capacidade contributiva (CF art. 145, § 1º) e os requisitos jurisprudenciais para a progressividade.

**Fundamentação:** CF arts. 145, § 1º, e 156, § 1º; STF, RE 423.768 (progressividade do IPTU após EC 29/2000); jurisprudência sobre necessidade de lei municipal específica e de fundamentação técnica da gradação. A progressividade no tempo do IPTU como instrumento urbanístico (CF art. 182, § 4º, II) é instituto **distinto** e tem regime próprio — o parecer não pode confundir.

**Procedimento de remediação:** parágrafo distinguindo (i) progressividade fiscal por valor venal (art. 156, § 1º, I); (ii) alíquotas diferenciadas por localização e uso (art. 156, § 1º, II); (iii) progressividade no tempo por descumprimento da função social (art. 182, § 4º, II). Cada uma exige fundamentação técnica própria e lei municipal específica. O parecer **rejeita** propostas que misturem os três institutos.

**Princípio associado:** ★8 (enfrentamento estrutural) e ★4 (exemplo concreto da diferença entre os três institutos).

**Fonte primária validada:** STF, RE 423.768; CF arts. 145, § 1º, 156, § 1º, e 182, § 4º, II; EC 29/2000. Validação em 15/05/2026.

---

## Família B-OSC — Terceiro Setor

> Aplicável quando a consulta envolver parceria com organização da sociedade civil em qualquer regime (MROSC — Lei 13.019/14, OS — Lei 9.637/98, OSCIP — Lei 9.790/99, CEBAS — LC 187/21). Vertente C da `parecer-municipal-geral`. Cinco bloqueios.

### B-OSC-1 — Silêncio sobre chamamento público como regra

**Vedação:** parecer sobre celebração de termo de fomento ou de colaboração no regime da Lei 13.019/14 que não enfrente expressamente o **chamamento público como procedimento ordinário de seleção** (art. 24) e a sua relação com as hipóteses excepcionais de dispensa (art. 30) e inexigibilidade (art. 31).

**Fundamentação:** Lei 13.019/2014, art. 24 (chamamento público como regra), art. 2º, XII (definição), art. 32 (justificativa formal para dispensa e inexigibilidade). A natureza excepcional das hipóteses dos arts. 30 e 31 é pacífica na jurisprudência do TCU e dos TCEs estaduais — a invocação de excepcionalidade exige fundamentação concreta nos autos, não apenas remissão genérica ao dispositivo.

**Procedimento de remediação:** parágrafo de abertura registrando (i) o chamamento público como procedimento de seleção que privilegia impessoalidade, moralidade e publicidade; (ii) a excepcionalidade das hipóteses dos arts. 30 e 31; (iii) o ônus argumentativo da Administração para afastar a regra. A presença de emenda parlamentar que identifique a OSC dispensa o chamamento, mas não dispensa as demais exigências da Lei 13.019 (art. 29 com redação dada pela Lei 13.204/15).

**Princípio associado:** ★8 (enfrentamento estrutural) e ★3 (paráfrase funcional do art. 24 após citação literal).

**Fonte primária validada:** Lei 13.019/2014, arts. 24, 30 e 31; Lei 13.204/2015 (alterações). Validação em 15/05/2026.

### B-OSC-2 — Silêncio sobre os requisitos da dispensa do art. 30 quando invocada

**Vedação:** parecer favorável a termo de fomento ou de colaboração com dispensa de chamamento público fundada em qualquer dos incisos do art. 30 da Lei 13.019/14 que não enfrente os pressupostos específicos do inciso invocado e o procedimento formal do art. 32.

**Fundamentação:** Lei 13.019/2014, art. 30 (incisos I a VI, com redação da Lei 13.204/15); art. 32 (justificativa formal, publicidade prévia de cinco dias, possibilidade de impugnação). A jurisprudência dos TCEs e do TCU é convergente no sentido de que cada inciso traz **pressupostos cumulativos próprios** que precisam ser demonstrados concretamente:
- **Inciso I** (urgência por paralisação) — prazo de até 180 dias improrrogável, vinculação à parceria já celebrada;
- **Inciso II** (guerra, calamidade, grave perturbação) — decreto ou ato formal de reconhecimento;
- **Inciso III** (proteção a pessoas ameaçadas) — programa estruturado;
- **Inciso VI** (educação, saúde, assistência social) — credenciamento prévio da OSC pelo órgão gestor da política.

**Procedimento de remediação:** parágrafo dedicado identificando (i) qual inciso é invocado; (ii) quais são seus pressupostos específicos; (iii) demonstração concreta nos autos. Se faltar qualquer pressuposto ou se a justificativa do art. 32 não estiver formalizada, parecer **reprova**. Atenção especial ao inciso VI, que pressupõe **credenciamento prévio** — quando a OSC não foi credenciada antes, a dispensa não se aplica.

**Princípio associado:** ★8 e ★4 (exemplo concreto da subsunção dos fatos ao inciso).

**Fonte primária validada:** Lei 13.019/2014, arts. 30 e 32 (com redação da Lei 13.204/15). Validação em 15/05/2026.

### B-OSC-3 — Silêncio sobre os requisitos da inexigibilidade do art. 31 quando invocada

**Vedação:** parecer favorável a parceria com inexigibilidade de chamamento público (art. 31 da Lei 13.019/14) que não enfrente expressamente a **inviabilidade de competição** entre organizações da sociedade civil — fundada na natureza singular do objeto ou na exclusividade material da OSC parceira.

**Fundamentação:** Lei 13.019/2014, art. 31 (redação da Lei 13.204/15) — "Será considerado inexigível o chamamento público na hipótese de inviabilidade de competição entre as organizações da sociedade civil, em razão da natureza singular do objeto da parceria ou se as metas somente puderem ser atingidas por uma entidade específica". Aplicação subsidiária da lógica do art. 25 da Lei 8.666/93 e do art. 74 da Lei 14.133/2021, em razão da analogia conceitual da inexigibilidade.

**Procedimento de remediação:** parágrafo demonstrando (i) por que a competição é inviável neste caso concreto; (ii) qual é a singularidade material do objeto ou da OSC; (iii) que outras OSCs do município ou da região foram efetivamente verificadas e descartadas, com registro nos autos. **Não basta afirmar singularidade — é preciso demonstrar.** Se a singularidade for por especialização territorial e a OSC for a única no município, registrar a inexistência de outras OSCs do ramo.

**Princípio associado:** ★8, ★4 (exemplo concreto) e advertência protetiva ★7 (risco de representação no MPCE ou no TCE-CE por inexigibilidade não demonstrada).

**Fonte primária validada:** Lei 13.019/2014, art. 31 (com redação da Lei 13.204/15). Validação em 15/05/2026.

### B-OSC-4 — Silêncio sobre os pressupostos da ADI 1.923 em contratação de OS

**Vedação:** parecer sobre celebração de contrato de gestão com Organização Social qualificada pela Lei 9.637/98 — federal — ou por lei municipal análoga, que não enfrente os pressupostos fixados pelo STF na **ADI 1.923/DF**: processo de qualificação **público, objetivo e impessoal**, observância dos princípios do art. 37 caput da Constituição, e procedimento de seleção análogo (ainda que não seja licitação formal).

**Fundamentação:** Lei 9.637/98 (regime federal das OS); **STF, ADI 1.923/DF**, Rel. Min. Ayres Britto, julgamento em 16/04/2015, com interpretação conforme — a Corte declarou que a dispensa de licitação para celebração de contrato de gestão é constitucional **desde que** o processo de qualificação da entidade e a celebração do contrato observem os princípios da Administração; **STF, ADPF 559** (2024, sobre teto remuneratório de dirigentes de OS); **STF, ADI 7.629/MG** (fev/2025, descentralização de serviços de saúde para terceiro setor — reafirma os pressupostos).

**Procedimento de remediação:** parágrafo registrando (i) que a Lei 9.637/98 institui regime distinto do MROSC, com qualificação prévia da entidade como OS e contrato de gestão como instrumento; (ii) que a dispensa de licitação **não dispensa** processo objetivo de seleção (em sentido amplo); (iii) que a qualificação como OS pelo município pressupõe lei municipal de qualificação ou adesão expressa ao regime federal; (iv) que a fiscalização do Ministério Público e do Tribunal de Contas sobre a utilização de verbas públicas é regular e esperada. Atenção: a confusão entre OS e OSC do MROSC é frequente — o parecer **distingue**.

**Princípio associado:** ★8 e ★3 (paráfrase funcional da tese da ADI 1.923 após citação literal do voto-condutor).

**Fonte primária validada:** Lei 9.637/98; STF, ADI 1.923/DF, j. 16/04/2015; STF, ADPF 559, Rel. Min. Roberto Barroso; STF, ADI 7.629/MG, Rel. Min. Dias Toffoli, j. 14/02/2025. Validação em 15/05/2026.

### B-OSC-5 — Silêncio sobre prestação de contas, nexo de causalidade e glosa em parecer subsidiando defesa de OSC

**Vedação:** parecer subsidiando defesa de OSC em prestação de contas com glosa parcial pela Administração ou em representação no TCE-CE/TCU que não enfrente expressamente (i) o **nexo de causalidade** entre receita pública e despesa realizada como critério de análise; (ii) a regra do **resultado real** (verdade material) introduzida pela Lei 13.019/14; (iii) a aplicação dos parâmetros do TCU sobre devolução proporcional ao dano (não confisco integral).

**Fundamentação:** Lei 13.019/2014, arts. 63 a 72 (prestação de contas), art. 69 (prazo), art. 64 (verdade real e resultados); Decreto 8.726/2016 (regulamento federal, aplicado por simetria); jurisprudência do TCU sobre proporcionalidade da devolução (Acórdão 1.187/2019-Plenário e correlatos); jurisprudência do TCE-CE convergente sobre verificação concreta do nexo antes da glosa integral.

**Procedimento de remediação:** parágrafo enfrentando (i) qual é o objeto da glosa específica; (ii) há nexo de causalidade entre o repasse e a despesa glosada? (iii) há demonstração de boa-fé objetiva da OSC? (iv) a glosa observa o princípio da proporcionalidade ou pretende devolução integral por irregularidade formal? Se a glosa for desproporcional ou se ignorar a verdade material, o parecer subsidia a defesa com argumentos consequencialistas (art. 22 da LINDB). **Ativa REGRA IRR-3** (modo quase-processual) — toda norma invocada pela Administração precisa ser confirmada via `web_search`.

**Princípio associado:** ★8, ★7 (advertência protetiva — risco de devolução integral sem fundamentação proporcional) e REGRA IRR-3.

**Fonte primária validada:** Lei 13.019/2014, arts. 63 a 72; Decreto 8.726/2016; TCU, jurisprudência sobre proporcionalidade da devolução; LINDB arts. 22-24. Validação em 15/05/2026.

---

## Família B-FIN — Direito Financeiro Municipal (LRF, RAP, Repasses)

> Aplicável quando a consulta envolver Lei de Responsabilidade Fiscal, planejamento orçamentário (PPA-LDO-LOA), restos a pagar, repasses constitucionais (FPM, ICMS, IPVA, ITR), precatórios e RPVs, operação de crédito. Vertente B da `parecer-municipal-geral`, dimensão financeira. Cinco bloqueios.

### B-FIN-1 — Silêncio sobre art. 42 da LRF em consulta de fim de mandato

**Vedação:** parecer sobre celebração de contrato, formalização de empenho, assunção de obrigação ou pagamento de despesa **nos dois últimos quadrimestres do último ano de mandato** que não enfrente expressamente o **art. 42 da Lei de Responsabilidade Fiscal** e os critérios jurisprudenciais consolidados para sua aferição.

**Fundamentação:** **LC 101/2000, art. 42** — "É vedado ao titular de Poder ou órgão referido no art. 20, nos últimos dois quadrimestres do seu mandato, contrair obrigação de despesa que não possa ser cumprida integralmente dentro dele, ou que tenha parcelas a serem pagas no exercício seguinte sem que haja suficiente disponibilidade de caixa para este efeito"; jurisprudência convergente do TCU, TCE-CE, TCE-SP, TCE-MG e TCE-ES sobre a aferição comparativa do estoque líquido de débitos entre 30 de abril e 31 de dezembro do último ano do mandato; possibilidade de **caracterização como ato de improbidade administrativa** com dolo genérico (jurisprudência do STJ sobre Lei 8.429/92, art. 11, c/c art. 73 da LRF).

**Procedimento de remediação:** parágrafo registrando (i) que a vedação alcança a assunção de obrigação, e não apenas o empenho — o momento decisivo é a formalização do contrato ou instrumento congênere; (ii) que a disponibilidade de caixa se afere por comparação entre 30/04 e 31/12 do último ano de mandato; (iii) que a finalidade pública da despesa **não exclui**, por si só, a violação ao art. 42; (iv) que a indisponibilidade de caixa autoriza a contratação apenas em situações excepcionais devidamente justificadas (emergência, calamidade, atividade essencial inadiável). Em caso de proximidade do fim de mandato, **advertência protetiva redobrada**.

**Princípio associado:** ★8 (enfrentamento estrutural) e ★7 (advertência protetiva — risco de improbidade, rejeição de contas, multa pessoal).

**Fonte primária validada:** LC 101/2000, art. 42; STJ, jurisprudência sobre dolo genérico em violação ao art. 42 (Lei 8.429/92, art. 11); TCE-SP, TCE-MG, TCE-ES — pareceres prévios e consultas sobre o critério de aferição. Validação em 15/05/2026.

### B-FIN-2 — Silêncio sobre limites de despesa com pessoal da LRF arts. 19-23 em consulta de criação ou majoração de gasto

**Vedação:** parecer favorável à criação de cargo, reajuste de subsídio, concessão de gratificação, contratação por tempo determinado ou qualquer ato que **aumente despesa com pessoal** sem enfrentar expressamente os limites do **art. 19, III** (60% da RCL para municípios), **art. 20, III, "b"** (54% para o Executivo municipal) e os **gatilhos do art. 22** (limite prudencial de 51,3% para o Executivo municipal).

**Fundamentação:** LC 101/2000, arts. 18-23, com a **LC 178/2021** que ajustou as regras de contenção; STF, RE 423.768 (sobre o conceito amplo de despesa com pessoal); jurisprudência do TCE-CE sobre obrigatoriedade do recálculo periódico da RCL e da Despesa Total com Pessoal (DTP); jurisprudência sobre vedação à criação de vantagem quando excedido o limite prudencial.

**Procedimento de remediação:** parágrafo registrando (i) qual é a DTP atual do Município sobre a RCL (dado que precisa estar nos autos — sem ele, parecer **provisório**); (ii) qual é o limite aplicável ao Poder solicitante (54% Executivo, 6% Legislativo); (iii) se o ato proposto eleva a DTP acima do limite prudencial; (iv) quais medidas de contenção do art. 22 (vedação a aumento de gastos, criação de cargo, etc.) já estão em vigor. Se o ato pretendido violar o limite prudencial ou o limite máximo, parecer **desfavorável** — ou, no mínimo, condicionado à demonstração de margem.

**Princípio associado:** ★8 e ★4 (exemplo concreto do cálculo DTP/RCL no caso).

**Fonte primária validada:** LC 101/2000, arts. 18-23; LC 178/2021; STF, RE 423.768. Validação em 15/05/2026.

### B-FIN-3 — Silêncio sobre os três pressupostos da renúncia de receita no art. 14 da LRF em vertente financeira

> Este bloqueio é o espelho **financeiro** do bloqueio tributário B-TRIB-2. A diferença é o foco: enquanto B-TRIB-2 enfrenta o art. 14 da LRF do ponto de vista do **benefício tributário** sob exame, B-FIN-3 enfrenta o mesmo art. 14 do ponto de vista da **gestão financeira global** — impacto consolidado de múltiplas renúncias, integração com a LDO e a LOA, e o efeito sobre o RREO e o RGF.

**Vedação:** parecer sobre projeto de lei orçamentária ou sobre adequação financeira de pacote de benefícios fiscais que não enfrente o art. 14 da LRF do ponto de vista do equilíbrio financeiro global do Município — incluindo a verificação de se a soma das renúncias considerada está dentro da projeção da LDO e se há demonstração de neutralidade fiscal.

**Fundamentação:** LC 101/2000, art. 14; CF art. 165, § 6º; jurisprudência do TCE-CE sobre representações por descumprimento dos pressupostos do art. 14 em pacotes de benefícios; integração com os RREOs (art. 52 da LRF) e RGFs (art. 54 da LRF).

**Procedimento de remediação:** parágrafo enfrentando (i) se a LDO vigente projeta renúncia para o exercício; (ii) se o valor da renúncia consolidada (todos os benefícios somados, não apenas o atual) está dentro da projeção; (iii) se as medidas de compensação foram efetivamente implementadas em folha ou apenas declaradas em texto. **Sem demonstração efetiva, parecer reprova.**

**Princípio associado:** ★8 e ★7 (advertência protetiva sobre risco em RGF).

**Fonte primária validada:** LC 101/2000, arts. 14, 52, 54; CF art. 165, § 6º. Validação em 15/05/2026.

### B-FIN-4 — Silêncio sobre regularidade da inscrição em restos a pagar e o art. 41 da Lei 4.320/64

**Vedação:** parecer sobre inscrição de despesa em restos a pagar — processados ou não processados — que não enfrente os pressupostos da **Lei 4.320/64, art. 41**, distinguindo os dois tipos de RAP, e que não os confronte com os limites do art. 42 da LRF quando aplicável ao caso.

**Fundamentação:** Lei 4.320/64, arts. 35-41 (estágios da despesa: empenho, liquidação, pagamento), art. 41 (definição de RAP processados — despesa liquidada — e não processados — despesa empenhada e não liquidada); jurisprudência do TCU e dos TCEs sobre o cancelamento automático de RAP não processados ao fim do exercício seguinte (regra geral, com exceções para vinculações constitucionais como educação e saúde); regulamento de procedimentos contábeis aplicáveis aos entes federados.

**Procedimento de remediação:** parágrafo registrando (i) qual é a natureza da despesa (RAP processado ou não processado); (ii) há suporte financeiro para inscrição? (iii) há vinculação constitucional (FUNDEB, saúde — CF art. 198, § 2º; educação — CF art. 212) que justifique manutenção em exercício posterior? (iv) há risco de art. 42 da LRF se a inscrição se der nos dois últimos quadrimestres do mandato? **A confusão entre RAP processados e não processados é frequente — o parecer distingue rigorosamente.**

**Princípio associado:** ★8 e ★4 (exemplo concreto da diferença entre os dois tipos de RAP).

**Fonte primária validada:** Lei 4.320/64, arts. 35-41; LC 101/2000, art. 42; CF arts. 198, § 2º, e 212. Validação em 15/05/2026.

### B-FIN-5 — Silêncio sobre retenção indevida de repasse constitucional (FPM, ICMS) em parecer subsidiando ação contra a União ou o Estado

**Vedação:** parecer subsidiando ação contra retenção de FPM, cota-parte do ICMS, IPVA, ITR ou demais repasses constitucionais que não enfrente expressamente a **vedação à retenção** do art. 160 da Constituição Federal e as estritas exceções de seu parágrafo único.

**Fundamentação:** **CF art. 160 e parágrafo único** — "É vedada a retenção ou qualquer restrição à entrega e ao emprego dos recursos atribuídos, nesta Seção, aos Estados, ao Distrito Federal e aos Municípios", com exceção apenas para crédito da União/Estado por seus serviços e para condicionamento ao cumprimento dos limites em educação e saúde; jurisprudência do STF reafirmando o caráter taxativo das exceções (MS impetrados por municípios contra retenções pela União).

**Procedimento de remediação:** parágrafo registrando (i) qual repasse foi retido e por qual valor; (ii) qual o fundamento invocado pelo ente repassante; (iii) se o fundamento se enquadra estritamente nas exceções do art. 160, parágrafo único — caso contrário, retenção é inconstitucional; (iv) instrumento processual cabível (mandado de segurança originário no STF, no STJ ou no TJ-CE, conforme a parte adversa); (v) pedido de liminar para liberação imediata do valor retido. **Ativa REGRA IRR-3** (modo quase-processual) — confirmar via `web_search` a fundamentação invocada pelo ente repassante.

**Princípio associado:** ★8, ★4 (exemplo concreto da subsunção da retenção ao art. 160) e REGRA IRR-3.

**Fonte primária validada:** CF art. 160; STF, jurisprudência sobre MS contra retenção de FPM e cota-parte do ICMS. Validação em 15/05/2026.

---

## Família B-URB — Urbanismo Municipal

> Aplicável quando a consulta envolver plano diretor, parcelamento do solo, edificação compulsória, função social da propriedade urbana, IPTU progressivo no tempo como instrumento urbanístico, regularização fundiária urbana (Lei 13.465/17), licenciamento urbanístico, estudo de impacto de vizinhança. Vertente A da `parecer-municipal-geral`, dimensão urbanística. Quatro bloqueios.

### B-URB-1 — Silêncio sobre a sucessividade dos instrumentos do art. 182, § 4º, da CF

**Vedação:** parecer sobre instituição ou aplicação concreta do **IPTU progressivo no tempo como instrumento urbanístico** (CF art. 182, § 4º, II) ou da **desapropriação-sanção com pagamento em títulos** (art. 182, § 4º, III) que não enfrente expressamente a **regra constitucional da sucessividade**: o IPTU progressivo no tempo só se aplica **após** a notificação para parcelamento, edificação ou utilização compulsórios (PEUC); a desapropriação-sanção só se aplica **após** cinco anos consecutivos de cobrança do IPTU progressivo sem cumprimento da função social.

**Fundamentação:** CF art. 182, § 4º, incisos I a III; Lei 10.257/2001 (Estatuto da Cidade), arts. 5º a 8º (regulamentando a tríade); **STF, Súmula 668** — "É inconstitucional a lei municipal que tenha estabelecido, antes da EC 29/2000, alíquotas progressivas para o IPTU, salvo se destinada a assegurar o cumprimento da função social da propriedade urbana"; jurisprudência convergente do STF reconhecendo a tríade como instrumento sucessivo e a impossibilidade de aplicação isolada do IPTU progressivo no tempo sem a notificação prévia para PEUC.

**Procedimento de remediação:** parágrafo registrando (i) a tríade do art. 182, § 4º, como sequência **sucessiva e não cumulativa**; (ii) que a aplicação do IPTU progressivo no tempo **pressupõe** notificação prévia da Administração para PEUC e descumprimento do prazo; (iii) que a desapropriação-sanção **pressupõe** cinco anos consecutivos de IPTU progressivo sem cumprimento; (iv) **distinção rigorosa** entre IPTU progressivo no tempo (instrumento urbanístico, art. 182, § 4º, II) e IPTU progressivo por valor venal (alíquota fiscal progressiva, art. 156, § 1º, I) — confusão entre os dois institutos é vício comum e descaracteriza o parecer. Para parecer sobre instituição de IPTU progressivo no tempo, condicionar à existência de plano diretor (obrigatório para municípios com mais de 20.000 habitantes — CF art. 182, § 1º — e em certas hipóteses específicas).

**Princípio associado:** ★8 (enfrentamento estrutural) e ★4 (exemplo concreto da diferença entre os dois IPTU progressivos).

**Fonte primária validada:** CF art. 182, § 4º; Lei 10.257/2001, arts. 5º a 8º; STF, Súmula 668; EC 29/2000. Validação em 15/05/2026.

### B-URB-2 — Silêncio sobre o plano diretor como pressuposto de instrumentos urbanísticos

**Vedação:** parecer favorável à aplicação de qualquer instrumento urbanístico do Estatuto da Cidade (PEUC, IPTU progressivo no tempo, desapropriação-sanção, outorga onerosa do direito de construir, operações urbanas consorciadas, direito de preempção, transferência do direito de construir) que não enfrente a **exigência de previsão expressa no plano diretor municipal** e os requisitos formais do plano (lei municipal aprovada pela Câmara, participação popular).

**Fundamentação:** CF art. 182, § 1º e § 2º; Lei 10.257/2001 (Estatuto da Cidade), arts. 39 a 42 (plano diretor) e arts. 25 a 33 (instrumentos que pressupõem previsão no plano); jurisprudência do STF sobre a indispensabilidade do plano diretor para aplicação dos instrumentos sancionatórios urbanísticos.

**Procedimento de remediação:** parágrafo registrando (i) que o plano diretor é **lei municipal específica** aprovada pela Câmara, com participação popular formalizada (art. 40, § 4º do Estatuto); (ii) que o instrumento urbanístico pretendido deve estar **expressamente previsto** no plano, com delimitação das áreas em que será aplicado; (iii) que, ausente o plano diretor ou ausente a previsão específica, o instrumento é **inaplicável**. Atenção: para municípios obrigados a ter plano diretor (CF art. 182, § 1º) que dele não dispõem, há **omissão sancionável** sob a Lei 8.429/92, conforme jurisprudência do STJ.

**Princípio associado:** ★8 e ★7 (advertência protetiva — risco de improbidade por omissão de plano diretor em município obrigado, e risco de nulidade dos atos urbanísticos isolados).

**Fonte primária validada:** CF art. 182; Lei 10.257/2001, arts. 39 a 42 e 25 a 33. Validação em 15/05/2026.

### B-URB-3 — Silêncio sobre a competência municipal exclusiva no licenciamento urbanístico e EIV

**Vedação:** parecer sobre licenciamento de empreendimento urbano de impacto, Estudo de Impacto de Vizinhança (EIV) ou intervenção territorial que confunda a competência **municipal** de licenciamento urbanístico (CF art. 30, I e VIII) com competências ambientais (que podem ser concorrentes ou cumulativas com União/Estado).

**Fundamentação:** CF art. 30, incisos I (interesse local), VIII (adequado ordenamento territorial), e art. 182 (política de desenvolvimento urbano como atribuição do município); Lei 10.257/2001, arts. 36 a 38 (EIV); jurisprudência consolidada do STF sobre o município como protagonista do planejamento urbano (vide ADIs 5.771, 5.787 e 5.883, contra a Lei 13.465/17, que reafirmam o papel municipal — ainda em julgamento, conferência recomendada na data da redação).

**Procedimento de remediação:** parágrafo distinguindo (i) **licenciamento urbanístico** (competência municipal exclusiva, salvo grandes obras de impacto regional); (ii) **licenciamento ambiental** (concorrente, podendo envolver IBAMA, órgão ambiental estadual ou municipal conforme o porte e a localização); (iii) **EIV** (instrumento urbanístico, exigido por lei municipal para empreendimentos de impacto significativo, não substitui EIA-RIMA quando este for cabível). O parecer **não confunde** EIV com EIA-RIMA — são instrumentos distintos, com finalidades distintas, que podem ser cumulativos.

**Princípio associado:** ★8 e ★3 (paráfrase funcional do art. 30, I e VIII após citação literal).

**Fonte primária validada:** CF art. 30, I e VIII; Lei 10.257/2001, arts. 36 a 38; STF, ADIs 5.771, 5.787, 5.883 (em julgamento — conferência recomendada). Validação em 15/05/2026.

### B-URB-4 — Silêncio sobre os requisitos da REURB (Lei 13.465/17) em parecer sobre regularização fundiária urbana

**Vedação:** parecer sobre regularização fundiária urbana que não enfrente a **distinção entre as modalidades** da Lei 13.465/17 (REURB-S para baixa renda, REURB-E para demais casos, e a modalidade do art. 69 para núcleos consolidados há mais de 30 anos), e não trate da **competência municipal exclusiva para emissão da Certidão de Regularização Fundiária (CRF)**.

**Fundamentação:** Lei 13.465/2017, especialmente arts. 9º a 14 (legitimados e classificação), art. 11, V (definição da CRF), arts. 18 a 24 (procedimento), art. 69 (núcleos consolidados há mais de 30 anos); Decreto 9.310/2018, art. 23 (competência municipal exclusiva para classificação, processamento, aprovação e emissão da CRF); STF, ADIs 5.771, 5.787, 5.883 (em julgamento, com discussão sobre limites do papel federal).

**Procedimento de remediação:** parágrafo distinguindo (i) **REURB-S** (interesse social, baixa renda, com ônus de infraestrutura e compensação ambiental majoritariamente sobre o Município ou ente público); (ii) **REURB-E** (interesse específico, com ônus de infraestrutura e compensação sobre ocupantes ou loteador irregular); (iii) **legitimação fundiária** como forma originária de aquisição (vedada usucapião disfarçada — requer núcleo consolidado até 22/12/2016); (iv) **competência municipal exclusiva para a CRF**. Quando o objeto for área da União ou do Estado, registrar que a competência **urbanística** permanece municipal, ainda que a **titularidade** seja federal ou estadual — instâncias notariais e urbanísticas não se confundem.

**Princípio associado:** ★8 e ★4 (exemplo concreto da diferença entre as modalidades).

**Fonte primária validada:** Lei 13.465/2017; Decreto 9.310/2018, art. 23; STF, ADIs 5.771, 5.787, 5.883. Validação em 15/05/2026.

---

## Família B-FUNDEB — Fundo de Manutenção e Desenvolvimento da Educação Básica

> Aplicável quando a consulta envolver gestão, aplicação ou prestação de contas dos recursos do Fundeb. Regime atual: EC 108/2020 (Fundeb permanente, art. 212-A da CF) + Lei 14.113/2020 (regulamentação, revogando a Lei 11.494/2007) + Lei 14.276/2021 (esclarecimentos quanto à abrangência dos profissionais). Vertente A da `parecer-municipal-geral`, interface administrativo-financeira. Quatro bloqueios.

### B-FUNDEB-1 — Silêncio sobre a subvinculação mínima de 70% para profissionais da educação básica

**Vedação:** parecer sobre aplicação dos recursos do Fundeb que não enfrente expressamente a **subvinculação constitucional de 70%** (mínima) destinada à remuneração de profissionais da educação básica em efetivo exercício, e a sua **abrangência ampliada** após a EC 108/2020 (não mais limitada ao magistério estrito).

**Fundamentação:** CF art. 212-A, inciso XI, com redação da EC 108/2020 — "proporção não inferior a 70% (setenta por cento) de cada fundo (...) será destinada ao pagamento dos profissionais da educação básica em efetivo exercício"; Lei 14.113/2020, art. 26; Lei 14.276/2021 (que esclareceu a abrangência da categoria "profissional da educação básica" para todo o corpo funcional, incluindo profissionais não-docentes em efetivo exercício, e admitiu o cumprimento dos 70% por bonificação, abono, aumento de salário, atualização ou correção). Recomendação CNMP nº 44/2016 sobre atuação do Ministério Público no controle do dever de gasto.

**Procedimento de remediação:** parágrafo registrando (i) que o piso de 70% é **constitucional** (CF art. 212-A, XI), não meramente legal; (ii) que a base de cálculo é "cada fundo" recebido (Fundo do Fundeb, não a receita global da educação); (iii) que estão **excluídos** da base os recursos da complementação-VAAR (alínea "c" do inciso V do caput); (iv) que a abrangência alcança hoje **todos os profissionais da educação básica em efetivo exercício**, não apenas o magistério (mudança da EC 108/2020); (v) que o eventual descumprimento enseja **rejeição de contas, multa pessoal ao gestor e responsabilização por improbidade administrativa**.

**Princípio associado:** ★8 e ★7 (advertência protetiva — risco de rejeição de contas no TCE-CE e de representação ao Ministério Público da Educação).

**Fonte primária validada:** CF art. 212-A, XI (EC 108/2020); Lei 14.113/2020, art. 26; Lei 14.276/2021; CNMP, Recomendação 44/2016. Validação em 15/05/2026.

### B-FUNDEB-2 — Silêncio sobre a obrigatoriedade do CACS-Fundeb e seu papel no controle

**Vedação:** parecer sobre estruturação, prestação de contas ou auditoria interna do Fundeb que não enfrente a **obrigatoriedade do Conselho de Acompanhamento e Controle Social (CACS-Fundeb)**, sua composição plural conforme a Lei 14.113/2020, e sua atribuição de **emissão de parecer prévio às contas** do Município.

**Fundamentação:** Lei 14.113/2020, arts. 30 a 36 (CACS-Fundeb); regulamentação local de cada município sobre composição e funcionamento; CF art. 206 (princípios da educação escolar, incluindo a gestão democrática).

**Procedimento de remediação:** parágrafo registrando (i) que o CACS-Fundeb é **obrigatório** em cada esfera (União, Estados, DF, Municípios); (ii) que sua composição mínima inclui representantes do Poder Executivo, dos professores, dos diretores, dos servidores técnico-administrativos, dos pais e dos estudantes (art. 34); (iii) que o conselho **emite parecer** sobre a prestação de contas do Fundeb antes do envio ao TCE-CE; (iv) que a **ausência de instalação** ou a **paralisia operacional** do conselho são vícios graves que comprometem a prestação de contas e podem gerar suspensão do repasse. Quando o consulente declarar a inexistência do conselho ou o seu funcionamento meramente formal, parecer **reprova** sem ressalva.

**Princípio associado:** ★8 e ★7 (advertência protetiva — risco de suspensão de repasse e responsabilização).

**Fonte primária validada:** Lei 14.113/2020, arts. 30 a 36; CF art. 206. Validação em 15/05/2026.

### B-FUNDEB-3 — Silêncio sobre o regime de aplicação dos recursos no exercício e a janela do art. 25, § 3º

**Vedação:** parecer sobre planejamento orçamentário do Fundeb ou sobre regularidade contábil em prestação de contas que não enfrente a regra de **aplicação dos recursos no próprio exercício financeiro** em que recebidos, e a **exceção** que admite até 10% para utilização no primeiro trimestre do exercício seguinte (art. 25, § 3º da Lei 14.113/2020).

**Fundamentação:** Lei 14.113/2020, art. 25, § 3º — admite que até 10% dos recursos recebidos à conta dos fundos, inclusive os oriundos da complementação da União, **sejam utilizados no primeiro trimestre do exercício imediatamente subsequente**; Lei 4.320/64, art. 35 (regime de competência); jurisprudência do TCU e dos TCEs sobre rejeição de contas por inaplicação tempestiva dos recursos vinculados.

**Procedimento de remediação:** parágrafo registrando (i) que a regra geral é a **aplicação integral no exercício** em que os recursos foram recebidos; (ii) que a exceção legal do art. 25, § 3º permite a "janela" de até 10% para o primeiro trimestre subsequente — mas a janela é **limite máximo**, não obrigação; (iii) que recursos não utilizados além da janela podem gerar **devolução à União** ou **glosa em prestação de contas**; (iv) que a janela **não autoriza** a inscrição genérica em restos a pagar para uso indefinido — o uso do saldo no primeiro trimestre seguinte deve estar **destinado** e **identificado**.

**Princípio associado:** ★8 e ★4 (exemplo concreto do cálculo dos 10%).

**Fonte primária validada:** Lei 14.113/2020, art. 25, § 3º; Lei 4.320/64, art. 35. Validação em 15/05/2026.

### B-FUNDEB-4 — Silêncio sobre a vedação ao uso dos recursos do Fundeb fora das finalidades constitucionais

**Vedação:** parecer sobre destinação de recurso do Fundeb a finalidade diversa da **manutenção e desenvolvimento do ensino da educação básica pública** que não enfrente expressamente a vedação constitucional e a tipologia de **despesas vedadas** consolidada na jurisprudência e na doutrina contábil aplicada.

**Fundamentação:** CF art. 212-A; Lei 14.113/2020, arts. 25 a 29 (finalidades de aplicação); Lei 9.394/96 (LDB), arts. 70 (despesas consideradas como MDE) e 71 (despesas vedadas como MDE); jurisprudência consolidada do TCU e dos TCEs sobre rejeição de despesas com publicidade institucional, alimentação escolar custeada por outras fontes, manutenção de creches conveniadas que não pertençam à rede pública, transporte escolar fora dos parâmetros da LDB, entre outras.

**Procedimento de remediação:** parágrafo registrando (i) a vinculação **finalística** estrita do Fundeb à educação básica pública; (ii) a aplicação subsidiária dos arts. 70 e 71 da LDB para definição de despesas elegíveis e vedadas; (iii) que despesas duvidosas (educação infantil em entidade conveniada, transporte escolar terceirizado, programa de alfabetização de adultos) demandam **análise específica caso a caso** sobre se atendem à educação básica pública na acepção constitucional; (iv) que a glosa em prestação de contas pode determinar **devolução pessoal pelo gestor** dos valores aplicados em finalidade vedada, sem prejuízo de improbidade administrativa.

**Princípio associado:** ★8, ★7 (advertência protetiva — risco pessoal do gestor) e ★4 (exemplo concreto de despesas no limite).

**Fonte primária validada:** CF art. 212-A; Lei 14.113/2020, arts. 25 a 29; Lei 9.394/96 (LDB), arts. 70 e 71. Validação em 15/05/2026.

---

> **Nota de progresso da Etapa 3 — encerramento.** Esta versão do arquivo entrega a totalidade das seis famílias temáticas planejadas: B-SERV (7 bloqueios), B-TRIB (6), B-OSC (5), B-FIN (5), B-URB (4) e B-FUNDEB (4) — **31 bloqueios temáticos** distribuídos em seis famílias, somados aos onze bloqueios universais (B1 a B11). A Etapa 3 da migração está, assim, **substantivamente concluída**. As próximas etapas (4, 5, 6 e 7) tratarão da decisão sobre numeração dos princípios essenciais, da Dimensão E do checklist, do teste-piloto em caso real e da consolidação do bump definitivo de versão.

---

## Síntese

Os onze bloqueios universais (B1 a B11) são **invariáveis e aplicáveis a todo parecer**, independentemente da matéria. Não há contexto que justifique violar B2 (subdivisão), B6 (URL inventada) ou B11 (conclusão sem indicação clara). Os demais admitem matizes em casos limites, mas a regra geral é a vedação.

Os bloqueios temáticos (Famílias B-SERV, B-TRIB, B-OSC, B-FIN, B-URB e B-FUNDEB) **complementam** os onze universais quando a consulta toca a matéria respectiva. Sua função é impedir o silêncio sobre pontos críticos da disciplina: concurso público, reserva de lei para vantagem, acumulação, teto, nepotismo, contratação temporária e devolução de valores (B-SERV); reserva de lei específica para benefício fiscal, art. 14 da LRF tributária, majoração disfarçada de IPTU, notificação por carnê, prescrição/decadência e progressividade (B-TRIB); chamamento público como regra, dispensa do art. 30, inexigibilidade do art. 31, contratação de OS sob a ADI 1.923 e proporcionalidade da glosa (B-OSC); art. 42 da LRF de fim de mandato, limites de despesa com pessoal, art. 14 da LRF financeira, RAP e retenção de repasses constitucionais (B-FIN); sucessividade da tríade do art. 182, § 4º, plano diretor, competência municipal urbanística e REURB (B-URB); subvinculação de 70%, CACS-Fundeb, regime de aplicação no exercício e vedação ao desvio de finalidade (B-FUNDEB). Em casos integrados que atravessam mais de uma vertente, aplica-se a interseção das famílias envolvidas.

Aplicar os bloqueios em conjunto com os princípios essenciais (★1-★12) produz o estilo do escritório.

A próxima leitura é `conectivos-arquiteturais.md` — o vocabulário de transição que substitui a subdivisão numerada.
