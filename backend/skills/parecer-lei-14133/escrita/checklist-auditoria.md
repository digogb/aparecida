# Checklist de Auditoria — Padrão da v5

**Versão 2.4** — calibrada para auditoria de pareceres alinhados ao parecer-modelo v5, com overrides autorais do Dr. Ione (v2.2.0 — ementa em maiúsculas e gate de parágrafos; v2.3.0 — verificação ativa de normas citadas pela parte adversa) **e Dimensão G específica do parecer jurídico prévio do art. 53 introduzida em v2.6.0 da skill**.

Este checklist é executado no **Passo 6 (Auto-auditoria)** do fluxo da skill. São **31 itens** para subtipos comuns (Dimensões A a F) e **34 itens** para o subtipo "Parecer jurídico prévio do art. 53" (Dimensões A a G). Cada item vale 1 ponto.

**Gate de aprovação:**
- Pareceres comuns: 29-31 pontos APROVADO COM MÉRITO; 26-28 APROVADO COM RESSALVAS; 23-25 REPROVADO; < 23 REPROVAÇÃO INTEGRAL
- Parecer art. 53: 32-34 pontos APROVADO COM MÉRITO; 29-31 APROVADO COM RESSALVAS; 25-28 REPROVADO; < 25 REPROVAÇÃO INTEGRAL

---

## DIMENSÃO A — Estrutura Formal (5 itens)

### A.1 — Estrutura tripartite estrita

✓ Parecer tem APENAS três blocos: I — RELATÓRIO, II — FUNDAMENTOS, III — CONCLUSÃO
✗ Há subdivisões numeradas dentro da seção II (REPROVA imediato)

### A.2 — Ausência de subseções na fundamentação

✓ Seção II flui em prosa contínua, sem títulos "1. Da...", "2. Da..."
✗ Aparecem títulos numerados dentro da fundamentação (REPROVA imediato — bloqueio ★1)

### A.3 — Ementa em palavras-chave separadas por travessão, TODAS EM MAIÚSCULAS

✓ Ementa em palavras-chave separadas por figure-dash (―, U+2015), terminando com a conclusão
✓ Todas as palavras-chave em MAIÚSCULAS (override autoral do Dr. Ione — registrado em 09/05/2026)
✓ Referências normativas preservam grafia legal (ex.: "Lei nº 14.133/2021", "art. 64")
✗ Ementa em prosa narrativa de várias linhas (REPROVA — bloqueio ★2)
✗ Palavras-chave em capitalização normal sem maiúsculas (PONTO PERDIDO — não reprova imediatamente, mas desconta 1 ponto e exige correção antes da entrega)

### A.4 — Bloco de assinaturas no padrão do escritório

✓ Ione centralizado no topo, Matheus + Flávio em linha dupla com tab stops, Valéria centralizado abaixo
✗ Bloco de assinaturas em outra ordem ou sem padrão correto

### A.5 — Fórmulas invariáveis presentes

✓ Aparece "É o breve relatório. Passa-se à fundamentação." ao final do Relatório
✓ Aparece "É o parecer, submetido à superior consideração." no fechamento

---

## DIMENSÃO B — Costura Argumentativa (6 itens)

### B.1 — Conectivos de transição entre os movimentos

✓ Movimentos argumentativos sinalizados por conectivos integrados ao texto
✗ Mudança brusca entre teses sem conectivo de transição

### B.2 — Vocabulário arquitetural canônico utilizado

✓ Aparecem frases-tipo como "Compreendida essa dualidade...", "Avancemos, então...", "Resta o terceiro pressuposto..."
✗ Transições genéricas tipo "Por outro lado...", "Ademais..."

### B.3 — Fundamentação organizada em movimentos lógicos sucessivos

✓ Há sequência clara de movimentos: tese → fundamento → aplicação → conclusão argumentativa
✗ Fundamentação parece desorganizada ou sem direção

### B.4 — Transição clara entre fundamentação e conclusão

✓ Seção III começa com "Diante do exposto" ou "Diante de todo o exposto", retomando a fundamentação
✗ Conclusão começa do nada ou repete a fundamentação

### B.5 — Citações literais seguidas de paráfrase funcional

✓ Toda citação em itálico recuado vem seguida de paráfrase que traduz o dispositivo
✗ Citação termina e o texto segue sem desenvolver o significado operacional (bloqueio ★8)

### B.6 — Frases curtas em pontos decisivos

✓ Há pelo menos 2 frases curtas isoladas (5-10 palavras) cravando conclusões em pontos decisivos
✗ Texto sem ritmo, sem martelos argumentativos

---

## DIMENSÃO C — Aterramento Operacional (4 itens)

### C.1 — Exemplos concretos do universo municipal

