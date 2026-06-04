// Ruler.tsx — Régua de recuos funcional, ao estilo do Word.
//
// Constantes espelhadas do DOCX gerado (docx_generator.py usa o template padrão
// do python-docx → papel US Letter):
//   - Página US Letter: 21,59 cm de largura (8,5")
//   - Margens laterais: 3 cm (esquerda e direita) → área útil de 15,59 cm
//   - Recuo de primeira linha padrão do corpo: 4 cm (RECUO_PRIMEIRA_LINHA = Cm(4.0))
//
// A numeração começa em 0 na margem esquerda (3 cm da borda do papel). Três
// marcadores arrastáveis controlam, POR PARÁGRAFO (atributos da extensão
// ParagraphIndent), o recuo de 1ª linha, o recuo à esquerda e o recuo à direita.
// Parágrafo sem atributo segue o padrão calibrado da casa (1ª linha 4 cm, esq/dir 0).
//
// Marcadores ficam ocultos quando o cursor está em heading/citação (formatação fixa).

import { useCallback, useEffect, useRef, useState } from 'react'
import type { Editor } from '@tiptap/react'

const PAGE_CM = 21.59 // US Letter (8,5")
const MARGIN_LEFT_CM = 3
const MARGIN_RIGHT_CM = 3
const TEXT_WIDTH_CM = PAGE_CM - MARGIN_LEFT_CM - MARGIN_RIGHT_CM // 15,59 cm
const DEFAULT_FIRST_LINE_CM = 4 // padrão da casa
const SNAP_CM = 0.25
const MIN_GAP_CM = 0.5 // folga mínima entre recuo esq e dir

type HandleType = 'first' | 'left' | 'right'

interface ParaIndents {
  first: number // recuo de 1ª linha efetivo (cm, a partir do recuo esquerdo)
  left: number // recuo à esquerda efetivo (cm)
  right: number // recuo à direita efetivo (cm)
}

function snap(cm: number): number {
  return Math.round(cm / SNAP_CM) * SNAP_CM
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, v))
}

function readIndents(editor: Editor | null | undefined): ParaIndents {
  const a = editor ? editor.getAttributes('paragraph') : {}
  return {
    first: a.firstLineIndent != null ? a.firstLineIndent : DEFAULT_FIRST_LINE_CM,
    left: a.leftIndent != null ? a.leftIndent : 0,
    right: a.rightIndent != null ? a.rightIndent : 0,
  }
}

