# Bloqueios Obrigatórios — Padrão Autoral do Escritório

**Versão 2.0** — alinhada à v5 do parecer-modelo.

Este arquivo carrega **sempre** durante a redação. São proibições absolutas que jamais podem ser violadas, sob nenhuma hipótese. Cada bloqueio aqui listado, se violado, descaracteriza o parecer como obra autoral do escritório e o aproxima do padrão genérico de IA.

---

## BLOQUEIO 1 — Subdivisão numerada da fundamentação

❌ **PROIBIDO:**

```
II — FUNDAMENTOS

1. Da impossibilidade de redução contratual unilateral por decreto
[texto]

2. Da prerrogativa unilateral e seus contornos
[texto]

3. O objeto da redução
[texto]
```

✅ **EXIGIDO:**

```
II — FUNDAMENTOS

[texto fluido, com parágrafos curtos costurados por conectivos de transição,
sem qualquer subdivisão interna]
```

**Justificativa:** subdivisão numerada é convenção legislativa ou acadêmica, não pertence à tradição forense consultiva. A organização do raciocínio se faz pela costura argumentativa em prosa, não por títulos numerados.

**Detecção automática:** se aparecer `subsecao(...)` ou título como "1. Da..." ou "2. Da..." dentro da fundamentação, REPROVAR e refazer.

---

## BLOQUEIO 2 — Ementa em prosa narrativa

❌ **PROIBIDO:**

```
EMENTA: Análise de viabilidade jurídica de Decreto Municipal que determinou
redução linear de 20% sobre o valor de todos os contratos administrativos
vigentes. Inviabilidade da medida por desrespeito aos limites legais da
prerrogativa de alteração unilateral. Necessidade de motivação individualizada.
Garantia constitucional do equilíbrio econômico-financeiro. Apresentação de
rota legítima em três etapas. Parecer desfavorável ao Decreto na forma
em que foi editado, com recomendação de procedimento individualizado.
```

✅ **EXIGIDO:**

```
EMENTA: Direito Administrativo ― Contratos administrativos ― Decreto Municipal
― Redução linear ― Inviabilidade jurídica ― Alteração unilateral ― Limites
do art. 125 da Lei 14.133/2021 ― Motivação individualizada ― Equilíbrio
econômico-financeiro ― Termo aditivo ― Rota legítima em três etapas ― Parecer
desfavorável.
```

**Justificativa:** ementa é cartão de visitas escaneável. Prosa narrativa de 9 linhas força releitura e tem cara de IA.

**Detecção automática:** se a ementa tem mais de 4 linhas em prosa contínua, REPROVAR.

---

## BLOQUEIO 3 — CAIXA ALTA dramática

❌ **PROIBIDO:**

```
ATENÇÃO: A MANUTENÇÃO DO DECRETO Nº 11/2026 EXPÕE A ADMINISTRAÇÃO MUNICIPAL
A APONTAMENTO PERANTE O TRIBUNAL DE CONTAS, COM RISCO DE RESPONSABILIZAÇÃO
PESSOAL E DETERMINAÇÃO DE RECOMPOSIÇÃO DOS VALORES.
```

✅ **EXIGIDO:**

```
Cumpre, ainda, advertir formalmente o gestor sobre o risco de
responsabilização pessoal perante o controle externo na hipótese de
manutenção do decreto na forma editada, com possível determinação de
recomposição dos valores indevidamente reduzidos, acrescidos de juros
e correção monetária.
```

**Justificativa:** caixa-alta dramática é gritar onde uma frase firme bastaria. Função protetiva é preservada em prosa institucional sóbria.

**Detecção automática:** se há frase com 10+ palavras em maiúsculas dentro do parecer, REPROVAR. Exceção: títulos de seções (I — RELATÓRIO, II — FUNDAMENTOS, III — CONCLUSÃO) e nomes em bloco de assinaturas.

---

## BLOQUEIO 4 — Elementos visuais de Visual Law

❌ **PROIBIDO** dentro da fundamentação ou da conclusão:

- Caixas ASCII tipo `┌─────┐ │ ... │ └─────┘`
- Fluxogramas
- Tabelas comparativas
- Mapas de fundamentação
- Quadros de enquadramento
- Roteiros operacionais em formato visual
- Linhas do tempo
- Matrizes de risco
- Diagramas de qualquer natureza

