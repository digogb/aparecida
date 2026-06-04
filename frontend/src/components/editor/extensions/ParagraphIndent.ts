import { Extension } from '@tiptap/core'

// ParagraphIndent — recuos por parágrafo controlados pela régua, ao estilo do Word.
//
// Adiciona 3 atributos APENAS ao tipo `paragraph` (não a heading/blockquote, para
// preservar a detecção de seções no backend e o estilo calibrado da citação legal):
//   - firstLineIndent → text-indent  (recuo só da 1ª linha)
//   - leftIndent       → margin-left  (recuo do parágrafo inteiro)
//   - rightIndent      → margin-right (recuo da borda direita)
//
// Valores em CENTÍMETROS (número). `null` = usar o padrão da casa (o CSS de
// `.ProseMirror p` aplica text-indent: 4cm; estilo inline só é emitido quando o
// atributo for != null, então parágrafos intocados continuam no gabarito do Dr. Ione).
//
// O backend (docx_generator.py) lê esses mesmos nomes de `node.attrs` no
// content_tiptap salvo para reproduzir o recuo no DOCX/PDF.

const CM_RE = /^(-?\d*\.?\d+)\s*cm$/i

function parseCm(value: string | null | undefined): number | null {
  if (!value) return null
  const m = CM_RE.exec(value.trim())
  return m ? parseFloat(m[1]) : null
}

const ParagraphIndent = Extension.create({
  name: 'paragraphIndent',

  addGlobalAttributes() {
    return [
      {
        types: ['paragraph'],
        attributes: {
          firstLineIndent: {
            default: null,
            parseHTML: (el) => parseCm((el as HTMLElement).style.textIndent),
            renderHTML: (attrs) =>
              attrs.firstLineIndent != null
                ? { style: `text-indent: ${attrs.firstLineIndent}cm` }
                : {},
          },
          leftIndent: {
            default: null,
            parseHTML: (el) => parseCm((el as HTMLElement).style.marginLeft),
            renderHTML: (attrs) =>
              attrs.leftIndent != null
                ? { style: `margin-left: ${attrs.leftIndent}cm` }
                : {},
          },
          rightIndent: {
            default: null,
            parseHTML: (el) => parseCm((el as HTMLElement).style.marginRight),
            renderHTML: (attrs) =>
              attrs.rightIndent != null
                ? { style: `margin-right: ${attrs.rightIndent}cm` }
                : {},
          },
        },
      },
    ]
  },
})

export default ParagraphIndent
