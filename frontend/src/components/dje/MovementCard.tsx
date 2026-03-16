import type { Movement, MovementType } from '../../types/movement'

const TYPE_LABELS: Record<MovementType, string> = {
  intimacao: 'Intimação',
  sentenca: 'Sentença',
  despacho: 'Despacho',
  acordao: 'Acórdão',
  publicacao: 'Publicação',
  distribuicao: 'Distribuição',
  outros: 'Outros',
}

const TYPE_COLORS: Record<MovementType, string> = {
  intimacao: 'bg-red-100 text-red-700',
  sentenca: 'bg-purple-100 text-purple-700',
  despacho: 'bg-blue-100 text-blue-700',
  acordao: 'bg-indigo-100 text-indigo-700',
  publicacao: 'bg-green-100 text-green-700',
  distribuicao: 'bg-yellow-100 text-yellow-700',
  outros: 'bg-gray-100 text-gray-700',
}

function deadlineColor(deadline: string | null): string {
  if (!deadline) return 'text-gray-400'
  const days = Math.ceil(
    (new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  )
  if (days < 0) return 'text-red-600 font-semibold'
  if (days <= 3) return 'text-orange-500 font-semibold'
  if (days <= 7) return 'text-yellow-600'
  return 'text-gray-500'
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR')
}

interface MovementCardProps {
  movement: Movement
  onClick: (movement: Movement) => void
}

export default function MovementCard({ movement, onClick }: MovementCardProps) {
  return (
    <button
      className={`w-full text-left bg-white rounded-lg border p-4 hover:shadow-md transition-shadow ${
        !movement.is_read ? 'border-l-4 border-l-blue-500' : 'border-gray-200'
      }`}
      onClick={() => onClick(movement)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                TYPE_COLORS[movement.movement_type]
              }`}
            >
              {TYPE_LABELS[movement.movement_type]}
            </span>
            {!movement.is_read && (
              <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
            )}
          </div>
          <p className="text-sm font-medium text-gray-900 truncate">
            {movement.process_number}
          </p>
          {movement.municipio_nome && (
            <p className="text-xs text-gray-500 mt-0.5">{movement.municipio_nome}</p>
          )}
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{movement.summary}</p>
        </div>
        <div className="text-right flex-shrink-0 text-xs space-y-1">
          <p className="text-gray-400">Pub: {formatDate(movement.publication_date)}</p>
          {movement.deadline_date && (
            <p className={deadlineColor(movement.deadline_date)}>
              Prazo: {formatDate(movement.deadline_date)}
            </p>
          )}
        </div>
      </div>
    </button>
  )
}
