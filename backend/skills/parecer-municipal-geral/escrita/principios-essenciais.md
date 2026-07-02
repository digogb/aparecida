# Princípios Essenciais da Prosa do Escritório

> 12 princípios estrelados que constituem o DNA redacional do escritório. Todo texto consultivo deve aplicar esses princípios. São cumulativos — nenhum substitui outro, todos coexistem em texto bem-construído. O ★12 é transversal: enquadra os demais, estabelecendo o critério de identidade autoral sob o qual eles devem ser aplicados.

---

## ★1 — Prosa fluida, parágrafos curtos, uma ideia por parágrafo

A prosa do escritório é fluida. Não é, contudo, prosa longa. Cada parágrafo carrega **uma única ideia**, expressa em duas a quatro frases, e termina antes de o leitor cansar.

**Por que isso importa:** parágrafos longos forçam o leitor a manter na memória curta múltiplos argumentos enquanto processa o atual. Parágrafos curtos *liberam* a memória curta a cada respiração, e o leitor avança sem fadiga.

**Exemplo do parecer-modelo v5:**

> A questão submetida à análise jurídica desta assessoria comporta resposta direta, embora exija fundamentação cuidadosa. O Decreto Municipal nº 11/2026 não tem aptidão jurídica, por si só, para reduzir o valor dos contratos administrativos vigentes.

Duas frases, uma ideia (a tese central), encerramento limpo. O leitor sabe imediatamente para onde o parecer vai.

> **⚠ GATE DE INTERVENÇÃO OBRIGATÓRIA (override v2.1.0 — 10/05/2026, propagado da `parecer-lei-14133` v2.5.0):**
> - **6 linhas:** sinal de alerta — revisar se há tese adicional embutida.
> - **7 linhas:** intervenção obrigatória — quebrar o parágrafo antes de prosseguir.
> - **8+ linhas:** reprovação automática no gate D.1 do checklist (Etapa 6.5), independentemente do score total.
>
> Esse gate é mais restritivo do que o limite anterior de "6+ frases por parágrafo". A experiência de calibragem do Dr. Ione (parecer-aditivo-creche/Potengi, 10/05/2026) revelou que parágrafos com 7-9 linhas já carregam teses múltiplas e comprometem a fluidez autoral, mesmo dentro do limite anterior. O auditor mecânico em `scripts/auditor_mecanico.py` mede objetivamente o cumprimento desta regra antes de qualquer entrega de `.docx`.
>
> **Procedimento quando detectado parágrafo de 7+ linhas:**
> 1. Identificar todas as teses embutidas no parágrafo longo.
> 2. Quebrar em tantos parágrafos quantas forem as teses.
> 3. Costurar a quebra com conectivo de transição (catálogo em `escrita/conectivos-arquiteturais.md`).
> 4. Nenhum parágrafo resultante deve passar de 6 linhas.

**Bloqueio associado:** B1 (prosa-bloco).

---

## ★2 — Costura argumentativa por conectivos integrados

Os movimentos do raciocínio são **costurados** por conectivos de transição que sinalizam ao leitor o caminho do argumento, sem precisar romper a prosa com títulos numerados.

A costura argumentativa exerce, *dentro do tecido textual*, a função que a subdivisão numerada exerceria *quebrando* o tecido. É o que permite que a fundamentação flua em prosa contínua mantendo clareza arquitetural.

**Exemplos de conectivos canônicos do escritório** (vocabulário detalhado em `conectivos-arquiteturais.md`):

- "Compreendida essa dualidade, é preciso examinar agora..."
- "O primeiro deles diz respeito a..."
- "Avançando, então, para o segundo pressuposto..."
- "Resta o terceiro pressuposto — e ele transcende..."
- "Pelo contrário. Existe rota legítima para..."

**Bloqueio associado:** B2 (subdivisão da fundamentação).

---

## ★3 — Paráfrase funcional após citação literal

Toda citação literal de dispositivo legal, súmula, acórdão ou doutrina vem **acompanhada de paráfrase funcional** — um parágrafo que traduz o dispositivo em linguagem operacional para o destinatário.

**Por que isso importa:** o gestor municipal lê o dispositivo legal e, frequentemente, não decodifica nele a regra prática que precisa observar. A paráfrase funcional faz essa ponte. O parecerista demonstra domínio do conteúdo, e ao mesmo tempo serve o leitor.

