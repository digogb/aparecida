import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

export const searchPluginKey = new PluginKey('searchHighlight')

export interface SearchHighlightStorage {
  searchTerm: string
  results: number
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    searchHighlight: {
      setSearchTerm: (term: string) => ReturnType
    }
  }
}

const SearchHighlight = Extension.create<Record<string, never>, SearchHighlightStorage>({
  name: 'searchHighlight',

  addStorage() {
    return { searchTerm: '', results: 0 }
  },

  addCommands() {
    return {
      setSearchTerm:
        (term: string) =>
        ({ tr, dispatch }) => {
          if (dispatch) {
            this.storage.searchTerm = term
            tr.setMeta(searchPluginKey, term)
            dispatch(tr)
          }
          return true
        },
    }
  },

  addProseMirrorPlugins() {
    const storage = this.storage
    return [
      new Plugin({
        key: searchPluginKey,
        state: {
          init() {
            return DecorationSet.empty
          },
          apply(tr, oldSet) {
            if (!tr.getMeta(searchPluginKey) && tr.getMeta(searchPluginKey) !== '') {
              if (tr.docChanged) {
                return oldSet.map(tr.mapping, tr.doc)
              }
              return oldSet
            }

            const term = storage.searchTerm
            if (!term || term.length < 2) {
              storage.results = 0
              return DecorationSet.empty
            }

            const decorations: Decoration[] = []
            const lowerTerm = term.toLowerCase()

            tr.doc.descendants((node, pos) => {
              if (!node.isText || !node.text) return
              const lowerText = node.text.toLowerCase()
              let idx = lowerText.indexOf(lowerTerm)
              while (idx !== -1) {
                decorations.push(
                  Decoration.inline(pos + idx, pos + idx + term.length, {
                    style: 'background-color: #C4953A55; border-radius: 2px; color: #1B2838;',
                  })
                )
                idx = lowerText.indexOf(lowerTerm, idx + 1)
              }
            })

            storage.results = decorations.length
            return DecorationSet.create(tr.doc, decorations)
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

export default SearchHighlight
