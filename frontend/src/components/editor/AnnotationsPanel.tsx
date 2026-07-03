import { useMemo, useState } from 'react'
import type { Editor } from '@tiptap/react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchAnnotations, deleteAnnotation } from '../../services/annotationApi'
import { useCurrentUser } from '../../hooks/useCurrentUser'
import type { Annotation } from '../../types/parecer'

interface Props {
  parecerId: string
  editor: Editor | null
}

const EMPTY: Annotation[] = []

function normalize(s: string): string {
  return s
    .replace(/[“”„‟″]/g, '"')
    .replace(/[‘’‚‛′]/g, "'")
    .replace(/[–—−]/g, '-')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
}

/**
 * Painel lateral das anotações inline (marca + questionamento). Substitui o painel de
 * peer review. Lista com cor do autor, questionamento e trecho; clicar rola até o
 * trecho; apagar liberado ao autor ou admin. Anotações cujo trecho não casa mais com
 * o texto atual aparecem em "Trecho não localizado".
 */
export default function AnnotationsPanel({ parecerId, editor }: Props) {
  const queryClient = useQueryClient()
  const { data: currentUser } = useCurrentUser()
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const { data: annotationsData } = useQuery({
    queryKey: ['annotations', parecerId],
    queryFn: () => fetchAnnotations(parecerId),
    staleTime: 10_000,
  })
  const annotations = annotationsData ?? EMPTY

  // Texto normalizado do documento atual, para detectar anotações órfãs e pular ao trecho.
  const docText = useMemo(() => (editor ? normalize(editor.getText()) : ''), [editor, annotations])

  const isFound = (a: Annotation) => docText.includes(normalize(a.trecho_texto))

  async function handleDelete(id: string) {
    setDeletingId(id)
    try {
      await deleteAnnotation(id)
      await queryClient.invalidateQueries({ queryKey: ['annotations', parecerId] })
    } catch (err) {
      console.error('Delete annotation failed:', err)
    } finally {
      setDeletingId(null)
    }
  }

  function jumpTo(a: Annotation) {
    if (!editor) return
    const target = normalize(a.trecho_texto)
    if (!target) return
    // Busca linear pelo trecho no doc (texto simples) e seleciona/rola.
    const full = normalize(editor.state.doc.textContent)
    const at = full.indexOf(target)
    if (at === -1) return
    // Aproxima a posição no doc: percorre acumulando texto normalizado.
    let acc = ''
    let posFrom = 1
    editor.state.doc.descendants((node, pos) => {
      if (acc.length > at) return false
      if (node.isText && node.text) {
        const before = acc.length
        acc = normalize(acc + node.text)
        if (before <= at && acc.length > at) posFrom = pos + Math.max(0, at - before)
      }
      return true
    })
    editor.chain().focus().setTextSelection(posFrom).scrollIntoView().run()
  }

  if (annotations.length === 0) {
    return (
      <div className="p-3" style={{ borderBottom: '1px solid #E0D9CE' }}>
        <h3 className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>
          Questionamentos
        </h3>
        <p className="text-sm" style={{ color: '#A69B8D' }}>
          Nenhum. Selecione um trecho no texto e clique em “Anotar trecho”.
        </p>
      </div>
    )
  }

  const canDelete = (a: Annotation) =>
    currentUser?.role === 'admin' || currentUser?.id === a.author_id

  return (
    <div className="p-3" style={{ borderBottom: '1px solid #E0D9CE' }}>
      <h3 className="text-sm font-medium uppercase tracking-widest mb-2 flex items-center gap-2" style={{ color: '#A69B8D' }}>
        <span>Questionamentos</span>
        <span className="px-1.5 rounded-full text-xs font-bold" style={{ background: '#142038', color: '#fff' }}>
          {annotations.length}
        </span>
      </h3>
      <ul className="space-y-1.5">
        {annotations.map((a) => {
          const found = isFound(a)
          return (
            <li
              key={a.id}
              className="text-xs px-2 py-1.5 rounded"
              style={{ background: '#FAF8F5', border: '1px solid #E0D9CE', borderLeft: `3px solid ${a.author_color}` }}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: a.author_color }} />
                <span className="font-medium truncate" style={{ color: '#3B3833' }}>{a.author_name ?? 'Anônimo'}</span>
                {canDelete(a) && (
                  <button
                    onClick={() => handleDelete(a.id)}
                    disabled={deletingId === a.id}
                    className="ml-auto text-xs cursor-pointer disabled:opacity-50"
                    style={{ color: '#8B2332' }}
                    title="Apagar questionamento"
                  >
                    {deletingId === a.id ? '...' : 'Apagar'}
                  </button>
                )}
              </div>
              <p className="mb-1" style={{ color: '#0A1120' }}>{a.questionamento}</p>
              {found ? (
                <button
                  onClick={() => jumpTo(a)}
                  className="italic text-left cursor-pointer hover:underline"
                  style={{ color: '#6B6860' }}
                  title="Ir para o trecho"
                >
                  “{a.trecho_texto.length > 80 ? a.trecho_texto.slice(0, 80) + '…' : a.trecho_texto}”
                </button>
              ) : (
                <span className="italic" style={{ color: '#A69B8D' }}>
                  Trecho não localizado no texto atual
                </span>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