**Exemplo do parecer-modelo v5:**

> "Art. 124. Os contratos regidos por esta Lei poderão ser alterados, com as devidas justificativas, nos seguintes casos: I — unilateralmente pela Administração: a) quando houver modificação do projeto ou das especificações, para melhor adequação técnica a seus objetivos; b) quando for necessária a modificação do valor contratual em decorrência de acréscimo ou diminuição quantitativa de seu objeto..."
>
> A leitura do dispositivo, à primeira vista, pode sugerir que a Administração detém poder amplo para modificar seus contratos a qualquer tempo. Não é o que ocorre.
>
> Em outras palavras, o que o artigo autoriza é a alteração em duas hipóteses bem delimitadas — adequação técnica do projeto ou modificação quantitativa do objeto —, sempre acompanhada de justificativa devida e dentro dos limites do dispositivo seguinte.

A citação aparece em itálico recuado em bloco. Em seguida, a paráfrase funcional desmonta a má-leitura possível ("Não é o que ocorre") e refaz a leitura correta em linguagem operacional ("Em outras palavras").

**Bloqueio associado:** B3 (citação solta).

---

## ★4 — Exemplos concretos aterrando o conceito

Conceitos jurídicos abstratos são **aterrados** no universo operacional do destinatário por exemplos concretos.

**Por que isso importa:** "supressão quantitativa do objeto" é, para o gestor, expressão técnica vazia. "Menos refeições no contrato de fornecimento alimentar, menos quilômetros rodados no contrato de transporte escolar, menos horas de serviço no contrato de limpeza urbana" é a mesma coisa, mas o gestor *entende imediatamente*. O conceito ganha lastro operacional.

**Exemplo do parecer-modelo v5:**

> A supressão autorizada pelo art. 125 deve incidir sobre o quantitativo do objeto contratado. Para entender em termos concretos: menos refeições no contrato de fornecimento alimentar, menos quilômetros rodados no contrato de transporte escolar, menos horas de serviço no contrato de limpeza urbana.

O exemplo concreto é introduzido por marcador explícito ("Para entender em termos concretos") e usa três casos do universo do consulente municipal — fornecimento, transporte, limpeza. O gestor reconhece esses contratos no próprio município.

**Bloqueio associado:** nenhum específico — a ausência de exemplos concretos não é vício, mas perda de oportunidade.

---

## ★5 — Frase curta isolada para cravar conclusão

Em pontos decisivos do raciocínio, uma **frase curta isolada** (entre 4 e 12 palavras) finca a conclusão antes de avançar. A frase curta é estilística — quebra o ritmo da prosa fluida e força o leitor a parar e absorver.

**Por que isso importa:** prosa contínua bem-feita avança em ritmo confortável, e o leitor desliza. Em alguns momentos, contudo, é preciso *frear*. A frase curta isolada é o freio: o leitor encontra-a, registra a conclusão, e só então retoma o fluxo.

**Exemplos do parecer-modelo v5:**

> A prerrogativa existe. O que não existe é a discricionariedade ilimitada que o decreto-bloco pretende exercer.

> Existe, portanto, margem de manobra unilateral. Mas ela é estreita.

> Refazer contrato é tarefa de instrumento bilateral, não de decreto unilateral.

> Em vez de gerar economia, gera passivo.

Cada uma dessas frases curtas vem encerrar um movimento argumentativo. O leitor para, registra, segue. O ritmo da leitura ganha cadência.

**Bloqueio associado:** nenhum específico — frase curta usada em excesso vira maneirismo. O ideal é 3 a 5 frases curtas em parecer de média complexidade, distribuídas em pontos-chave.

---

## ★6 — Ementa em palavras-chave separadas por travessão — TODAS EM MAIÚSCULAS

A ementa do parecer é construída em **palavras-chave separadas por travessão (―)**, com 1 a 2 palavras por bloco, terminando com a conclusão. É escaneável em segundos, e funciona como índice mental do parecer.

**Por que isso importa:** o destinatário do parecer raramente lê a fundamentação inteira na primeira passagem. Ele varre a ementa, identifica os conceitos centrais e a conclusão, e depois mergulha. A ementa em palavras-chave acelera essa varredura inicial. Ementas em prosa corrida (parágrafo de nove linhas) atrasam.

