import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchPeerReviews,
  cancelPeerReview,
} from '../../services/editorApi'
import type { PeerReviewListItem } from '../../types/parecer'

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

const STATUS_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  pendente:  { bg: '#C4953A18', color: '#C4953A', label: 'Pendente' },
  concluida: { bg: '#5B755318', color: '#5B7553', label: 'Concluída' },
  cancelada: { bg: '#EBE8E2',   color: '#A69B8D', label: 'Cancelada' },
}

function ReviewDetailModal({
  review,
  onClose,
}: {
  review: PeerReviewListItem
  onClose: () => void
}) {
  const trechos = review.trechos_marcados ?? []
  const respostas = review.resposta_trechos ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl w-full max-w-5xl mx-4 max-h-[85vh] flex flex-col" style={{ background: '#FAF8F5', border: '1.5px solid #DDD9D2', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        {/* Header */}
        <div className="p-4" style={{ borderBottom: '1px solid #EBE8E2' }}>
          <h3 className="text-base font-medium" style={{ color: '#2D2D3A' }}>
            Revisão de {review.reviewer_name}
          </h3>
          <p className="text-sm mt-1" style={{ color: '#A69B8D' }}>
            Solicitada por {review.requested_by_name} em {formatDate(review.created_at)}
            {review.completed_at && ` — concluída em ${formatDate(review.completed_at)}`}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Observações do solicitante */}
          {review.observacoes && (
            <div className="rounded-xl p-3" style={{ background: '#C4953A12', border: '1.5px solid #C4953A33' }}>
              <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#C4953A' }}>
                Observações do solicitante
              </p>
              <p className="text-sm leading-relaxed" style={{ color: '#6B6860' }}>
                {review.observacoes}
              </p>
            </div>
          )}

          {/* Trechos com respostas */}
          {trechos.length > 0 && trechos.map((t, i) => {
            const resposta = respostas[i]
            return (
              <div key={i} className="rounded-xl overflow-hidden" style={{ border: '1.5px solid #DDD9D2' }}>
                {/* Trecho original */}
                <div className="px-4 py-3" style={{ background: '#1B283808' }}>
                  <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#A69B8D' }}>
                    Trecho {i + 1}
                  </p>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#6B6860' }}>
                    "{t.texto}"
                  </p>
                </div>
                {/* Sugestão do revisor */}
                {resposta?.sugestao && (
                  <div className="px-4 py-3" style={{ borderTop: '1px solid #EBE8E2', background: '#5B755308' }}>
                    <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#5B7553' }}>
                      Sugestão do revisor
                    </p>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#2D2D3A' }}>
                      {resposta.sugestao}
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
              <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: '#2D2D3A' }}>
                {review.resposta_geral}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-4" style={{ borderTop: '1px solid #EBE8E2' }}>
          <button
            onClick={onClose}
            className="px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer"
            style={{ color: '#6B6860', background: '#FAF8F5', border: '1.5px solid #DDD9D2' }}
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}

export default function PeerReviewPanel({ parecerId, currentUserId }: Props) {
  const queryClient = useQueryClient()
  const [cancellingId, setCancellingId] = useState<string | null>(null)
  const [viewingReview, setViewingReview] = useState<PeerReviewListItem | null>(null)

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

  return (
    <div className="p-3" style={{ borderTop: '1px solid #DDD9D2' }}>
      <h3 className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>
        Revisões
      </h3>
      <ul className="space-y-1.5">
        {reviews.map((review) => {
          const isReviewer = review.reviewer_id === currentUserId
          const isRequester = review.requested_by === currentUserId
          const st = STATUS_STYLE[review.status] ?? STATUS_STYLE.cancelada

          return (
            <li
              key={review.id}
              className="rounded-lg px-2.5 py-2"
              style={{ background: '#FAF8F5', border: '1px solid #DDD9D2' }}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span
                  className="text-xs px-1.5 py-0.5 rounded-full font-medium"
                  style={{ background: st.bg, color: st.color }}
                >
                  {st.label}
                </span>
                <span className="text-xs ml-auto" style={{ color: '#A69B8D' }}>
                  {formatDate(review.created_at)}
                </span>
              </div>
              <p className="text-xs truncate" style={{ color: '#6B6860' }}>
                {isReviewer
                  ? `De: ${review.requested_by_name}`
                  : `Para: ${review.reviewer_name}`}
              </p>

              {/* Ver revisão — revisões concluídas */}
              {review.status === 'concluida' && (
                <button
                  onClick={() => setViewingReview(review)}
                  className="mt-1.5 w-full px-2 py-1 text-xs rounded-lg cursor-pointer transition-all duration-150 hover:brightness-[0.97]"
                  style={{ color: '#5B7553', border: '1px solid #5B755344', background: '#5B755308' }}
                >
                  Ver revisão
                </button>
              )}

              {/* Cancelar — apenas solicitante com revisão pendente */}
              {isRequester && review.status === 'pendente' && (
                <button
                  onClick={() => handleCancel(review.id)}
                  disabled={cancellingId === review.id}
                  className="mt-1.5 w-full px-2 py-1 text-xs rounded-lg cursor-pointer disabled:opacity-50"
                  style={{ color: '#8B2332', border: '1px solid #8B233244', background: '#8B233208' }}
                >
                  {cancellingId === review.id ? 'Cancelando...' : 'Cancelar revisão'}
                </button>
              )}
            </li>
          )
        })}
      </ul>

      {/* Modal de detalhes da revisão */}
      {viewingReview && (
        <ReviewDetailModal
          review={viewingReview}
          onClose={() => setViewingReview(null)}
        />
      )}
    </div>
  )
}
