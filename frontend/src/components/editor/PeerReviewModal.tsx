import { useEffect, useState } from 'react'
import { fetchLawyers } from '../../services/editorApi'
import type { Lawyer } from '../../types/parecer'

interface Props {
  markedTexts: string[]
  onSubmit: (reviewerId: string, observacoes: string) => void
  onClose: () => void
  isLoading?: boolean
}

export default function PeerReviewModal({
  markedTexts,
  onSubmit,
  onClose,
  isLoading,
}: Props) {
  const [lawyers, setLawyers] = useState<Lawyer[]>([])
  const [selectedReviewerId, setSelectedReviewerId] = useState('')
  const [observacoes, setObservacoes] = useState('')
  const [loadingLawyers, setLoadingLawyers] = useState(true)

  useEffect(() => {
    fetchLawyers()
      .then(setLawyers)
      .catch(console.error)
      .finally(() => setLoadingLawyers(false))
  }, [])

  const canSubmit = selectedReviewerId && observacoes.trim() && !isLoading

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(27,40,56,0.5)' }}
    >
      <div
        className="rounded-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col"
        style={{
          background: '#FAF8F5',
          border: '1.5px solid #E0D9CE',
          boxShadow: '0 20px 60px rgba(27,40,56,0.15)',
        }}
      >
        {/* Header */}
        <div className="p-4" style={{ borderBottom: '1px solid #EDE8DF' }}>
          <h3 className="text-base font-medium" style={{ color: '#0A1120' }}>
            Enviar para revisão de colega
          </h3>
          <p className="text-sm mt-1" style={{ color: '#A69B8D' }}>
            {markedTexts.length > 0
              ? 'Os trechos marcados serão enviados junto com suas observações.'
              : 'O colega poderá revisar o parecer e enviar sugestões.'}
          </p>
        </div>

        <div className="p-4 overflow-y-auto flex-1 space-y-4">
          {/* Trechos marcados */}
          {markedTexts.length > 0 && (
            <div>
              <label
                className="text-sm font-medium uppercase tracking-widest"
                style={{ color: '#A69B8D' }}
              >
                Trechos marcados ({markedTexts.length})
              </label>
              <ul className="mt-2 space-y-1.5">
                {markedTexts.map((text, i) => (
                  <li
                    key={i}
                    className="text-sm px-3 py-2 rounded-lg"
                    style={{
                      background: '#14203810',
                      borderLeft: '3px solid #142038',
                      color: '#6B6860',
                    }}
                  >
                    "{text}"
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Seleção de revisor */}
          <div>
            <label
              className="text-sm font-medium uppercase tracking-widest"
              style={{ color: '#A69B8D' }}
            >
              Revisor
            </label>
            {loadingLawyers ? (
              <div className="mt-2 text-sm" style={{ color: '#A69B8D' }}>
                Carregando advogados...
              </div>
            ) : lawyers.length === 0 ? (
              <div className="mt-2 text-sm" style={{ color: '#A69B8D' }}>
                Nenhum advogado disponível.
              </div>
            ) : (
              <select
                className="mt-2 w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2 disabled:opacity-50"
                style={{
                  border: '1.5px solid #E0D9CE',
                  color: selectedReviewerId ? '#0A1120' : '#A69B8D',
                  background: '#FAF8F5',
                } as React.CSSProperties}
                value={selectedReviewerId}
                onChange={(e) => setSelectedReviewerId(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Selecione um advogado...</option>
                {lawyers.map((l) => (
                  <option key={l.id} value={l.id}>
                    {l.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Observações */}
          <div>
            <label
              className="text-sm font-medium uppercase tracking-widest"
              style={{ color: '#A69B8D' }}
            >
              Observações para o revisor
            </label>
            <textarea
              className="mt-2 w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2 resize-none disabled:opacity-50"
              style={{
                border: '1.5px solid #E0D9CE',
                color: '#0A1120',
                background: '#FAF8F5',
              } as React.CSSProperties}
              rows={4}
              placeholder="Ex: Verificar a fundamentação legal do parágrafo 3. A citação da Lei 14.133 pode estar desatualizada..."
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
          </div>
        </div>

        {/* Footer */}
        <div
          className="flex justify-end gap-2 p-4"
          style={{ borderTop: '1px solid #EDE8DF' }}
        >
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              color: '#6B6860',
              background: '#FAF8F5',
              border: '1.5px solid #E0D9CE',
            }}
          >
            Cancelar
          </button>
          <button
            onClick={() => onSubmit(selectedReviewerId, observacoes)}
            disabled={!canSubmit}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            style={{ background: '#142038', color: '#FAF8F5' }}
          >
            {isLoading && (
              <svg
                className="animate-spin w-4 h-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
              >
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
            )}
            {isLoading ? 'Enviando...' : 'Enviar para colega'}
          </button>
        </div>
      </div>
    </div>
  )
}
