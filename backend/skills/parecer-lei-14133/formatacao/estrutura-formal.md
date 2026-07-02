# Estrutura Formal do Documento

> Especificação da estrutura visual do documento .docx do escritório. Posicionamento de cada elemento — título, órgão consulente, ementa, seções, citações, conclusão, bloco de assinaturas.

---

## 1. Ordem dos elementos

A ordem canônica do documento é:

```
1.  Título: PARECER JURÍDICO (centralizado, negrito)
2.  Órgão Consulente (alinhado à esquerda, com rótulo em negrito)
3.  EMENTA (bloco recuado, em palavras-chave separadas por travessão)
4.  I — RELATÓRIO (título, depois prosa)
5.  II — FUNDAMENTOS (título, depois prosa contínua)
6.  III — CONCLUSÃO (título, depois prosa + recomendações + alerta + fechamento)
7.  Local e data
8.  Bloco de assinaturas
```

Cada elemento é detalhado nas seções seguintes.

---

## 2. Título do documento

```
                          PARECER JURÍDICO
```

- **Texto:** "PARECER JURÍDICO" (em maiúsculas, sem variação para "Parecer Consultivo" ou similar)
- **Alinhamento:** Centralizado
- **Negrito:** Sim
- **Fonte:** Consolas 12pt (mesma do corpo)
- **Espaçamento antes:** 12pt
- **Espaçamento depois:** 12pt

Não confundir com:
- Pareceres em consultas internas → mesmo título
- Pareceres em representação a TCE/TCU → mesmo título
- Notas Técnicas → título próprio "NOTA TÉCNICA"

---

## 3. Órgão Consulente

```
Órgão Consulente: Procuradoria-Geral do Município de Araripe/CE
```

- **Rótulo "Órgão Consulente:"** em negrito
- **Nome do órgão** em texto regular
- **Alinhamento:** Esquerda
- **Sem recuo de primeira linha**
- **Espaçamento antes:** 12pt
- **Espaçamento depois:** 12pt

Pode ser substituído por:
- "Consulente:" (forma curta, em parecer interno)
- "Solicitado por:" (em pareceres provocados por particular ou ente externo)

---

## 4. Ementa

A ementa é o **cartão de visitas escaneável** do parecer. Construída em palavras-chave separadas por travessão `―` (figure dash, U+2015).

### Formato visual

```
            EMENTA: DIREITO ADMINISTRATIVO ― CONTRATOS ADMINISTRATIVOS
            ― DECRETO MUNICIPAL ― REDUÇÃO LINEAR ― INVIABILIDADE
            JURÍDICA ― ALTERAÇÃO UNILATERAL ― LIMITES DO art. 125 DA
            Lei nº 14.133/2021 ― MOTIVAÇÃO INDIVIDUALIZADA ― EQUILÍBRIO
            ECONÔMICO-FINANCEIRO ― TERMO ADITIVO ― ROTA LEGÍTIMA EM
            TRÊS ETAPAS ― PARECER DESFAVORÁVEL.
```

> **⚠ Override autoral do Dr. Ione (09/05/2026):** todas as palavras-chave em MAIÚSCULAS. Exceção: referências normativas ("Lei nº 14.133/2021", "art. 64") preservam grafia legal canônica.

### Especificação técnica

- **Recuo esquerdo:** 3,0 cm (1701 DXA) — formato bloco
- **Recuo de primeira linha:** zero
- **Alinhamento:** Justificado
- **Negrito:** TODA a ementa em negrito (rótulo + corpo)
- **Espaçamento antes:** 12pt
- **Espaçamento depois:** 12pt

### Regras de redação da ementa

