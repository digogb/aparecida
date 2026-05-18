# Cabeçalho e Rodapé

> ## ⚠ ATENÇÃO — DOCUMENTO DE REFERÊNCIA HISTÓRICA (a partir da v3.2.0)
>
> A partir da v3.2.0, a fonte canônica única de geração do `.docx` é
> **`scripts/gerador_docx.py`**. Este arquivo passa a ser **documentação
> histórica** da especificação textual do cabeçalho e do rodapé, mantido
> para fins de auditoria e referência.
>
> **NÃO use este arquivo como base para improvisar código de geração `.docx`.**
> O Passo 7 do SKILL.md proíbe expressamente a improvisação — toda geração
> deve passar pela chamada `gerador_docx.gerar_parecer(minuta, output_path)`.
>
> Se algo precisar mudar na formatação do cabeçalho ou do rodapé, a alteração
> é feita **no `gerador_docx.py`** e este arquivo é atualizado em seguida
> para manter a documentação coerente.

---

## 1. Cabeçalho institucional — especificação canônica (v3.2.0)

### Layout visual

```
                            Advocacia & Assessoria

                  Dr. Francisco Ione Pereira Lima

                                                                            1
```

Três linhas no cabeçalho:

- Linha 1: nome do escritório
- Linha 2: nome do titular
- Linha 3: número da página, à direita

A separação da numeração em um parágrafo próprio (em vez de tabs no mesmo
parágrafo do nome) elimina o conflito histórico CENTER + RIGHT que causou
bugs em todas as iterações anteriores (v2.4.0 a v3.1.0).

### Estrutura técnica (replicada no `gerador_docx.py`)

#### Linha 1

- Texto: `"Advocacia & Assessoria"`
- Alinhamento: `align=CENTER`
- Fonte: Garamond 12pt
- Estilo: Small Caps, sem negrito
- Tab stops: nenhum

#### Linha 2

- Texto: `"Dr. Francisco Ione Pereira Lima"`
- Alinhamento: `align=CENTER` puro
- Fonte: Garamond 12pt
- Estilo: Small Caps, **negrito**
- Tab stops: nenhum
- **Sem caracteres tab no run** — o nome ocupa o parágrafo inteiro

#### Linha 3

- Texto: campo PAGE dinâmico (não literal `"1"`)
- Alinhamento: `align=RIGHT` puro
- Fonte: Garamond 12pt
- Estilo: negrito, sem Small Caps
- Tab stops: nenhum
- Estrutura XML do campo:

  ```xml
  <w:r>
    <w:fldChar w:fldCharType="begin"/>
    <w:instrText xml:space="preserve"> PAGE </w:instrText>
    <w:fldChar w:fldCharType="end"/>
  </w:r>
  ```

---

## 2. Rodapé institucional — especificação canônica (v3.2.0)

### Layout visual

```
Rua Gen. Caiado de Castro 462, Luciano Cavalcante, Fortaleza-Ce, Fone (85)
3021-7701/ (85) 99981-4392/ (85) 99223-6716. Email: dr.ione@uol.com.br.
Site: http://www.ioneadvogados.com.br
```

### Estrutura técnica

- Conteúdo:
  `Rua Gen. Caiado de Castro 462, Luciano Cavalcante, Fortaleza-Ce, Fone (85) 3021-7701/ (85) 99981-4392/ (85) 99223-6716. Email: dr.ione@uol.com.br. Site: http://www.ioneadvogados.com.br`
- Fonte: Consolas 10pt (alterado de 9pt na v3.2.0)
- Alinhamento: `align=LEFT`
- Espaçamento antes: 0
- Espaçamento depois: 0
- Espaçamento entre linhas: simples

### Por que Consolas 10pt no rodapé

Consolidação determinada pelo Dr. Matheus em 14/05/2026 com base no comando
padrão do escritório: *"Rodapé com endereço completo, telefones e e-mail
em fonte 10 pt"*. Versões anteriores usavam 9pt; v3.2.0 unifica em 10pt.

---

## 3. Por que esta especificação deixou de ser fonte de execução

A história operacional desta especificação:

- **v1.x a v3.1.0:** especificação textual em prosa + pseudocódigo em Python
  e Node.js. A instância do Claude lia o `.md` no Passo 7 e improvisava o
  código de geração `.docx`.
- **Bugs documentados:** múltiplas iterações apresentaram falhas de cabeçalho
  — tab stops CENTER+RIGHT combinados produziam o nome do titular grudado
  no número da página, ou o número sumindo, dependendo da execução.
- **Diagnóstico (v3.2.0):** improvisação por especificação textual é
  intrinsecamente instável. Mesmo com especificação correta, a tradução
  para código `python-docx` varia entre execuções.
- **Solução (v3.2.0):** mover o código de geração para um arquivo Python
  determinístico, com constantes no topo, sem decisão da instância. Este
  arquivo `.md` passa a ser documentação histórica.

---

## 4. Atualização do conteúdo do rodapé

Em caso de mudança de endereço, telefone, email ou site, o conteúdo do
rodapé deve ser atualizado **simultaneamente** em:

- `scripts/gerador_docx.py` (constante `TEXTO_RODAPE` — **fonte canônica**)
- Este arquivo (`formatacao/cabecalho-rodape.md`) para manter a documentação coerente
- Templates internos do escritório (Word/Google Docs)

A constante `TEXTO_RODAPE` no `gerador_docx.py` é a única que efetivamente
afeta o `.docx` gerado. As demais atualizações são documentais.

---

## Síntese

O cabeçalho e o rodapé compõem o **timbre institucional** do escritório,
agora produzido programaticamente pelo `gerador_docx.py`. A v3.2.0 encerra
o ciclo de calibragens da família "cabeçalho" iniciado na v2.4.0.

Próxima leitura: `bloco-assinaturas.md` — também documentação histórica
desde a v3.2.0.
