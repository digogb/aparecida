# Checklist de Auditoria — Padrão da v5

**Versão 2.3** — calibrada para auditoria de pareceres alinhados ao parecer-modelo v5, com overrides autorais do Dr. Ione (v2.2.0 — ementa em maiúsculas e gate de parágrafos; v2.3.0 — verificação ativa de normas citadas pela parte adversa).

Este checklist é executado no **Passo 6 (Auto-auditoria)** do fluxo da skill. São **31 itens fixos universais** (dimensões A, B, C, D, E.universais e F) + **até 31 itens condicionais** por vertente (dimensão E.condicional — acionados apenas quando a vertente correspondente está ativa no parecer).

**Gate de aprovação (proporcional ao denominador do parecer):**

O gate é calculado sobre os itens **efetivamente aplicáveis** ao parecer em questão. Itens de vertente não acionada recebem N/A e ficam fora do denominador.

- ≥ 90% dos itens aplicáveis: APROVADO COM MÉRITO — entrega liberada
- 84–89% dos itens aplicáveis: APROVADO COM RESSALVAS — corrigir itens reprovados antes da entrega
- 75–83% dos itens aplicáveis: REPROVADO — reescrita obrigatória, retorno ao Passo 5
- < 75% dos itens aplicáveis: REPROVADO COM REFAÇÃO INTEGRAL — refazer do zero

**Exemplo de cálculo:** parecer monovertente A (servidores) → 31 fixos + 7 E.SERV = 38 itens aplicáveis. Gate de aprovação com ressalvas = 32 itens (84%). Parecer integrado A+B (tributário) → 31 + 7 + 6 = 44 itens aplicáveis. Gate = 37 itens.

---

## DIMENSÃO A — Estrutura Formal (5 itens)

### A.1 — Estrutura tripartite estrita

✓ Parecer tem APENAS três blocos: I — RELATÓRIO, II — FUNDAMENTOS, III — CONCLUSÃO
✗ Há subdivisões numeradas dentro da seção II (REPROVA imediato)

### A.2 — Ausência de subseções na fundamentação

✓ Seção II flui em prosa contínua, sem títulos "1. Da...", "2. Da..."
✗ Aparecem títulos numerados dentro da fundamentação (REPROVA imediato — bloqueio B2)

### A.3 — Ementa em palavras-chave separadas por travessão, TODAS EM MAIÚSCULAS

✓ Ementa em palavras-chave separadas por figure-dash (―, U+2015), terminando com a conclusão
✓ Todas as palavras-chave em MAIÚSCULAS (override autoral do Dr. Ione — registrado em 09/05/2026)
✓ Referências normativas preservam grafia legal (ex.: "Lei nº 14.133/2021", "art. 64")
✗ Ementa em prosa narrativa de várias linhas (REPROVA — bloqueio B4)
✗ Palavras-chave em capitalização normal sem maiúsculas (PONTO PERDIDO — não reprova imediatamente, mas desconta 1 ponto e exige correção antes da entrega)

### A.4 — Bloco de assinaturas no padrão do escritório

✓ Ione centralizado no topo, Matheus + Flávio em linha dupla com tab stops, Valéria centralizado abaixo
✗ Bloco de assinaturas em outra ordem ou sem padrão correto

### A.5 — Fórmulas invariáveis presentes

✓ Aparece "É o breve relatório. Passa-se à fundamentação." ao final do Relatório
✓ Aparece "É o parecer." no fechamento

---

## DIMENSÃO B — Costura Argumentativa (6 itens)

### B.1 — Conectivos de transição entre os movimentos

✓ Movimentos argumentativos sinalizados por conectivos integrados ao texto
✗ Mudança brusca entre teses sem conectivo de transição

### B.2 — Vocabulário arquitetural canônico utilizado

✓ Aparecem frases-tipo como "Compreendida essa dualidade...", "Avançando, então...", "Resta o terceiro pressuposto..."
✗ Transições genéricas tipo "Por outro lado...", "Ademais..."

### B.3 — Fundamentação organizada em movimentos lógicos sucessivos

✓ Há sequência clara de movimentos: tese → fundamento → aplicação → conclusão argumentativa
✗ Fundamentação parece desorganizada ou sem direção

### B.4 — Transição clara entre fundamentação e conclusão

✓ Seção III começa com "Diante do exposto" ou "Diante de todo o exposto", retomando a fundamentação
✗ Conclusão começa do nada ou repete a fundamentação

