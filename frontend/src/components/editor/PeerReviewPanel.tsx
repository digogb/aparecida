import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchPeerReviews,
  respondToPeerReview,
  cancelPeerReview,
} from '../../services/editorApi'
import type { PeerReviewListItem, RespostaTrecho } from '../../types/parecer'

interface Props {
  parecerId: string
  currentUserId: string
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

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, React.CSSProperties> = {
    pendente: { background: '#C4953A18', color: '#C4953A', border: '1px solid #C4953A44' },
    concluida: { background: '#5B755318', color: '#5B7553', border: '1px solid #5B755344' },
    cancelada: { background: '#EBE8E2', color: '#A69B8D', border: '1px solid #DDD9D2' },
  }
  const labels: Record<string, string> = {
    pendente: 'Pendente',
    concluida: 'Concluída',
    cancelada: 'Cancelada',
  }
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-full font-medium"
      style={styles[status] ?? styles.cancelada}
    >
      {labels[status] ?? status}
    </span>
  )
}

function ReviewResponseForm({
  review,
  onResponded,
}: {
  review: PeerReviewListItem
  onResponded: () => void
}) {
  const [respostaGeral, setRespostaGeral] = useState('')
  const [respostasTrechos, setRespostasTrechos] = useState<RespostaTrecho[]>(
    (review.trechos_marcados ?? []).map((t) => ({
      original: t.texto,
      sugestao: '',
      comentario: '',
    }))
  )
  const [isSubmitting, setIsSubmitting] = useState(false)

  const updateTrecho = (idx: number, field: keyof RespostaTrecho, value: string) => {
    setRespostasTrechos((prev) =>
      prev.map((rt, i) => (i === idx ? { ...rt, [field]: value } : rt))
    )
  }

  const handleSubmit = async () => {
    if (!respostaGeral.trim()) return
    setIsSubmitting(true)
    try {
      await respondToPeerReview(review.id, {
        resposta_geral: respostaGeral,
        resposta_trechos: respostasTrechos,
      })
      onResponded()
    } catch (err) {
      console.error('Respond failed:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-3 mt-2">
      {/* Trechos */}
      {respostasTrechos.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
            Trechos para revisar
          </p>
          {respostasTrechos.map((rt, i) => (
            <div
              key={i}
              className="rounded-lg p-2 space-y-1.5"
              style={{ background: '#1B283808', border: '1px solid #DDD9D2' }}
            >
              <p className="text-xs leading-relaxed" style={{ color: '#6B6860' }}>
                "{rt.original}"
              </p>
              <textarea
                className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none resize-none"
                style={{ border: '1px solid #DDD9D2', background: '#FAF8F5', color: '#2D2D3A' }}
                rows={2}
                placeholder="Sua sugestão para este trecho..."
                value={rt.sugestao}
                onChange={(e) => updateTrecho(i, 'sugestao', e.target.value)}
                disabled={isSubmitting}
              />
            </div>
          ))}
        </div>
      )}

      {/* Resposta geral */}
      <div>
        <p className="text-xs font-medium uppercase tracking-widest mb-1" style={{ color: '#A69B8D' }}>
          Parecer geral
        </p>
        <textarea
          className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none resize-none"
          style={{ border: '1px solid #DDD9D2', background: '#FAF8F5', color: '#2D2D3A' }}
          rows={3}
          placeholder="Seu comentário geral sobre os trechos..."
          value={respostaGeral}
          onChange={(e) => setRespostaGeral(e.target.value)}
          disabled={isSubmitting}
          autoFocus
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!respostaGeral.trim() || isSubmitting}
        className="w-full px-3 py-2 text-sm font-medium rounded-lg transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        style={{ background: '#1B2838', color: '#FAF8F5' }}
      >
        {isSubmitting && (
          <svg className="animate-spin w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
        )}
        {isSubmitting ? 'Enviando...' : 'Enviar revisão'}
      </button>
    </div>
  )
}

