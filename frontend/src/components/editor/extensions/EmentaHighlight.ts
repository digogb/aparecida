import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'
import type { Node as PmNode } from '@tiptap/pm/model'

/**
 * Espelha a EMENTA do DOCX dentro do editor, SEM alterar o conteúdo salvo
 * (o mesmo TipTap alimenta o gerador DOCX canônico via `minuta_from_tiptap`).
 *
 * No DOCX a ementa é um parágrafo único: "EMENTA: PALAVRA1 ― PALAVRA2 ―
 * PARECER FAVORÁVEL." em negrito, recuado 4 cm à esquerda (bloco inteiro),
 * justificado. Não há um título "EMENTA" separado à esquerda.
 *
 * O conteúdo salvo, porém, ainda traz o heading H2 "EMENTA" (necessário para o
 * parser de export identificar a seção) seguido do texto da ementa SEM o rótulo.
 * Esta extensão, por decoration:
 *   1. ESCONDE o heading H2 "EMENTA" (o rótulo à esquerda que o cliente não quer);
 *   2. PREFIXA "EMENTA: " (negrito, não-editável) no início do 1º parágrafo da
 *      ementa, reproduzindo o rótulo inline do DOCX;
 *   3. aplica a classe `ementa-block` (negrito + recuo 4 cm) aos parágrafos da
 *      ementa, via CSS de `.ProseMirror p.ementa-block` (index.css).
 *
 * Tudo é camada de exibição: o texto persistido continua intacto, então o
 * round-trip para o DOCX não muda. Recuos manuais da régua continuam tendo
 * precedência sobre a classe.
 */

export const ementaHighlightPluginKey = new PluginKey('ementaHighlight')

function buildDecorations(doc: PmNode): DecorationSet {
  const decorations: Decoration[] = []
  let inEmenta = false
  let labelInjected = false

  doc.forEach((node, offset) => {
    // Parágrafo CONSULENTE: no DOCX tem space_after = 12pt (não 6pt). Marca para
    // o CSS aplicar o espaçamento correto — afeta a paginação (1 linha por página).
    if (
      node.type.name === 'paragraph' &&
      (node.textContent || '').trim().toUpperCase().startsWith('CONSULENTE')
    ) {
      decorations.push(
        Decoration.node(offset, offset + node.nodeSize, { class: 'consulente-block' })
      )
    }

    if (node.type.name === 'heading') {
      const isEmenta = (node.textContent || '').trim().toUpperCase() === 'EMENTA'
      if (isEmenta) {
        // Esconde o título "EMENTA" alinhado à esquerda — o rótulo passa a ser inline.
        decorations.push(
          Decoration.node(offset, offset + node.nodeSize, { class: 'ementa-heading-hidden' })
        )
      }
      inEmenta = isEmenta
      return
    }

    if (inEmenta && node.type.name === 'paragraph') {
      decorations.push(
        Decoration.node(offset, offset + node.nodeSize, { class: 'ementa-block' })
      )

      // Injeta o rótulo "EMENTA: " inline, só no primeiro parágrafo da ementa
      // e desde que o texto já não comece por "EMENTA" (defensivo).
      const startsWithLabel = (node.textContent || '').trim().toUpperCase().startsWith('EMENTA')
      if (!labelInjected && !startsWithLabel) {
        decorations.push(
          Decoration.widget(
            offset + 1,
            () => {
              const span = document.createElement('span')
              span.className = 'ementa-label'
              span.setAttribute('contenteditable', 'false')
              span.textContent = 'EMENTA: '
              return span
            },
            { side: -1, key: 'ementa-label' }
          )
        )
        labelInjected = true
      }
    }
  })

  return DecorationSet.create(doc, decorations)
}

const EmentaHighlight = Extension.create({
  name: 'ementaHighlight',

  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: ementaHighlightPluginKey,
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

export default EmentaHighlight