### B.5 — Citações literais seguidas de paráfrase funcional

✓ Toda citação em itálico recuado vem seguida de paráfrase que traduz o dispositivo
✗ Citação termina e o texto segue sem desenvolver o significado operacional (bloqueio B3)

### B.6 — Frases curtas em pontos decisivos

✓ Há pelo menos 2 frases curtas isoladas (5-10 palavras) cravando conclusões em pontos decisivos
✗ Texto sem ritmo, sem martelos argumentativos

---

## DIMENSÃO C — Aterramento Operacional (4 itens)

### C.1 — Exemplos concretos do universo municipal

✓ Após cada conceito abstrato há exemplo concreto do mundo do gestor (alimentação escolar, transporte, limpeza)
✗ Conceitos jurídicos sem aterramento (viola o princípio ★4)

### C.2 — Linguagem operacional para o gestor

✓ Texto fala COM o gestor, não SOBRE a lei. Ele consegue visualizar a operação.
✗ Texto puramente abstrato, dirigido a outro jurista

### C.3 — Recomendações executáveis

✓ Conclusão lista alíneas (a, b, c, d) com providências concretas que o gestor pode implementar
✗ Recomendações vagas tipo "agir com cuidado" ou "observar a legislação"

### C.4 — Advertência protetiva sóbria

✓ Risco de responsabilização aparece em prosa institucional, sem caixa-alta
✗ ATENÇÃO em maiúsculas (REPROVA — bloqueio B5)

---

## DIMENSÃO D — Linguagem e Estilo (5 itens)

### D.1 — Parágrafos curtos com uma ideia por bloco

✓ Tamanho médio de parágrafo: 3 a 5 linhas. Nenhum passa de 6 linhas sem justificativa.
⚠ Parágrafo com 7 linhas: intervenção obrigatória — quebrar antes de liberar o parecer.
✗ Há parágrafos de 8+ linhas (REPROVA IMEDIATO — override do Dr. Ione registrado em 09/05/2026; mais restritivo que a regra anterior à v2.2.0 que tolerava até 10 linhas)

**Procedimento quando detectado:**
1. Identificar todas as teses embutidas no parágrafo longo.
2. Quebrar em tantos parágrafos quantas forem as teses.
3. Costurar a quebra com conectivo de transição (catálogo em `escrita/conectivos-arquiteturais.md`).
4. Nenhum parágrafo resultante deve passar de 6 linhas.

### D.2 — Frases médias com 15-25 palavras

✓ Frase média entre 15 e 25 palavras. Nenhuma passa de 40.
✗ Frases longas, prolixas, com múltiplas subordinadas

### D.3 — Vocabulário técnico vivo, sem juridiquês arcaico

✓ Não aparece "destarte", "outrossim", "in casu" decorativo
✗ Vocabulário pomposo presente (bloqueio B7)

### D.4 — Voz ativa predominante

✓ Mais de 70% das construções em voz ativa
✗ Voz passiva decorativa em excesso ("Foi praticada pela autoridade a conduta...")

### D.5 — Ausência de advérbios decorativos

✓ Sem "efetivamente", "certamente", "evidentemente", "induvidosamente" sem função
✗ Texto inflado por advérbios decorativos (princípio ★12)

---

## DIMENSÃO E — Conteúdo Jurídico (7 itens universais + 31 condicionais por vertente)

### E.1 — Tese central clara nas primeiras linhas dos Fundamentos

✓ Primeiro parágrafo da seção II já entrega a tese central
✗ Tese aparece só ao final da fundamentação

### E.2 — Citação literal de pelo menos 1 dispositivo legal

✓ Há ao menos uma citação literal de dispositivo (art. ou inciso) em itálico recuado
✗ Parecer apenas resume a lei sem citar texto literal

### E.3 — Aplicação dos dispositivos ao caso concreto

✓ Dispositivos citados são confrontados com a situação concreta do caso
✗ Pareceres "doutrinários" abstratos, sem aplicação ao caso

### E.4 — Hyperlinks de jurisprudência validados ou marcados

✓ Toda referência a acórdão/súmula tem URL validada OU marcador `[URL_VALIDAR]`
✗ URLs inventadas (REPROVA imediato — bloqueio B6)

### E.5 — Não há listas com bullet points dentro do corpo

✓ Texto inteiramente em prosa, exceto alíneas das recomendações
✗ Há `\n-` ou `\n•` dentro do corpo (bloqueio B1)