> **⚠ OVERRIDE AUTORAL DO DR. IONE (override v2.1.0 — propagado da `parecer-lei-14133` v2.5.0):** todas as palavras-chave da ementa devem ser redigidas em **MAIÚSCULAS**, incluindo artigos, preposições, conjunções, **e referências normativas** (ex.: "LEI Nº 14.133/2021", "ART. 156", "§ 6º"). Exceção única: letras de alíneas entre aspas ('a', 'b', 'c') preservam minúsculas (citação legal). Os indicadores ordinais (`º`, `°`, `ª`) também preservam sua forma original. Esta instrução prevalece sobre o modelo canônico antigo.

**Modelo atualizado (v2.1.0):**

> **EMENTA:** DIREITO TRIBUTÁRIO ― DIREITO FINANCEIRO ― IPTU ― PROGRAMA DE REGULARIZAÇÃO FISCAL (REFIS) ― DECOMPOSIÇÃO EM TRÊS FIGURAS: PARCELAMENTO, ANISTIA E REMISSÃO PARCIAL ― RESERVA DE LEI ESPECÍFICA (CF ART. 150, § 6º) ― RENÚNCIA DE RECEITA (LRF ART. 14) ― ESTIMATIVA DE IMPACTO ORÇAMENTÁRIO ― ATENDIMENTO À LDO ― RISCO DE RESPONSABILIZAÇÃO DO GESTOR PERANTE O TCE-CE ― **PARECER FAVORÁVEL COM RESSALVAS.**

**Modelo INCORRETO (estilo antigo, abolido após calibragem do Dr. Ione):**

> **EMENTA:** Direito Tributário ― Direito Financeiro ― IPTU ― Programa de regularização fiscal (REFIS) ― [...] ― art. 14 da Lei nº 14.133/2021 ― [...] ― Parecer favorável com ressalvas.

**Características:**
- **Travessão usado:** ― (figure-dash, U+2015), nunca hífen (-) nem en-dash (–)
- **Capitalização:** TODAS AS PALAVRAS-CHAVE EM MAIÚSCULAS (override autoral)
- **Tamanho:** 8 a 14 blocos. Menos é seco demais; mais é prolixo.
- **Bloco final:** sempre a conclusão em maiúsculas ("PARECER FAVORÁVEL.", "PARECER DESFAVORÁVEL.", "PARECER FAVORÁVEL COM RESSALVAS.")
- **Ordem dos blocos:** do geral ao específico — ramo do direito → instituto → caso concreto → fundamentos → conclusão
- **Negrito:** ementa inteira em negrito, em bloco recuado

**Bloqueio associado:** B4 (ementa em prosa corrida) e novo gate IRR-1 (ementa em maiúsculas, medido pelo `auditor_mecanico.py`).

---

## ★7 — Advertência protetiva sóbria, sem caixa-alta dramática

O parecer consultivo do escritório alerta o gestor sobre risco jurídico em **prosa institucional sóbria**, jamais em CAIXA-ALTA dramática. A função protetiva — preservar o gestor da omissão informativa — é cumprida pelo *conteúdo* do alerta, não pelo *grafismo* dele.

**Por que isso importa:** alertar em CAIXA-ALTA tem três custos. Compromete a unidade tipográfica do documento. Sugere que o parecerista grita por não confiar no peso de seu próprio texto. Empobrece o ethos do parecer ao trocar dignidade institucional por exclamação retórica. Em peças contenciosas, a CAIXA-ALTA tem função (golpe argumentativo); em parecer consultivo, é incompatível com o registro.

**Exemplo do parecer-modelo v5:**

> Cumpre, ainda, advertir formalmente o gestor sobre o risco de responsabilização pessoal perante o controle externo na hipótese de manutenção do decreto na forma editada, com possível determinação de recomposição dos valores indevidamente reduzidos, acrescidos de juros e correção monetária.

A advertência está lá, é firme, é completa, protege juridicamente quem a redige. Mas o tom é institucional, não dramático.

**Bloqueio associado:** B5 (CAIXA-ALTA dramática).

---

## ★8 — Estrutura tripartite estrita: Relatório, Fundamentos, Conclusão

