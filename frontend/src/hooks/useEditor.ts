import { useCallback, useEffect, useRef, useState } from 'react'
import { useEditor as useTipTapEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import Typography from '@tiptap/extension-typography'
import { useQueryClient } from '@tanstack/react-query'
import CitacaoLegal from '../components/editor/extensions/CitacaoLegal'
import Ementa from '../components/editor/extensions/Ementa'
import AIContent from '../components/editor/extensions/AIContent'
import CorrectionMark from '../components/editor/extensions/CorrectionMark'
import SearchHighlight from '../components/editor/extensions/SearchHighlight'
import {
  saveVersion,
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
import type { ParecerRequestDetail, ParecerVersion, PeerReviewListItem } from '../types/parecer'

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

/** Apply correctionMark to text fragments that match the given strings */
function applyCorrectionsMarks(editor: ReturnType<typeof useTipTapEditor>, trechos: string[]) {
  if (!editor || trechos.length === 0) return
  const { doc, tr } = editor.state
  const markType = editor.schema.marks.correctionMark
  if (!markType) return

  doc.descendants((node, pos) => {
    if (!node.isText || !node.text) return
    for (const trecho of trechos) {
      let idx = node.text.indexOf(trecho)
      while (idx !== -1) {
        tr.addMark(pos + idx, pos + idx + trecho.length, markType.create())
        idx = node.text.indexOf(trecho, idx + trecho.length)
      }
    }
  })
  editor.view.dispatch(tr)
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
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
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
      CitacaoLegal,
      Ementa,
      AIContent,
      CorrectionMark,
      SearchHighlight,
    ],
    content: activeVersion?.content_tiptap || activeVersion?.content_html || '',
    onUpdate: () => {
      setIsDirty(true)
    },
    editorProps: {
      attributes: {
        class:
          'prose prose-sm max-w-none focus:outline-none min-h-[500px] px-8 py-6',
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

  // Sync content when activeVersion changes
  useEffect(() => {
    if (editor && activeVersion) {
      const newContent = activeVersion.content_tiptap || activeVersion.content_html || ''
      editor.commands.setContent(newContent)
      setIsDirty(false)
      setCorrectionCount(0)
    }
  }, [activeVersion, editor])

  // Auto-save debounce 2s
  useEffect(() => {
    if (!isDirty || !editor || !parecer || !activeVersion) return
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(async () => {
      setIsSaving(true)
      try {
        await saveVersion(parecer.id, activeVersion.id, editor.getHTML(), editor.getJSON())
        setIsDirty(false)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
      } catch (err) {
        console.error('Auto-save failed:', err)
      } finally {
        setIsSaving(false)
      }
    }, 2000)
    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    }
  }, [isDirty, editor, parecer, activeVersion, queryClient])

  // Fetch peer reviews to detect pending review for current user
  useEffect(() => {
    if (!parecer) return
    const userId = getCurrentUserId()
    if (!userId) return
    fetchPeerReviews(parecer.id).then((reviews) => {
      const pending = reviews.find(
        (r) => r.reviewer_id === userId && r.status === 'pendente'
      )
      setPendingReviewForMe(pending ?? null)
    }).catch(() => setPendingReviewForMe(null))
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

  const handleSave = useCallback(async () => {
    if (!editor || !parecer || !activeVersion) return
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    setIsSaving(true)
    try {
      await saveVersion(parecer.id, activeVersion.id, editor.getHTML(), editor.getJSON())
      setIsDirty(false)
      queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
    } catch (err) {
      console.error('Save failed:', err)
    } finally {
      setIsSaving(false)
    }
  }, [editor, parecer, activeVersion, queryClient])

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

  const handleExport = useCallback(
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
  }
}