### E.6 — Não há elementos visuais de Visual Law

✓ Texto inteiramente em prosa, sem caixas ASCII, fluxogramas, tabelas, mapas
✗ Há caracteres `┌ ─ │ └ ┐ ┘ ├ ┤` (REPROVA imediato — bloqueio B9)

### E.7 — Verificação ativa de normas citadas pela parte adversa

✓ Toda norma invocada pela parte adversa (recorrente, impugnante, autor de contrarrazões, licitante) foi confirmada via `web_search` quanto a existência, vigência e teor.
✓ Achados de norma inexistente, com numeração errada, ou com teor distorcido foram incorporados à minuta como parágrafo dedicado, com indicação da norma vigente correta quando houver.
✗ Há `[!VERIFICAR: ... !]` na minuta **final** referente a norma citada pela parte adversa — isto é, o redator não concluiu a verificação e deixou o marcador aberto (REPROVA IMEDIATO — override do Dr. Ione registrado em 09/05/2026; v2.3.0). Nota: `[!VERIFICAR: ... !]` é permitido no parecer final para dados que não puderam ser confirmados via web_search em geral; a proibição aqui é específica para normas da parte adversa, onde a verificação é obrigatória e não admite ponto em aberto.
✗ Norma da parte adversa foi reproduzida sem confirmação de existência (REPROVA — viola princípio fundamental nº 4).

**Procedimento quando detectado erro de numeração na petição da parte adversa:**
1. Identificar com precisão a norma efetivamente vigente sobre a matéria, via `web_search` em fontes oficiais (Planalto, ANVISA, ANS, ANATEL, agência reguladora competente).
2. Dedicar 1 a 2 parágrafos do parecer ao achado, em prosa institucional sóbria.
3. Registrar (a) o erro de numeração; (b) a norma efetivamente vigente; (c) o impacto sobre o argumento da parte adversa; (d) reserva técnica de correção humana posterior.
4. Nunca omitir o achado nem deixar marcador `[!VERIFICAR: ... !]` aberto em texto final referente a norma de parte adversa.

---

### Itens condicionais por vertente

> Esta subseção foi acrescentada em **v3.1.0** (Etapa 5 da migração, com refinamento para granularidade fina a pedido do Dr. Matheus em 15/05/2026). Os itens E.SERV.*, E.TRIB.*, E.OSC.*, E.FIN.*, E.URB.* e E.FUNDEB.* abaixo **só são pontuáveis quando a vertente correspondente é acionada** pelo parecer. Em parecer de vertente pura (apenas servidores, ou apenas tributário, etc.), os itens das vertentes não acionadas recebem **N/A** e ficam **fora do denominador** do score. Em parecer integrado (que atravessa mais de uma vertente), aplicam-se cumulativamente os itens das vertentes envolvidas.
>
> Cada item condicional faz **ponte expressa e exclusiva** para um bloqueio temático do arquivo `bloqueios-obrigatorios.md` — mapeamento bijetivo, um para um. A correspondência é registrada explicitamente em cada item (E.SERV.1 ↔ B-SERV-1, e assim por diante).

#### Família servidor público — vertente A (7 itens)

##### E.SERV.1 — Concurso público em criação ou reestruturação de cargo

✓ Parecer sobre criação, reestruturação, fusão ou reenquadramento de cargo enfrenta expressamente o art. 37, II, da CF e a Súmula Vinculante 43, distinguindo provimento derivado vedado de reestruturação legítima. Quando o ato envolver nível de escolaridade distinto entre cargo de origem e de destino, registra a vedação expressamente.
✗ Ato sobre cargo é validado sem qualquer menção a concurso público ou à SV 43 (viola **B-SERV-1**).

##### E.SERV.2 — Acumulação de cargos e requisitos cumulativos

✓ Parecer sobre situação funcional com dois ou mais vínculos enquadra a hipótese no inciso correto do art. 37, XVI, da CF e enfrenta compatibilidade de horários e teto remuneratório como requisitos **cumulativos**, não alternativos. A compatibilidade é aferida materialmente — não pela soma aritmética.
✗ Parecer admite acumulação com base apenas na soma aritmética de horas (60h/80h semanais) sem exame material de compatibilidade (viola **B-SERV-2**).

##### E.SERV.3 — Teto remuneratório constitucional em consulta de pagamento