- O **rótulo "EMENTA:"** abre o bloco, em maiúsculas, seguido de espaço.
- **Todas as palavras-chave em MAIÚSCULAS** — override autoral do Dr. Ione (09/05/2026). Inclui artigos, preposições e conjunções dentro dos blocos.
- Exceção: referências normativas preservam grafia legal canônica ("Lei nº 14.133/2021", "art. 64", "§ 1º").
- Cada bloco de palavras-chave tem **1 a 2 palavras** (ocasionalmente 3, se for termo composto inseparável).
- Os blocos são separados pelo travessão `―` (U+2015), com espaço antes e depois.
- O **primeiro bloco** ancora a área do direito (DIREITO ADMINISTRATIVO, DIREITO TRIBUTÁRIO, DIREITO ELEITORAL, etc.).
- Os **blocos intermediários** percorrem os conceitos centrais do parecer em ordem que reproduz, em síntese, a estrutura argumentativa.
- O **último bloco** é a conclusão em maiúsculas — **PARECER FAVORÁVEL.** / **PARECER DESFAVORÁVEL.** / **PARECER FAVORÁVEL COM RESSALVAS.**
- A ementa termina com **ponto final**.

### Bloqueio: ementa em prosa corrida

❌ Vedado: ementa redigida como parágrafo de prosa corrida com sintaxe completa. Detalhes em `escrita/bloqueios-obrigatorios.md` — bloqueio B4.

---

## 5. Títulos das seções

```
I — RELATÓRIO
```

- **Texto:** algarismo romano + travessão `—` (em dash, U+2014, **não confundir** com o figure dash da ementa) + nome em maiúsculas
- **Alinhamento:** Esquerda
- **Negrito:** Sim
- **Fonte:** Consolas 12pt
- **Espaçamento antes:** 12pt (separação do bloco anterior)
- **Espaçamento depois:** 12pt (separação do parágrafo seguinte)
- **Sem recuo de primeira linha**

Os três títulos canônicos são:

```
I — RELATÓRIO
II — FUNDAMENTOS
III — CONCLUSÃO
```

**Observação importante sobre os travessões:**
- Em **títulos de seção:** travessão é em dash `—` (U+2014). Convenção tradicional do português brasileiro forense.
- Em **ementa:** travessão é figure dash `―` (U+2015). Convenção autoral do escritório para distinguir o uso ementário.

---

## 6. Corpo das seções

### Relatório (seção I)

Dois a quatro parágrafos curtos descrevendo a consulta, os documentos que a acompanham e a finalidade da medida questionada. Encerra com fórmula consagrada:

> É o breve relatório. Passa-se à fundamentação.

### Fundamentos (seção II)

**Prosa contínua, sem subdivisão.** Detalhamento do estilo redacional em `escrita/principios-essenciais.md` e do vocabulário de transição em `escrita/conectivos-arquiteturais.md`.

### Conclusão (seção III)

A primeira frase carrega a posição do parecer com indicação clara em maiúsculas + negrito da palavra-chave (**FAVORÁVEL**, **DESFAVORÁVEL** ou **FAVORÁVEL COM RESSALVAS**). Em seguida, recomendações alfabéticas, eventual advertência protetiva, e fechamento.

---

## 7. Citações literais

### Formato visual

A citação literal de dispositivo legal, súmula, acórdão ou doutrina vem em **itálico, recuada em bloco**, com aspas iniciais e finais.

```
Dispõe o art. 124, inciso I, da Lei 14.133/2021:

            "Art. 124. Os contratos regidos por esta Lei poderão ser
            alterados, com as devidas justificativas, nos seguintes
            casos: I — unilateralmente pela Administração: a) quando
            houver modificação do projeto ou das especificações [...]"

A leitura do dispositivo, à primeira vista, [...]
```

### Especificação técnica

- **Recuo esquerdo:** 3,0 cm (1701 DXA)
- **Recuo de primeira linha:** zero
- **Alinhamento:** Justificado
- **Itálico:** Sim, em todo o conteúdo da citação
- **Aspas:** Curvas tipográficas (`"` e `"`), não aspas retas (`"`)
- **Espaçamento antes:** 12pt
- **Espaçamento depois:** 0pt (porque o parágrafo seguinte — paráfrase funcional — terá seu próprio "antes" de 12pt)

