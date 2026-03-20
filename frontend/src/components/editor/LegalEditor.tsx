import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { EditorContent } from '@tiptap/react'
import { useParecer } from '../../hooks/useParecer'
import { useEditorInstance } from '../../hooks/useEditor'
import EditorToolbar from './EditorToolbar'
import EditorSidebar from './EditorSidebar'
import SplitView from './SplitView'

function CorrectionModal({
  markedTexts,
  onSubmit,
  onClose,
  isLoading,
}: {
  markedTexts: string[]
  onSubmit: (instructions: string) => void
  onClose: () => void
  isLoading?: boolean
}) {
  const [instructions, setInstructions] = useState('')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[80vh] flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Solicitar correção para IA
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {markedTexts.length > 0
              ? 'Os trechos marcados serão enviados junto com suas instruções.'
              : 'Descreva o que a IA deve corrigir na minuta.'}
          </p>
        </div>

        <div className="p-4 overflow-y-auto flex-1 space-y-4">
          {/* Marked fragments */}
          {markedTexts.length > 0 && (
            <div>
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Trechos marcados ({markedTexts.length})
              </label>
              <ul className="mt-2 space-y-1.5">
                {markedTexts.map((text, i) => (
                  <li
                    key={i}
                    className="text-sm px-3 py-2 rounded-lg border-l-3"
                    style={{
                      background: '#FEF3C7',
                      borderLeft: '3px solid #F59E0B',
                      color: '#92400E',
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
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Instruções para a IA
            </label>
            <textarea
              className="mt-2 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 resize-none"
              rows={4}
              placeholder="Ex: Reescrever a fundamentação com base na Lei 14.133/2021..."
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              autoFocus
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancelar
          </button>
          <button
            onClick={() => onSubmit(instructions)}
            disabled={!instructions.trim() || isLoading}
            className="px-4 py-2 text-sm bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
    handleReturnToAI,
    isReprocessing,
    handleApprove,
    handleExport,
    getMarkedTexts,
    correctionCount,
  } = useEditorInstance(parecer ?? null)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Carregando parecer...</div>
      </div>
    )
  }

  if (error || !parecer) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-red-500 mb-2">Erro ao carregar parecer</p>
          <button
            onClick={() => navigate('/pareceres')}
            className="text-sm text-indigo-600 hover:underline"
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
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/pareceres')}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            ← Voltar
          </button>
          <h1 className="text-sm font-semibold text-gray-900 truncate max-w-md">
            {parecer.numero_parecer || parecer.subject || 'Parecer'}
          </h1>
          {isSaving && (
            <span className="text-xs text-gray-400">Salvando...</span>
          )}
          {isDirty && !isSaving && (
            <span className="text-xs text-amber-500">Não salvo</span>
          )}
          {!isDirty && !isSaving && activeVersion && (
            <span className="text-xs text-green-500">Salvo</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSplitView(!showSplitView)}
            className={`px-3 py-1 text-xs rounded border transition-colors ${
              showSplitView
                ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                : 'border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            Split View
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <EditorToolbar
        editor={editor}
        onExport={handleExport}
        onSave={handleSave}
        isSaving={isSaving}
        isDirty={isDirty}
      />

      {/* Pipeline processing state — shown while classify + generate runs in background */}
      {!activeVersion && (parecer.status === 'classificado' || parecer.status === 'pendente') && (
        <div className="flex flex-1 items-center justify-center bg-gray-50">
          <div className="text-center max-w-sm">
            <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-4">
              <svg className="animate-spin" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" strokeWidth="2.5">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
            </div>
            <h2 className="text-base font-semibold text-gray-900 mb-1">Gerando minuta...</h2>
            <p className="text-sm text-gray-500 mb-2">A IA está classificando o pedido e redigindo a minuta do parecer. Isso pode levar alguns segundos.</p>
            {generateError && (
              <p className="text-sm text-red-600 mb-3">{generateError}</p>
            )}
          </div>
        </div>
      )}

      {/* Main content area */}
      <div className={`flex flex-1 overflow-hidden ${!activeVersion && (parecer.status === 'classificado' || parecer.status === 'pendente') ? 'hidden' : ''}`}>
        {/* Editor area */}
        <div className="flex-1 overflow-y-auto bg-white">
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

      {/* Footer action bar */}
      <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowReturnModal(true)}
            className="px-4 py-2 text-sm border border-amber-300 text-amber-700 bg-amber-50 rounded-lg hover:bg-amber-100 flex items-center gap-2"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Solicitar correção para IA
            {correctionCount > 0 && (
              <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold bg-amber-500 text-white rounded-full">
                {correctionCount}
              </span>
            )}
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleApprove(false)}
            className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Aprovar
          </button>
          <button
            onClick={() => handleApprove(true)}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Aprovar e enviar
          </button>
        </div>
      </div>

      {/* Correction Modal */}
      {showReturnModal && (
        <CorrectionModal
          markedTexts={getMarkedTexts()}
          onSubmit={handleReturnToAI}
          onClose={() => setShowReturnModal(false)}
          isLoading={isReprocessing}
        />
      )}
    </div>
  )
}
