# Arquitetura de Prompts — Pipeline de Pareceres

## Visão Geral

O prompt monolítico v4.0 (~16k tokens) foi decomposto em **4 prompts especializados**
que correspondem às etapas do pipeline de automação:

```
Email recebido
    │
    ▼
┌─────────────────────────┐
│ P1: CLASSIFICAÇÃO       │  ~1.5k tokens  ←  rápido, barato
│ Extrai dados + classifica│
│ Retorna: JSON estruturado│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ P2: GERAÇÃO DO PARECER  │  ~8k tokens    ←  principal
│ Recebe JSON do P1 +     │
│ documentos originais    │
│ Retorna: XML estruturado │
└────────┬────────────────┘
         │
         ▼
   TipTap Editor (advogado revisa)
         │
         ▼  (se devolvido com observações)
┌─────────────────────────┐
│ P3: REVISÃO             │  ~3k tokens    ←  focado
│ Recebe parecer atual +  │
│ observações do advogado │
│ Retorna: seções revisadas│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ P4: TEMPLATE HTML       │  0 tokens (código puro)
│ Renderiza o parecer     │
│ Determinístico, sem IA  │
└─────────────────────────┘
```

## Decisões de Design

### 1. Anti-Alucinação Honesta

O prompt original exigia "validação em fonte oficial" — impossível sem tool use.
A nova abordagem:

- **Legislação federal consolidada** (CF/88, Lei 14.133, LRF, etc.): o modelo pode citar
  com confiança alta, pois são textos estáveis amplamente presentes no treinamento.
- **Jurisprudência**: o modelo cita apenas precedentes "landmark" que tem certeza
  (SV 13, Tema 1000, etc.). Para os demais, usa formulações genéricas:
  "O STF tem entendimento consolidado no sentido de que..." sem fabricar números.
- **Campo `verificar_citacoes`**: toda citação específica (número de acórdão, relator,
  data) é listada no output para checagem humana pelo advogado.
- **Nenhuma citação doutrinária fabricada**: o modelo pode mencionar correntes
  doutrinárias sem atribuir a autores específicos, a menos que tenha certeza absoluta.

### 2. Output Estruturado (XML delimitado)

Em vez de HTML monolítico, o P2 retorna XML com seções parseáveis:

```xml
<parecer>
  <metadata>{ JSON com dados do caso }</metadata>
  <ementa>Texto livre da ementa</ementa>
  <relatorio>Texto livre do relatório</relatorio>
  <fundamentos>Texto livre dos fundamentos (com sub-seções)</fundamentos>
  <conclusao>Texto livre da conclusão</conclusao>
  <citacoes_verificar>[ array JSON de citações para checagem ]</citacoes_verificar>
</parecer>
```

**Vantagens:**
- TipTap carrega cada seção como bloco editável independente
- "Retorno à IA" pode enviar só a seção que precisa de ajuste
- `citacoes_verificar` alimenta um checklist na UI do advogado
- HTML é renderizado deterministicamente pelo template (P4)

### 3. Redução de Tokens

| Componente removido/trimado          | Economia estimada |
|--------------------------------------|-------------------|
| Credenciais acadêmicas fictícias     | ~800 tokens       |
| Estrutura duplicada (4 cópias → 1)   | ~2000 tokens      |
| Protocolos de interação (UI resolve) | ~1500 tokens      |
| Exemplos completos (few-shot sob demanda) | ~2500 tokens |
| Fontes oficiais (modelo não acessa)  | ~300 tokens       |
| **Total economizado**               | **~7100 tokens**  |

### 4. Few-Shot sob Demanda

Os 3 exemplos de parecer do prompt original (~2500 tokens) foram movidos para
um arquivo separado (`examples_fewshot.md`). O sistema pode injetá-los
condicionalmente:

- **Primeira geração para um novo município**: inclui 1 exemplo relevante
- **Gerações subsequentes**: omite (o modelo já "calibrou" o estilo)
- **Área específica (licitações)**: injeta exemplo de licitação em vez do genérico

## Arquivos

| Arquivo                        | Uso no pipeline                    |
|--------------------------------|-------------------------------------|
| `p1_classification.txt`       | System prompt para etapa de classificação |
| `p2_parecer_generation.txt`   | System prompt para geração do parecer     |
| `p3_parecer_revision.txt`     | System prompt para revisão com observações|
| `p4_html_template.html`       | Template HTML (código, sem IA)           |
| `examples_fewshot.md`         | Exemplos para injeção condicional        |
| `ARCHITECTURE.md`             | Este arquivo                             |

## Integração no Código

```python
# Exemplo de uso no FastAPI

async def generate_parecer(classification: dict, documents: list[str]):
    system_prompt = load_prompt("p2_parecer_generation.txt")
    
    # Injetar few-shot se necessário
    if is_first_for_municipality(classification["municipio"]):
        examples = load_prompt("examples_fewshot.md")
        system_prompt += f"\n\n# EXEMPLO DE REFERÊNCIA\n{examples}"
    
    user_message = build_user_message(classification, documents)
    
    response = await anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    # Parse XML estruturado
    parecer = parse_parecer_xml(response.content[0].text)
    
    # Extrair citações para verificação
    citacoes = json.loads(parecer["citacoes_verificar"])
    
    return parecer, citacoes
```

## Prompt Version Tracking

Cada parecer salvo no banco deve incluir `prompt_version` para garantir
consistência quando o advogado devolver com observações:

```sql
ALTER TABLE pareceres ADD COLUMN prompt_version VARCHAR(10) DEFAULT '4.1';
```

A revisão (P3) recebe o `prompt_version` original e mantém o mesmo estilo.