export default function Ruler({ editor }: { editor?: Editor | null }) {
  const rulerRef = useRef<HTMLDivElement>(null)
  const dragRef = useRef<HandleType | null>(null)
  const [, force] = useState(0)
  const [dragLabel, setDragLabel] = useState<{ cm: number; leftCm: number } | null>(null)

  // Re-renderiza ao mudar seleção/documento para reposicionar os marcadores.
  useEffect(() => {
    if (!editor) return
    const rerender = () => force((n) => n + 1)
    editor.on('selectionUpdate', rerender)
    editor.on('transaction', rerender)
    return () => {
      editor.off('selectionUpdate', rerender)
      editor.off('transaction', rerender)
    }
  }, [editor])

  const interactive =
    !!editor && !editor.isActive('heading') && !editor.isActive('blockquote')
  const indents = readIndents(editor)

  // Converte clientX → cm dentro da área útil (0..15), com snap.
  const xToAreaCm = useCallback((clientX: number): number => {
    const rect = rulerRef.current?.getBoundingClientRect()
    if (!rect || rect.width === 0) return 0
    const cmFromRulerLeft = ((clientX - rect.left) / rect.width) * PAGE_CM
    return snap(clamp(cmFromRulerLeft - MARGIN_LEFT_CM, 0, TEXT_WIDTH_CM))
  }, [])

  const applyDrag = useCallback(
    (type: HandleType, areaCm: number) => {
      if (!editor) return
      const cur = readIndents(editor)
      let attrs: Record<string, number> = {}
      let label = { cm: 0, leftCm: 0 }

      if (type === 'left') {
        const left = clamp(areaCm, 0, TEXT_WIDTH_CM - cur.right - MIN_GAP_CM)
        attrs = { leftIndent: left }
        label = { cm: left, leftCm: left }
      } else if (type === 'first') {
        // areaCm é a posição absoluta da 1ª linha; o atributo é o offset a partir do recuo esquerdo.
        const first = clamp(areaCm - cur.left, 0, TEXT_WIDTH_CM - cur.left - cur.right)
        attrs = { firstLineIndent: first }
        label = { cm: first, leftCm: cur.left + first }
      } else {
        const right = clamp(TEXT_WIDTH_CM - areaCm, 0, TEXT_WIDTH_CM - cur.left - MIN_GAP_CM)
        attrs = { rightIndent: right }
        label = { cm: right, leftCm: TEXT_WIDTH_CM - right }
      }

      editor.commands.updateAttributes('paragraph', attrs)
      setDragLabel(label)
    },
    [editor]
  )

  const onHandleMouseDown = useCallback(
    (type: HandleType) => (e: React.MouseEvent) => {
      if (!interactive) return
      e.preventDefault()
      dragRef.current = type
      applyDrag(type, xToAreaCm(e.clientX))

      const onMove = (ev: MouseEvent) => {
        if (!dragRef.current) return
        applyDrag(dragRef.current, xToAreaCm(ev.clientX))
      }
      const onUp = () => {
        dragRef.current = null
        setDragLabel(null)
        window.removeEventListener('mousemove', onMove)
        window.removeEventListener('mouseup', onUp)
      }
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    },
    [interactive, applyDrag, xToAreaCm]
  )

  const ticks = Array.from({ length: TEXT_WIDTH_CM + 1 }, (_, i) => i)

  // Posições dos marcadores (cm a partir da borda esquerda da régua).
  const leftMarkerCm = MARGIN_LEFT_CM + indents.left
  const firstMarkerCm = MARGIN_LEFT_CM + indents.left + indents.first
  const rightMarkerCm = MARGIN_LEFT_CM + TEXT_WIDTH_CM - indents.right

  return (
    <div
      ref={rulerRef}
      className="editor-ruler select-none"
      style={{
        width: '21.59cm',
        height: 26,
        // position: sticky vem da classe .editor-ruler (index.css) — NÃO definir
        // position inline aqui, senão sobrescreve o sticky e a régua some após a
        // primeira tela de rolagem. sticky já é contexto p/ os filhos absolutos.
        background: '#EDE8DF',
        borderBottom: '1px solid #E0D9CE',
      }}
    >
      {/* Área útil de texto (entre as margens) */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: `${MARGIN_LEFT_CM}cm`,
          width: `${TEXT_WIDTH_CM}cm`,
          background: '#FAF8F5',
          borderLeft: '1px solid #D8CFBF',
          borderRight: '1px solid #D8CFBF',
        }}
      />

      {/* Ticks + números (1 em 1 cm, a partir da margem esquerda) */}
      {ticks.map((n) => (
        <div
          key={n}
          style={{ position: 'absolute', top: 0, left: `${MARGIN_LEFT_CM + n}cm`, height: '100%' }}
        >
          <div style={{ position: 'absolute', top: 12, height: 8, width: 1, background: '#B7AD9C' }} />
          <span
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              transform: 'translateX(-50%)',
              fontSize: 9,
              lineHeight: '11px',
              color: '#8A8170',
              fontFamily: 'Outfit, sans-serif',
            }}
          >
            {n}
          </span>
        </div>
      ))}

      {/* ===== Marcadores ===== */}
      {/* Recuo de 1ª linha — triângulo no TOPO (apontando p/ baixo) */}
      <div
        onMouseDown={onHandleMouseDown('first')}
        title="Recuo de primeira linha"
        style={{
          position: 'absolute',
          top: 1,
          left: `${firstMarkerCm}cm`,
          transform: 'translateX(-50%)',
          width: 0,
          height: 0,
          borderLeft: '5px solid transparent',
          borderRight: '5px solid transparent',
          borderTop: '7px solid #C9A94E',
          cursor: interactive ? 'ew-resize' : 'default',
          opacity: interactive ? 1 : 0.45,
          zIndex: 2,
        }}
      />

      {/* Recuo à esquerda — triângulo na BASE (apontando p/ cima) */}
      <div
        onMouseDown={onHandleMouseDown('left')}
        title="Recuo à esquerda"
        style={{
          position: 'absolute',
          bottom: 1,
          left: `${leftMarkerCm}cm`,
          transform: 'translateX(-50%)',
          width: 0,
          height: 0,
          borderLeft: '5px solid transparent',
          borderRight: '5px solid transparent',
          borderBottom: '7px solid #9C7B2E',
          cursor: interactive ? 'ew-resize' : 'default',
          opacity: interactive ? 1 : 0.45,
          zIndex: 2,
        }}
      />

      {/* Recuo à direita — triângulo na BASE (apontando p/ cima) */}
      <div
        onMouseDown={onHandleMouseDown('right')}
        title="Recuo à direita"
        style={{
          position: 'absolute',
          bottom: 1,
          left: `${rightMarkerCm}cm`,
          transform: 'translateX(-50%)',
          width: 0,
          height: 0,
          borderLeft: '5px solid transparent',
          borderRight: '5px solid transparent',
          borderBottom: '7px solid #9C7B2E',
          cursor: interactive ? 'ew-resize' : 'default',
          opacity: interactive ? 1 : 0.45,
          zIndex: 2,
        }}
      />

      {/* Tooltip de cm durante o arraste */}
      {dragLabel && (
        <div
          style={{
            position: 'absolute',
            top: -20,
            left: `${MARGIN_LEFT_CM + dragLabel.leftCm}cm`,
            transform: 'translateX(-50%)',
            background: '#2E2A22',
            color: '#fff',
            fontSize: 10,
            lineHeight: '14px',
            padding: '1px 6px',
            borderRadius: 4,
            fontFamily: 'Outfit, sans-serif',
            whiteSpace: 'nowrap',
            zIndex: 3,
          }}
        >
          {dragLabel.cm.toFixed(2).replace('.', ',')} cm
        </div>
      )}
    </div>
  )
}
