import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'
import type { Node as PmNode } from '@tiptap/pm/model'

/**
 * Esconde asteriscos soltos (`*`) que vazaram como caractere literal no conteúdo
 * já salvo — itálico markdown que a IA insere em volta de citações legais. O DOCX
 * canônico descarta esses asteriscos (`_normalizar_blockquote`), então mostrá-los
 * no editor quebra o "espelho fiel".
 *
 * Camada de exibição: os `*` continuam no conteúdo salvo (inofensivos — o DOCX os
 * remove), apenas ficam ocultos na tela via decoration. Pareceres novos já saem
 * limpos da geração (`_parse_inline_marks` remove os asteriscos soltos).
 *
 * Só esconde asterisco ISOLADO — `**` de negrito real (raro no conteúdo, já vira
 * mark) é preservado.
 */

export const asteriskCleanupPluginKey = new PluginKey('asteriskCleanup')

// Asterisco que não é precedido nem seguido por outro asterisco (≠ **negrito**).
const LONE_ASTERISK = /(?<!\*)\*(?!\*)/g

function buildDecorations(doc: PmNode): DecorationSet {
  const decorations: Decoration[] = []
  doc.descendants((node, pos) => {
    if (!node.isText || !node.text) return
    const text = node.text
    LONE_ASTERISK.lastIndex = 0
    let m: RegExpExecArray | null
    while ((m = LONE_ASTERISK.exec(text)) !== null) {
      const from = pos + m.index
      decorations.push(Decoration.inline(from, from + 1, { class: 'md-asterisk-hidden' }))
    }
  })
  return DecorationSet.create(doc, decorations)
}

const AsteriskCleanup = Extension.create({
  name: 'asteriskCleanup',

  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: asteriskCleanupPluginKey,
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

export default AsteriskCleanup
