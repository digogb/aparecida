import { useState } from 'react'
import type { PeerReviewListItem } from '../../types/parecer'

interface Props {
  review: PeerReviewListItem
  onApplySuggestion: (original: string, sugestao: string) => boolean
  onDismiss: (reviewId: string) => void
  onClose: () => void
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function CompletedReviewModal({
  review,
  onApplySuggestion,
  onDismiss,
  onClose,
}: Props) {
  const trechos = review.trechos_marcados ?? []
  const respostas = review.resposta_trechos ?? []
  const [applied, setApplied] = useState<Record<number, 'ok' | 'fail'>>({})

  const handleApply = (idx: number) => {
    const original = trechos[idx]?.texto ?? ''
    const sugestao = respostas[idx]?.sugestao ?? ''
    if (!original || !sugestao) return
    const ok = onApplySuggestion(original, sugestao)
    setApplied((prev) => ({ ...prev, [idx]: ok ? 'ok' : 'fail' }))
  }

  const handleApplyAll = () => {
    const next: Record<number, 'ok' | 'fail'> = { ...applied }
    trechos.forEach((t, i) => {
      if (applied[i] === 'ok') return
      const sugestao = respostas[i]?.sugestao ?? ''
      if (!t.texto || !sugestao) return
      next[i] = onApplySuggestion(t.texto, sugestao) ? 'ok' : 'fail'
    })
    setApplied(next)
  }

  const totalAplicaveis = trechos.filter((t, i) => t.texto && respostas[i]?.sugestao).length
  const totalAplicados = Object.values(applied).filter((v) => v === 'ok').length
  const hasAppliedSome = totalAplicados > 0

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl w-full max-w-5xl mx-4 max-h-[85vh] flex flex-col" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        {/* Header */}
        <div className="p-4" style={{ borderBottom: '1px solid #EDE8DF' }}>
          <h3 className="text-base font-medium" style={{ color: '#0A1120' }}>
            Revisão de {review.reviewer_name}
          </h3>
          <p className="text-sm mt-1" style={{ color: '#A69B8D' }}>
            Concluída em {review.completed_at ? formatDate(review.completed_at) : '—'}
            {totalAplicaveis > 0 && ` — ${totalAplicaveis} sugestão(ões) por trecho`}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {/* Observações do solicitante */}
          {review.observacoes && (
            <div className="rounded-xl p-3" style={{ background: '#C9A94E12', border: '1.5px solid #C9A94E33' }}>
              <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#C9A94E' }}>
                Suas observações (enviadas ao revisor)
              </p>
              <p className="text-sm leading-relaxed" style={{ color: '#6B6860' }}>
                {review.observacoes}
              </p>
            </div>
          )}

          {/* Trechos com sugestões */}
          {trechos.map((t, i) => {
            const resposta = respostas[i]
            const state = applied[i]
            const hasSugestao = !!resposta?.sugestao
            return (
              <div key={i} className="rounded-xl overflow-hidden" style={{ border: '1.5px solid #E0D9CE' }}>
                {/* Header do trecho */}
                <div className="flex items-center justify-between px-4 py-2" style={{ background: state === 'ok' ? '#5B755310' : '#14203808' }}>
                  <span className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
                    Trecho {i + 1}
                  </span>
                  {state === 'ok' && (
                    <span className="text-xs font-medium px-2 py-0.5 rounded-lg" style={{ background: '#5B7553', color: '#FAF8F5' }}>
                      Aplicado
                    </span>
                  )}
                  {state === 'fail' && (
                    <span className="text-xs font-medium px-2 py-0.5 rounded-lg" style={{ background: '#8B2332', color: '#FAF8F5' }}>
                      Não localizado no editor
                    </span>
                  )}
                </div>

                {/* Original */}
                <div className="px-4 py-3" style={{ borderTop: '1px solid #EDE8DF', background: '#8B233208' }}>
                  <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#8B2332' }}>
                    Trecho original
                  </p>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#6B6860' }}>
                    "{t.texto}"
                  </p>
                </div>

                {/* Arrow */}
                {hasSugestao && (
                  <div className="flex items-center justify-center py-1" style={{ background: '#FAF8F5' }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 5v14M19 12l-7 7-7-7"/>
                    </svg>
                  </div>
                )}

                {/* Sugestão */}
                {hasSugestao ? (
                  <div className="px-4 py-3" style={{ background: '#5B755308' }}>
                    <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#5B7553' }}>
                      Sugestão do revisor
                    </p>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap mb-2" style={{ color: '#0A1120' }}>
                      {resposta?.sugestao}
                    </p>
                    {resposta?.comentario && (
                      <p className="text-sm italic mb-2" style={{ color: '#A69B8D' }}>
                        {resposta.comentario}
                      </p>
                    )}
                    <button
                      onClick={() => handleApply(i)}
                      disabled={state === 'ok'}
                      className="px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{ background: '#5B7553', color: '#FAF8F5' }}
                    >
                      {state === 'ok' ? 'Sugestão aplicada' : 'Aplicar sugestão'}
                    </button>
                  </div>
                ) : (
                  <div className="px-4 py-3" style={{ background: '#EDE8DF' }}>
                    <p className="text-sm italic" style={{ color: '#A69B8D' }}>
                      Sem sugestão específica para este trecho.
                    </p>
                  </div>
                )}
              </div>
            )
          })}

          {/* Parecer geral do revisor */}
          {review.resposta_geral && (
            <div className="rounded-xl p-3" style={{ background: '#5B755308', border: '1.5px solid #5B755344' }}>
              <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#5B7553' }}>
                Parecer geral de {review.reviewer_name}
              </p>
              <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#0A1120' }}>
                {review.resposta_geral}
              </p>
            </div>
          )}

          {trechos.length === 0 && !review.resposta_geral && (
            <p className="text-sm text-center py-6" style={{ color: '#A69B8D' }}>
              O revisor não deixou sugestões específicas.
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between gap-2 p-4" style={{ borderTop: '1px solid #EDE8DF' }}>
          <span className="text-sm" style={{ color: '#A69B8D' }}>
            {totalAplicaveis > 0
              ? `${totalAplicados} de ${totalAplicaveis} sugestão(ões) aplicada(s)`
              : ''}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => onDismiss(review.id)}
              className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer"
              style={{ color: '#6B6860', background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}
              title="Não mostrar mais este alerta"
            >
              Dispensar
            </button>
            {totalAplicaveis > 0 && totalAplicados < totalAplicaveis && (
              <button
                onClick={handleApplyAll}
                className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
                style={{ background: '#5B7553', color: '#FAF8F5' }}
              >
                Aplicar todas as sugestões
              </button>
            )}
            <button
              onClick={() => {
                if (hasAppliedSome) {
                  onDismiss(review.id)
                } else {
                  onClose()
                }
              }}
              className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
              style={{ background: '#142038', color: '#FAF8F5' }}
            >
              {hasAppliedSome ? 'Concluir' : 'Fechar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
