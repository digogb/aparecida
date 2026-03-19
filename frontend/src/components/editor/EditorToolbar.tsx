import type { Editor } from '@tiptap/react'

interface Props {
  editor: Editor | null
  onExport: (format: 'docx' | 'pdf') => void
  onSave: () => void
  isSaving: boolean
  isDirty: boolean
}

export default function EditorToolbar({ editor, onExport, onSave, isSaving, isDirty }: Props) {
  if (!editor) return null

  const btnClass = (active: boolean) =>
    `px-2 py-1 rounded text-sm font-medium transition-colors ${
      active
        ? 'bg-indigo-100 text-indigo-700'
        : 'text-gray-600 hover:bg-gray-100'
    }`

  return (
    <div className="flex items-center gap-1 border-b border-gray-200 px-4 py-2 bg-white flex-wrap">
      {/* Block type dropdown */}
      <select
        className="text-sm border border-gray-300 rounded px-2 py-1 mr-2"
        value={
          editor.isActive('heading', { level: 1 })
            ? 'h1'
            : editor.isActive('heading', { level: 2 })
              ? 'h2'
              : editor.isActive('heading', { level: 3 })
                ? 'h3'
                : 'p'
        }
        onChange={(e) => {
          const val = e.target.value
          if (val === 'p') editor.chain().focus().setParagraph().run()
          else
            editor
              .chain()
              .focus()
              .toggleHeading({ level: Number(val[1]) as 1 | 2 | 3 })
              .run()
        }}
      >
        <option value="p">Parágrafo</option>
        <option value="h1">Título 1</option>
        <option value="h2">Título 2</option>
        <option value="h3">Título 3</option>
      </select>

      <div className="w-px h-5 bg-gray-300 mx-1" />

      {/* Inline formatting */}
      <button
        className={btnClass(editor.isActive('bold'))}
        onClick={() => editor.chain().focus().toggleBold().run()}
        title="Negrito"
      >
        <strong>B</strong>
      </button>
      <button
        className={btnClass(editor.isActive('italic'))}
        onClick={() => editor.chain().focus().toggleItalic().run()}
        title="Itálico"
      >
        <em>I</em>
      </button>
      <button
        className={btnClass(editor.isActive('underline'))}
        onClick={() => editor.chain().focus().toggleUnderline().run()}
        title="Sublinhado"
      >
        <u>U</u>
      </button>

      <div className="w-px h-5 bg-gray-300 mx-1" />

      {/* Legal blocks */}
      <button
        className={btnClass(editor.isActive('citacaoLegal'))}
        onClick={() => editor.chain().focus().setCitacaoLegal({ referencia: 'Lei/Artigo' }).run()}
        title="Citação Legal"
      >
        Citação
      </button>
      <button
        className={btnClass(editor.isActive('ementa'))}
        onClick={() => editor.chain().focus().setEmenta().run()}
        title="Ementa"
      >
        Ementa
      </button>
      <button
        className="px-2 py-1 rounded text-sm text-gray-600 hover:bg-gray-100"
        onClick={() =>
          editor
            .chain()
            .focus()
            .setCitacaoLegal({ referencia: 'Art. ' })
            .run()
        }
        title="Artigo"
      >
        Art.
      </button>

      <div className="w-px h-5 bg-gray-300 mx-1" />

      {/* Lists */}
      <button
        className={btnClass(editor.isActive('orderedList'))}
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        title="Lista numerada"
      >
        1.
      </button>
      <button
        className={btnClass(editor.isActive('bulletList'))}
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        title="Lista"
      >
        •
      </button>

      <div className="w-px h-5 bg-gray-300 mx-1" />

      {/* Clear formatting */}
      <button
        className="px-2 py-1 rounded text-sm text-gray-600 hover:bg-gray-100"
        onClick={() => editor.chain().focus().unsetAllMarks().clearNodes().run()}
        title="Limpar formatação"
      >
        T̶
      </button>

      <div className="w-px h-5 bg-gray-300 mx-1" />

      {/* Correction mark */}
      <button
        className={`px-2 py-1 rounded text-sm font-medium transition-colors ${
          editor.isActive('correctionMark')
            ? 'bg-amber-100 text-amber-700 border border-amber-300'
            : 'text-amber-600 hover:bg-amber-50'
        }`}
        onClick={() => editor.chain().focus().toggleCorrectionMark().run()}
        title="Marcar trecho para correção (Ctrl+Shift+M)"
      >
        <span className="flex items-center gap-1">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          Corrigir
        </span>
      </button>

      <div className="flex-1" />

      {/* Save */}
      <button
        className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
          isSaving
            ? 'text-gray-400 cursor-not-allowed'
            : isDirty
              ? 'bg-indigo-600 text-white hover:bg-indigo-700'
              : 'text-gray-400 border border-gray-200'
        }`}
        onClick={onSave}
        disabled={isSaving || !isDirty}
        title="Salvar (Ctrl+S)"
      >
        {isSaving ? 'Salvando…' : 'Salvar'}
      </button>

      <div className="w-px h-5 bg-gray-300 mx-1" />

      {/* Export */}
      <button
        className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded"
        onClick={() => onExport('docx')}
      >
        .docx
      </button>
      <button
        className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded"
        onClick={() => onExport('pdf')}
      >
        .pdf
      </button>
    </div>
  )
}