✅ **EXIGIDO:**

- Toda informação que se quer comunicar deve ser traduzida em **prosa fluida**
- Se há três pressupostos a examinar, eles aparecem em prosa contínua: "O primeiro deles diz respeito a... Avancemos para o segundo... Resta o terceiro..."
- Se há quatro etapas a executar, elas aparecem em prosa contínua: "Essa rota se desenvolve em três momentos sucessivos. O primeiro momento... O segundo momento... O terceiro momento..."

**Justificativa:** em parecer consultivo bem-construído, o texto bem feito *já é* visual law. A estrutura argumentativa em si é o mapa de fundamentação. A paráfrase funcional é o quadro de enquadramento. A sequência de recomendações é o roteiro operacional. Acrescentar caixa visual é redundância, não complementaridade.

**Exceção tolerada:** alíneas das recomendações (a, b, c, d) na seção III — CONCLUSÃO, em prosa, sem caixa visual.

**Detecção automática:** se aparecer `linhaVisual(...)` ou `┌`, `─`, `│`, `└`, `┐`, `┘`, `├`, `┤` dentro do conteúdo do parecer, REPROVAR.

---

## BLOQUEIO 5 — URLs inventadas

❌ **PROIBIDO:**

```
Conforme Acórdão TCU 1234/2025-Plenário (https://www.tcu.gov.br/acordao/1234/2025),
a alteração contratual unilateral exige motivação específica.
```
(quando a URL não foi validada por consulta real)

✅ **EXIGIDO:**

```
Essa diretriz vem sendo reafirmada pela jurisprudência do controle externo,
no sentido de que alterações contratuais não prescindem de motivação concreta
[Acórdão TCU a ser confirmado via `web_search` — URL a validar].
```

**Justificativa:** parecer com URL inventada compromete a credibilidade do escritório e do parecerista.

**Marcadores admissíveis quando ainda não houve validação:**
- `[URL_VALIDAR]`
- `[Acórdão TCU a indicar]`
- `[VERIFICAR]`

**Detecção automática:** todo hyperlink (texto entre parênteses começando com `http://` ou `https://`) deve ter passado por validação real (carga via `web_search` ou consulta a banco curado da skill). Se não passou, REPROVAR.

---

## BLOQUEIO 6 — Juridiquês arcaico decorativo

❌ **PROIBIDO** (vocabulário decorativo):

- destarte
- outrossim
- in casu
- data venia (quando puramente decorativo)
- a contrario sensu
- mutatis mutandis (quando puramente decorativo)
- ex vi
- ad argumentandum
- de cujus (fora do contexto sucessório onde realmente se aplica)
- ab initio
- conditio sine qua non

✅ **EXIGIDO** (vocabulário técnico vivo):

| Em vez de... | Usar... |
|---|---|
| destarte | assim, portanto, logo |
| outrossim | além disso, também, ademais |
| in casu | no caso, na hipótese, no presente caso |
| data venia | com o devido respeito, com a devida vênia (uma única vez se necessário) ou omitir |
| a contrario sensu | em sentido oposto, ao contrário |
| mutatis mutandis | com as adaptações necessárias |
| ex vi | nos termos de, na forma de |

**Justificativa:** linguagem fluida e prazerosa, técnica e elegante. Não pomposa. Não arcaica.

**Detecção automática:** se aparecer qualquer termo da lista vermelha, REPROVAR e substituir.

---

## BLOQUEIO 7 — Parágrafos longos com múltiplas teses

❌ **PROIBIDO:**

> O Decreto Municipal nº 11/2026 não tem aptidão jurídica para reduzir o valor dos contratos administrativos vigentes, porque o contrato administrativo é ato bilateral submetido a regime especial, e a Lei 14.133/2021 estabelece em seu art. 124 que a alteração unilateral só é admitida em hipóteses restritas, sendo certo, ademais, que o art. 125 fixa teto aritmético de 25% para acréscimos ou supressões, e que o art. 37, XXI, da Constituição assegura o equilíbrio econômico-financeiro do contratado, garantia que se desdobra em vários dispositivos infralegais e que torna a redução genérica e linear, como pretendida pelo decreto-bloco, juridicamente inviável e fonte segura de passivo futuro para a Administração Municipal.

