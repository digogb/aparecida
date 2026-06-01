// Ruler.tsx — Régua de recuos espelhando as margens do DOCX impresso.
//
// Constantes espelhadas de backend/app/services/docx_generator.py:
//   - Página A4: 21 cm de largura
//   - Margens laterais: 3 cm (esquerda e direita) → área útil de 15 cm
//   - Recuo de primeira linha do corpo: 4 cm (RECUO_PRIMEIRA_LINHA = Cm(4.0))
//
// A numeração começa em 0 na margem esquerda (3 cm da borda do papel), então o
// marcador de recuo cai exatamente sobre o "4" — comunicando "recuo de 4 cm".

const PAGE_CM = 21
const MARGIN_LEFT_CM = 3
const MARGIN_RIGHT_CM = 3
const TEXT_WIDTH_CM = PAGE_CM - MARGIN_LEFT_CM - MARGIN_RIGHT_CM // 15 cm
const FIRST_LINE_INDENT_CM = 4

export default function Ruler() {
  // Ticks dentro da área de texto: 0..15
  const ticks = Array.from({ length: TEXT_WIDTH_CM + 1 }, (_, i) => i)

  return (
    <div
      className="editor-ruler select-none"
      style={{
        width: '21cm',
        height: 26,
        position: 'relative',
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
          <div
            style={{
              position: 'absolute',
              top: 12,
              height: 8,
              width: 1,
              background: '#B7AD9C',
            }}
          />
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

      {/* Marcador do recuo de primeira linha (4 cm) — triângulo dourado */}
      <div
        title="Recuo de primeira linha: 4 cm"
        style={{
          position: 'absolute',
          top: 1,
          left: `${MARGIN_LEFT_CM + FIRST_LINE_INDENT_CM}cm`,
          transform: 'translateX(-50%)',
          width: 0,
          height: 0,
          borderLeft: '5px solid transparent',
          borderRight: '5px solid transparent',
          borderTop: '7px solid #C9A94E',
        }}
      />
    </div>
  )
}