✓ Parecer que examine pagamento de vantagem, gratificação, abono, indenização ou subsídio menciona expressamente o teto remuneratório constitucional (CF art. 37, XI) e sua expressão pelo subsídio do Prefeito municipal. Registra se a vantagem tem natureza remuneratória sujeita ao teto e recomenda aferição em folha pela Secretaria de Administração antes do pagamento.
✗ Pagamento de vantagem é validado sem qualquer menção ao teto constitucional municipal (viola **B-SERV-3**).

##### E.SERV.4 — Reserva de lei para criação ou majoração de vantagem

✓ Parecer sobre criação ou majoração de vencimento, gratificação, abono, adicional ou indenização identifica a lei municipal que institui a parcela, examina iniciativa adequada (art. 61, § 1º, II, "a", CF) e confronta a invocação eventual de isonomia com a SV 37 e os Temas 315 e 600 do STF.
✗ Vantagem é validada por isonomia isolada, sem lei (viola **B-SERV-4**). Ou parecer omite o teste de iniciativa.

##### E.SERV.5 — Nepotismo em nomeação de parente

✓ Parecer sobre nomeação para cargo em comissão, função de confiança ou função gratificada com vínculo de parentesco enfrenta a SV 13. Identifica a natureza do cargo (administrativo ou político), aplica o teste de qualificação técnica e idoneidade moral em caso de cargo político, e confere o status atual do Tema 1000 do STF (em julgamento — conferência via `web_search` recomendada na data da redação). Em caso de **nepotismo cruzado**, aplica a SV 13 mesmo a cargos políticos.
✗ Nomeação de parente é admitida sem sequer mencionar a SV 13 (viola **B-SERV-5**).

##### E.SERV.6 — Pressupostos do art. 37, IX em contratação temporária

✓ Parecer sobre contratação temporária por excepcional interesse público aplica os cinco testes do Tema 612 do STF (RE 658.026): hipótese prevista em lei, prazo predeterminado, necessidade temporária, interesse excepcional, atividade não-permanente. Cada teste demonstrado no caso concreto.
✗ Contratação temporária é validada sem aplicação dos cinco testes do Tema 612, ou validada para suprir atividade ordinária permanente (viola **B-SERV-6**).

##### E.SERV.7 — Devolução de valores em revisão de ato favorável ao servidor

✓ Parecer que opine pela revisão ou anulação de ato gerador de vantagem percebida pelo servidor enfrenta a boa-fé objetiva, o Tema 531 do STF (RE 638.115), a decadência decenal do art. 54 da Lei 9.784/99 (aplicável aos municípios) e os arts. 22 a 24 da LINDB. Conclui expressamente sobre devolução ou não devolução.
✗ Revisão é admitida sem enfrentar a boa-fé do servidor nem o Tema 531 (viola **B-SERV-7**).

#### Família tributário municipal — vertente B (tributária) (6 itens)

##### E.TRIB.1 — Reserva de lei específica para benefício fiscal

✓ Parecer favorável a isenção, anistia, remissão, REFIS, redução de base ou subsídio enfrenta expressamente o art. 150, § 6º, da CF e o Tema 682 do STF (ARE 743.480), exigindo lei municipal específica (não decreto, não autorização genérica).
✗ Decreto do Executivo perdoa ou reduz dívida tributária sem lei específica (viola **B-TRIB-1**). Ou lei genérica autoriza o Prefeito a conceder benefícios casuísticos.

##### E.TRIB.2 — Três pressupostos do art. 14 da LRF (vertente tributária)

✓ Parecer sobre renúncia de receita tributária registra os três pressupostos do art. 14 da LRF: (i) estimativa de impacto no exercício e nos dois subsequentes; (ii) consideração na lei orçamentária; (iii) medida de compensação. Cada um demonstrado concretamente nos autos.
✗ Renúncia é admitida sem qualquer dos três (viola **B-TRIB-2**). Ou os três aparecem apenas como cláusula de estilo na lei sem demonstração efetiva.

##### E.TRIB.3 — Majoração disfarçada de base de cálculo de IPTU por decreto

✓ Parecer sobre revisão da PGV ou atualização do IPTU distingue atualização monetária (admissível por decreto, dentro do índice oficial) de majoração da base de cálculo (exige lei). Aplica a Súmula 160 do STJ e o art. 97, § 1º, do CTN. Em caso de revisão da PGV em si, registra reserva à lei municipal.
✗ Atualização por decreto excede índice oficial, ou parecer admite revisão da PGV sem lei (viola **B-TRIB-3**).

