import { useCallback, useEffect, useRef, useState } from 'react'
import { useEditor as useTipTapEditor } from '@tiptap/react'
import type { Node as PmNode } from '@tiptap/pm/model'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import Typography from '@tiptap/extension-typography'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import AIContent from '../components/editor/extensions/AIContent'
import CorrectionMark from '../components/editor/extensions/CorrectionMark'
import SearchHighlight from '../components/editor/extensions/SearchHighlight'
import DiffHighlight from '../components/editor/extensions/DiffHighlight'
import RevisaoMarkerHighlight from '../components/editor/extensions/RevisaoMarkerHighlight'
import ParagraphIndent from '../components/editor/extensions/ParagraphIndent'
import EmentaHighlight from '../components/editor/extensions/EmentaHighlight'
import SignatureBlock from '../components/editor/extensions/SignatureBlock'
import AnnotationHighlight, { type AnnotationDeco } from '../components/editor/extensions/AnnotationHighlight'
import AsteriskCleanup from '../components/editor/extensions/AsteriskCleanup'
import type { DiffAnnotation } from '../components/editor/extensions/DiffHighlight'
import {
  saveVersionSnapshot,
  previewCorrection,
  applyCorrection,
  approveParecer,
  exportParecer,
  generateParecer,
  createPeerReview,
  fetchPeerReviews,
  respondToPeerReview,
} from '../services/editorApi'
import type { CorrectionPreview, PeerReviewCreatePayload, PeerReviewRespondPayload } from '../services/editorApi'
import { fetchAnnotations, createAnnotation, deleteAnnotation } from '../services/annotationApi'
import type { Annotation, ParecerRequestDetail, ParecerVersion, PeerReviewListItem } from '../types/parecer'
import { contarMarcadoresRevisao, extrairMarcadoresRevisao, type MarcadorRevisao } from '../utils/revisaoMarkers'

// getMonth() → 0–11
const MESES_EXTENSO = [
  'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
  'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
]

function getCurrentUserId(): string {
  try {
    const token = localStorage.getItem('token')
    if (!token) return ''
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub ?? ''
  } catch {
    return ''
  }
}

/** Extract all text fragments marked with correctionMark from the editor */
function getMarkedFragments(editor: ReturnType<typeof useTipTapEditor>): string[] {
  if (!editor) return []
  const fragments: string[] = []
  let current = ''
  let lastEnd = -1
  const { doc } = editor.state
  doc.descendants((node, pos) => {
    if (!node.isText) {
      // Non-text node breaks adjacency — flush current fragment
      if (current) { fragments.push(current); current = '' }
      lastEnd = -1
      return
    }
    const hasMark = node.marks.some((m) => m.type.name === 'correctionMark')
    if (hasMark && node.text) {
      if (pos === lastEnd) {
        // Adjacent marked text node — merge into current fragment
        current += node.text
      } else {
        // New fragment — flush previous if any
        if (current) fragments.push(current)
        current = node.text
      }
      lastEnd = pos + node.nodeSize
    } else {
      // Unmarked text node breaks adjacency
      if (current) { fragments.push(current); current = '' }
      lastEnd = -1
    }
  })
  if (current) fragments.push(current)
  return fragments
}

/**
 * Aplica o correctionMark aos trechos informados, casando de forma ROBUSTA:
 * texto normalizado (aspas/traços/espaços/caixa) e atravessando nós/parágrafos —
 * igual ao replaceTextInEditor. Antes o match era `indexOf` exato dentro de um
 * único text node, então trechos com formatação, quebra ou pequena edição não
 * eram realçados e a observação "sumia" (auditoria — Erro 5).
 */
function applyCorrectionsMarks(editor: ReturnType<typeof useTipTapEditor>, trechos: string[]) {
  if (!editor || trechos.length === 0) return
  const markType = editor.schema.marks.correctionMark
  if (!markType) return

  const { normText, normToPos } = buildNormalizedDocMap(editor)
  const { tr } = editor.state
  let applied = false

  for (const trecho of trechos) {
    const target = normalizeForMatch(trecho)
    if (!target) continue
    let idx = normText.indexOf(target)
    while (idx !== -1) {
      const from = normToPos[idx]
      const to = normToPos[idx + target.length - 1] + 1
      if (from < to) {
        tr.addMark(from, to, markType.create())
        applied = true
      }
      idx = normText.indexOf(target, idx + target.length)
    }
  }

  if (applied) editor.view.dispatch(tr)
}

/** Remove all correctionMark marks from the entire document */
function clearAllCorrectionMarks(editor: ReturnType<typeof useTipTapEditor>) {
  if (!editor) return
  const { doc } = editor.state
  const { tr } = editor.state
  doc.descendants((node, pos) => {
    if (!node.isText) return
    const mark = node.marks.find((m) => m.type.name === 'correctionMark')
    if (mark) {
      tr.removeMark(pos, pos + node.nodeSize, mark.type)
    }
  })
  editor.view.dispatch(tr)
}

