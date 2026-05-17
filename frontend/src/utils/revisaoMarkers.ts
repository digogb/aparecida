/**
 * Detecção de marcadores de revisão humana no conteúdo TipTap.
 *
 * Marcadores reconhecidos (idênticos aos do backend `docx_generator.py`):
 * - `[REVISAR — TEXTO]`   — vertente licitação (IRR-4 da skill parecer-lei-14133)
 * - `[!VERIFICAR: TEXTO !]` — vertente municipal-geral (Regra ZT-5)
 *
 * No DOCX exportado, ambos são renderizados em vermelho institucional
 * RGB(192,0,0), negrito. Esta utilidade conta quantos existem antes do
 * download para emitir aviso ao usuário.
 */

const PADRAO_MARCADOR =
  /\[REVISAR\s*[\-–—]\s*[^\]]+\]|\[!VERIFICAR:[^!]+!\]/gi

type TipTapNode = {
  type?: string
  text?: string
  content?: TipTapNode[]
}

function extractPlainText(node: TipTapNode | null | undefined): string {
  if (!node) return ''
  if (node.type === 'text') return node.text ?? ''
  if (!node.content) return ''
  return node.content.map(extractPlainText).join('\n')
}

/**
 * Conta o número de marcadores de revisão humana no conteúdo TipTap.
 *
 * Aceita tanto `{ type: 'doc', content: [...] }` quanto qualquer nó parcial.
 * Retorna 0 quando o conteúdo é null/undefined/string vazia.
 */
export function contarMarcadoresRevisao(tiptap: unknown): number {
  if (!tiptap || typeof tiptap !== 'object') return 0
  const texto = extractPlainText(tiptap as TipTapNode)
  if (!texto) return 0
  const matches = texto.match(PADRAO_MARCADOR)
  return matches ? matches.length : 0
}

export type MarcadorRevisao = {
  /** "revisar" (vertente licitação) ou "verificar" (vertente municipal-geral) */
  tipo: 'revisar' | 'verificar'
  /** Texto completo do marcador, incluindo colchetes */
  textoCompleto: string
  /** Conteúdo interno (sem prefixo "REVISAR —" ou "!VERIFICAR:" e sem colchetes) */
  conteudo: string
  /** Seção do parecer onde o marcador aparece (EMENTA, RELATÓRIO, FUNDAMENTOS, CONCLUSÃO ou null) */
  secao: string | null
  /** Índice 0-based de ocorrência no documento (estável para chaveação React) */
  indice: number
}

const PADRAO_REVISAR = /\[REVISAR\s*[\-–—]\s*([^\]]+)\]/i
const PADRAO_VERIFICAR = /\[!VERIFICAR:([^!]+)!\]/i

function parseMarcador(textoCompleto: string, indice: number, secao: string | null): MarcadorRevisao {
  const mRevisar = textoCompleto.match(PADRAO_REVISAR)
  if (mRevisar) {
    return {
      tipo: 'revisar',
      textoCompleto,
      conteudo: mRevisar[1].trim(),
      secao,
      indice,
    }
  }
  const mVerificar = textoCompleto.match(PADRAO_VERIFICAR)
  if (mVerificar) {
    return {
      tipo: 'verificar',
      textoCompleto,
      conteudo: mVerificar[1].trim(),
      secao,
      indice,
    }
  }
  return {
    tipo: 'revisar',
    textoCompleto,
    conteudo: textoCompleto,
    secao,
    indice,
  }
}

/**
 * Extrai todos os marcadores de revisão humana do TipTap JSON,
 * preservando a seção do parecer (EMENTA / RELATÓRIO / FUNDAMENTOS / CONCLUSÃO)
 * onde cada marcador aparece.
 */
export function extrairMarcadoresRevisao(tiptap: unknown): MarcadorRevisao[] {
  if (!tiptap || typeof tiptap !== 'object') return []
  const doc = tiptap as TipTapNode
  if (!doc.content) return []

  const marcadores: MarcadorRevisao[] = []
  let secaoAtual: string | null = null
  let indice = 0

  for (const node of doc.content) {
    if (node.type === 'heading') {
      const titulo = extractPlainText(node).trim()
      // Mapeia "I — RELATÓRIO" para "RELATÓRIO" para chave estável
      const upper = titulo.toUpperCase()
      if (upper.includes('EMENTA')) secaoAtual = 'EMENTA'
      else if (upper.includes('RELATÓRIO')) secaoAtual = 'RELATÓRIO'
      else if (upper.includes('FUNDAMENTOS')) secaoAtual = 'FUNDAMENTOS'
      else if (upper.includes('CONCLUSÃO')) secaoAtual = 'CONCLUSÃO'
      continue
    }
    const texto = extractPlainText(node)
    const matches = texto.match(PADRAO_MARCADOR)
    if (!matches) continue
    for (const match of matches) {
      marcadores.push(parseMarcador(match, indice, secaoAtual))
      indice += 1
    }
  }
  return marcadores
}