✅ **EXIGIDO:**

> O Decreto Municipal nº 11/2026 não tem aptidão jurídica, por si só, para reduzir o valor dos contratos administrativos vigentes.
>
> A medida que se pretende implementar é, em tese, juridicamente possível. Depende, contudo, de procedimento próprio em cada contrato, e não pode ser imposta de forma genérica, automática e linear pela via do decreto.
>
> Para entender o porquê dessa impossibilidade, é necessário compreender a natureza dúplice do contrato administrativo.

**Justificativa:** uma ideia por parágrafo. Parágrafo de 12 linhas com 5 teses entrelaçadas obriga releitura e o gestor desiste antes de chegar à conclusão.

**Detecção automática:** se algum parágrafo passa de 7 linhas, REPROVAR e quebrar.

---

## BLOQUEIO 8 — Citação literal sem paráfrase funcional

❌ **PROIBIDO:**

```
Dispõe o art. 124, inciso I, da Lei 14.133/2021:

"Art. 124. Os contratos regidos por esta Lei poderão ser alterados, com as
devidas justificativas, nos seguintes casos: I — unilateralmente pela
Administração: a) quando houver modificação do projeto..."

Conforme se vê do dispositivo, a alteração unilateral é possível.
```

✅ **EXIGIDO:**

```
Dispõe o art. 124, inciso I, da Lei 14.133/2021:

"Art. 124. Os contratos regidos por esta Lei poderão ser alterados [...]"

A leitura do dispositivo, à primeira vista, pode sugerir que a Administração
detém poder amplo para modificar seus contratos a qualquer tempo. Não é o
que ocorre.

Em outras palavras, o que o artigo autoriza é a alteração em duas hipóteses
bem delimitadas — adequação técnica do projeto ou modificação quantitativa
do objeto —, sempre acompanhada de justificativa devida e dentro dos
limites do dispositivo seguinte.
```

**Justificativa:** a paráfrase NÃO repete o texto da lei. Ela traduz. Mostra ao gestor o que aquele dispositivo significa na rotina dele.

**Detecção automática:** se há citação literal em itálico recuado e o parágrafo seguinte é "Conforme se vê do dispositivo..." ou "Da leitura do artigo depreende-se..." sem desenvolvimento operacional, REPROVAR.

---

## BLOQUEIO 9 — Conceito abstrato sem exemplo concreto

❌ **PROIBIDO:**

> A supressão autorizada pelo art. 125 deve incidir sobre o quantitativo do objeto contratado, não sobre o valor unitário pactuado.

(parágrafo seco, encerra sem aterramento operacional)

✅ **EXIGIDO:**

> A supressão autorizada pelo art. 125 deve incidir sobre o quantitativo do objeto contratado. Para entender em termos concretos: menos refeições no contrato de fornecimento alimentar, menos quilômetros rodados no contrato de transporte escolar, menos horas de serviço no contrato de limpeza urbana.

**Justificativa:** conceitos abstratos sem aterramento operacional ficam etéreos. O leitor é gestor público — ele precisa visualizar a operação física.

**Detecção automática:** após enunciar conceito jurídico abstrato (alteração quantitativa, equilíbrio econômico-financeiro, motivação individualizada, etc.), o parágrafo deve ter ou exemplo concreto ou paráfrase funcional. Se não tem, REPROVAR.

---

## BLOQUEIO 10 — Bullet points dentro do corpo do parecer

❌ **PROIBIDO** dentro do corpo (relatório, fundamentos, conclusão):

```
São três os pressupostos da alteração unilateral:
- Pressuposto 1: incidência sobre quantitativo
- Pressuposto 2: motivação individualizada
- Pressuposto 3: forma de instrumentalização
```

✅ **EXIGIDO:**

```
Estreita porque submetida a três pressupostos cumulativos que decorrem da
própria sistemática da lei: o objeto da redução, a motivação individualizada
e a forma de instrumentalização. Examinemos, à luz do Decreto nº 11/2026,
cada um deles.

O primeiro deles diz respeito ao objeto da redução. [desenvolvimento]

Avancemos, então, para o segundo pressuposto — a exigência de motivação
individualizada. [desenvolvimento]

Resta o terceiro pressuposto. [desenvolvimento]
```