##### E.TRIB.4 — Notificação por carnê em cobrança ou execução de IPTU

✓ Parecer subsidiando cobrança ou execução fiscal de IPTU enfrenta a Súmula 397 do STJ e o REsp 1.111.124/PR (Tema 248): a notificação se opera presumidamente pelo envio do carnê; o ônus de demonstrar o não-recebimento é do contribuinte; ausente prova do envio, a presunção não se forma e a CDA pode ser anulada.
✗ IPTU é cobrado sem nota de notificação válida nos autos, ou parecer silencia sobre o Tema 248 (viola **B-TRIB-4**).

##### E.TRIB.5 — Prescrição e decadência tributárias em crédito antigo

✓ Parecer sobre crédito tributário com ≥ 5 anos do fato gerador ou da constituição definitiva distingue decadência (art. 173 do CTN; Tema 163 do STJ) de prescrição (art. 174; Tema 383). Identifica o termo inicial específico do tributo e da modalidade, eventos suspensivos ou interruptivos, e conclui sobre exigibilidade. Quando aplicável, invoca a SV 8 do STF.
✗ Os dois institutos são confundidos ou tratados em bloco genérico (viola **B-TRIB-5**). Ou o parecer não enfrenta termo inicial específico.

##### E.TRIB.6 — Capacidade contributiva em alíquota progressiva ou diferenciada

✓ Parecer favorável à instituição de IPTU progressivo (fiscal, por valor venal — art. 156, § 1º, I) ou de alíquotas diferenciadas de ISS enfrenta o princípio da capacidade contributiva (art. 145, § 1º) e o RE 423.768. **Distingue rigorosamente** três institutos: (a) progressividade fiscal por valor venal (art. 156, § 1º, I); (b) alíquotas diferenciadas por localização e uso (art. 156, § 1º, II); (c) progressividade no tempo como instrumento urbanístico (art. 182, § 4º, II — regime próprio, ver E.URB.1).
✗ Os três institutos são misturados ou tratados como um só, ou parecer admite progressividade sem fundamentação técnica da gradação (viola **B-TRIB-6**).

#### Família terceiro setor — vertente C (5 itens)

##### E.OSC.1 — Chamamento público como regra na Lei 13.019/14

✓ Parecer sobre termo de fomento ou colaboração trata o chamamento público como **regra** (art. 24 da Lei 13.019/14) e registra a excepcionalidade das hipóteses dos arts. 30 e 31. Quando há emenda parlamentar identificando a OSC, o parecer registra a dispensa de chamamento mas confirma a aplicação das demais exigências da Lei 13.019.
✗ Parecer admite parceria sem enfrentar a regra do chamamento ou a excepcionalidade das dispensas (viola **B-OSC-1**).

##### E.OSC.2 — Requisitos da dispensa do art. 30 quando invocada

✓ Quando a Administração invocar dispensa do art. 30, o parecer identifica o **inciso específico** (I a VI) e demonstra concretamente seus pressupostos: urgência por paralisação (I), calamidade/perturbação (II), proteção de pessoas (III), educação/saúde/assistência com credenciamento prévio (VI). Trata da justificativa formal do art. 32, com publicidade prévia de cinco dias.
✗ Dispensa do art. 30, VI é admitida sem credenciamento prévio da OSC, ou justificativa do art. 32 não foi formalizada (viola **B-OSC-2**).

##### E.OSC.3 — Requisitos da inexigibilidade do art. 31 quando invocada

✓ Quando a Administração invocar inexigibilidade do art. 31, o parecer demonstra a **inviabilidade de competição** entre OSCs no caso concreto: registra a singularidade material do objeto ou da OSC, e registra que outras OSCs do município ou da região foram efetivamente verificadas e descartadas (não basta afirmar — é preciso demonstrar).
✗ Inexigibilidade é afirmada genericamente, sem demonstração de inviabilidade real (viola **B-OSC-3**).

##### E.OSC.4 — Pressupostos da ADI 1.923 em contratação de OS

✓ Parecer sobre contrato de gestão com Organização Social (Lei 9.637/98 ou lei municipal análoga) enfrenta os pressupostos da ADI 1.923/DF: qualificação **pública, objetiva e impessoal**, observância dos princípios do art. 37 caput da CF, e procedimento de seleção análogo (ainda que não seja licitação formal). Distingue rigorosamente OS (Lei 9.637) de OSC do MROSC (Lei 13.019). Quando relevante, registra a confirmação atualizada via ADI 7.629/MG (fev/2025) e ADPF 559.
✗ Contratação de OS é validada por simples qualificação genérica, ou parecer confunde OS com OSC do MROSC (viola **B-OSC-4**).