✓ Após cada conceito abstrato há exemplo concreto do mundo do gestor (alimentação escolar, transporte, limpeza)
✗ Conceitos jurídicos sem aterramento (bloqueio ★9)

### C.2 — Linguagem operacional para o gestor

✓ Texto fala COM o gestor, não SOBRE a lei. Ele consegue visualizar a operação.
✗ Texto puramente abstrato, dirigido a outro jurista

### C.3 — Recomendações executáveis

✓ Conclusão lista alíneas (a, b, c, d) com providências concretas que o gestor pode implementar
✗ Recomendações vagas tipo "agir com cuidado" ou "observar a legislação"

### C.4 — Advertência protetiva sóbria

✓ Risco de responsabilização aparece em prosa institucional, sem caixa-alta
✗ ATENÇÃO em maiúsculas (REPROVA — bloqueio ★3)

---

## DIMENSÃO D — Linguagem e Estilo (5 itens)

### D.1 — Parágrafos curtos com uma ideia por bloco

✓ Tamanho médio de parágrafo: 3 a 5 linhas. Nenhum passa de 6 linhas sem justificativa.
⚠ Parágrafo com 7 linhas: intervenção obrigatória — quebrar antes de liberar o parecer.
✗ Há parágrafos de 8+ linhas (REPROVA IMEDIATO — override do Dr. Ione registrado em 09/05/2026; mais restritivo que o bloqueio ★7 anterior que tolerava até 10 linhas)

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
✗ Vocabulário pomposo presente (bloqueio ★6)

### D.4 — Voz ativa predominante

✓ Mais de 70% das construções em voz ativa
✗ Voz passiva decorativa em excesso ("Foi praticada pela autoridade a conduta...")

### D.5 — Ausência de advérbios decorativos

✓ Sem "efetivamente", "certamente", "evidentemente", "induvidosamente" sem função
✗ Texto inflado por advérbios decorativos (bloqueio ★11)

---

## DIMENSÃO E — Conteúdo Jurídico (7 itens)

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
✗ URLs inventadas (REPROVA imediato — bloqueio ★5)

### E.5 — Não há listas com bullet points dentro do corpo

✓ Texto inteiramente em prosa, exceto alíneas das recomendações
✗ Há `\n-` ou `\n•` dentro do corpo (bloqueio ★10)

### E.6 — Não há elementos visuais de Visual Law

✓ Texto inteiramente em prosa, sem caixas ASCII, fluxogramas, tabelas, mapas
✗ Há caracteres `┌ ─ │ └ ┐ ┘ ├ ┤` (REPROVA imediato — bloqueio ★4)

### E.7 — Verificação ativa de normas citadas pela parte adversa

✓ Toda norma invocada pela parte adversa (recorrente, impugnante, autor de contrarrazões, licitante) foi confirmada via `web_search` quanto a existência, vigência e teor.
✓ Achados de norma inexistente, com numeração errada, ou com teor distorcido foram incorporados à minuta como parágrafo dedicado, com indicação da norma vigente correta quando houver.
✗ Há `[VERIFICAR]` na minuta final referente a norma citada pela parte adversa (REPROVA IMEDIATO — override do Dr. Ione registrado em 09/05/2026; v2.3.0).
✗ Norma da parte adversa foi reproduzida sem confirmação de existência (REPROVA — viola princípio fundamental nº 4).

**Procedimento quando detectado erro de numeração na petição da parte adversa:**
1. Identificar com precisão a norma efetivamente vigente sobre a matéria, via `web_search` em fontes oficiais (Planalto, ANVISA, ANS, ANATEL, agência reguladora competente).
2. Dedicar 1 a 2 parágrafos do parecer ao achado, em prosa institucional sóbria.
3. Registrar (a) o erro de numeração; (b) a norma efetivamente vigente; (c) o impacto sobre o argumento da parte adversa; (d) reserva técnica de correção humana posterior.
4. Nunca omitir o achado nem deixar `[VERIFICAR]` em texto final.

---

## DIMENSÃO F — Identidade Autoral (4 itens)

### F.1 — Marcadores autorais presentes

✓ Pelo menos 4 dos 11 princípios estrelados são reconhecíveis no texto
✗ Texto poderia ter saído de qualquer escritório

### F.2 — Não parece feito por IA genérica

✓ Texto tem ritmo, costura, voz autoral. Não é template preenchido.
✗ Cara de ChatGPT (subdivisões excessivas, bullet points, jargão decorativo, frases bombásticas)

### F.3 — Encerramento conforme padrão

✓ Aparece "É o parecer, submetido à superior consideração." como fórmula invariável de fechamento
✗ Encerramento livre, sem fórmula institucional