### Regra estilística obrigatória

Toda citação literal deve ser **seguida imediatamente** por parágrafo de paráfrase funcional. Detalhes em `escrita/principios-essenciais.md` — princípio ★3 — e em `escrita/bloqueios-obrigatorios.md` — bloqueio B3.

---

## 8. Citações livres (sem aspas, sem recuo)

Citações livres — referências a doutrina ou jurisprudência *integradas à prosa*, sem aspas e sem recuo de bloco — seguem a formatação padrão do corpo, com identificação clara da fonte na frase de abertura:

> Como ensina Marçal Justen Filho, a alteração unilateral do contrato administrativo pressupõe motivação concreta, vinculada às particularidades de cada avença.

A obra do autor pode ser citada em hyperlink ou em nota de rodapé, conforme protocolo do escritório (preferencialmente hyperlink azul `0563C1`).

---

## 9. Recomendações alfabéticas (na conclusão)

```
Recomenda-se à Administração Municipal:

a) a revogação ou substituição do Decreto nº 11/2026 por ato normativo
que se limite a regular a atividade administrativa interna [...];

b) a adoção do procedimento individualizado em três etapas — mapeamento
dos contratos vigentes, análise individualizada e formalização [...];

c) a observância, em cada termo aditivo, dos limites do art. 125 [...]
```

### Especificação

- **Frase de abertura** ("Recomenda-se à [destinatário]:") como parágrafo independente, com recuo de primeira linha 3,0 cm como qualquer parágrafo.
- **Cada item alfabético** como parágrafo independente, **sem recuo de primeira linha** (a letra "a)", "b)", "c)" abre na margem do recuo padrão).
- **Espaçamento antes** de cada item: 12pt (padrão).
- **Texto de cada item** em prosa fluida, com 1 a 3 frases. Não usar tópicos enxutos.
- **Pontuação:** ponto-e-vírgula entre os itens, ponto final no último.

---

## 10. Advertência protetiva (na conclusão)

Após as recomendações alfabéticas, antes do fechamento, vem o parágrafo de advertência protetiva:

> Cumpre, ainda, advertir formalmente o gestor sobre o risco de responsabilização pessoal perante o controle externo na hipótese de manutenção do decreto na forma editada, com possível determinação de recomposição dos valores indevidamente reduzidos, acrescidos de juros e correção monetária.

### Especificação

- **Formatação:** parágrafo padrão do corpo (Consolas 12pt, recuo 3,0 cm primeira linha, justificado, 1,5 entrelinhas, 12pt antes).
- **Sem negrito, sem itálico, sem caixa-alta.**
- **Marcadores típicos de abertura** detalhados em `escrita/conectivos-arquiteturais.md` — seção 5.

---

## 11. Fechamento canônico

```
É o parecer.

Este parecer expressa opinião técnica e não substitui a decisão final
do gestor, que possui discricionariedade administrativa.

Fortaleza/CE, [dia] de [mês] de [ano].
```

### Especificação

- **Frase 1** ("É o parecer..."): parágrafo padrão.
- **Frase 2** (cláusula de discricionariedade): parágrafo padrão.
- **Local e data**: parágrafo independente, alinhado à esquerda, **sem recuo de primeira linha**, espaçamento antes de 24pt (deslocamento maior para separar do fechamento).

---

## 12. Bloco de assinaturas

Detalhamento completo em `bloco-assinaturas.md`. A formatação técnica é específica e merece arquivo próprio.

---

## Síntese

Os elementos estruturais visuais do documento seguem ordem fixa, posicionamento estável e formatação técnica precisa. Combinados com a tipografia (especificada em `pagina-tipografia.md`) e o cabeçalho/rodapé institucional (em `cabecalho-rodape.md`), produzem o **layout identitário do escritório**.

Próxima leitura: `cabecalho-rodape.md` — timbre institucional padrão.