export default function PeerReviewPanel({ parecerId, currentUserId }: Props) {
  const queryClient = useQueryClient()
  const [cancellingId, setCancellingId] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data: reviews = [] } = useQuery({
    queryKey: ['peer-reviews', parecerId],
    queryFn: () => fetchPeerReviews(parecerId),
    staleTime: 10_000,
  })

  if (reviews.length === 0) return null

  const handleCancel = async (reviewId: string) => {
    setCancellingId(reviewId)
    try {
      await cancelPeerReview(reviewId)
      queryClient.invalidateQueries({ queryKey: ['peer-reviews', parecerId] })
      queryClient.invalidateQueries({ queryKey: ['parecer', parecerId] })
    } catch (err) {
      console.error('Cancel failed:', err)
    } finally {
      setCancellingId(null)
    }
  }

  const handleResponded = () => {
    queryClient.invalidateQueries({ queryKey: ['peer-reviews', parecerId] })
    queryClient.invalidateQueries({ queryKey: ['parecer', parecerId] })
    setExpandedId(null)
  }

  return (
    <div className="p-3" style={{ borderTop: '1px solid #DDD9D2' }}>
      <h3 className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>
        Revisões
      </h3>
      <ul className="space-y-2">
        {reviews.map((review) => {
          const isReviewer = review.reviewer_id === currentUserId
          const isRequester = review.requested_by === currentUserId
          const isExpanded = expandedId === review.id

          return (
            <li
              key={review.id}
              className="rounded-lg overflow-hidden"
              style={{ border: '1px solid #DDD9D2' }}
            >
              {/* Header */}
              <div
                className="px-3 py-2 flex items-start justify-between gap-2 cursor-pointer"
                style={{ background: '#FAF8F5' }}
                onClick={() => setExpandedId(isExpanded ? null : review.id)}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <StatusBadge status={review.status} />
                  </div>
                  <p className="text-xs mt-1 truncate" style={{ color: '#6B6860' }}>
                    {isReviewer
                      ? `De: ${review.requested_by_name}`
                      : `Para: ${review.reviewer_name}`}
                  </p>
                  <p className="text-xs" style={{ color: '#A69B8D' }}>
                    {formatDate(review.created_at)}
                  </p>
                </div>
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#A69B8D"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{
                    flexShrink: 0,
                    marginTop: 4,
                    transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 150ms',
                  }}
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </div>

              {/* Expanded content */}
              {isExpanded && (
                <div className="px-3 pb-3" style={{ borderTop: '1px solid #EBE8E2' }}>
                  {/* Observações do solicitante */}
                  {review.observacoes && (
                    <div className="mt-2">
                      <p className="text-xs font-medium uppercase tracking-widest mb-1" style={{ color: '#A69B8D' }}>
                        Observações
                      </p>
                      <p className="text-xs leading-relaxed" style={{ color: '#6B6860' }}>
                        {review.observacoes}
                      </p>
                    </div>
                  )}

                  {/* Trechos marcados (visualização) */}
                  {review.trechos_marcados && review.trechos_marcados.length > 0 && review.status !== 'pendente' && (
                    <div className="mt-2">
                      <p className="text-xs font-medium uppercase tracking-widest mb-1" style={{ color: '#A69B8D' }}>
                        Trechos ({review.trechos_marcados.length})
                      </p>
                      <ul className="space-y-1">
                        {review.trechos_marcados.map((t, i) => (
                          <li
                            key={i}
                            className="text-xs px-2 py-1 rounded"
                            style={{ background: '#1B283808', color: '#6B6860' }}
                          >
                            "{t.texto}"
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Resposta do revisor (revisão concluída) */}
                  {review.status === 'concluida' && review.resposta_geral && (
                    <div className="mt-2 rounded-lg p-2" style={{ background: '#5B755308', border: '1px solid #5B755344' }}>
                      <p className="text-xs font-medium uppercase tracking-widest mb-1" style={{ color: '#5B7553' }}>
                        Parecer de {review.reviewer_name}
                      </p>
                      <p className="text-xs leading-relaxed" style={{ color: '#2D2D3A' }}>
                        {review.resposta_geral}
                      </p>
                    </div>
                  )}

                  {/* Formulário de resposta — apenas para o revisor com revisão pendente */}
                  {isReviewer && review.status === 'pendente' && (
                    <ReviewResponseForm review={review} onResponded={handleResponded} />
                  )}

                  {/* Cancelar — apenas para o solicitante com revisão pendente */}
                  {isRequester && review.status === 'pendente' && (
                    <button
                      onClick={() => handleCancel(review.id)}
                      disabled={cancellingId === review.id}
                      className="mt-2 w-full px-3 py-1.5 text-xs rounded-lg cursor-pointer disabled:opacity-50"
                      style={{ color: '#8B2332', border: '1px solid #8B233244', background: '#8B233208' }}
                    >
                      {cancellingId === review.id ? 'Cancelando...' : 'Cancelar revisão'}
                    </button>
                  )}
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
