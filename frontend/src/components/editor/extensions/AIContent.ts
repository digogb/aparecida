import { Node, mergeAttributes } from '@tiptap/core'

export interface AIContentOptions {
  HTMLAttributes: Record<string, unknown>
  onAccept?: (nodeId: string) => void
  onReject?: (nodeId: string) => void
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    aiContent: {
      setAIContent: () => ReturnType
      acceptAIContent: () => ReturnType
      rejectAIContent: () => ReturnType
    }
  }
}

const AIContent = Node.create<AIContentOptions>({
  name: 'aiContent',
  group: 'block',
  content: 'block+',
  isolating: true,
  defining: true,

  addOptions() {
    return {
      HTMLAttributes: {},
      onAccept: undefined,
      onReject: undefined,
    }
  },

  addAttributes() {
    return {
      id: {
        default: () => crypto.randomUUID(),
        parseHTML: (el) => el.getAttribute('data-ai-id'),
        renderHTML: (attrs) => ({ 'data-ai-id': attrs.id }),
      },
      accepted: {
        default: null,
        parseHTML: (el) => {
          const val = el.getAttribute('data-accepted')
          return val === null ? null : val === 'true'
        },
        renderHTML: (attrs) =>
          attrs.accepted !== null ? { 'data-accepted': String(attrs.accepted) } : {},
      },
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="ai-content"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    const accepted = HTMLAttributes['data-accepted']
    let borderClass = 'border-green-400 bg-green-50'
    if (accepted === 'true') borderClass = 'border-blue-400 bg-blue-50'
    if (accepted === 'false') borderClass = 'border-red-300 bg-red-50 opacity-50'

    return [
      'div',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-type': 'ai-content',
        class: `border-l-4 ${borderClass} pl-4 py-2 my-3 rounded-r relative`,
      }),
      [
        'div',
        {
          class:
            'flex items-center gap-2 mb-2 text-xs',
        },
        [
          'span',
          {
            class:
              'inline-flex items-center px-2 py-0.5 rounded bg-green-200 text-green-800 font-medium',
          },
          '✦ Gerado por IA',
        ],
      ],
      ['div', { class: 'ai-content-body' }, 0],
    ]
  },

  addCommands() {
    return {
      setAIContent:
        () =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            content: [{ type: 'paragraph' }],
          })
        },
      acceptAIContent:
        () =>
        ({ tr, state, dispatch }) => {
          const { selection } = state
          const node = state.doc.nodeAt(selection.from)
          if (!node || node.type.name !== this.name) return false
          if (dispatch) {
            tr.setNodeMarkup(selection.from, undefined, {
              ...node.attrs,
              accepted: true,
            })
          }
          return true
        },
      rejectAIContent:
        () =>
        ({ tr, state, dispatch }) => {
          const { selection } = state
          const node = state.doc.nodeAt(selection.from)
          if (!node || node.type.name !== this.name) return false
          if (dispatch) {
            tr.setNodeMarkup(selection.from, undefined, {
              ...node.attrs,
              accepted: false,
            })
          }
          return true
        },
    }
  },
})

export default AIContent