### F.4 — Local, data e bloco de assinaturas no padrão

✓ "Fortaleza/CE, [data por extenso]." seguido do bloco de 4 advogados em ordem hierárquica
✗ Padrão de assinaturas alterado

---

## DIMENSÃO G — Conformidade ao Art. 53 (3 itens — aplicáveis APENAS ao subtipo "Parecer jurídico prévio do art. 53")

Esta dimensão foi introduzida na v2.6.0. Os itens **só são pontuáveis quando o subtipo do parecer for o art. 53** (acionado pelo pedido expresso do consulente ou pelo critério de definição do subtipo quando o documento central da análise é o edital). Quando o subtipo for outro (dispensa, inexigibilidade, aditivo etc.), os três itens são marcados como **N/A** e o denominador da pontuação da dimensão é zerado — não interferem na nota final.

### G.1 — Os cinco vetores do § 1º foram percorridos na fundamentação

✓ A costura argumentativa da seção II passa pelos cinco vetores do § 1º do art. 53 — exame jurídico do processo, modalidade e tipo, pressupostos materiais, habilitação, critérios de julgamento e minuta de contrato — na ordem que o caso pedir
✓ Os vetores são tratados em prosa contínua, **sem subdivisão numerada** (preserva A.1 e A.2)
✗ Vetor inteiramente ausente da fundamentação **sem menção à insuficiência documental que o motivou** (PONTO PERDIDO)
✗ Vetores apresentados em subseções numeradas tipo "Da modalidade", "Da habilitação" (REPROVA — viola A.1)

### G.2 — Ausência documental tratada em prosa, sem destaque tipográfico

✓ Quando algum vetor não pôde ser examinado por insuficiência documental, a menção é feita em prosa fluida no ponto da costura argumentativa em que o vetor seria tratado
✓ A menção está **sem negrito, sem caixa alta, sem isolamento em parágrafo próprio dramático** — opera como observação técnica integrada
✗ Item ausente foi destacado tipograficamente, criando alerta visual que descaracteriza a prosa institucional (PONTO PERDIDO)

### G.3 — Conclusão adequada ao regime do art. 53

✓ Dispositivo da conclusão usa fórmula consultiva ("Recomenda-se…")
✓ A intensidade do dispositivo é proporcional à gravidade dos achados:
- favorável sem ressalvas, quando não há achados;
- favorável com ressalvas, quando há saneamentos pontuais;
- contrário, quando há vícios estruturais que impedem o prosseguimento
✓ Se há documento faltante relevante, a conclusão recomenda sua juntada para subsidiar análise complementar quando pertinente
✗ Conclusão usa fórmula quase-processual ("Pertinente/Impertinente") em caso de parecer art. 53 (REPROVA — confusão de modo)

---

## CÁLCULO DA NOTA

A pontuação é a soma dos itens aprovados (1 ponto por item). 

**Para subtipos diversos do art. 53** (dispensa, inexigibilidade, aditivo, sanção, impugnação, recurso, adesão, credenciamento, SRP): total possível = **31 pontos** (Dimensões A a F; Dimensão G integralmente N/A).

**Para o subtipo "Parecer jurídico prévio do art. 53"**: total possível = **34 pontos** (Dimensões A a G ativas). Faixas escalonadas proporcionalmente:

| Faixa (subtipos comuns / art. 53) | Status | Ação |
|---|---|---|
| 29-31 / 32-34 | APROVADO COM MÉRITO | Entrega liberada |
| 26-28 / 29-31 | APROVADO COM RESSALVAS | Corrigir itens reprovados antes da entrega |
| 23-25 / 25-28 | REPROVADO | Reescrita obrigatória, retorno ao Passo 5 |
| < 23 / < 25 | REPROVAÇÃO INTEGRAL | Refazer do zero |

---

## REPROVAÇÕES IMEDIATAS (qualquer destes força nota < 23)

Independentemente da pontuação, o parecer é **REPROVADO IMEDIATAMENTE** se ocorrer qualquer um dos seguintes:

1. Subdivisão numerada dentro da fundamentação (bloqueio ★1)
2. Ementa em prosa narrativa de 4+ linhas (bloqueio ★2)
3. Frase com 10+ palavras em CAIXA ALTA dramática (bloqueio ★3)
4. Elementos visuais de Visual Law presentes (bloqueio ★4)
5. URL de jurisprudência não validada (bloqueio ★5)
6. Parágrafo com 8+ linhas (override v2.2.0 — gate D.1)
7. Marcador `[VERIFICAR]` em texto final referente a norma citada pela parte adversa (override v2.3.0 — gate E.7)

Esses são os "tiros de canhão" — qualquer um deles, sozinho, descaracteriza o parecer.
