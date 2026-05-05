import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'
import { highlightColorForInitials } from '../../../utils/authorColors'

export const diffPluginKey = new PluginKey<DecorationSet>('diffHighlight')

export interface DiffRange {
  from: number
  to: number
  /** Iniciais do autor que adicionou estas palavras (controla a cor do destaque) */
  initials?: string
}

export interface DiffAnnotation {
  wordRanges: DiffRange[]
  /** Posição do primeiro char de cada parágrafo alterado (para medir Y no DOM) */
  paraFirstPositions: number[]
  initials: string
  /** Iniciais por parágrafo (substitui initials quando presente).
   *  Múltiplos autores no mesmo parágrafo são separados por ' / '. */
  paraInitials?: string[]
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    diffHighlight: {
      setDiffAnnotation: (annotation: DiffAnnotation | null) => ReturnType
    }
  }
}

const DiffHighlight = Extension.create({
  name: 'diffHighlight',

  addCommands() {
    return {
      setDiffAnnotation:
        (annotation: DiffAnnotation | null) =>
        ({ tr, dispatch }) => {
          if (dispatch) {
            tr.setMeta(diffPluginKey, annotation ?? false)
            dispatch(tr)
          }
          return true
        },
    }
  },

  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: diffPluginKey,
        state: {
          init: () => DecorationSet.empty,
          apply(tr, oldSet) {
            const meta = tr.getMeta(diffPluginKey)
            if (meta !== undefined) {
              if (!meta) return DecorationSet.empty
              const ann = meta as DiffAnnotation
              const decos: Decoration[] = ann.wordRanges.map(r => {
                const bg = highlightColorForInitials(r.initials || ann.initials || '')
                return Decoration.inline(r.from, r.to, {
                  style: `background:${bg};border-radius:2px;`,
                })
              })
              return DecorationSet.create(tr.doc, decos)
            }
            if (tr.docChanged) return oldSet.map(tr.mapping, tr.doc)
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

export default DiffHighlight
