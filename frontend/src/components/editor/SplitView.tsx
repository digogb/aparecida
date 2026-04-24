import { useState } from 'react'
import { EditorContent } from '@tiptap/react'
import type { Editor } from '@tiptap/react'

interface Props {
  originalText: string | null
  editor: Editor | null
}

type Tab = 'original' | 'editado'

export default function SplitView({ originalText, editor }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('editado')

  const tabBtn = (tab: Tab, label: string) => (
    <button
      onClick={() => setActiveTab(tab)}
      className="flex-1 py-2 text-sm font-medium transition-all duration-150 cursor-pointer"
      style={
        activeTab === tab
          ? { color: '#142038', borderBottom: '2px solid #C9A94E' }
          : { color: '#A69B8D', borderBottom: '2px solid transparent' }
      }
    >
      {label}
    </button>
  )

  return (
    <div className="flex flex-1 overflow-hidden flex-col lg:flex-row">
      {/* Mobile: abas toggle */}
      <div
        className="lg:hidden flex border-b"
        style={{ background: '#EDE8DF', borderColor: '#E0D9CE' }}
      >
        {tabBtn('original', 'Original')}
        {tabBtn('editado', 'Editado')}
      </div>

      {/* Left: consulta original */}
      <div
        className={`overflow-y-auto lg:w-1/2 ${activeTab === 'original' ? 'flex-1' : 'hidden'} lg:flex lg:flex-col`}
        style={{ borderRight: '1px solid #EDE8DF', background: '#EDE8DF' }}
      >
        <div className="px-4 md:px-6 py-4">
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

      {/* Right: editor */}
      <div
        className={`overflow-y-auto lg:w-1/2 ${activeTab === 'editado' ? 'flex-1' : 'hidden'} lg:flex lg:flex-col`}
        style={{ background: '#F5F0E8' }}
      >
        <EditorContent editor={editor} className="h-full" />
      </div>
    </div>
  )
}
