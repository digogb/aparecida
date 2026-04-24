import { useRef } from 'react'
import type { Editor } from '@tiptap/react'

interface Props {
  editor: Editor | null
  onExport: (format: 'docx' | 'pdf') => void
  onSave: () => void
  isSaving: boolean
  isDirty: boolean
  showSearch: boolean
  searchTerm: string
  searchResults: number
  onToggleSearch: () => void
  onSearchChange: (value: string) => void
  onCloseSearch: () => void
  onSidebarToggle?: () => void
}

export default function EditorToolbar({ editor, onExport, onSave, isSaving, isDirty, showSearch, searchTerm, searchResults, onToggleSearch, onSearchChange, onCloseSearch, onSidebarToggle }: Props) {
  const searchInputRef = useRef<HTMLInputElement>(null)
  if (!editor) return null

  const btnClass = (active: boolean) =>
    `px-2 py-1 rounded text-sm font-medium transition-all duration-150 cursor-pointer ${
      active
        ? ''
        : ''
    }`

  const btnStyle = (active: boolean) =>
    active
      ? { background: '#C9A94E18', color: '#C9A94E' }
      : { color: '#6B6860' }

  return (
    <div className="flex items-center gap-1 px-4 py-2 flex-wrap" style={{ background: '#FAF8F5', borderBottom: '1px solid #EDE8DF' }}>
      {/* Block type dropdown */}
      <select
        className="text-sm rounded-lg px-2 py-1 mr-2 focus:outline-none"
        style={{ border: '1.5px solid #E0D9CE', color: '#0A1120', background: '#FAF8F5' }}
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

      <div className="w-px h-5 mx-1" style={{ background: '#E0D9CE' }} />

      {/* Inline formatting */}
      <button
        className={btnClass(editor.isActive('bold'))}
        style={btnStyle(editor.isActive('bold'))}
        onClick={() => editor.chain().focus().toggleBold().run()}
        title="Negrito"
      >
        <strong>B</strong>
      </button>
      <button
        className={btnClass(editor.isActive('italic'))}
        style={btnStyle(editor.isActive('italic'))}
        onClick={() => editor.chain().focus().toggleItalic().run()}
        title="Itálico"
      >
        <em>I</em>
      </button>
      <button
        className={btnClass(editor.isActive('underline'))}
        style={btnStyle(editor.isActive('underline'))}
        onClick={() => editor.chain().focus().toggleUnderline().run()}
        title="Sublinhado"
      >
        <u>U</u>
      </button>

      <div className="w-px h-5 mx-1" style={{ background: '#E0D9CE' }} />

      {/* Citação (blockquote — mesmo formato que a IA usa para citar lei/jurisprudência) */}
      <button
        className={btnClass(editor.isActive('blockquote'))}
        style={btnStyle(editor.isActive('blockquote'))}
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        title="Citação (Lei, jurisprudência, doutrina)"
      >
        Citação
      </button>

      <div className="w-px h-5 mx-1" style={{ background: '#E0D9CE' }} />

      {/* Lists */}
      <button
        className={btnClass(editor.isActive('orderedList'))}
        style={btnStyle(editor.isActive('orderedList'))}
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        title="Lista numerada"
      >
        1.
      </button>
      <button
        className={btnClass(editor.isActive('bulletList'))}
        style={btnStyle(editor.isActive('bulletList'))}
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        title="Lista"
      >
        •
      </button>

      <div className="w-px h-5 mx-1" style={{ background: '#E0D9CE' }} />

      {/* Clear formatting */}
      <button
        className="px-2 py-1 rounded text-sm transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
        onClick={() => editor.chain().focus().unsetAllMarks().clearNodes().run()}
        title="Limpar formatação"
      >
        T̶
      </button>

      <div className="w-px h-5 mx-1" style={{ background: '#E0D9CE' }} />

      {/* Correction mark */}
      <button
        className="px-2 py-1 rounded text-sm font-medium transition-all duration-150 cursor-pointer"
        style={
          editor.isActive('correctionMark')
            ? { background: '#C9A94E18', color: '#C9A94E', border: '1px solid #C9A94E44' }
            : { color: '#C9A94E' }
        }
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

      <div className="w-px h-5 mx-1" style={{ background: '#E0D9CE' }} />

      {/* Search */}
      {showSearch ? (
        <div className="flex items-center gap-1.5">
          <div className="relative">
            <input
              ref={searchInputRef}
              type="text"
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Escape') onCloseSearch() }}
              placeholder="Buscar..."
              autoFocus
              className="pl-7 pr-2 py-1 text-sm rounded-lg w-44 focus:outline-none"
              style={{ border: '1.5px solid #E0D9CE', background: '#FAF8F5', color: '#0A1120' }}
            />
            <svg className="absolute left-2 top-1/2 -translate-y-1/2" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
          </div>
          {searchTerm.length >= 2 && (
            <span className="text-xs whitespace-nowrap" style={{ color: '#A69B8D' }}>
              {searchResults}
            </span>
          )}
          <button
            onClick={onCloseSearch}
            className="p-0.5 rounded cursor-pointer"
            style={{ color: '#A69B8D' }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6 6 18" /><path d="m6 6 12 12" />
            </svg>
          </button>
        </div>
      ) : (
        <button
          onClick={() => { onToggleSearch(); setTimeout(() => searchInputRef.current?.focus(), 50) }}
          className="px-2 py-1 rounded text-sm transition-all duration-150 cursor-pointer"
          style={{ color: '#6B6860' }}
          title="Buscar (Ctrl+F)"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </button>
      )}

      <div className="flex-1" />

      {/* Save */}
      <button
        className="px-3 py-1 text-sm rounded-lg font-medium transition-all duration-150 cursor-pointer"
        style={
          isSaving
            ? { color: '#A69B8D', cursor: 'not-allowed' }
            : isDirty
              ? { background: '#142038', color: '#FAF8F5' }
              : { color: '#A69B8D', border: '1.5px solid #E0D9CE' }
        }
        onClick={onSave}
        disabled={isSaving || !isDirty}
        title="Salvar (Ctrl+S)"
      >
        {isSaving ? 'Salvando…' : 'Salvar'}
      </button>

      <div className="w-px h-5 mx-1" style={{ background: '#E0D9CE' }} />

      {/* Export — escondido em mobile para economizar espaço */}
      <button
        className="hidden xs:block px-3 py-1 text-sm rounded-lg transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
        onClick={() => onExport('docx')}
      >
        .docx
      </button>
      <button
        className="hidden xs:block px-3 py-1 text-sm rounded-lg transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
        onClick={() => onExport('pdf')}
      >
        .pdf
      </button>

      {/* Botão de info/sidebar — só em mobile (lg: sidebar é inline) */}
      {onSidebarToggle && (
        <button
          onClick={onSidebarToggle}
          className="lg:hidden px-2 py-1 rounded text-sm transition-all duration-150 cursor-pointer"
          style={{ color: '#6B6860' }}
          title="Informações do parecer"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </button>
      )}
    </div>
  )
}
