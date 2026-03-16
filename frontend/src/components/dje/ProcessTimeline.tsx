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

const TYPE_DOT_COLORS: Record<MovementType, string> = {
  intimacao: 'bg-red-400',
  sentenca: 'bg-purple-400',
  despacho: 'bg-blue-400',
  acordao: 'bg-indigo-400',
  publicacao: 'bg-green-400',
  distribuicao: 'bg-yellow-400',
  outros: 'bg-gray-400',
}

interface ProcessTimelineProps {
  movements: Movement[]
  currentId: string
  onSelect: (movement: Movement) => void
}

export default function ProcessTimeline({
  movements,
  currentId,
  onSelect,
}: ProcessTimelineProps) {
  const sorted = [...movements].sort(
    (a, b) =>
      new Date(a.publication_date).getTime() - new Date(b.publication_date).getTime()
  )

  return (
    <div className="relative">
      <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-gray-200" />
      <ul className="space-y-3">
        {sorted.map((m) => (
          <li key={m.id} className="relative pl-8">
            <div
              className={`absolute left-1.5 top-2 w-3 h-3 rounded-full border-2 border-white ${
                TYPE_DOT_COLORS[m.movement_type]
              } ${currentId === m.id ? 'ring-2 ring-offset-1 ring-blue-400' : ''}`}
            />
            <button
              className={`text-left w-full rounded-md px-2 py-1 hover:bg-gray-50 transition-colors ${
                currentId === m.id ? 'bg-blue-50' : ''
              }`}
              onClick={() => onSelect(m)}
            >
              <p className="text-xs font-medium text-gray-700">
                {TYPE_LABELS[m.movement_type]}
              </p>
              <p className="text-xs text-gray-400">
                {new Date(m.publication_date).toLocaleDateString('pt-BR')}
              </p>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
