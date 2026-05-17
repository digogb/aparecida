# Módulo `escrita/` — Camada Estilística da Skill `parecer-lei-14133`

**Versão 2.0** — alinhada à v5 do parecer-modelo de validação (Decreto Municipal 11/2026 — Araripe/CE), maio de 2026.

## Propósito

Este módulo internaliza o padrão autoral de redação dos pareceres consultivos do escritório Dr. Francisco Ione Pereira Lima — Advocacia & Assessoria. É a fonte canônica de:

- Princípios de redação (★1 a ★11)
- Bloqueios absolutos (proibições estilísticas)
- Checklist de auditoria (31 itens em 6 dimensões para subtipos comuns; 34 itens em 7 dimensões para o subtipo "Parecer jurídico prévio do art. 53", introduzido em v2.6.0 da skill)
- Exemplos de passagem (10 trechos canônicos da v5)

## Quando carrega

| Arquivo | Quando carrega | Função |
|---|---|---|
| `principios-essenciais.md` | **Sempre** durante a redação (Passo 5) | Define os 11 princípios estrelados do estilo do escritório |
| `bloqueios-obrigatorios.md` | **Sempre** durante a redação (Passo 5) | Lista as 11 proibições absolutas que descaracterizam o parecer |
| `checklist-auditoria.md` | Na auto-auditoria (Passo 6) | Permite calcular nota de aprovação (31 itens para subtipos comuns; 34 para parecer art. 53) |
| `exemplos-de-passagem.md` | **Sob demanda** (Passo 5) | Referência de como o escritório constrói cada movimento |

## Histórico de evolução

### v1.0 — original (até abril/2026)

7 princípios estrelados focados em peças contenciosas. Privilegiava "tese na primeira linha" e "argumento mais forte primeiro" — adequado a contestações, recursos e alegações finais.

### v2.0 — maio/2026 — calibragem com o parecer-modelo

Reescrita completa após 5 rodadas de calibragem do parecer-modelo de validação:

- **v1 → v2:** adoção de prosa mais fluida, com menos rigidez de "tese na primeira linha" (que é regra de peça, não de parecer)
- **v2 → v3:** ementa migrou de prosa narrativa para palavras-chave separadas por travessão; adoção de paráfrase funcional após citação literal
- **v3 → v4:** abolição dos elementos visuais de Visual Law (caixas ASCII, mapas, quadros, roteiros) e da CAIXA ALTA dramática
- **v4 → v5:** abolição da subdivisão numerada da fundamentação (II.1, II.2, II.3) — estrutura tripartite estrita

A versão 2.0 contém os 11 princípios estabilizados na v5 e os 11 bloqueios obrigatórios derivados das anti-marcas observadas durante a calibragem.

## Como interpretar este módulo

Os princípios são **prescritivos**: orientam como redigir.
Os bloqueios são **proibitivos**: definem o que jamais pode aparecer.
O checklist é **avaliativo**: calcula nota de aprovação.
Os exemplos são **referenciais**: mostram o registro autoral do escritório.

A leitura sugerida é, na ordem:

1. **principios-essenciais.md** — para entender o estilo
2. **bloqueios-obrigatorios.md** — para saber o que jamais fazer
3. **exemplos-de-passagem.md** — para ver o estilo aplicado
4. **checklist-auditoria.md** — para auditar o produto final

## Skills que herdam este módulo

Este módulo é a fonte canônica usada inicialmente pela `parecer-lei-14133`. As demais skills produtoras de parecer do escritório (`parecer-administrativo-geral`, `parecer-tributario-financeiro`, `parecer-auditoria-licitacoes`, `parecer-terceiro-setor`) devem **espelhar** o conteúdo deste módulo, com adaptações terminológicas próprias da matéria.

A atualização de qualquer princípio aqui implica revisar as cinco skills.
