import { Node, mergeAttributes } from '@tiptap/core'

export interface EmentaOptions {
  HTMLAttributes: Record<string, unknown>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    ementa: {
      setEmenta: () => ReturnType
    }
  }
}

const Ementa = Node.create<EmentaOptions>({
  name: 'ementa',
  group: 'block',
  content: 'block+',
  isolating: true,
  defining: true,

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="ementa"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-type': 'ementa',
        class:
          'border-l-4 pl-6 py-3 my-3 italic rounded-r',
        style: 'border-color: #DDD9D2; background: #EBE8E2; color: #6B6860;',
      }),
      0,
    ]
  },

  addCommands() {
    return {
      setEmenta:
        () =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            content: [{ type: 'paragraph' }],
          })
        },
    }
  },
})

export default Ementa