/**
 * Normalize text for fuzzy matching: collapse whitespace, unify smart quotes
 * and dashes, and lowercase. Typography extension converts these on the fly,
 * so the saved "original" string may differ from the rendered doc text.
 */
function normalizeForMatch(s: string): string {
  return s
    .replace(/[\u201C\u201D\u201E\u201F\u2033]/g, '"')
    .replace(/[\u2018\u2019\u201A\u201B\u2032]/g, "'")
    .replace(/[\u2013\u2014\u2212]/g, '-')
    .replace(/\u00A0/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
}

/**
 * Constr\u00F3i o texto do documento normalizado (mesma normaliza\u00E7\u00E3o de normalizeForMatch,
 * atravessando text nodes e tratando fronteira de bloco como espa\u00E7o) + um mapa
 * `normToPos` de cada \u00EDndice-normalizado para a posi\u00E7\u00E3o ProseMirror real da fonte.
 * Base compartilhada do matching robusto (marca\u00E7\u00E3o e substitui\u00E7\u00E3o).
 */
function buildNormalizedDocMap(
  editor: ReturnType<typeof useTipTapEditor>,
): { normText: string; normToPos: number[] } {
  const { doc } = editor!.state
  let normText = ''
  const normToPos: number[] = []
  let lastPos: number | null = null
  let prevWasSpace = true // leading trim

  const pushChar = (c: string, pos: number) => {
    const isSpace = /\s/.test(c) || c === '\u00A0'
    if (isSpace) {
      if (!prevWasSpace) {
        normText += ' '
        normToPos.push(pos)
        prevWasSpace = true
      }
      return
    }
    const ch = c
      .replace(/[\u201C\u201D\u201E\u201F\u2033]/g, '"')
      .replace(/[\u2018\u2019\u201A\u201B\u2032]/g, "'")
      .replace(/[\u2013\u2014\u2212]/g, '-')
      .toLowerCase()
    normText += ch
    normToPos.push(pos)
    prevWasSpace = false
  }

  doc.descendants((node, pos) => {
    if (node.isText && node.text) {
      for (let i = 0; i < node.text.length; i++) {
        pushChar(node.text[i], pos + i)
      }
      lastPos = pos + node.text.length
    } else if (node.isBlock && lastPos !== null) {
      if (!prevWasSpace) {
        normText += ' '
        normToPos.push(lastPos)
        prevWasSpace = true
      }
    }
  })

  while (normText.endsWith(' ')) {
    normText = normText.slice(0, -1)
    normToPos.pop()
  }

  return { normText, normToPos }
}

/**
 * Find `originalText` in the editor (across text nodes, tolerating whitespace,
 * smart-quote/dash, and case differences) and replace with `newText`.
 * Returns true if the replacement happened.
 */
function replaceTextInEditor(
  editor: ReturnType<typeof useTipTapEditor>,
  originalText: string,
  newText: string,
): boolean {
  if (!editor || !originalText) return false

  const target = normalizeForMatch(originalText)
  if (!target) return false

  const { normText, normToPos } = buildNormalizedDocMap(editor)

  const matchIdx = normText.indexOf(target)
  if (matchIdx === -1) return false

  const from = normToPos[matchIdx]
  const lastCharNormIdx = matchIdx + target.length - 1
  // Walk back from the last normalized char to find the last real text
  // character's position; end = that pos + 1.
  let to = normToPos[lastCharNormIdx] + 1
  // Safety: ensure from < to
  if (from >= to) return false

  editor
    .chain()
    .focus()
    .insertContentAt({ from, to }, newText)
    .run()

  return true
}

// ── Diff utilities ────────────────────────────────────────────────────────────────────────────

type DiffToken = { type: 'same' | 'add' | 'remove'; value: string }

// Strip leading/trailing punctuation before comparing — avoids marking
// "interno." ≠ "interno" when a word is inserted before the sentence-final period.
const normTok = (s: string) =>
  s.replace(/^[.,;:!?()[\]{}'"""''«»—–…]+|[.,;:!?()[\]{}'"""''«»—–…]+$/g, '').toLowerCase()

function diffWords(a: string[], b: string[]): DiffToken[] {
  const m = a.length, n = b.length
  const al = a.map(normTok)
  const bl = b.map(normTok)
  const lcs = Array.from({ length: m + 1 }, () => new Int32Array(n + 1))
  for (let i = m - 1; i >= 0; i--)
    for (let j = n - 1; j >= 0; j--)
      lcs[i][j] = al[i] === bl[j] ? lcs[i+1][j+1] + 1 : Math.max(lcs[i+1][j], lcs[i][j+1])
  const result: DiffToken[] = []
  let i = 0, j = 0
  while (i < m && j < n) {
    if (al[i] === bl[j]) { result.push({ type: 'same', value: b[j] }); i++; j++ }
    else if (lcs[i+1][j] >= lcs[i][j+1]) { result.push({ type: 'remove', value: a[i] }); i++ }
    else { result.push({ type: 'add', value: b[j] }); j++ }
  }
  while (j < n) result.push({ type: 'add', value: b[j++] })
  return result
}

interface ParaSegment {
  rawText: string
  charToPos: number[]
  firstPos: number
}

function extractParaSegments(doc: PmNode): ParaSegment[] {
  const result: ParaSegment[] = []
  doc.descendants((node: PmNode, pos: number) => {
    if (node.type.name !== 'paragraph' && node.type.name !== 'heading') return
    const charToPos: number[] = []
    const parts: string[] = []
    node.forEach((child: PmNode, offset: number) => {
      if (child.isText && child.text) {
        const absStart = pos + 1 + offset
        for (let i = 0; i < child.text.length; i++) charToPos.push(absStart + i)
        parts.push(child.text)
      }
    })
    if (charToPos.length > 0) {
      result.push({ rawText: parts.join(''), charToPos, firstPos: charToPos[0] })
    }
  })
  return result
}

function extractPrevParaTexts(html: string): string[] {
  const div = document.createElement('div')
  div.innerHTML = html
  const texts: string[] = []
  function walk(el: Element) {
    for (const child of Array.from(el.children)) {
      const tag = child.tagName.toLowerCase()
      if (['p','h1','h2','h3','h4','h5','h6','li'].includes(tag)) {
        const t = (child.textContent ?? '').replace(/\s+/g, ' ').trim()
        if (t) texts.push(t)
      } else {
        walk(child)
      }
    }
  }
  walk(div)
  return texts
}

/** Extrai textos dos paragraph/heading de um doc TipTap (JSON), recursivamente.
 *  Reflete o comportamento de `extractParaSegments` (que usa doc.descendants) —
 *  só assim os índices alinham entre versões. */
function extractTiptapParaTexts(tiptap: Record<string, unknown> | null | undefined): string[] {
  if (!tiptap) return []
  const result: string[] = []

  const collectText = (n: Record<string, unknown>): string => {
    if (n.type === 'text' && typeof n.text === 'string') return n.text
    const children = Array.isArray(n.content) ? n.content : []
    return children.map((c) => collectText(c as Record<string, unknown>)).join('')
  }

  const walk = (node: Record<string, unknown>) => {
    const type = node.type
    if (type === 'paragraph' || type === 'heading') {
      const children = Array.isArray(node.content) ? node.content : []
      const text = children
        .map((c) => collectText(c as Record<string, unknown>))
        .join('')
        .replace(/\s+/g, ' ')
        .trim()
      if (text) result.push(text)
    }
    // Continua descendo para pegar paragraph/heading aninhados (ex: dentro de blockquote)
    const children = Array.isArray(node.content) ? node.content : []
    for (const c of children) walk(c as Record<string, unknown>)
  }

  const top = Array.isArray(tiptap.content) ? tiptap.content : []
  for (const n of top) walk(n as Record<string, unknown>)
  return result
}

/** Pega os parágrafos da versão anterior priorizando o TipTap JSON (estável)
 *  e caindo para HTML quando o JSON não está disponível. */
function getPrevVersionParaTexts(version: { content_tiptap?: Record<string, unknown> | null; content_html?: string | null }): string[] {
  if (version.content_tiptap) {
    const texts = extractTiptapParaTexts(version.content_tiptap)
    if (texts.length > 0) return texts
  }
  return extractPrevParaTexts(version.content_html ?? '')
}

// ── End diff utilities ──────────────────────────────────────────────────────────────────────────

function textExistsInEditor(
  editor: ReturnType<typeof useTipTapEditor>,
  text: string,
): boolean {
  if (!editor || !text) return false
  const target = normalizeForMatch(text)
  if (!target) return false

  let normText = ''
  let prevWasSpace = true
  editor.state.doc.descendants((node) => {
    if (node.isText && node.text) {
      for (const c of node.text) {
        const isSpace = /\s/.test(c) || c === ' '
        if (isSpace) {
          if (!prevWasSpace) { normText += ' '; prevWasSpace = true }
        } else {
          normText += c
            .replace(/[“”„‟″]/g, '"')
            .replace(/[‘’‚‛′]/g, "'")
            .replace(/[–—−]/g, '-')
            .toLowerCase()
          prevWasSpace = false
        }
      }
    }
  })
  return normText.includes(target)
}

function getDismissedReviewIds(parecerId: string): string[] {
  try {
    const raw = localStorage.getItem(`peer_review_dismissed:${parecerId}`)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function addDismissedReviewId(parecerId: string, reviewId: string): void {
  const existing = getDismissedReviewIds(parecerId)
  if (!existing.includes(reviewId)) {
    localStorage.setItem(
      `peer_review_dismissed:${parecerId}`,
      JSON.stringify([...existing, reviewId]),
    )
  }
}

export function useEditorInstance(parecer: ParecerRequestDetail | null) {
  const [activeVersion, setActiveVersion] = useState<ParecerVersion | null>(null)
  const [isDirty, setIsDirty] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [showSplitView, setShowSplitView] = useState(false)
  const [showReturnModal, setShowReturnModal] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [correctionCount, setCorrectionCount] = useState(0)
  const [isReprocessing, setIsReprocessing] = useState(false)
  const [correctionPreview, setCorrectionPreview] = useState<CorrectionPreview | null>(null)
  const [isApplying, setIsApplying] = useState(false)
  const [correctionInstructions, setCorrectionInstructions] = useState('')
  const [showPeerReviewModal, setShowPeerReviewModal] = useState(false)
  const [isPeerReviewSending, setIsPeerReviewSending] = useState(false)
  const [showReviewResponseModal, setShowReviewResponseModal] = useState(false)
  const [isReviewResponding, setIsReviewResponding] = useState(false)
  const [pendingReviewForMe, setPendingReviewForMe] = useState<PeerReviewListItem | null>(null)
  const [completedReviewsForMe, setCompletedReviewsForMe] = useState<PeerReviewListItem[]>([])
  const [activeCompletedReview, setActiveCompletedReview] = useState<PeerReviewListItem | null>(null)
  const [showCompletedReviewModal, setShowCompletedReviewModal] = useState(false)
  const [diffAnnotation, setDiffAnnotation] = useState<DiffAnnotation | null>(null)
  // Modal de aviso ao exportar com marcadores de revisão humana pendentes.
  const [exportMarkersState, setExportMarkersState] = useState<{
    format: 'docx' | 'pdf'
    marcadores: MarcadorRevisao[]
  } | null>(null)
  const saveRef = useRef<() => void>(() => {})
  const queryClient = useQueryClient()

  // Pick latest version on initial load only (activeVersion === null)
  useEffect(() => {
    if (parecer?.versions?.length && activeVersion === null) {
      const sorted = [...parecer.versions].sort(
        (a, b) => b.version_number - a.version_number
      )
      setActiveVersion(sorted[0])
    }
  }, [parecer, activeVersion])

  const editor = useTipTapEditor({
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      Underline,
      Placeholder.configure({ placeholder: 'Comece a digitar a minuta...' }),
      Typography,
      AIContent,
      CorrectionMark,
      SearchHighlight,
      DiffHighlight,
      RevisaoMarkerHighlight,
      ParagraphIndent,
      EmentaHighlight,
      SignatureBlock,
      AnnotationHighlight,
      AsteriskCleanup,
    ],
    content: activeVersion?.content_tiptap || activeVersion?.content_html || '',
    onUpdate: () => {
      setIsDirty(true)
    },
    editorProps: {
      attributes: {
        // A aparência (folha A4, fonte, recuos) é controlada pelo CSS .ProseMirror
        // em index.css — espelho fiel do DOCX. Sem classes utilitárias aqui para
        // não conflitar com as margens/recuos em cm.
        class: 'focus:outline-none',
      },
      handleKeyDown: (_view, event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
          event.preventDefault()
          saveRef.current()
          return true
        }
        return false
      },
    },
  })

  // Alimenta a linha "Município/UF, DD de mês de AAAA." do bloco de assinaturas
  // (widget fixo). Espelha o `_adicionar_fortaleza_data` do docx_generator: cidade
  // do consulente (fallback Fortaleza) + data de hoje. Apenas exibição — não entra
  // no conteúdo salvo.
  useEffect(() => {
    if (!editor) return
    const cidadeRaw = (parecer?.municipio_nome || 'Fortaleza').trim()
    const cidade = cidadeRaw.includes('/') ? cidadeRaw : `${cidadeRaw}/CE`
    const now = new Date()
    const dataLine = `${cidade}, ${now.getDate()} de ${MESES_EXTENSO[now.getMonth()]} de ${now.getFullYear()}.`
    editor.commands.setSignatureDataLine(dataLine)
  }, [editor, parecer?.municipio_nome])

  // Track correction mark count
  useEffect(() => {
    if (!editor) return
    const updateCount = () => {
      setCorrectionCount(getMarkedFragments(editor).length)
    }
    editor.on('transaction', updateCount)
    return () => {
      editor.off('transaction', updateCount)
    }
  }, [editor])

  // Sync content when activeVersion changes.
  // `setContent(..., false)` evita emitir onUpdate — caso contrário a troca
  // de versão (ex.: restauração) marcaria isDirty=true e geraria nova versão
  // ao salvar/enviar mesmo sem o usuário ter editado nada.
  useEffect(() => {
    if (editor && activeVersion) {
      const newContent = activeVersion.content_tiptap || activeVersion.content_html || ''
      editor.commands.setContent(newContent, false)
      setIsDirty(false)
      setCorrectionCount(0)
    }
  }, [activeVersion, editor])

  // Diff highlight acumulado: percorre o histórico efetivo até a versão ativa
  // e marca cada palavra adicionada com as iniciais do autor da versão.
  // Restauração: ao encontrar uma versão `restaurado`, descarta as versões
  // intermediárias e retoma o histórico até a versão de origem.
  useEffect(() => {
    if (!editor || !activeVersion || !parecer) {
      editor?.commands.setDiffAnnotation(null)
      setDiffAnnotation(null)
      return
    }

    const toInitials = (name: string | null | undefined, source?: string) => {
      // Versões geradas pela IA (sem created_by) sempre aparecem como 'IA',
      // incluindo `ia_gerado` e `ia_reprocessado` (correção solicitada à IA).
      if (!name || source === 'ia_gerado' || source === 'ia_reprocessado') return 'IA'
      return name.split(' ').filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('')
    }

    const allSorted = [...parecer.versions].sort((a, b) => a.version_number - b.version_number)
    const activeIdx = allSorted.findIndex(v => v.id === activeVersion.id)
    if (activeIdx < 0) {
      editor.commands.setDiffAnnotation(null)
      setDiffAnnotation(null)
      return
    }

    // Histórico efetivo: aplica restaurações truncando a linha do tempo.
    // Ex.: v1, v2 (RB), v3 (MM), v4 (restaurado da v2) → efetivo: v1, v2.
    // Edições de v3 desaparecem; marcações de RB em v2 permanecem.
    const effective: typeof allSorted = []
    for (let i = 0; i <= activeIdx; i++) {
      const v = allSorted[i]
      if (v.source === 'restaurado' && v.reprocess_instructions) {
        const m = v.reprocess_instructions.match(/v(\d+)/)
        if (m) {
          const fromNum = parseInt(m[1], 10)
          const fromIdx = allSorted.findIndex(x => x.version_number === fromNum)
          if (fromIdx >= 0) {
            effective.length = 0
            for (let j = 0; j <= fromIdx; j++) effective.push(allSorted[j])
            continue
          }
        }
        // Fallback: se não conseguir parsear, trata como versão normal
        effective.push(v)
      } else {
        effective.push(v)
      }
    }

    if (effective.length < 2) {
      editor.commands.setDiffAnnotation(null)
      setDiffAnnotation(null)
      return
    }

    const timer = setTimeout(() => {
      // Para cada par consecutivo (vN, vN+1) do histórico efetivo: faz diff
      // palavra-a-palavra dos parágrafos correspondentes (por índice). Cada
      // palavra adicionada é marcada com as iniciais do autor de vN+1.
      // Múltiplos autores no mesmo parágrafo → iniciais acumulam ('RB / MM').
      const paraMap = new Map<number, Set<string>>() // paraIdx → conjunto de iniciais
      const allWordRanges: DiffAnnotation['wordRanges'] = []
      const curParas = extractParaSegments(editor.state.doc)

      // Normaliza um parágrafo para fins de comparação:
      // - remove marcadores **bold** e _italic_
      // - unifica aspas, traços e espaços
      // - lowercase
      const normalizePara = (s: string) =>
        s
          .replace(/\*\*/g, '')
          .replace(/[“”„‟″]/g, '"')
          .replace(/[‘’‚‛′]/g, "'")
          .replace(/[–—−]/g, '-')
          .replace(/ /g, ' ')
          .replace(/\s+/g, ' ')
          .trim()
          .toLowerCase()

      for (let i = 1; i < effective.length; i++) {
        const prev = effective[i - 1]
        const next = effective[i]

        const prevParas = getPrevVersionParaTexts(prev)
        const nextParas = getPrevVersionParaTexts(next)
        if (prevParas.length === 0 || nextParas.length === 0) continue

        const initials = toInitials(next.created_by_name, next.source)

        // Set de parágrafos prévios (normalizados) para detectar quando o texto
        // foi preservado mesmo que o índice tenha mudado (ex.: a IA reconstrói
        // todos os nodes TipTap mesmo em seções inalteradas).
        const prevSet = new Set(prevParas.map(normalizePara))

        const minLen = Math.min(prevParas.length, nextParas.length)

        for (let p = 0; p < minLen; p++) {
          const prevRaw = prevParas[p].replace(/\s+/g, ' ').trim()
          const nextRaw = nextParas[p].replace(/\s+/g, ' ').trim()
          if (!prevRaw || !nextRaw || prevRaw === nextRaw) continue
          // Texto idêntico (em qualquer posição da versão anterior) → preservado
          if (prevSet.has(normalizePara(nextRaw))) continue
          if (p >= curParas.length) continue

          const cur = curParas[p]
          const prevToks = prevRaw.match(/\S+/g) ?? []
          const nextToks = nextRaw.match(/\S+/g) ?? []
          const tokens = diffWords(prevToks, nextToks)

          const addedCount = tokens.filter(t => t.type === 'add').length
          // Reescrita total (>60%): só badge, sem word ranges para não poluir
          const fullRewrite = nextToks.length > 0 && addedCount / nextToks.length > 0.6

          let addedRanges = 0
          if (!fullRewrite) {
            const curRaw = cur.rawText.replace(/\s+/g, ' ').trim()
            let charOffset = 0
            for (const tok of tokens) {
              if (tok.type === 'remove') continue
              const idx = curRaw.indexOf(tok.value, charOffset)
              if (idx === -1) { charOffset += tok.value.length; continue }
              charOffset = idx
              if (tok.type === 'add' && tok.value.trim() && idx < cur.charToPos.length) {
                allWordRanges.push({
                  from: cur.charToPos[idx],
                  to: cur.charToPos[Math.min(idx + tok.value.length - 1, cur.charToPos.length - 1)] + 1,
                  initials,
                })
                addedRanges++
              }
              charOffset += tok.value.length
            }
          }

          // Badge: aparece quando houve word ranges OU reescrita total
          if (addedRanges > 0 || fullRewrite) {
            const set = paraMap.get(p) ?? new Set<string>()
            set.add(initials)
            paraMap.set(p, set)
          }
        }
      }

      const paraFirstPositions: number[] = []
      const paraInitials: string[] = []
      const sortedEntries = [...paraMap.entries()].sort(([a], [b]) => a - b)
      for (const [idx, set] of sortedEntries) {
        if (idx < curParas.length) {
          paraFirstPositions.push(curParas[idx].firstPos)
          // Ordenar: 'IA' primeiro, depois iniciais humanas alfabeticamente
          const list = [...set].sort((a, b) => {
            if (a === 'IA') return -1
            if (b === 'IA') return 1
            return a.localeCompare(b)
          })
          paraInitials.push(list.join(' / '))
        }
      }

      if (paraFirstPositions.length === 0 && allWordRanges.length === 0) {
        editor.commands.setDiffAnnotation(null)
        setDiffAnnotation(null)
        return
      }

      const annotation: DiffAnnotation = {
        wordRanges: allWordRanges,
        paraFirstPositions,
        initials: '',
        paraInitials,
      }
      editor.commands.setDiffAnnotation(annotation)
      setDiffAnnotation(annotation)
    }, 80)

    return () => clearTimeout(timer)
  }, [activeVersion, editor, parecer])

  // Fetch peer reviews to detect pending review (as reviewer)
  // and completed reviews that the user requested (as requester, awaiting action)
  useEffect(() => {
    if (!parecer) return
    const userId = getCurrentUserId()
    if (!userId) return
    fetchPeerReviews(parecer.id).then((reviews) => {
      const pending = reviews.find(
        (r) => r.reviewer_id === userId && r.status === 'pendente'
      )
      setPendingReviewForMe(pending ?? null)

      const dismissedIds = getDismissedReviewIds(parecer.id)
      const completed = reviews.filter(
        (r) =>
          r.requested_by === userId &&
          r.status === 'concluida' &&
          !dismissedIds.includes(r.id),
      )
      setCompletedReviewsForMe(completed)
    }).catch(() => {
      setPendingReviewForMe(null)
      setCompletedReviewsForMe([])
    })
  }, [parecer])

  // Aplicar marcações amarelas no editor quando o revisor abre o parecer
  const appliedMarksRef = useRef(false)
  useEffect(() => {
    if (!editor || !pendingReviewForMe || !activeVersion || appliedMarksRef.current) return
    const trechos = (pendingReviewForMe.trechos_marcados ?? []).map((t) => t.texto)
    if (trechos.length === 0) return
    // Pequeno delay para garantir que o conteúdo foi renderizado
    const timer = setTimeout(() => {
      applyCorrectionsMarks(editor, trechos)
      appliedMarksRef.current = true
    }, 300)
    return () => clearTimeout(timer)
  }, [editor, pendingReviewForMe, activeVersion])

  // --- Anotações inline (marca + questionamento, cor por autor) ---
  const { data: annotations = [] } = useQuery({
    queryKey: ['annotations', parecer?.id],
    queryFn: () => fetchAnnotations(parecer!.id),
    enabled: !!parecer?.id,
    staleTime: 10_000,
  })

  // Alimenta a extensão de decoration sempre que a lista ou o editor mudam.
  useEffect(() => {
    if (!editor) return
    const decos: AnnotationDeco[] = (annotations as Annotation[]).map((a) => ({
      id: a.id,
      trecho: a.trecho_texto,
      color: a.author_color,
      hint: `${a.author_name ?? 'Anônimo'}: ${a.questionamento}`,
    }))
    editor.commands.setAnnotations(decos)
  }, [editor, annotations, activeVersion])

  const getSelectionText = useCallback((): string => {
    if (!editor) return ''
    const { from, to } = editor.state.selection
    if (from === to) return ''
    return editor.state.doc.textBetween(from, to, '\n').trim()
  }, [editor])

  const handleAddAnnotation = useCallback(
    async (trecho: string, questionamento: string) => {
      if (!parecer) return
      await createAnnotation(parecer.id, trecho, questionamento)
      await queryClient.invalidateQueries({ queryKey: ['annotations', parecer.id] })
    },
    [parecer, queryClient],
  )

  const handleDeleteAnnotation = useCallback(
    async (annotationId: string) => {
      if (!parecer) return
      await deleteAnnotation(annotationId)
      await queryClient.invalidateQueries({ queryKey: ['annotations', parecer.id] })
    },
    [parecer, queryClient],
  )

  const handleSave = useCallback(async () => {
    if (!editor || !parecer || !activeVersion) return
    // Não cria nova versão se o conteúdo não foi alterado pelo usuário.
    // Evita gerar snapshot supérfluo após restaurar versão ou aprovar/enviar
    // sem ter editado nada.
    if (!isDirty) return
    setIsSaving(true)
    try {
      const newVersion = await saveVersionSnapshot(parecer.id, editor.getHTML(), editor.getJSON())
      setIsDirty(false)
      setActiveVersion(newVersion)
      queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
    } catch (err) {
      console.error('Save failed:', err)
    } finally {
      setIsSaving(false)
    }
  }, [editor, parecer, activeVersion, isDirty, queryClient])

  // Keep saveRef current so Ctrl+S always calls the latest handleSave
  saveRef.current = handleSave

  const getMarkedTexts = useCallback(() => {
    return getMarkedFragments(editor)
  }, [editor])

  /** Fase 1: enviar para IA e obter preview */
  const handleRequestPreview = useCallback(
    async (instructions: string) => {
      if (!parecer) return
      setIsReprocessing(true)
      setCorrectionInstructions(instructions)
      try {
        const trechos = getMarkedFragments(editor)
        const fullObservacoes = trechos.length > 0
          ? `## TRECHOS MARCADOS PARA CORREÇÃO\nOs seguintes trechos foram marcados e DEVEM ser reescritos/corrigidos:\n${trechos.map((t, i) => `${i + 1}. "${t}"`).join('\n')}\n\n## INSTRUÇÕES DO REVISOR\n${instructions}`
          : instructions
        const preview = await previewCorrection(parecer.id, fullObservacoes)
        setCorrectionPreview(preview)
      } catch (err) {
        console.error('Preview correction failed:', err)
      } finally {
        setIsReprocessing(false)
      }
    },
    [parecer, editor]
  )

  /** Fase 2: aplicar seções aprovadas */
  const handleApplyCorrection = useCallback(
    async (secoes_aprovadas: Record<string, string>) => {
      if (!parecer || !correctionPreview) return
      setIsApplying(true)
      try {
        const newVersion = await applyCorrection(
          parecer.id,
          secoes_aprovadas,
          correctionInstructions,
          correctionPreview.notas_revisor,
          correctionPreview.citacoes_verificar,
        )
        clearAllCorrectionMarks(editor)
        setActiveVersion(newVersion)
        setCorrectionPreview(null)
        setCorrectionInstructions('')
        setShowReturnModal(false)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
      } catch (err) {
        console.error('Apply correction failed:', err)
      } finally {
        setIsApplying(false)
      }
    },
    [parecer, correctionPreview, correctionInstructions, editor, queryClient]
  )

  const handleCloseModal = useCallback(() => {
    setShowReturnModal(false)
    setCorrectionPreview(null)
    setCorrectionInstructions('')
  }, [])

  const handleRequestPeerReview = useCallback(
    async (reviewerId: string, observacoes: string) => {
      if (!parecer) return
      setIsPeerReviewSending(true)
      try {
        const trechos = getMarkedFragments(editor)
        const payload: PeerReviewCreatePayload = {
          reviewer_id: reviewerId,
          trechos_marcados: trechos.map((t) => ({ texto: t, instrucao: '' })),
          observacoes,
        }
        await createPeerReview(parecer.id, payload)
        clearAllCorrectionMarks(editor)
        setShowPeerReviewModal(false)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
        queryClient.invalidateQueries({ queryKey: ['peer-reviews', parecer.id] })
      } catch (err) {
        console.error('Peer review request failed:', err)
      } finally {
        setIsPeerReviewSending(false)
      }
    },
    [parecer, editor, queryClient]
  )

  const handleRespondPeerReview = useCallback(
    async (payload: PeerReviewRespondPayload) => {
      if (!parecer || !pendingReviewForMe) return
      setIsReviewResponding(true)
      try {
        await respondToPeerReview(pendingReviewForMe.id, payload)
        clearAllCorrectionMarks(editor)
        setShowReviewResponseModal(false)
        setPendingReviewForMe(null)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
        queryClient.invalidateQueries({ queryKey: ['peer-reviews', parecer.id] })
      } catch (err) {
        console.error('Respond to peer review failed:', err)
      } finally {
        setIsReviewResponding(false)
      }
    },
    [parecer, pendingReviewForMe, queryClient]
  )

  const handleOpenCompletedReview = useCallback((review: PeerReviewListItem) => {
    setActiveCompletedReview(review)
    setShowCompletedReviewModal(true)
  }, [])

  const handleCloseCompletedReview = useCallback(() => {
    setShowCompletedReviewModal(false)
    setActiveCompletedReview(null)
  }, [])

  /** Apply a single suggestion: replace `original` with `sugestao` in the editor.
   *  If the backend already applied the replacement (sugestao text already present
   *  and original text absent), treat as success without modifying the editor. */
  const handleApplySuggestion = useCallback(
    (original: string, sugestao: string): boolean => {
      const alreadyApplied = !textExistsInEditor(editor, original) && textExistsInEditor(editor, sugestao)
      const ok = alreadyApplied || replaceTextInEditor(editor, original, sugestao)
      if (ok && parecer && activeCompletedReview) {
        const reviewId = activeCompletedReview.id
        addDismissedReviewId(parecer.id, reviewId)
        setCompletedReviewsForMe((prev) => prev.filter((r) => r.id !== reviewId))
      }
      return ok
    },
    [editor, parecer, activeCompletedReview],
  )

  /** Dismiss a completed review: persist in localStorage and hide from UI. */
  const handleDismissCompletedReview = useCallback(
    (reviewId: string) => {
      if (!parecer) return
      addDismissedReviewId(parecer.id, reviewId)
      setCompletedReviewsForMe((prev) => prev.filter((r) => r.id !== reviewId))
      setShowCompletedReviewModal(false)
      setActiveCompletedReview(null)
    },
    [parecer],
  )

  const handleApprove = useCallback(
    async (sendEmail: boolean): Promise<boolean> => {
      if (!parecer) return false
      await handleSave()
      try {
        await approveParecer(parecer.id, sendEmail)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
        return true
      } catch (err) {
        console.error('Approve failed:', err)
        return false
      }
    },
    [parecer, handleSave, queryClient]
  )

  const performExport = useCallback(
    async (format: 'docx' | 'pdf') => {
      if (!parecer) return
      try {
        const blob = await exportParecer(parecer.id, format)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${parecer.numero_parecer || 'parecer'}.${format}`
        a.click()
        URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Export failed:', err)
      }
    },
    [parecer]
  )

  const handleExport = useCallback(
    async (format: 'docx' | 'pdf') => {
      if (!parecer) return
      // Sem marcadores: exporta direto.
      // Com marcadores: abre o modal (ExportWithMarkersModal) listando os
      // pontos pendentes — no DOCX/PDF eles saem em vermelho/negrito.
      const tiptap = editor?.getJSON() ?? activeVersion?.content_tiptap ?? null
      if (contarMarcadoresRevisao(tiptap) === 0) {
        await performExport(format)
        return
      }
      setExportMarkersState({
        format,
        marcadores: extrairMarcadoresRevisao(tiptap),
      })
    },
    [parecer, editor, activeVersion, performExport]
  )

  const confirmExportWithMarkers = useCallback(async () => {
    if (!exportMarkersState) return
    const fmt = exportMarkersState.format
    setExportMarkersState(null)
    await performExport(fmt)
  }, [exportMarkersState, performExport])

  const closeExportModal = useCallback(() => setExportMarkersState(null), [])

  const handleGenerate = useCallback(async () => {
    if (!parecer) return
    setIsGenerating(true)
    setGenerateError(null)
    try {
      const newVersion = await generateParecer(parecer.id)
      setActiveVersion(newVersion)
      queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
    } catch (err: unknown) {
      setGenerateError(err instanceof Error ? err.message : 'Erro ao gerar parecer')
    } finally {
      setIsGenerating(false)
    }
  }, [parecer, queryClient])

  return {
    editor,
    activeVersion,
    setActiveVersion,
    isDirty,
    isSaving,
    diffAnnotation,
    showSplitView,
    setShowSplitView,
    showReturnModal,
    setShowReturnModal,
    handleSave,
    handleGenerate,
    isGenerating,
    generateError,
    handleRequestPreview,
    handleApplyCorrection,
    handleCloseModal,
    isReprocessing,
    isApplying,
    correctionPreview,
    handleApprove,
    handleExport,
    exportMarkersState,
    confirmExportWithMarkers,
    closeExportModal,
    getMarkedTexts,
    correctionCount,
    showPeerReviewModal,
    setShowPeerReviewModal,
    handleRequestPeerReview,
    isPeerReviewSending,
    pendingReviewForMe,
    showReviewResponseModal,
    setShowReviewResponseModal,
    handleRespondPeerReview,
    isReviewResponding,
    completedReviewsForMe,
    activeCompletedReview,
    showCompletedReviewModal,
    handleOpenCompletedReview,
    handleCloseCompletedReview,
    handleApplySuggestion,
    handleDismissCompletedReview,
    // Anotações inline
    annotations: annotations as Annotation[],
    getSelectionText,
    handleAddAnnotation,
    handleDeleteAnnotation,
  }
}