**Exceção tolerada:** alíneas das recomendações na conclusão (a, b, c, d), em prosa.

**Justificativa:** parecer consultivo é prosa contínua. Bullet points fragmentam a costura argumentativa e padronizam visualmente o documento.

**Detecção automática:** se há `\n- ` ou `\n• ` dentro do corpo (excluídas as alíneas da conclusão), REPROVAR.

---

## BLOQUEIO 11 — Repetição decorativa de advérbios

❌ **PROIBIDO** (uso decorativo, sem função):

- "efetivamente"
- "certamente"
- "evidentemente"
- "induvidosamente"
- "indubitavelmente"
- "inequivocamente"
- "manifestamente"
- "sobejamente"
- "amplamente"

✅ **PERMITIDO** com parcimônia (uso quando agrega significado):

- "efetivamente" (em contraste com o pretendido — "efetivamente reduzir, e não apenas pretender")
- "claramente" (quando a clareza é argumentativamente relevante)

**Justificativa:** advérbios decorativos não fortalecem o argumento — apenas inflam o texto. Argumento forte sustenta-se sozinho.

**Detecção automática:** se algum dos advérbios da lista vermelha aparece sem função argumentativa clara, REPROVAR e remover.

---

## FAMÍLIA DE BLOQUEIOS COMPLEMENTARES — PARECER JURÍDICO PRÉVIO DO ART. 53

Os três bloqueios a seguir **integram** o regime estilístico geral (11 bloqueios acima permanecem inalterados) e **acrescentam** restrições específicas para o subtipo "Parecer jurídico prévio do art. 53". Foram introduzidos na v2.6.0 do `references/fase-preparatoria.md` § 8 e estão aqui **replicados** para visibilidade na rotina de auto-auditoria — o Passo 6 da skill carrega este arquivo, e a existência dos bloqueios B-53.x apenas no reference temático fazia o auditor estilístico perdê-los quando o reference não era carregado por engano.

### BLOQUEIO B-53.1 — Omissão de vetor examinável do § 1º

❌ **PROIBIDO:** o parecer art. 53 deixa de examinar qualquer um dos cinco vetores do § 1º do art. 53 quando a documentação disponível **permite** o exame, sem qualquer menção à omissão.

Os cinco vetores são:

| Vetor | Conteúdo |
|---|---|
| I | Regularidade processual — formação do procedimento e fase preparatória |
| II | Modalidade, critério de julgamento e modo de disputa |
| III | Pressupostos materiais — regime jurídico aplicável (licitação ou contratação direta com inciso específico) |
| IV | Habilitação — exigências do edital quanto a habilitação jurídica, técnica, fiscal-social-trabalhista, econômico-financeira |
| V | Minuta do edital, anexos e contrato — cláusulas necessárias, reajuste, sanções, foro |

✅ **PERMITIDO:** examinar todos os vetores acessíveis. Quando um vetor **não puder** ser examinado por insuficiência documental (TR ausente, planilha orçamentária não anexada), a circunstância **deve** ser mencionada em prosa fluida, no ponto da costura argumentativa em que o vetor seria tratado, **sem destaque tipográfico** — sem negrito, sem caixa alta, sem isolamento em parágrafo dramático.

**Detecção automática:** se o parecer art. 53 trata explicitamente do edital mas omite qualquer dos cinco vetores **sem mencionar a razão da omissão**, REPROVAR.

**Justificativa:** a integralidade da análise é o que distingue o parecer art. 53 de um parecer parcial sobre edital. O § 1º **lista** os cinco vetores como conteúdo mínimo do controle prévio — omissão silenciosa enfraquece o parecer perante o TCE-CE em eventual fiscalização posterior.

---

### BLOQUEIO B-53.2 — Silêncio sobre vício evidente

❌ **PROIBIDO:** o parecer emite conclusão favorável (com ou sem ressalvas) sem registrar vício **identificável** na documentação examinada — atestado acima do limite da Súmula TCU 263, visita técnica obrigatória sem fundamentação no ETP, cláusula contratual essencial ausente (reajuste, sanções, foro), cumulação indevida na habilitação econômico-financeira, ETP genérico copia-cola, pesquisa de preços com fontes únicas ou desatualizadas.

