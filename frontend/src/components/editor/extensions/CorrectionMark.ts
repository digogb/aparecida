import { Mark, mergeAttributes } from '@tiptap/core'

export interface CorrectionMarkOptions {
  HTMLAttributes: Record<string, unknown>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    correctionMark: {
      setCorrectionMark: () => ReturnType
      unsetCorrectionMark: () => ReturnType
      toggleCorrectionMark: () => ReturnType
    }
  }
}

const CorrectionMark = Mark.create<CorrectionMarkOptions>({
  name: 'correctionMark',

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  parseHTML() {
    return [{ tag: 'mark[data-correction]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'mark',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-correction': 'true',
        style:
          'background-color: #FEF3C7; border-bottom: 2px solid #F59E0B; padding: 1px 0; cursor: pointer;',
      }),
      0,
    ]
  },

  addCommands() {
    return {
      setCorrectionMark:
        () =>
        ({ commands }) =>
          commands.setMark(this.name),
      unsetCorrectionMark:
        () =>
        ({ commands }) =>
          commands.unsetMark(this.name),
      toggleCorrectionMark:
        () =>
        ({ commands }) =>
          commands.toggleMark(this.name),
    }
  },

  addKeyboardShortcuts() {
    return {
      'Mod-Shift-m': () => this.editor.commands.toggleCorrectionMark(),
    }
  },
})

export default CorrectionMark
