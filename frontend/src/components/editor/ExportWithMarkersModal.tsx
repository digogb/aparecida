import type { MarcadorRevisao } from '../../utils/revisaoMarkers'

interface Props {
  format: 'docx' | 'pdf'
  marcadores: MarcadorRevisao[]
  onConfirm: () => void
  onClose: () => void
}

/**
 * Modal que avisa o advogado sobre marcadores `[REVISAR—]` / `[!VERIFICAR:!]`
 * antes de exportar o parecer. Lista cada marcador agrupado por seção e
 * explica como resolvê-lo. Substitui o `window.confirm` nativo, alinhado
 * ao padrão visual do app.
 */
export default function ExportWithMarkersModal({
  format,
  marcadores,
  onConfirm,
  onClose,
}: Props) {
  // Agrupa por seção
  const porSecao = new Map<string, MarcadorRevisao[]>()
  for (const m of marcadores) {
    const chave = m.secao ?? '—'
    const lista = porSecao.get(chave) ?? []
    lista.push(m)
    porSecao.set(chave, lista)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(27,40,56,0.5)' }}
      onClick={onClose}
    >
      <div
        className="rounded-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col"
        style={{
          background: '#FAF8F5',
          border: '1.5px solid #E0D9CE',
          boxShadow: '0 20px 60px rgba(27,40,56,0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 flex items-start gap-3" style={{ borderBottom: '1px solid #EDE8DF' }}>
          <div
            className="shrink-0 rounded-full p-2"
            style={{ background: '#C0000018', color: '#C00000' }}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-base font-medium" style={{ color: '#0A1120' }}>
              {marcadores.length} ponto{marcadores.length > 1 ? 's' : ''} pendente
              {marcadores.length > 1 ? 's' : ''} de revisão humana
            </h3>
            <p className="text-sm mt-1" style={{ color: '#6B6860' }}>
              No <span className="font-mono">.{format}</span> exportado, esses trechos aparecerão
              em <span style={{ color: '#C00000', fontWeight: 700 }}>VERMELHO/NEGRITO</span>.
              Verifique cada um e remova os marcadores antes de assinar.
            </p>
          </div>
        </div>

        {/* Lista de marcadores */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {[...porSecao.entries()].map(([secao, lista]) => (
            <div key={secao}>
              <div
                className="text-xs font-semibold uppercase tracking-wider mb-2"
                style={{ color: '#A69B8D' }}
              >
                {secao}
              </div>
              <ul className="space-y-2">
                {lista.map((m) => (
                  <li
                    key={m.indice}
                    className="text-sm px-3 py-2 rounded-lg"
                    style={{
                      background: '#FBF7EE',
                      borderLeft: '3px solid #C00000',
                    }}
                  >
                    <div
                      className="font-mono text-xs mb-1"
                      style={{ color: '#C00000', fontWeight: 700 }}
                    >
                      {m.tipo === 'revisar' ? '[REVISAR]' : '[VERIFICAR]'}
                    </div>
                    <div style={{ color: '#3B3833' }}>{m.conteudo}</div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Como resolver */}
        <div className="px-4 py-3" style={{ background: '#C9A94E10', borderTop: '1px solid #EDE8DF' }}>
          <p className="text-sm" style={{ color: '#6B6860' }}>
            <span className="font-medium" style={{ color: '#0A1120' }}>Como resolver: </span>
            no editor, localize o trecho em vermelho (passe o mouse para o tooltip),
            verifique a informação e edite o texto para substituir o marcador pelo dado definitivo.
          </p>
        </div>

        {/* Footer */}
        <div
          className="flex justify-end gap-2 p-4"
          style={{ borderTop: '1px solid #EDE8DF' }}
        >
          <button
            onClick={onClose}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer"
            style={{
              color: '#6B6860',
              background: '#FAF8F5',
              border: '1.5px solid #E0D9CE',
            }}
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
            style={{ background: '#142038', color: '#FAF8F5' }}
          >
            Exportar mesmo assim
          </button>
        </div>
      </div>
    </div>
  )
}
