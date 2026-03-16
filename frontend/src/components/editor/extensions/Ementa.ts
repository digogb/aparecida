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
          'border-l-4 border-gray-400 bg-gray-50 pl-6 py-3 my-3 italic text-gray-700 rounded-r',
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
