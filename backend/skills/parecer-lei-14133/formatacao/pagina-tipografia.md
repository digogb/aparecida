# Página e Tipografia

> Especificação técnica de configuração de página, fontes e espaçamento do padrão .docx do escritório.

---

## 1. Configuração da Página

### Tamanho do papel
- **Padrão:** A4 (210 mm × 297 mm)
- **DXA:** 11906 × 16838

### Orientação
- **Padrão:** Retrato (portrait)

### Margens

| Margem | Centímetros | DXA |
|--------|-------------|-----|
| Superior (top)     | 2,5 cm | 1417 |
| Direita (right)    | 3,0 cm | 1701 |
| Inferior (bottom)  | 3,0 cm | 1700 |
| Esquerda (left)    | 3,0 cm | 1701 |

### Posição de cabeçalho e rodapé
- **Cabeçalho (header):** 1,25 cm do topo da página = 708 DXA
- **Rodapé (footer):** 1,0 cm do fundo da página = 567 DXA

---

## 2. Fontes

### Corpo do documento
- **Família:** Consolas
- **Estilo:** regular
- **Tamanho:** 12 pt
- **DXA do tamanho:** 24 (unidade interna do Word usa half-points)

### Cabeçalho institucional
- **Família:** Garamond
- **Estilo:** Small Caps (variante caixa-alta pequena)
- **Tamanho:** 12 pt
- **DXA do tamanho:** 24
- **Negrito:** linha 2 (nome do titular) em negrito; linha 1 sem negrito

### Rodapé
- **Família:** Consolas
- **Estilo:** regular
- **Tamanho:** 9 pt (necessário para caber endereço completo na linha)
- **DXA do tamanho:** 18

### Hyperlinks
- **Cor:** azul padrão Word, código hex `0563C1`
- **Sublinhado:** sim (single underline)
- **Família:** mesma do corpo (Consolas)

---

## 3. Espaçamento e Recuos

### Recuo de primeira linha (corpo do documento)
- **Centímetros:** 4,0 cm
- **DXA:** 2268

Este é o **recuo padrão da prosa do escritório** (decisão do Dr. Ione, refletida no `gerador_docx.py` — constante `RECUO_PRIMEIRA_LINHA`). Aplica-se a todos os parágrafos do corpo, incluindo a seção de Relatório, Fundamentos e Conclusão.

### Recuo de bloco (citações literais)
- **Centímetros:** 3,0 cm (recuo esquerdo)
- **DXA:** 1701
- **Recuo de primeira linha:** zero (a citação não tem recuo adicional)

A citação literal vem em bloco recuado à esquerda em 3,0 cm, sem recuo de primeira linha — o texto inicia na margem do recuo de bloco.

### Recuo da ementa
- **Centímetros:** 3,0 cm (recuo esquerdo)
- **DXA:** 1701
- A ementa é tratada como bloco recuado, com o rótulo "EMENTA:" em negrito iniciando o bloco.

### Espaçamento entre linhas
- **Múltiplo:** 1,5 (auto)
- **DXA:** 360
- **lineRule:** auto

### Espaçamento antes do parágrafo
- **Pontos:** 12 pt antes de cada parágrafo
- **DXA:** 240 (12 × 20)

### Espaçamento depois do parágrafo
- **Pontos:** 0 pt
- O espaçamento é aplicado apenas **antes** do parágrafo. Espaçamento posterior fica em zero para evitar acumulação dupla.

---

## 4. Alinhamento

### Padrão do corpo
- **Alinhamento:** Justificado (both)

Toda a prosa do corpo é justificada, com hifenização desativada (configuração padrão do Word brasileiro).

### Títulos de seção (I — RELATÓRIO, II — FUNDAMENTOS, III — CONCLUSÃO)
- **Alinhamento:** Esquerda (left)
- **Negrito:** Sim
- **Caixa-alta:** Sim, conforme grafia (I, II, III em algarismo romano + travessão + nome em maiúsculas)

### Cabeçalho institucional
- **Linha 1 ("Advocacia & Assessoria"):** Centralizado
- **Linha 2 ("Dr. Francisco Ione Pereira Lima" + número de página):** Tab stops (centro = nome, direita = número)

### Rodapé
- **Alinhamento:** Esquerda

---

## 5. Tabela-resumo dos parâmetros

```
PÁGINA
  Papel:                  A4 (11906 × 16838 DXA)
  Margem superior:        2,5 cm  (1417 DXA)
  Margem direita:         3,0 cm  (1701 DXA)
  Margem inferior:        3,0 cm  (1700 DXA)
  Margem esquerda:        3,0 cm  (1701 DXA)
  Posição do cabeçalho:   1,25 cm (708 DXA)
  Posição do rodapé:      1,0 cm  (567 DXA)

FONTES
  Corpo:                  Consolas 12pt (size 24 em DXA half-points)
  Cabeçalho:              Garamond Small Caps 12pt
  Rodapé:                 Consolas 9pt (size 18)
  Hyperlinks:             cor 0563C1, sublinhado

PARÁGRAFOS DO CORPO
  Recuo 1ª linha:         4,0 cm  (2268 DXA)
  Espaçamento antes:      12pt    (240 DXA)
  Espaçamento depois:     0
  Linha:                  1,5 auto (360 DXA)
  Alinhamento:            Justificado

CITAÇÕES E EMENTA (BLOCO)
  Recuo esquerdo:         3,0 cm  (1701 DXA)
  Recuo 1ª linha:         0
  Demais parâmetros:      idênticos ao corpo
```

---

## 6. Notas técnicas

### Sobre a unidade DXA
DXA (em inglês "twentieths of a point") é a unidade interna usada pelo XML do Word. Equivalências:
- 1 ponto (pt) = 20 DXA
- 1 centímetro (cm) = 567 DXA (aproximação)
- 1 polegada = 1440 DXA

Bibliotecas como `docx` (Node.js) e `python-docx` (Python) aceitam DXA diretamente em vários parâmetros.

### Sobre o tamanho de fonte
No XML interno do Word, o tamanho da fonte é expresso em "half-points" (meios-pontos). Por isso:
- Corpo 12pt = `size: 24`
- Rodapé 9pt = `size: 18`

A biblioteca `docx` do Node.js aceita `size: 24` como 12pt automaticamente.

### Sobre a fonte Garamond Small Caps
"Small Caps" é uma variante tipográfica disponível na maioria dos sistemas operacionais modernos para a família Garamond. Caso o destinatário não tenha a fonte instalada, o Word substitui por aproximação com Times New Roman Small Caps. A substituição é tolerável.

### Sobre a fonte Consolas
Consolas é fonte monoespaçada da Microsoft, instalada por padrão em sistemas Windows e disponível para macOS/Linux via instalação. **A escolha da Consolas é deliberada** — a monospaçada confere ao parecer ar técnico e identitário do escritório, distinto do parecer em Times New Roman / Arial usual.

---

## Síntese

A especificação completa de página, fontes e espaçamento permite que qualquer skill consumidora gere arquivos .docx no padrão exato do escritório, com plena compatibilidade entre Word, LibreOffice e Google Docs.

Próxima leitura: `estrutura-formal.md` — formatação dos blocos do documento (ementa, seções, citações).
