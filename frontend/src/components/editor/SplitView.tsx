import { EditorContent } from '@tiptap/react'
import type { Editor } from '@tiptap/react'

interface Props {
  originalText: string | null
  editor: Editor | null
}

export default function SplitView({ originalText, editor }: Props) {
  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Left: Original consultation (read-only) */}
      <div className="w-1/2 overflow-y-auto" style={{ borderRight: '1px solid #EDE8DF', background: '#EDE8DF' }}>
        <div className="px-6 py-4">
          <h3 className="text-sm font-medium uppercase tracking-widest mb-3" style={{ color: '#A69B8D' }}>
            Consulta Original
          </h3>
          <div className="prose prose-sm max-w-none whitespace-pre-wrap" style={{ color: '#0A1120' }}>
            {originalText || (
              <span className="italic" style={{ color: '#A69B8D' }}>
                Texto original não disponível
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Right: Editor */}
      <div className="w-1/2 overflow-y-auto" style={{ background: '#F5F0E8' }}>
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
