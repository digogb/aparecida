import { Node, mergeAttributes } from '@tiptap/core'

export interface CitacaoLegalOptions {
  HTMLAttributes: Record<string, unknown>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    citacaoLegal: {
      setCitacaoLegal: (attrs?: { referencia?: string }) => ReturnType
    }
  }
}

const CitacaoLegal = Node.create<CitacaoLegalOptions>({
  name: 'citacaoLegal',
  group: 'block',
  content: 'block+',
  isolating: true,
  defining: true,

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  addAttributes() {
    return {
      referencia: {
        default: '',
        parseHTML: (el) => el.getAttribute('data-referencia') || '',
        renderHTML: (attrs) => ({ 'data-referencia': attrs.referencia }),
      },
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="citacao-legal"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-type': 'citacao-legal',
        class:
          'border-l-4 border-purple-500 bg-purple-50 pl-4 py-2 my-3 rounded-r',
      }),
      [
        'div',
        { class: 'text-xs text-purple-600 font-semibold mb-1' },
        HTMLAttributes['data-referencia'] || 'Citação Legal',
      ],
      ['div', { class: 'citacao-content' }, 0],
    ]
  },

  addCommands() {
    return {
      setCitacaoLegal:
        (attrs) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs,
            content: [{ type: 'paragraph' }],
          })
        },
    }
  },
})

export default CitacaoLegal
