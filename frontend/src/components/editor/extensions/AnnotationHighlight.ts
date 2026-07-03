import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import type { Node as PmNode } from '@tiptap/pm/model'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

/**
 * Realça os trechos anotados (marca + questionamento) no editor, com COR POR AUTOR
 * e o questionamento no hint (tooltip). Substitui o antigo realce de peer review.
 *
 * É camada de EXIBIÇÃO: renderizado como decoration (nunca marca salva), então não
 * entra no content_tiptap (canon do DOCX) e some se a anotação for apagada. As
 * anotações vêm do backend (tabela parecer_annotations) e alimentam a extensão via
 * o comando `setAnnotations`. Os trechos são casados de forma robusta (normalização
 * de aspas/traços/espaços/caixa), então seguem o texto mesmo com pequenas edições.
 */

export const annotationHighlightPluginKey = new PluginKey('annotationHighlight')

export interface AnnotationDeco {
  id: string
  trecho: string
  color: string // cor de fundo (do autor)
  hint: string // "Autor: questionamento" — vai no title
}

interface AnnotationStorage {
  annotations: AnnotationDeco[]
}

/** Normaliza um caractere para matching (mesma lógica de useEditor.buildNormalizedDocMap). */
function normalizeChar(c: string): string {
  return c
    .replace(/[“”„‟″]/g, '"')
    .replace(/[‘’‚‛′]/g, "'")
    .replace(/[–—−]/g, '-')
    .toLowerCase()
}

function normalizeTrecho(s: string): string {
  return s
    .replace(/[“”„‟″]/g, '"')
    .replace(/[‘’‚‛′]/g, "'")
    .replace(/[–—−]/g, '-')
    .replace(/ /g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
}

/** Texto normalizado do doc + mapa índice-normalizado → posição ProseMirror. */
function buildDocMap(doc: PmNode): { normText: string; normToPos: number[] } {
  let normText = ''
  const normToPos: number[] = []
  let lastPos: number | null = null
  let prevWasSpace = true

  const pushChar = (c: string, pos: number) => {
    const isSpace = /\s/.test(c) || c === ' '
    if (isSpace) {
      if (!prevWasSpace) {
        normText += ' '
        normToPos.push(pos)
        prevWasSpace = true
      }
      return
    }
    normText += normalizeChar(c)
    normToPos.push(pos)
    prevWasSpace = false
  }

  doc.descendants((node, pos) => {
    if (node.isText && node.text) {
      for (let i = 0; i < node.text.length; i++) pushChar(node.text[i], pos + i)
      lastPos = pos + node.text.length
    } else if (node.isBlock && lastPos !== null) {
      if (!prevWasSpace) {
        normText += ' '
        normToPos.push(lastPos)
        prevWasSpace = true
      }
    }
  })

  return { normText, normToPos }
}

function buildDecorations(doc: PmNode, annotations: AnnotationDeco[]): DecorationSet {
  if (!annotations.length) return DecorationSet.empty
  const { normText, normToPos } = buildDocMap(doc)
  const decorations: Decoration[] = []

  for (const ann of annotations) {
    const target = normalizeTrecho(ann.trecho)
    if (!target) continue
    let idx = normText.indexOf(target)
    while (idx !== -1) {
      const from = normToPos[idx]
      const to = normToPos[idx + target.length - 1] + 1
      if (from != null && to != null && from < to) {
        decorations.push(
          Decoration.inline(from, to, {
            class: 'pm-annotation',
            style: `background-color:${ann.color}; border-radius:2px; padding:0 1px; cursor:help;`,
            title: ann.hint,
            'data-annotation-id': ann.id,
          }),
        )
      }
      idx = normText.indexOf(target, idx + target.length)
    }
  }

  return DecorationSet.create(doc, decorations)
}

const AnnotationHighlight = Extension.create<unknown, AnnotationStorage>({
  name: 'annotationHighlight',

  addStorage() {
    return { annotations: [] }
  },

  addCommands() {
    return {
      setAnnotations:
        (annotations: AnnotationDeco[]) =>
        ({ editor, dispatch, tr }) => {
          editor.storage.annotationHighlight.annotations = annotations
          if (dispatch) {
            dispatch(tr.setMeta(annotationHighlightPluginKey, true).setMeta('addToHistory', false))
          }
          return true
        },
    }
  },

  addProseMirrorPlugins() {
    const extension = this
    return [
      new Plugin({
        key: annotationHighlightPluginKey,
        state: {
          init(_, { doc }) {
            return buildDecorations(doc, extension.storage.annotations)
          },
          apply(tr, oldSet) {
            if (tr.docChanged || tr.getMeta(annotationHighlightPluginKey)) {
              return buildDecorations(tr.doc, extension.storage.annotations)
            }
            return oldSet.map(tr.mapping, tr.doc)
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

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    annotationHighlight: {
      /** Define a lista de anotações a realçar (cor + hint por trecho). */
      setAnnotations: (annotations: AnnotationDeco[]) => ReturnType
    }
  }
}

export default AnnotationHighlight