##### E.OSC.5 — Nexo de causalidade e proporcionalidade em prestação de contas

✓ Parecer subsidiando defesa em prestação de contas com glosa enfrenta (i) o nexo de causalidade receita-despesa; (ii) a regra da verdade material (Lei 13.019, art. 64); (iii) a proporcionalidade da glosa, conforme jurisprudência do TCU (Acórdão 1.187/2019-Plenário e correlatos); (iv) os arts. 22 a 24 da LINDB. Ativa REGRA IRR-3 — toda norma invocada pela Administração passa por `web_search` obrigatório.
✗ Glosa é aceita como integral sem exame de proporcionalidade, ou parecer não confirma normas da Administração (viola **B-OSC-5**).

#### Família financeiro municipal — vertente B (financeira) (5 itens)

##### E.FIN.1 — Art. 42 da LRF em consulta de fim de mandato

✓ Parecer sobre celebração, empenho ou assunção de despesa nos dois últimos quadrimestres do último ano de mandato enfrenta o art. 42 da LRF. Aplica o critério de aferição comparativa do estoque líquido entre 30/04 e 31/12, registra que o momento decisivo é a formalização do contrato (não o empenho), e adverte sobre o risco de improbidade administrativa (Lei 8.429/92, art. 11, c/c art. 73 da LRF) com dolo genérico já reconhecido pelo STJ. Advertência protetiva redobrada.
✗ Assunção de despesa em fim de mandato é validada sem qualquer menção ao art. 42, ou se admite que a "finalidade pública" da despesa exclui a vedação (viola **B-FIN-1**).

##### E.FIN.2 — Limites de despesa com pessoal (arts. 19-23 da LRF)

✓ Parecer sobre criação ou majoração de despesa com pessoal enfrenta os limites dos arts. 18-23 da LRF e da LC 178/2021: 54% para o Executivo municipal, 6% para o Legislativo, gatilho prudencial de 51,3%. Inclui verificação atualizada da DTP/RCL (dado que precisa estar nos autos — sem ele, parecer **provisório**). Registra eventuais medidas de contenção do art. 22 já em vigor.
✗ Despesa com pessoal é validada sem cálculo atualizado da DTP/RCL, ou ato eleva DTP acima do limite prudencial sem demonstrar margem (viola **B-FIN-2**).

##### E.FIN.3 — Art. 14 da LRF em vertente financeira (espelho global)

✓ Parecer sobre projeto de lei orçamentária ou sobre adequação financeira de pacote de benefícios enfrenta o art. 14 da LRF do ponto de vista do **equilíbrio financeiro global**: verifica se a soma das renúncias consolidada está dentro da projeção da LDO; se as medidas de compensação foram efetivamente implementadas em folha; e a integração com RREO (art. 52) e RGF (art. 54).
✗ Renúncia consolidada é admitida sem demonstração efetiva das medidas de compensação, ou parecer silencia sobre RREO/RGF (viola **B-FIN-3**).

##### E.FIN.4 — Inscrição em restos a pagar e o art. 41 da Lei 4.320/64

✓ Parecer sobre inscrição em RAP distingue rigorosamente RAP processado (despesa liquidada) de RAP não processado (empenhada e não liquidada), conforme art. 41 da Lei 4.320/64. Verifica suporte financeiro, eventual vinculação constitucional (FUNDEB, saúde — art. 198, § 2º; educação — art. 212) que justifique manutenção em exercício posterior, e risco de art. 42 da LRF se a inscrição se der no fim de mandato.
✗ RAPs são tratados em bloco genérico, ou parecer admite inscrição sem suporte financeiro (viola **B-FIN-4**).

##### E.FIN.5 — Retenção indevida de repasse constitucional (art. 160 da CF)

✓ Parecer subsidiando ação contra retenção de FPM, cota-parte do ICMS, IPVA ou ITR enfrenta a vedação do art. 160 da CF e a taxatividade das exceções de seu parágrafo único. Identifica o fundamento invocado pelo ente repassante, verifica se enquadra-se estritamente nas exceções, e indica o instrumento processual cabível (MS originário no STF, STJ ou TJ-CE conforme a parte adversa). Ativa REGRA IRR-3 (confirma via `web_search` a fundamentação da retenção).
✗ Retenção de FPM é aceita como regular sem exame estrito das exceções do art. 160 (viola **B-FIN-5**).

