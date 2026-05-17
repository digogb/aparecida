import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

/**
 * Realça os marcadores de revisão humana no editor:
 * - `[REVISAR — TEXTO]` (vertente licitação)
 * - `[!VERIFICAR: TEXTO !]` (vertente municipal-geral)
 *
 * Renderização: vermelho institucional #C00000, negrito — mesmo formato
 * usado no DOCX/PDF exportado. O usuário vê EXATAMENTE no editor o que
 * sairá no arquivo final, sem precisar abrir a sidebar.
 *
 * Para "resolver" um marcador: o advogado verifica a informação e edita
 * o texto manualmente, removendo os colchetes e substituindo pelo dado
 * definitivo.
 */

export const revisaoMarkerPluginKey = new PluginKey('revisaoMarkerHighlight')

const PADRAO = /\[REVISAR\s*[\-–—]\s*[^\]]+\]|\[!VERIFICAR:[^!]+!\]/gi

function buildDecorations(doc: import('@tiptap/pm/model').Node): DecorationSet {
  const decorations: Decoration[] = []
  let index = 0
  doc.descendants((node, pos) => {
    if (!node.isText || !node.text) return
    const text = node.text
    let match: RegExpExecArray | null
    PADRAO.lastIndex = 0
    while ((match = PADRAO.exec(text)) !== null) {
      const from = pos + match.index
      const to = from + match[0].length
      decorations.push(
        Decoration.inline(from, to, {
          class: 'revisao-marker',
          style:
            'color:#C00000; font-weight:700; background:#C0000010; ' +
            'border-radius:2px; padding:0 2px; cursor:help;',
          'data-revisao-marker-index': String(index),
          title:
            'Marcador de revisão humana. Verifique a informação e edite ' +
            'o texto para remover este marcador antes de exportar.',
        })
      )
      index += 1
    }
  })
  return DecorationSet.create(doc, decorations)
}

const RevisaoMarkerHighlight = Extension.create({
  name: 'revisaoMarkerHighlight',

  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: revisaoMarkerPluginKey,
        state: {
          init(_, { doc }) {
            return buildDecorations(doc)
          },
          apply(tr, oldSet) {
            if (tr.docChanged) {
              return buildDecorations(tr.doc)
            }
            return oldSet
          },
        },
        props: {
          decorations(state) {
            return this.getState(state)
          },
        },
      }),
    ]
  },
})

export default RevisaoMarkerHighlight
