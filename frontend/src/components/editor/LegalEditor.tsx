import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { EditorContent } from '@tiptap/react'
import { useParecer } from '../../hooks/useParecer'
import { useEditorInstance } from '../../hooks/useEditor'
import EditorToolbar from './EditorToolbar'
import EditorSidebar from './EditorSidebar'
import SplitView from './SplitView'

function ReturnModal({
  onSubmit,
  onClose,
}: {
  onSubmit: (instructions: string) => void
  onClose: () => void
}) {
  const [instructions, setInstructions] = useState('')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Devolver para IA
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Descreva as instruções para a IA gerar uma nova versão.
          </p>
        </div>
        <div className="p-4">
          <textarea
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            rows={5}
            placeholder="Ex: Reescrever a fundamentação com base na Lei 14.133/2021..."
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            autoFocus
          />
        </div>
        <div className="flex justify-end gap-2 p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            Cancelar
          </button>
          <button
            onClick={() => onSubmit(instructions)}
            disabled={!instructions.trim()}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Enviar para IA
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
    handleReturnToAI,
    handleApprove,
    handleExport,
    handleRequestCorrection,
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
      <EditorToolbar editor={editor} onExport={handleExport} />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
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
        />
      </div>

      {/* Footer action bar */}
      <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <button
            onClick={handleRequestCorrection}
            className="px-4 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100"
          >
            Solicitar correção
          </button>
          <button
            onClick={() => setShowReturnModal(true)}
            className="px-4 py-2 text-sm border border-amber-300 text-amber-700 bg-amber-50 rounded-lg hover:bg-amber-100"
          >
            Devolver para IA
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('docx')}
            className="px-4 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100"
          >
            Exportar .docx
          </button>
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

      {/* Return to AI Modal */}
      {showReturnModal && (
        <ReturnModal
          onSubmit={handleReturnToAI}
          onClose={() => setShowReturnModal(false)}
        />
      )}
    </div>
  )
}