✅ **PERMITIDO:** parecer **favorável com ressalvas** que registra o vício explicitamente e recomenda saneamento prévio à publicação. Parecer **desfavorável** que sustenta a impossibilidade de prosseguir sem retomar a fase preparatória.

**Detecção automática:** se a documentação anexa contém vício do catálogo de armadilhas recorrentes (`references/armadilhas-tce-ce.md`, §§ 1 a 5) e o parecer **não** o registra, REPROVAR.

**Justificativa:** o parecer favorável sem ressalvas que omite vício identificável funciona como **aval do parecerista ao vício**. Em fiscalização posterior do TCE-CE, o parecer é exibido como prova da adesão técnica ao ato — fragiliza o parecerista (art. 184 da Lei 14.133/2021 c/c art. 28 da LINDB — erro grosseiro presumível) e o gestor (que se valeu da chancela). A ressalva explícita é o **mecanismo defensivo do parecerista**.

---

### BLOQUEIO B-53.3 — Aplicação do regime simplificado dos §§ 4º e 5º

❌ **PROIBIDO:** adotar o regime simplificado do art. 53, §§ 4º e 5º (parecer dispensado em contratações repetitivas com minuta-padrão previamente aprovada), independentemente das circunstâncias do caso.

✅ **PERMITIDO:** **única hipótese** — emissão de parecer completo, em todos os casos, com análise dos cinco vetores do § 1º.

**Detecção automática:** se o parecer menciona "minuta-padrão", "dispensa de parecer prévio", "regime simplificado", "§ 4º do art. 53" ou "§ 5º do art. 53" como **fundamento para reduzir a profundidade da análise**, REPROVAR.

**Justificativa (decisão institucional do escritório, registrada em 10/05/2026):** o regime simplificado, embora autorizado em lei, eleva a exposição do parecerista (art. 184) quando a minuta-padrão não foi previamente chancelada por procuradoria municipal ou consultoria jurídica geral. Em municípios cearenses pequenos e médios (Araripe, Salitre, Potengi, Saboeiro), a existência de minuta-padrão formalmente aprovada por ato administrativo é rara — e a aplicação do regime simplificado em ambiente sem essa base prévia expõe o parecerista a responsabilização. Por opção do escritório, **a skill mantém sempre análise completa**.

---

## RESUMO — 11 BLOQUEIOS ABSOLUTOS

| # | Bloqueio | Detecção |
|---|---|---|
| 1 | Subdivisão numerada da fundamentação | Títulos "1. Da...", "2. Da..." dentro da seção II |
| 2 | Ementa em prosa narrativa | Mais de 4 linhas em prosa contínua |
| 3 | CAIXA ALTA dramática | Frase com 10+ palavras em maiúsculas |
| 4 | Elementos visuais de Visual Law | Caracteres `┌ ─ │ └ ┐ ┘ ├ ┤` |
| 5 | URLs inventadas | Hyperlinks não validados |
| 6 | Juridiquês arcaico | "destarte", "outrossim", "in casu" decorativo |
| 7 | Parágrafos longos | Acima de 7 linhas |
| 8 | Citação sem paráfrase | Itálico recuado seguido só de "Conforme se vê..." |
| 9 | Conceito sem exemplo concreto | Abstração jurídica sem aterramento |
| 10 | Bullet points no corpo | `\n- ` ou `\n• ` fora das alíneas da conclusão |
| 11 | Advérbios decorativos | "efetivamente", "evidentemente", etc. |

Se algum desses 11 bloqueios é violado, o parecer **NÃO PASSA NA AUDITORIA** e deve ser reescrito antes da entrega.

**Família de bloqueios complementares B-53.x — específica do subtipo "Parecer jurídico prévio do art. 53":** os bloqueios **B-53.1** (omissão de vetor examinável), **B-53.2** (silêncio sobre vício evidente) e **B-53.3** (aplicação do regime simplificado dos §§ 4º e 5º) **acrescem** este catálogo quando o subtipo for o controle prévio do art. 53. Violação de qualquer um deles também reprova o parecer. Detalhamento técnico no `references/fase-preparatoria.md` § 8 e na seção "Família de Bloqueios Complementares" deste arquivo.