#### Família urbanismo — vertente A (urbanística) (4 itens)

##### E.URB.1 — Sucessividade da tríade do art. 182, § 4º, CF

✓ Parecer sobre IPTU progressivo no tempo (CF art. 182, § 4º, II) ou desapropriação-sanção (inciso III) enfrenta a regra constitucional da sucessividade: PEUC → IPTU progressivo no tempo → desapropriação. Aplica a Súmula 668 do STF para fundamentar a progressividade pré-EC 29/2000 atrelada à função social. **Distingue rigorosamente** IPTU progressivo no tempo (instrumento urbanístico, art. 182, § 4º, II) de IPTU progressivo por valor venal (alíquota fiscal, art. 156, § 1º, I) — confusão entre os dois descaracteriza o parecer.
✗ IPTU progressivo no tempo é aplicado sem notificação prévia para PEUC, ou parecer mistura os dois IPTU progressivos (viola **B-URB-1**).

##### E.URB.2 — Plano diretor como pressuposto dos instrumentos urbanísticos

✓ Parecer favorável à aplicação de PEUC, IPTU progressivo no tempo, desapropriação-sanção, outorga onerosa do direito de construir, operações urbanas consorciadas, direito de preempção ou transferência do direito de construir enfrenta a exigência de previsão expressa no plano diretor municipal (CF art. 182, § 1º; Estatuto da Cidade arts. 39-42, 25-33). Para municípios obrigados a ter plano diretor (mais de 20.000 habitantes), registra eventual omissão sancionável.
✗ Instrumento urbanístico é admitido sem plano diretor que o preveja, ou sem demonstração de aprovação pela Câmara e participação popular (viola **B-URB-2**).

##### E.URB.3 — Competência municipal exclusiva em licenciamento urbanístico e EIV

✓ Parecer sobre licenciamento urbanístico distingue (i) licenciamento urbanístico (competência **municipal** exclusiva, salvo grande obra de impacto regional); (ii) licenciamento ambiental (competência concorrente — IBAMA, órgão estadual ou municipal); (iii) Estudo de Impacto de Vizinhança (instrumento urbanístico, não substitui EIA-RIMA quando este for cabível). Quando relevante, confere status atual das ADIs 5.771, 5.787 e 5.883 no STF.
✗ EIV é tratado como substituto do EIA-RIMA ou vice-versa, ou competência municipal urbanística é confundida com a ambiental concorrente (viola **B-URB-3**).

##### E.URB.4 — Requisitos da REURB (Lei 13.465/17) e competência sobre a CRF

✓ Parecer sobre regularização fundiária urbana classifica a modalidade aplicável (Reurb-S para baixa renda; Reurb-E para demais casos; modalidade do art. 69 para núcleos consolidados há mais de 30 anos). Registra a competência **municipal exclusiva** para emissão da CRF (Decreto 9.310/2018, art. 23). Quando o imóvel é da União ou do Estado, distingue titularidade (federal/estadual) de competência urbanística (municipal).
✗ Modalidades da REURB não são distinguidas, ou competência sobre CRF é confundida com competência da União ou do Estado em razão da titularidade do imóvel (viola **B-URB-4**).

#### Família Fundeb — vertente A (financeira-educacional) (4 itens)

##### E.FUNDEB.1 — Subvinculação de 70% e abrangência ampliada pela EC 108/2020

✓ Parecer sobre aplicação dos recursos do Fundeb enfrenta a subvinculação constitucional mínima de 70% para profissionais da educação básica em efetivo exercício (art. 212-A, XI, CF — EC 108/2020; Lei 14.113/2020, art. 26). Reconhece a abrangência ampliada após Lei 14.276/2021 (não mais limitada ao magistério, mas todo o corpo funcional). Registra base de cálculo correta (cada fundo recebido, excluídos os recursos da complementação-VAAR).
✗ Parecer trata os 70% como "limite ao magistério" sob o regime anterior à EC 108/2020, ou aplica a subvinculação sobre a receita global da educação e não sobre o fundo (viola **B-FUNDEB-1**).

##### E.FUNDEB.2 — Obrigatoriedade do CACS-Fundeb

