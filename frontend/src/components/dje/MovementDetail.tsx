import { useEffect } from 'react'
import { X } from 'lucide-react'
import type { Movement, MovementType } from '../../types/movement'
import ProcessTimeline from './ProcessTimeline'
import { useMarkMovementRead } from '../../hooks/useMovements'

const TYPE_LABELS: Record<MovementType, string> = {
  intimacao: 'Intimação',
  sentenca: 'Sentença',
  despacho: 'Despacho',
  acordao: 'Acórdão',
  publicacao: 'Publicação',
  distribuicao: 'Distribuição',
  outros: 'Outros',
}

function deadlineLabel(deadline: string | null): { text: string; cls: string } | null {
  if (!deadline) return null
  const days = Math.ceil(
    (new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  )
  const text = `${new Date(deadline).toLocaleDateString('pt-BR')} (${
    days < 0 ? `${Math.abs(days)}d vencido` : days === 0 ? 'hoje' : `${days}d restantes`
  })`
  const cls =
    days < 0
      ? 'text-red-600 font-semibold'
      : days <= 3
      ? 'text-orange-500 font-semibold'
      : days <= 7
      ? 'text-yellow-600'
      : 'text-gray-700'
  return { text, cls }
}

interface MovementDetailProps {
  movement: Movement
  relatedMovements: Movement[]
  onClose: () => void
  onSelectRelated: (m: Movement) => void
}

export default function MovementDetail({
  movement,
  relatedMovements,
  onClose,
  onSelectRelated,
}: MovementDetailProps) {
  const markRead = useMarkMovementRead()

  useEffect(() => {
    if (!movement.is_read) {
      markRead.mutate(movement.id)
    }
  }, [movement.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const deadline = deadlineLabel(movement.deadline_date)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                {TYPE_LABELS[movement.movement_type]}
              </span>
              {movement.municipio_nome && (
                <span className="text-xs text-gray-500">{movement.municipio_nome}</span>
              )}
            </div>
            <h2 className="text-lg font-semibold text-gray-900">
              {movement.process_number}
            </h2>
            <p className="text-sm text-gray-500 mt-0.5">{movement.summary}</p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 p-1.5 rounded hover:bg-gray-100 text-gray-400"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Main content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {/* Meta */}
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-400 text-xs uppercase tracking-wide">
                  Publicação
                </span>
                <p className="text-gray-800 mt-0.5">
                  {new Date(movement.publication_date).toLocaleDateString('pt-BR')}
                </p>
              </div>
              {deadline && (
                <div>
                  <span className="text-gray-400 text-xs uppercase tracking-wide">
                    Prazo
                  </span>
                  <p className={`mt-0.5 ${deadline.cls}`}>{deadline.text}</p>
                </div>
              )}
            </div>

            {/* Full text */}
            <div>
              <p className="text-gray-400 text-xs uppercase tracking-wide mb-2">
                Texto Completo
              </p>
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto">
                {movement.full_text || 'Texto não disponível.'}
              </div>
            </div>
          </div>

          {/* Sidebar: Timeline */}
          {relatedMovements.length > 1 && (
            <div className="w-52 border-l p-4 overflow-y-auto flex-shrink-0">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                Histórico
              </p>
              <ProcessTimeline
                movements={relatedMovements}
                currentId={movement.id}
                onSelect={onSelectRelated}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