A estrutura formal do parecer é **inviolavelmente tripartite**: I — Relatório, II — Fundamentos, III — Conclusão. **A seção II não admite subdivisão numerada interna.** A organização arquitetural do raciocínio é feita inteiramente pela costura argumentativa (★2), não por títulos hierárquicos.

**Por que isso importa:** subdivisão numerada da fundamentação é convenção de lei (estrutura legislativa) ou de tese (estrutura acadêmica), e não pertence à tradição do parecer consultivo brasileiro. Quando aplicada ao parecer, fragmenta o raciocínio jurídico maduro — que é fluxo, não lista. Documentos altamente subdivididos têm cara de modelo preenchido por gerador automático. Documentos em prosa contínua têm cara de obra autoral.

**Aplicação concreta:** após `II — FUNDAMENTOS`, segue-se prosa contínua até `III — CONCLUSÃO`. Os movimentos argumentativos internos são sinalizados por parágrafos de transição, não por subtítulos numerados ou alfabéticos.

**Esta é a regra mais distintiva do estilo do escritório.** É também a mais difícil de manter para quem está acostumado com a fragmentação. Aplica-se sem exceção, mesmo em pareceres complexos.

**Bloqueio associado:** B2 (subdivisão da fundamentação).

---

## ★9 — Ritmo de leitura: alternância entre prosa fluida e frase de remate

A prosa do escritório não é monótona. Alterna entre **trechos de prosa fluida** (3 a 5 parágrafos curtos costurados por conectivos, desenvolvendo um movimento argumentativo) e **frases curtas de remate** (★5) que cravam a conclusão e dão respiro ao leitor.

A alternância produz ritmo. Sem ela, o texto vira ou monótono (só prosa contínua) ou martelado (só frases curtas, como em peça contenciosa). O equilíbrio caracteriza o registro consultivo expositivo do escritório.

**Cadência típica em fundamentação madura:**

```
[3 parágrafos curtos desenvolvem um movimento argumentativo]
[1 frase curta de remate]
[transição argumentativa]
[3-4 parágrafos curtos desenvolvem o próximo movimento]
[1 frase curta de remate]
[transição argumentativa]
...
```

O parecerista experiente sente o ritmo intuitivamente. O parecerista em formação aplica a cadência conscientemente, e ela vira intuitiva com o uso.

---

## ★10 — Hyperlinks de jurisprudência apenas com URL validada

Toda referência jurisprudencial vem com **URL validada por pesquisa-jurisprudencial**. Se a URL não foi validada, o texto traz marcador explícito `[a validar pela pesquisa-jurisprudencial]` no lugar do hyperlink.

**Por que isso importa:** URL inventada de jurisprudência é o vício mais letal em documento consultivo do escritório. Compromete a confiabilidade do parecer em cascata. Um cliente que descobre URL falsa em um parecer passa a desconfiar de todos os pareceres anteriores.

**Aplicação concreta:** sempre que houver referência jurisprudencial, esta skill invoca a skill `pesquisa-jurisprudencial` antes de finalizar. A URL volta validada e entra no texto. Se a invocação não puder ocorrer na rodada atual (rascunho inicial, prazo apertado), o texto traz o marcador de validação pendente, jamais URL inventada.

**Bloqueio associado:** B6 (URL inventada).

---

## ★11 — Bloco de assinaturas no padrão do escritório

Todo documento finalizado em .docx encerra com **bloco de assinaturas** no padrão estável do escritório:

```
                FRANCISCO IONE PEREIRA LIMA
                       OAB-CE nº 4.585

MATHEUS NOGUEIRA PEREIRA LIMA              FLÁVIO HENRIQUE LUNA SILVA
       OAB-CE nº 31.251                          OAB-CE nº 31.252

                  VALÉRIA MATIAS DE ALENCAR
                        OAB/CE 36.666
```

Atenção a duas particularidades:
- Os três primeiros nomes usam **OAB-CE com hífen** seguido de "nº" e ponto no número (4.585, 31.251, 31.252).
- Valéria usa **OAB/CE com barra**, sem "nº", com ponto no número (36.666).

A assimetria é histórica e deve ser preservada como marca identitária.

**Especificação técnica completa em `formatacao/bloco-assinaturas.md`.**

---

## ★12 — Identidade autoral — o parecer não deve parecer gerado por IA