✓ Parecer sobre estruturação ou prestação de contas do Fundeb registra a obrigatoriedade do CACS-Fundeb (Lei 14.113/2020, arts. 30-36), sua composição plural (representantes do Executivo, professores, diretores, técnico-administrativos, pais, estudantes) e sua atribuição de emitir parecer prévio às contas. Quando o conselho está inativo, registra como vício grave.
✗ Conselho está inativo ou inexistente e o parecer não problematiza, ou conselho meramente formal é tratado como regular (viola **B-FUNDEB-2**).

##### E.FUNDEB.3 — Regime de aplicação no exercício e janela do art. 25, § 3º

✓ Parecer sobre planejamento orçamentário do Fundeb enfrenta a regra geral de aplicação no próprio exercício e a exceção da janela do art. 25, § 3º (até 10% para o primeiro trimestre subsequente). Registra que a janela é **limite máximo** (não obrigação) e que o uso do saldo deve estar destinado e identificado.
✗ Saldos do Fundeb são inscritos genericamente em restos a pagar fora da janela, ou janela é usada como autorização irrestrita (viola **B-FUNDEB-3**).

##### E.FUNDEB.4 — Vedação ao uso fora das finalidades constitucionais

✓ Parecer sobre destinação de recurso do Fundeb confronta despesas com as finalidades constitucionais (art. 212-A) e aplica subsidiariamente os arts. 70 e 71 da LDB. Despesas duvidosas (educação infantil em entidade conveniada, transporte escolar terceirizado, publicidade institucional) demandam análise específica caso a caso. Advertência protetiva sobre devolução pessoal e improbidade administrativa.
✗ Despesa-limite (publicidade institucional, transporte fora de parâmetros, creche conveniada sem caráter público) é validada sem aplicação dos arts. 70 e 71 da LDB (viola **B-FUNDEB-4**).

---

## DIMENSÃO F — Identidade Autoral (4 itens)

### F.1 — Marcadores autorais presentes

✓ Pelo menos 4 dos 12 princípios estrelados são reconhecíveis no texto
✗ Texto poderia ter saído de qualquer escritório

### F.2 — Não parece feito por IA genérica

✓ Texto tem ritmo, costura, voz autoral. Não é template preenchido.
✗ Cara de ChatGPT (subdivisões excessivas, bullet points, jargão decorativo, frases bombásticas)

### F.3 — Encerramento conforme padrão

✓ Aparece "É o parecer." seguido do disclaimer de discricionariedade
✗ Encerramento livre, sem fórmula institucional

### F.4 — Local, data e bloco de assinaturas no padrão

✓ "Fortaleza/CE, [data por extenso]." seguido do bloco de 4 advogados em ordem hierárquica
✗ Padrão de assinaturas alterado

---

## CÁLCULO DA NOTA

A pontuação é calculada sobre os itens **efetivamente aplicáveis** ao parecer (itens de vertente não acionada recebem N/A e ficam fora do denominador). São **31 itens fixos universais** + até **31 itens condicionais** por vertente.

| Faixa (% dos itens aplicáveis) | Status | Ação |
|---|---|---|
| ≥ 90% | APROVADO COM MÉRITO | Entrega liberada |
| 84–89% | APROVADO COM RESSALVAS | Corrigir itens reprovados antes da entrega |
| 75–83% | REPROVADO | Reescrita obrigatória, retorno ao Passo 5 |
| < 75% | REPROVAÇÃO INTEGRAL | Refazer do zero |

---

## REPROVAÇÕES IMEDIATAS (qualquer destes força reprovação integral)

Independentemente da pontuação proporcional, o parecer é **REPROVADO IMEDIATAMENTE** se ocorrer qualquer um dos seguintes:

1. Subdivisão numerada dentro da fundamentação (bloqueio B2)
2. Ementa em prosa narrativa de 4+ linhas (bloqueio B4)
3. Frase com 10+ palavras em CAIXA ALTA dramática (bloqueio B5)
4. Elementos visuais de Visual Law presentes (bloqueio B9)
5. URL de jurisprudência não validada (bloqueio B6)
6. Parágrafo com 8+ linhas (override v2.2.0 — gate D.1)
7. Marcador `[!VERIFICAR: ... !]` aberto em texto final referente a norma citada pela parte adversa — onde a verificação é obrigatória e não admite ponto em aberto (override v2.3.0 — gate E.7)

Esses são os "tiros de canhão" — qualquer um deles, sozinho, descaracteriza o parecer.
