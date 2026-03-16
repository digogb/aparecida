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
      <div className="w-1/2 border-r border-gray-200 overflow-y-auto bg-gray-50">
        <div className="px-6 py-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">
            Consulta Original
          </h3>
          <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
            {originalText || (
              <span className="text-gray-400 italic">
                Texto original não disponível
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Right: Editor */}
      <div className="w-1/2 overflow-y-auto bg-white">
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
