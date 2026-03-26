import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { EditorContent } from '@tiptap/react'
import { useParecer } from '../../hooks/useParecer'
import { useEditorInstance } from '../../hooks/useEditor'
import type { CorrectionPreview, PeerReviewRespondPayload } from '../../services/editorApi'
import type { PeerReviewListItem, RespostaTrecho } from '../../types/parecer'
import EditorToolbar from './EditorToolbar'
import EditorSidebar from './EditorSidebar'
import SplitView from './SplitView'
import PeerReviewModal from './PeerReviewModal'

const SECTION_LABELS: Record<string, string> = {
  ementa: 'Ementa',
  relatorio: 'I — Relatório',
  fundamentos: 'II — Fundamentos',
  conclusao: 'III — Conclusão',
}

function CorrectionModal({
  markedTexts,
  onSubmit,
  onApply,
  onClose,
  isLoading,
  isApplying,
  preview,
}: {
  markedTexts: string[]
  onSubmit: (instructions: string) => void
  onApply: (secoes: Record<string, string>) => void
  onClose: () => void
  isLoading?: boolean
  isApplying?: boolean
  preview: CorrectionPreview | null
}) {
  const [instructions, setInstructions] = useState('')
  const [approvedTrechos, setApprovedTrechos] = useState<Record<number, boolean>>({})

  const isTrechoApproved = (idx: number) => approvedTrechos[idx] ?? true

  const toggleTrecho = (idx: number) => {
    setApprovedTrechos((prev) => ({ ...prev, [idx]: !isTrechoApproved(idx) }))
  }

  const handleApply = () => {
    if (!preview) return
    // Montar seções aprovadas: para cada trecho aprovado, incluir a seção revisada completa
    // Se pelo menos 1 trecho de uma seção foi aprovado, incluir a seção inteira
    const secoesComAprovacao = new Set<string>()
    preview.trechos.forEach((t, i) => {
      if (isTrechoApproved(i)) {
        secoesComAprovacao.add(t.secao)
      }
    })
    // Se não há trechos (instrução geral), aprovar todas as seções alteradas
    if (preview.trechos.length === 0) {
      for (const secao of preview.secoes_alteradas) {
        secoesComAprovacao.add(secao)
      }
    }
    const secoes: Record<string, string> = {}
    for (const secao of secoesComAprovacao) {
      if (preview.revisado[secao]) {
        secoes[secao] = preview.revisado[secao]
      }
    }
    onApply(secoes)
  }

  const approvedCount = preview
    ? preview.trechos.length > 0
      ? preview.trechos.filter((_, i) => isTrechoApproved(i)).length
      : preview.secoes_alteradas.length
    : 0
  const totalCount = preview
    ? preview.trechos.length > 0
      ? preview.trechos.length
      : preview.secoes_alteradas.length
    : 0

  // ── Fase 2: Comparação por trecho ──
  if (preview) {
    const hasTrechos = preview.trechos.length > 0

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(27,40,56,0.5)' }}>
        <div className="rounded-xl w-full max-w-5xl mx-4 max-h-[85vh] flex flex-col" style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
          {/* Header */}
          <div className="p-4" style={{ borderBottom: '1px solid #EDE8DF' }}>
            <h3 className="text-base font-medium" style={{ color: '#0A1120' }}>
              Revisão da IA — {hasTrechos ? `${preview.trechos.length} trecho(s)` : `${preview.secoes_alteradas.length} seção(ões)`}
            </h3>
            <p className="text-sm mt-1" style={{ color: '#A69B8D' }}>
              {hasTrechos
                ? 'Compare cada trecho marcado com a proposta da IA. Aprove ou rejeite individualmente.'
                : 'A IA alterou as seções abaixo. Revise e aplique.'}
            </p>
          </div>

          {/* Trechos comparison */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {hasTrechos ? (
              preview.trechos.map((trecho, i) => (
                <div key={i} className="rounded-xl overflow-hidden" style={{ border: '1.5px solid #E0D9CE' }}>
                  {/* Trecho header */}
                  <div
                    className="flex items-center justify-between px-4 py-2 cursor-pointer"
                    style={{ background: isTrechoApproved(i) ? '#5B755310' : '#EDE8DF' }}
                    onClick={() => toggleTrecho(i)}
                  >
                    <span className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
                      {SECTION_LABELS[trecho.secao] || trecho.secao}
                    </span>
                    <button
                      className="px-3 py-0.5 text-xs font-medium rounded-lg transition-all duration-150"
                      style={
                        isTrechoApproved(i)
                          ? { background: '#5B7553', color: '#F5F0E8' }
                          : { background: '#E0D9CE', color: '#6B6860' }
                      }
                    >
                      {isTrechoApproved(i) ? 'Aprovado' : 'Rejeitado'}
                    </button>
                  </div>

                  {/* Original → Proposta */}
                  <div style={{ borderTop: '1px solid #EDE8DF' }}>
                    {/* Original */}
                    <div className="px-4 py-3" style={{ background: '#8B233208' }}>
                      <div className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#8B2332' }}>
                        Trecho original
                      </div>
                      <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#6B6860' }}>
                        "{trecho.original}"
                      </div>
                    </div>
                    {/* Arrow */}
                    <div className="flex items-center justify-center py-1" style={{ background: '#F5F0E8' }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 5v14M19 12l-7 7-7-7"/>
                      </svg>
                    </div>
                    {/* Proposta */}
                    <div className="px-4 py-3" style={{ background: isTrechoApproved(i) ? '#5B755308' : '#F5F0E8' }}>
                      <div className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: isTrechoApproved(i) ? '#5B7553' : '#A69B8D' }}>
                        Proposta da IA
                      </div>
                      <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#0A1120' }}>
                        "{trecho.revisado}"
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              // Fallback: sem trechos marcados, mostrar seções alteradas
              preview.secoes_alteradas.map((secao) => (
                <div key={secao} className="rounded-xl p-4" style={{ border: '1.5px solid #E0D9CE' }}>
                  <div className="text-sm font-medium mb-1" style={{ color: '#0A1120' }}>
                    {SECTION_LABELS[secao] || secao}
                  </div>
                  <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#6B6860' }}>
                    {preview.revisado[secao]?.slice(0, 300)}
                    {(preview.revisado[secao]?.length ?? 0) > 300 && '...'}
                  </div>
                </div>
              ))
            )}

            {/* Notas do revisor */}
            {preview.notas_revisor.length > 0 && (
              <div className="rounded-xl p-3" style={{ background: '#C9A94E12', border: '1.5px solid #C9A94E33' }}>
                <div className="text-xs font-medium uppercase tracking-widest mb-2" style={{ color: '#C9A94E' }}>
                  Notas da IA
                </div>
                <ul className="space-y-1">
                  {preview.notas_revisor.map((nota, i) => (
                    <li key={i} className="text-sm" style={{ color: '#6B6860' }}>
                      {nota}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-between items-center gap-2 p-4" style={{ borderTop: '1px solid #EDE8DF' }}>
            <span className="text-sm" style={{ color: '#A69B8D' }}>
              {approvedCount} de {totalCount} aprovado(s)
            </span>
            <div className="flex gap-2">
              <button
                onClick={onClose}
                disabled={isApplying}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ color: '#6B6860', background: '#F5F0E8', border: '1.5px solid #E0D9CE' }}
              >
                Descartar
              </button>
              <button
                onClick={handleApply}
                disabled={approvedCount === 0 || isApplying}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                style={{ background: '#5B7553', color: '#F5F0E8' }}
              >
                {isApplying && (
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                  </svg>
                )}
                {isApplying ? 'Aplicando...' : `Aplicar ${approvedCount} correção(ões)`}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ── Fase 1: Input de instruções ──
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col" style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        <div className="p-4" style={{ borderBottom: '1px solid #EDE8DF' }}>
          <h3 className="text-base font-medium" style={{ color: '#0A1120' }}>
            Solicitar correção para IA
          </h3>
          <p className="text-sm mt-1" style={{ color: '#A69B8D' }}>
            {markedTexts.length > 0
              ? 'Os trechos marcados serão enviados junto com suas instruções.'
              : 'Descreva o que a IA deve corrigir na minuta.'}
          </p>
        </div>

        <div className="p-4 overflow-y-auto flex-1 space-y-4">
          {/* Marked fragments */}
          {markedTexts.length > 0 && (
            <div>
              <label className="text-sm font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
                Trechos marcados ({markedTexts.length})
              </label>
              <ul className="mt-2 space-y-1.5">
                {markedTexts.map((text, i) => (
                  <li
                    key={i}
                    className="text-sm px-3 py-2 rounded-lg"
                    style={{
                      background: '#C9A94E18',
                      borderLeft: '3px solid #C9A94E',
                      color: '#6B6860',
                    }}
                  >
                    "{text}"
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Instructions */}
          <div>
            <label className="text-sm font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
              Instruções para a IA
            </label>
            <textarea
              className="mt-2 w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2 resize-none disabled:opacity-50"
              style={{ border: '1.5px solid #E0D9CE', color: '#0A1120', background: '#F5F0E8', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              rows={4}
              placeholder="Ex: Reescrever a fundamentação com base na Lei 14.133/2021..."
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 p-4" style={{ borderTop: '1px solid #EDE8DF' }}>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ color: '#6B6860', background: '#F5F0E8', border: '1.5px solid #E0D9CE' }}
          >
            Cancelar
          </button>
          <button
            onClick={() => onSubmit(instructions)}
            disabled={!instructions.trim() || isLoading}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            style={{ background: '#C9A94E', color: '#F5F0E8' }}
          >
            {isLoading && (
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
            )}
            {isLoading ? 'Processando...' : 'Enviar para IA'}
          </button>
        </div>
      </div>
    </div>
  )
}

function ReviewResponseModal({
  review,
  onSubmit,
  onClose,
  isLoading,
}: {
  review: PeerReviewListItem
  onSubmit: (payload: PeerReviewRespondPayload) => void
  onClose: () => void
  isLoading?: boolean
}) {
  const [respostaGeral, setRespostaGeral] = useState('')
  const [respostasTrechos, setRespostasTrechos] = useState<RespostaTrecho[]>(
    (review.trechos_marcados ?? []).map((t) => ({
      original: t.texto,
      sugestao: '',
      comentario: '',
    }))
  )

  const updateTrecho = (idx: number, field: keyof RespostaTrecho, value: string) => {
    setRespostasTrechos((prev) =>
      prev.map((rt, i) => (i === idx ? { ...rt, [field]: value } : rt))
    )
  }

  const canSubmit = respostaGeral.trim() && !isLoading

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl w-full max-w-5xl mx-4 max-h-[85vh] flex flex-col" style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        {/* Header */}
        <div className="p-4" style={{ borderBottom: '1px solid #EDE8DF' }}>
          <h3 className="text-base font-medium" style={{ color: '#0A1120' }}>
            Revisar parecer
          </h3>
          <p className="text-sm mt-1" style={{ color: '#A69B8D' }}>
            Solicitado por {review.requested_by_name}
            {review.trechos_marcados && review.trechos_marcados.length > 0
              ? ` — ${review.trechos_marcados.length} trecho(s) marcado(s)`
              : ''}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Observações do solicitante */}
          {review.observacoes && (
            <div className="rounded-xl p-3" style={{ background: '#C9A94E12', border: '1.5px solid #C9A94E33' }}>
              <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#C9A94E' }}>
                Observações do solicitante
              </p>
              <p className="text-sm leading-relaxed" style={{ color: '#6B6860' }}>
                {review.observacoes}
              </p>
            </div>
          )}

          {/* Trechos marcados com campos de sugestão */}
          {respostasTrechos.length > 0 && respostasTrechos.map((rt, i) => (
            <div key={i} className="rounded-xl overflow-hidden" style={{ border: '1.5px solid #E0D9CE' }}>
              {/* Trecho original */}
              <div className="px-4 py-3" style={{ background: '#14203808' }}>
                <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#A69B8D' }}>
                  Trecho {i + 1}
                </p>
                <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#6B6860' }}>
                  "{rt.original}"
                </p>
              </div>
              {/* Campo de sugestão */}
              <div className="px-4 py-3" style={{ borderTop: '1px solid #EDE8DF' }}>
                <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#142038' }}>
                  Sua sugestão
                </p>
                <textarea
                  className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 resize-none disabled:opacity-50"
                  style={{ border: '1.5px solid #E0D9CE', background: '#F5F0E8', color: '#0A1120' } as React.CSSProperties}
                  rows={3}
                  placeholder="Sua sugestão para este trecho..."
                  value={rt.sugestao}
                  onChange={(e) => updateTrecho(i, 'sugestao', e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>
          ))}

          {/* Parecer geral */}
          <div>
            <label className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
              Seu parecer geral
            </label>
            <textarea
              className="mt-2 w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2 resize-none disabled:opacity-50"
              style={{ border: '1.5px solid #E0D9CE', color: '#0A1120', background: '#F5F0E8' } as React.CSSProperties}
              rows={4}
              placeholder="Seu comentário geral sobre o parecer..."
              value={respostaGeral}
              onChange={(e) => setRespostaGeral(e.target.value)}
              disabled={isLoading}
              autoFocus={respostasTrechos.length === 0}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 p-4" style={{ borderTop: '1px solid #EDE8DF' }}>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ color: '#6B6860', background: '#F5F0E8', border: '1.5px solid #E0D9CE' }}
          >
            Cancelar
          </button>
          <button
            onClick={() => onSubmit({ resposta_geral: respostaGeral, resposta_trechos: respostasTrechos })}
            disabled={!canSubmit}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            style={{ background: '#142038', color: '#F5F0E8' }}
          >
            {isLoading && (
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
            )}
            {isLoading ? 'Enviando...' : 'Enviar revisão'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function LegalEditor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: parecer, isLoading, error } = useParecer(id)

  const {
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
  } = useEditorInstance(parecer ?? null)

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  const searchResults = editor?.storage.searchHighlight?.results ?? 0

  // Ctrl+F to toggle search
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        setShowSearch((v) => {
          if (v) {
            setSearchTerm('')
            editor?.commands.setSearchTerm('')
          }
          return !v
        })
      }
      if (e.key === 'Escape' && showSearch) {
        setShowSearch(false)
        setSearchTerm('')
        editor?.commands.setSearchTerm('')
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [editor, showSearch])

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    editor?.commands.setSearchTerm(value)
  }

  const handleApproveWithLoading = useCallback(async (sendEmail: boolean) => {
    setIsSubmitting(true)
    try {
      const ok = await handleApprove(sendEmail)
      if (ok && sendEmail) navigate('/pareceres')
    } finally {
      setIsSubmitting(false)
    }
  }, [handleApprove, navigate])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full" style={{ background: '#F5F0E8' }}>
        <div className="text-base" style={{ color: '#A69B8D' }}>Carregando parecer...</div>
      </div>
    )
  }

  if (error || !parecer) {
    return (
      <div className="flex items-center justify-center h-full" style={{ background: '#F5F0E8' }}>
        <div className="text-center">
          <p className="text-base mb-2" style={{ color: '#8B2332' }}>Erro ao carregar parecer</p>
          <button
            onClick={() => navigate('/pareceres')}
            className="text-sm cursor-pointer"
            style={{ color: '#C9A94E' }}
          >
            Voltar para lista
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2" style={{ background: '#F5F0E8', borderBottom: '1px solid #EDE8DF' }}>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/pareceres')}
            className="text-sm cursor-pointer transition-all duration-150"
            style={{ color: '#A69B8D' }}
          >
            ← Voltar
          </button>
          <h1 className="text-sm font-medium truncate max-w-md" style={{ color: '#0A1120' }}>
            {parecer.numero_parecer || parecer.subject || 'Parecer'}
          </h1>
          {isSaving && (
            <span className="text-sm" style={{ color: '#A69B8D' }}>Salvando...</span>
          )}
          {isDirty && !isSaving && (
            <span className="text-sm" style={{ color: '#C9A94E' }}>Não salvo</span>
          )}
          {!isDirty && !isSaving && activeVersion && (
            <span className="text-sm" style={{ color: '#5B7553' }}>Salvo</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSplitView(!showSplitView)}
            className="px-3 py-1 text-sm rounded-lg transition-all duration-150 cursor-pointer"
            style={
              showSplitView
                ? { background: '#C9A94E18', color: '#C9A94E', border: '1.5px solid #C9A94E44' }
                : { color: '#6B6860', border: '1.5px solid #E0D9CE' }
            }
          >
            Split View
          </button>
        </div>
      </div>

      {/* Toolbar — hidden while generating */}
      {activeVersion && (
        <EditorToolbar
          editor={editor}
          onExport={handleExport}
          onSave={handleSave}
          isSaving={isSaving}
          isDirty={isDirty}
          showSearch={showSearch}
          searchTerm={searchTerm}
          searchResults={searchResults}
          onToggleSearch={() => setShowSearch(true)}
          onSearchChange={handleSearchChange}
          onCloseSearch={() => { setShowSearch(false); setSearchTerm(''); editor?.commands.setSearchTerm('') }}
        />
      )}

      {/* Pipeline processing state — shown while classify + generate runs in background */}
      {!activeVersion && (parecer.status === 'classificado' || parecer.status === 'pendente') && (
        <div className="flex flex-1 items-center justify-center" style={{ background: '#F5F0E8' }}>
          <div className="text-center max-w-sm">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4" style={{ background: '#C9A94E18' }}>
              <svg className="animate-spin" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#C9A94E" strokeWidth="2.5">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
            </div>
            <h2 className="text-base font-medium mb-1" style={{ color: '#0A1120' }}>Gerando minuta...</h2>
            <p className="text-sm mb-2" style={{ color: '#A69B8D' }}>A IA está classificando o pedido e redigindo a minuta do parecer. Isso pode levar alguns segundos.</p>
            {generateError && (
              <p className="text-sm mb-3" style={{ color: '#8B2332' }}>{generateError}</p>
            )}
          </div>
        </div>
      )}

      {/* Main content area */}
      <div className={`flex flex-1 overflow-hidden ${!activeVersion && (parecer.status === 'classificado' || parecer.status === 'pendente') ? 'hidden' : ''}`}>
        {/* Editor area */}
        <div className="flex-1 overflow-y-auto" style={{ background: '#F5F0E8' }}>
          {showSplitView ? (
            <SplitView
              originalText={parecer.extracted_text}
              editor={editor}
            />
          ) : (
            <EditorContent editor={editor} />
          )}
        </div>

        {/* Sidebar */}
        <EditorSidebar
          parecer={parecer}
          activeVersion={activeVersion}
          onVersionSelect={setActiveVersion}
          onVersionRestored={setActiveVersion}
        />
      </div>

      {/* Footer action bar — hidden while generating */}
      {activeVersion && (
        <div className="flex items-center justify-between px-4 py-3" style={{ background: '#EDE8DF', borderTop: '1px solid #E0D9CE' }}>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowReturnModal(true)}
              disabled={isReprocessing || isGenerating || isPeerReviewSending}
              className="px-4 py-2 text-sm rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ border: '1.5px solid #C9A94E44', color: '#C9A94E', background: '#C9A94E18' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Solicitar correção para IA
              {correctionCount > 0 && (
                <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold rounded-full" style={{ background: '#C9A94E', color: '#F5F0E8' }}>
                  {correctionCount}
                </span>
              )}
            </button>
            {pendingReviewForMe ? (
              <button
                onClick={() => setShowReviewResponseModal(true)}
                disabled={isReprocessing || isGenerating || isReviewResponding}
                className="px-4 py-2 text-sm rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ border: '1.5px solid #14203844', color: '#142038', background: '#14203812' }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                Revisar parecer
              </button>
            ) : (
              <button
                onClick={() => setShowPeerReviewModal(true)}
                disabled={isReprocessing || isGenerating || isPeerReviewSending}
                className="px-4 py-2 text-sm rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ border: '1.5px solid #14203844', color: '#142038', background: '#14203812' }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                Enviar para colega
                {correctionCount > 0 && (
                  <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold rounded-full" style={{ background: '#142038', color: '#F5F0E8' }}>
                    {correctionCount}
                  </span>
                )}
              </button>
            )}
          </div>
          <div className="flex items-center gap-2">
            {parecer.status !== 'aprovado' && parecer.status !== 'enviado' && (
              <button
                onClick={() => handleApproveWithLoading(false)}
                disabled={isSubmitting || isReprocessing || isGenerating}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                style={{ background: '#5B7553', color: '#F5F0E8' }}
              >
                {isSubmitting && <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />}
                Aprovar
              </button>
            )}
            {parecer.status !== 'enviado' && (
              <button
                onClick={() => handleApproveWithLoading(true)}
                disabled={isSubmitting || isReprocessing || isGenerating}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                style={{ background: '#142038', color: '#F5F0E8' }}
              >
                {isSubmitting && <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />}
                {parecer.status === 'aprovado' ? 'Enviar' : 'Aprovar e enviar'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Correction Modal */}
      {showReturnModal && (
        <CorrectionModal
          markedTexts={getMarkedTexts()}
          onSubmit={handleRequestPreview}
          onApply={handleApplyCorrection}
          onClose={handleCloseModal}
          isLoading={isReprocessing}
          isApplying={isApplying}
          preview={correctionPreview}
        />
      )}

      {/* Peer Review Modal — solicitar revisão */}
      {showPeerReviewModal && (
        <PeerReviewModal
          markedTexts={getMarkedTexts()}
          onSubmit={handleRequestPeerReview}
          onClose={() => setShowPeerReviewModal(false)}
          isLoading={isPeerReviewSending}
        />
      )}

      {/* Review Response Modal — responder revisão */}
      {showReviewResponseModal && pendingReviewForMe && (
        <ReviewResponseModal
          review={pendingReviewForMe}
          onSubmit={handleRespondPeerReview}
          onClose={() => setShowReviewResponseModal(false)}
          isLoading={isReviewResponding}
        />
      )}
    </div>
  )
}
