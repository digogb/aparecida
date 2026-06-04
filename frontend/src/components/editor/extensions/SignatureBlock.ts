import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import type { Node as PmNode } from '@tiptap/pm/model'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

/**
 * Renderiza o fecho final do parecer — "É o parecer..." + data + bloco de
 * assinaturas — como um widget NÃO-EDITÁVEL ao final do documento, espelhando
 * exatamente o que o `docx_generator.py` (canon) acrescenta na exportação.
 *
 * É camada de exibição: NÃO entra no conteúdo salvo (content_tiptap), então o
 * gerador DOCX continua reconstruindo o fecho/assinaturas a partir das próprias
 * constantes — sem duplicação nem risco de o usuário descalibrar o bloco fixo
 * do Dr. Ione.
 *
 * Constantes byte-espelhadas de docx_generator.py
 * (NÃO ALTERAR sem aprovação do Dr. Ione).
 */

export const signatureBlockPluginKey = new PluginKey('signatureBlock')

const FECHO = 'É o parecer, submetido à superior consideração.'

const ADVOGADOS = {
  ione: ['FRANCISCO IONE PEREIRA LIMA', 'OAB-CE nº 4.585'],
  matheus: ['MATHEUS NOGUEIRA PEREIRA LIMA', 'OAB-CE nº 31.251'],
  flavio: ['FLÁVIO HENRIQUE LUNA SILVA', 'OAB-CE nº 31.252'],
  valeria: ['VALÉRIA MATIAS DE ALENCAR', 'OAB/CE nº 36.666'],
}

interface SignatureStorage {
  dataLine: string
}

function buildDeco(doc: PmNode, dataLine: string): DecorationSet {
  const showFecho = !docHasFecho(doc)
  return DecorationSet.create(doc, [
    Decoration.widget(doc.content.size, () => buildSignatureDom(dataLine, showFecho), {
      side: 1,
      key: `signature-${showFecho ? 'f' : 'n'}-${dataLine}`,
    }),
  ])
}

function assinaturaSimples(nome: string, oab: string, extraClass = ''): HTMLElement {
  const wrap = document.createElement('div')
  wrap.className = `pm-signature-single ${extraClass}`.trim()
  const n = document.createElement('div')
  n.className = 'pm-signature-nome'
  n.textContent = nome
  const o = document.createElement('div')
  o.className = 'pm-signature-oab'
  o.textContent = oab
  wrap.append(n, o)
  return wrap
}

/** O fecho já costuma estar no texto da conclusão (conteúdo editável). Detecta
 *  isso pra NÃO duplicar a frase no bloco fixo. */
function docHasFecho(doc: PmNode): boolean {
  const txt = (doc.textContent || '').toLowerCase()
  return txt.includes('submetido à superior consideração')
}

function buildSignatureDom(dataLine: string, showFecho: boolean): HTMLElement {
  const root = document.createElement('div')
  root.className = 'pm-signature'
  root.setAttribute('contenteditable', 'false')

  if (showFecho) {
    const fecho = document.createElement('p')
    fecho.className = 'pm-signature-fecho'
    fecho.textContent = FECHO
    root.appendChild(fecho)
  }

  if (dataLine) {
    const data = document.createElement('p')
    data.className = 'pm-signature-data'
    data.textContent = dataLine
    root.appendChild(data)
  }

  // Ione (centralizado/recuado, sozinho na primeira linha)
  root.appendChild(assinaturaSimples(ADVOGADOS.ione[0], ADVOGADOS.ione[1], 'pm-signature-ione'))

  // Matheus + Flávio lado a lado (duas colunas)
  const dupla = document.createElement('div')
  dupla.className = 'pm-signature-dupla'
  dupla.appendChild(assinaturaSimples(ADVOGADOS.matheus[0], ADVOGADOS.matheus[1]))
  dupla.appendChild(assinaturaSimples(ADVOGADOS.flavio[0], ADVOGADOS.flavio[1]))
  root.appendChild(dupla)

  // Valéria (sozinha, recuada)
  root.appendChild(assinaturaSimples(ADVOGADOS.valeria[0], ADVOGADOS.valeria[1], 'pm-signature-valeria'))

  return root
}

const SignatureBlock = Extension.create<unknown, SignatureStorage>({
  name: 'signatureBlock',

  addStorage() {
    return { dataLine: '' }
  },

  addCommands() {
    return {
      setSignatureDataLine:
        (line: string) =>
        ({ editor, dispatch, tr }) => {
          editor.storage.signatureBlock.dataLine = line
          if (dispatch) {
            dispatch(tr.setMeta(signatureBlockPluginKey, true).setMeta('addToHistory', false))
          }
          return true
        },
    }
  },

  addProseMirrorPlugins() {
    const extension = this
    return [
      new Plugin({
        key: signatureBlockPluginKey,
        state: {
          init(_, { doc }) {
            return buildDeco(doc, extension.storage.dataLine as string)
          },
          apply(tr, oldSet) {
            // Reconstrói quando o documento muda (posição final / presença do
            // fecho) ou quando a linha de data é atualizada (meta).
            if (tr.docChanged || tr.getMeta(signatureBlockPluginKey)) {
              return buildDeco(tr.doc, extension.storage.dataLine as string)
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
    signatureBlock: {
      /** Define a linha "Município/UF, DD de mês de AAAA." do fecho. */
      setSignatureDataLine: (line: string) => ReturnType
    }
  }
}

export default SignatureBlock
