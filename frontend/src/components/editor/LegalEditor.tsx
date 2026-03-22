import { useCallback, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { EditorContent } from '@tiptap/react'
import { useParecer } from '../../hooks/useParecer'
import { useEditorInstance } from '../../hooks/useEditor'
import type { CorrectionPreview } from '../../services/editorApi'
import EditorToolbar from './EditorToolbar'
import EditorSidebar from './EditorSidebar'
import SplitView from './SplitView'

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
        <div className="rounded-xl w-full max-w-3xl mx-4 max-h-[85vh] flex flex-col" style={{ background: '#FAF8F5', border: '1.5px solid #DDD9D2', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
          {/* Header */}
          <div className="p-4" style={{ borderBottom: '1px solid #EBE8E2' }}>
            <h3 className="text-base font-medium" style={{ color: '#2D2D3A' }}>
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
                <div key={i} className="rounded-xl overflow-hidden" style={{ border: '1.5px solid #DDD9D2' }}>
                  {/* Trecho header */}
                  <div
                    className="flex items-center justify-between px-4 py-2 cursor-pointer"
                    style={{ background: isTrechoApproved(i) ? '#5B755310' : '#EBE8E2' }}
                    onClick={() => toggleTrecho(i)}
                  >
                    <span className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
                      {SECTION_LABELS[trecho.secao] || trecho.secao}
                    </span>
                    <button
                      className="px-3 py-0.5 text-xs font-medium rounded-lg transition-all duration-150"
                      style={
                        isTrechoApproved(i)
                          ? { background: '#5B7553', color: '#FAF8F5' }
                          : { background: '#DDD9D2', color: '#6B6860' }
                      }
                    >
                      {isTrechoApproved(i) ? 'Aprovado' : 'Rejeitado'}
                    </button>
                  </div>

                  {/* Original → Proposta */}
                  <div style={{ borderTop: '1px solid #EBE8E2' }}>
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
                    <div className="flex items-center justify-center py-1" style={{ background: '#FAF8F5' }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 5v14M19 12l-7 7-7-7"/>
                      </svg>
                    </div>
                    {/* Proposta */}
                    <div className="px-4 py-3" style={{ background: isTrechoApproved(i) ? '#5B755308' : '#FAF8F5' }}>
                      <div className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: isTrechoApproved(i) ? '#5B7553' : '#A69B8D' }}>
                        Proposta da IA
                      </div>
                      <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#2D2D3A' }}>
                        "{trecho.revisado}"
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              // Fallback: sem trechos marcados, mostrar seções alteradas
              preview.secoes_alteradas.map((secao) => (
                <div key={secao} className="rounded-xl p-4" style={{ border: '1.5px solid #DDD9D2' }}>
                  <div className="text-sm font-medium mb-1" style={{ color: '#2D2D3A' }}>
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
              <div className="rounded-xl p-3" style={{ background: '#C4953A12', border: '1.5px solid #C4953A33' }}>
                <div className="text-xs font-medium uppercase tracking-widest mb-2" style={{ color: '#C4953A' }}>
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
          <div className="flex justify-between items-center gap-2 p-4" style={{ borderTop: '1px solid #EBE8E2' }}>
            <span className="text-sm" style={{ color: '#A69B8D' }}>
              {approvedCount} de {totalCount} aprovado(s)
            </span>
            <div className="flex gap-2">
              <button
                onClick={onClose}
                disabled={isApplying}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ color: '#6B6860', background: '#FAF8F5', border: '1.5px solid #DDD9D2' }}
              >
                Descartar
              </button>
              <button
                onClick={handleApply}
                disabled={approvedCount === 0 || isApplying}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                style={{ background: '#5B7553', color: '#FAF8F5' }}
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
      <div className="rounded-xl w-full max-w-lg mx-4 max-h-[80vh] flex flex-col" style={{ background: '#FAF8F5', border: '1.5px solid #DDD9D2', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        <div className="p-4" style={{ borderBottom: '1px solid #EBE8E2' }}>
          <h3 className="text-base font-medium" style={{ color: '#2D2D3A' }}>
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
                      background: '#C4953A18',
                      borderLeft: '3px solid #C4953A',
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
              style={{ border: '1.5px solid #DDD9D2', color: '#2D2D3A', background: '#FAF8F5', '--tw-ring-color': '#C4953A' } as React.CSSProperties}
              rows={4}
              placeholder="Ex: Reescrever a fundamentação com base na Lei 14.133/2021..."
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 p-4" style={{ borderTop: '1px solid #EBE8E2' }}>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ color: '#6B6860', background: '#FAF8F5', border: '1.5px solid #DDD9D2' }}
          >
            Cancelar
          </button>
          <button
            onClick={() => onSubmit(instructions)}
            disabled={!instructions.trim() || isLoading}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            style={{ background: '#C4953A', color: '#FAF8F5' }}
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
  } = useEditorInstance(parecer ?? null)

  const [isSubmitting, setIsSubmitting] = useState(false)

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
      <div className="flex items-center justify-center h-full" style={{ background: '#FAF8F5' }}>
        <div className="text-base" style={{ color: '#A69B8D' }}>Carregando parecer...</div>
      </div>
    )
  }

  if (error || !parecer) {
    return (
      <div className="flex items-center justify-center h-full" style={{ background: '#FAF8F5' }}>
        <div className="text-center">
          <p className="text-base mb-2" style={{ color: '#8B2332' }}>Erro ao carregar parecer</p>
          <button
            onClick={() => navigate('/pareceres')}
            className="text-sm cursor-pointer"
            style={{ color: '#C4953A' }}
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
      <div className="flex items-center justify-between px-4 py-2" style={{ background: '#FAF8F5', borderBottom: '1px solid #EBE8E2' }}>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/pareceres')}
            className="text-sm cursor-pointer transition-all duration-150"
            style={{ color: '#A69B8D' }}
          >
            ← Voltar
          </button>
          <h1 className="text-sm font-medium truncate max-w-md" style={{ color: '#2D2D3A' }}>
            {parecer.numero_parecer || parecer.subject || 'Parecer'}
          </h1>
          {isSaving && (
            <span className="text-sm" style={{ color: '#A69B8D' }}>Salvando...</span>
          )}
          {isDirty && !isSaving && (
            <span className="text-sm" style={{ color: '#C4953A' }}>Não salvo</span>
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
                ? { background: '#C4953A18', color: '#C4953A', border: '1.5px solid #C4953A44' }
                : { color: '#6B6860', border: '1.5px solid #DDD9D2' }
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
        />
      )}

      {/* Pipeline processing state — shown while classify + generate runs in background */}
      {!activeVersion && (parecer.status === 'classificado' || parecer.status === 'pendente') && (
        <div className="flex flex-1 items-center justify-center" style={{ background: '#FAF8F5' }}>
          <div className="text-center max-w-sm">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4" style={{ background: '#C4953A18' }}>
              <svg className="animate-spin" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#C4953A" strokeWidth="2.5">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
            </div>
            <h2 className="text-base font-medium mb-1" style={{ color: '#2D2D3A' }}>Gerando minuta...</h2>
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
        <div className="flex-1 overflow-y-auto" style={{ background: '#FAF8F5' }}>
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
        <div className="flex items-center justify-between px-4 py-3" style={{ background: '#EBE8E2', borderTop: '1px solid #DDD9D2' }}>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowReturnModal(true)}
              disabled={isReprocessing || isGenerating}
              className="px-4 py-2 text-sm rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ border: '1.5px solid #C4953A44', color: '#C4953A', background: '#C4953A18' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Solicitar correção para IA
              {correctionCount > 0 && (
                <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold rounded-full" style={{ background: '#C4953A', color: '#FAF8F5' }}>
                  {correctionCount}
                </span>
              )}
            </button>
          </div>
          <div className="flex items-center gap-2">
            {parecer.status !== 'aprovado' && parecer.status !== 'enviado' && (
              <button
                onClick={() => handleApproveWithLoading(false)}
                disabled={isSubmitting || isReprocessing || isGenerating}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                style={{ background: '#5B7553', color: '#FAF8F5' }}
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
                style={{ background: '#1B2838', color: '#FAF8F5' }}
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
    </div>
  )
}
