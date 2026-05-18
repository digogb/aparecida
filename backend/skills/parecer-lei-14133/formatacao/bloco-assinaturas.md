# Bloco de Assinaturas

> ## ⚠ ATENÇÃO — DOCUMENTO DE REFERÊNCIA HISTÓRICA (a partir da v3.2.0)
>
> A partir da v3.2.0, a fonte canônica única de geração do `.docx` é
> **`scripts/gerador_docx.py`**. Este arquivo passa a ser **documentação
> histórica** da especificação textual do bloco de assinaturas, mantido
> para fins de auditoria e referência.
>
> **NÃO use este arquivo como base para improvisar código de geração `.docx`.**
> O Passo 7 do SKILL.md proíbe expressamente a improvisação — toda geração
> deve passar pela chamada `gerador_docx.gerar_parecer(minuta, output_path)`.
>
> Se algo precisar mudar no bloco de assinaturas (entrada/saída de advogado,
> alteração de OAB), a alteração é feita **no `gerador_docx.py`** (constantes
> `ASSINATURA_IONE`, `ASSINATURA_MATHEUS`, `ASSINATURA_FLAVIO`, `ASSINATURA_VALERIA`)
> e este arquivo é atualizado em seguida para manter a documentação coerente.

---

## 1. Layout visual canônico (v3.2.0)

Calibrado byte por byte contra o arquivo de referência `assinaturas.txt`
do escritório (fornecido pelo Dr. Matheus em 14/05/2026):

```
                         FRANCISCO IONE PEREIRA LIMA
                         OAB-CE nº 4.585

MATHEUS NOGUEIRA PEREIRA LIMA             FLÁVIO HENRIQUE LUNA SILVA
OAB-CE nº 31.251                          OAB-CE nº 31.252

                          VALÉRIA MATIAS DE ALENCAR
                          OAB/CE nº 36.666
```

**Princípio estrutural:** alinhamento mecânico por espaços manuais em
fonte monoespaçada (Consolas), em vez de tab stops ou alinhamento
centralizado calculado pelo Word. O alinhamento mecânico é à prova de
variações de renderização de fonte entre versões do Word.

---

## 2. Estrutura técnica (replicada no `gerador_docx.py`)

### Fonte universal do bloco

- **Família:** Consolas
- **Tamanho:** 10pt (não 12pt!)
- **Estilo:** negrito em todos os textos
- **Por que 10pt:** a linha dupla Matheus + Flávio tem 68 caracteres totais.
  Em Consolas 10pt cada caractere ocupa ~0,21 cm, totalizando 14,28 cm —
  cabe nos 15 cm de largura útil (margens 3+3 cm em A4 de 21 cm). Em 12pt
  extrapolaria a largura útil e o nome direito quebraria para a linha de baixo
  (bug histórico documentado nas v3.0.0 a v3.1.0).

### Bloco 1 — Francisco Ione Pereira Lima (titular)

Dois parágrafos, ambos com `align=LEFT` e 25 espaços de avanço:

```
[25 espaços]FRANCISCO IONE PEREIRA LIMA
[25 espaços]OAB-CE nº 4.585
```

A escolha de `align=LEFT` (não `align=CENTER`) com o mesmo número de
espaços para nome e OAB garante que o **início do nome** e o **início da
OAB** fiquem mecanicamente alinhados na mesma coluna — independentemente
de cálculos de centralização do Word, que variam com a fonte renderizada.

### Bloco 2 — Matheus Nogueira Pereira Lima + Flávio Henrique Luna Silva

Dois parágrafos com estrutura idêntica, ambos com `align=LEFT`, sem avanço
inicial. Cada parágrafo contém três runs:

**Parágrafo dos nomes:**

```
Run 1: "MATHEUS NOGUEIRA PEREIRA LIMA"  (29 chars)
Run 2: "             "  (13 espaços)
Run 3: "FLÁVIO HENRIQUE LUNA SILVA"  (26 chars)
```

Total: 68 caracteres em uma única linha física.

**Parágrafo das OABs:**

```
Run 1: "OAB-CE nº 31.251"  (16 chars)
Run 2: "                          "  (26 espaços)
Run 3: "OAB-CE nº 31.252"  (16 chars)
```

Total: 58 caracteres em uma única linha física.

### Bloco 3 — Valéria Matias de Alencar (associada)

Dois parágrafos, ambos com `align=LEFT` e 26 espaços de avanço:

```
[26 espaços]VALÉRIA MATIAS DE ALENCAR
[26 espaços]OAB/CE nº 36.666
```