O parecer do escritório precisa ser **identificável como obra autoral** pelo cliente recorrente, pelo controle externo e por quem o leia em sucessão de outros pareceres. Esta marca de autoria é o que diferencia um parecer do escritório de um texto consultivo qualquer gerado por modelo de linguagem sem direção editorial.

Este princípio é **transversal**: ele não substitui nenhum dos onze anteriores. Ele os enquadra, estabelecendo o **critério de avaliação** sob o qual os demais devem ser aplicados. A pergunta-mestra é simples: *"este parágrafo é marca do escritório, ou poderia ter saído de qualquer lugar?"* Se a resposta é a segunda, reescrever.

**Marcas positivas de autoria (presença obrigatória):**
- Estrutura tripartite estrita (★8) e abertura de parágrafo por conectivo arquitetural (★2).
- Citação literal de norma seguida de paráfrase funcional (★3), aterrada por exemplo concreto (★4).
- Frase curta isolada em pontos decisivos (★5), alternando ritmo (★9).
- Ementa em palavras-chave separadas por travessão, sempre em MAIÚSCULAS (★6).
- Vocabulário técnico vivo, sem arcaísmos vazios.

**Anti-marcas (presença = sinal de cara de IA, reescrever):**
- Subdivisão numerada da fundamentação em itens curtos — vício formal mais reconhecível de saída de IA bruta sem direção.
- Ementa em prosa narrativa de múltiplas linhas em vez de palavras-chave.
- Listas com marcadores (bullet points) dentro do corpo do parecer.
- Caixa-alta dramática ou negrito decorativo fora dos lugares prescritos.
- Elementos visuais (caixas ASCII, fluxogramas, tabelas) intercalados na fundamentação consultiva.
- Frases longas em cadeia, parágrafos densos, blocos compactos sem oxigênio.
- Advérbios e expressões decorativas que não fazem trabalho: "efetivamente", "certamente", "evidentemente", "destarte", "outrossim", "data venia" — todos vetados em conjunto.
- Repetição de fórmulas de transição sem justificativa argumentativa ("ademais", "outrossim", "destarte" usados como muletas em vez de articulação real).
- Saída em primeira pessoa do plural retórica ("podemos afirmar que...") quando o parecer deve enunciar em terceira pessoa institucional ou em primeira pessoa do singular consultiva.

**Aplicação prática durante a revisão:** ao reler o parecer pronto, percorrer parágrafo a parágrafo e, para cada um, fazer a pergunta-mestra. Quando o parágrafo passa no teste, deixa-se intacto. Quando falha, reescreve-se até passar. O texto final é aquele em que **todo parágrafo** é reconhecível como marca do escritório.

Este princípio dialoga diretamente com a **Dimensão F do checklist de auditoria** (`checklist-auditoria.md`), onde a aplicação operacional é detalhada item por item. O ★12 é o princípio; a Dimensão F é o método de verificação.

**Origem e racional:** este princípio foi incorporado ao rol em **v3.1.0** (Etapa 4 da migração da camada `parecer-lei-14133`, 15/05/2026). Adapta-se de um meta-princípio análogo da skill-irmã (★11 da `parecer-lei-14133` v3.2.1), aqui posicionado como ★12 para preservar a numeração v3.0.0 desta skill (caminho c da Etapa 4, deliberadamente escolhido pelo Dr. Matheus em 15/05/2026).

**Bloqueio associado:** B2 (subdivisão numerada na fundamentação) é o caso mais nítido em que a violação do ★12 fica visível. Mas o ★12 alcança muito além: o parecer pode passar pelos onze bloqueios universais e ainda assim falhar no ★12 se a prosa for genérica, decorativa ou estatisticamente plausível em vez de autoral.

---

## Síntese

Os 12 princípios são cumulativos. Texto consultivo bem-construído aplica todos eles simultaneamente, tendo o ★12 como princípio transversal que enquadra os demais. O parecer-modelo v5 (em `exemplos/parecer-modelo-v5.docx`) é o caso paradigmático que demonstra os onze primeiros em ação concreta — o ★12 se manifesta neste modelo como **o resultado** da aplicação coerente dos onze: o modelo não parece feito por IA porque aplica os onze sem deixar lacunas.

A próxima leitura é `bloqueios-obrigatorios.md` — o que jamais fazer.