Mesma lógica do bloco 1, com 26 espaços (vs 25 para Ione) — calibração
extraída diretamente do `assinaturas.txt`.

---

## 3. Assimetria das identificações OAB

A assimetria abaixo é **histórica e proposital**, preservada como marca
identitária do escritório:

| Advogado(a) | Identificação OAB | Característica |
|-------------|-------------------|----------------|
| Francisco Ione Pereira Lima | `OAB-CE nº 4.585` | Hífen + `nº` + ponto |
| Matheus Nogueira Pereira Lima | `OAB-CE nº 31.251` | Hífen + `nº` + ponto |
| Flávio Henrique Luna Silva | `OAB-CE nº 31.252` | Hífen + `nº` + ponto |
| Valéria Matias de Alencar | `OAB/CE nº 36.666` | **Barra** + `nº` + ponto |

A única assimetria preservada é a sigla: `OAB-CE` (hífen) para Ione,
Matheus e Flávio; `OAB/CE` (barra) para Valéria. Todas as quatro entradas
têm `nº`.

---

## 4. Espaçamento entre blocos

Entre cada bloco (Ione → Matheus+Flávio → Valéria) há **um parágrafo vazio**
de separação, em Consolas 12pt (não 10pt — o vazio segue a fonte do corpo).

---

## 5. Por que esta especificação deixou de ser fonte de execução

A história operacional dos bugs corrigidos pela v3.2.0:

- **v2.x a v3.0.0:** especificação descrevia tab stops RIGHT/LEFT em
  posições diversas. A instância improvisava código com tabelas, ora tab
  stops, ora alignment CENTER — produzindo:
  - `MATHEUS...LIMAFLÁVIO...` (nomes concatenados, sem tab entre runs)
  - OABs jogadas à margem direita (tab stop RIGHT)
  - FLÁVIO/SILVA quebrando linha (tab stop LEFT a 7,5 cm + fonte 12pt)
- **Diagnóstico:** improvisação textual em pseudocódigo não traduz de forma
  estável para `python-docx`. Tab stops e alinhamento centralizado se
  comportam diferente conforme a versão do Word, a fonte instalada e a
  largura física da renderização.
- **Solução (v3.2.0):** abandonar tab stops e alinhamento centralizado para
  o bloco de assinaturas. Usar **espaços manuais em fonte monoespaçada**
  com `align=LEFT` — estrutura matematicamente determinística, calibrada
  byte por byte contra o `assinaturas.txt` do escritório.

---

## 6. Variantes de uso

### Documento assinado apenas pelo titular

Bloco 1 apenas (Ione). Sem blocos 2 e 3.

### Documento assinado apenas pelos associados

Blocos 2 e 3 (Matheus + Flávio + Valéria), sem o bloco 1.

### Adaptações de quantidade

A função `_adicionar_bloco_assinaturas(doc)` no `gerador_docx.py` chama
sequencialmente as três sub-funções. Variantes podem ser produzidas
omitindo ou reordenando as chamadas — a alteração se faz no gerador, não
nesta documentação.

---

## 7. Atualização de OABs

Em caso de:

- **Entrada de novo advogado:** atualizar `gerador_docx.py` com nova
  constante `ASSINATURA_NOVO` e ajustar `_adicionar_bloco_assinaturas`.
- **Alteração de número de OAB:** alterar a constante correspondente no
  `gerador_docx.py`.
- **Saída de advogado:** remover constante e chamada no `gerador_docx.py`.

A atualização deve ser feita simultaneamente em:

- `scripts/gerador_docx.py` — **fonte canônica única**
- Este arquivo (`formatacao/bloco-assinaturas.md`) para documentação
- Templates internos do escritório

---

## Síntese

O bloco de assinaturas é a **assinatura visual do escritório** no
documento, agora produzido programaticamente pelo `gerador_docx.py` em
estrutura matematicamente determinística (espaços manuais em fonte
monoespaçada).

A v3.2.0 encerra o ciclo de calibragens da família "bloco de assinaturas"
iniciado na v2.1.0. Pareceres futuros sairão com formatação byte-idêntica
entre execuções.

Este é o último arquivo do módulo `formatacao/`. Combinado com:

- `pagina-tipografia.md` (configuração base)
- `estrutura-formal.md` (estrutura visual)
- `cabecalho-rodape.md` (timbre institucional)

...completa a especificação técnica `.docx` do escritório como
**documentação histórica**. A execução efetiva acontece no
`scripts/gerador_docx.py`.
