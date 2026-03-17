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
  intimacao:    '#DC2626',
  sentenca:     '#7C3AED',
  despacho:     '#0284C7',
  acordao:      '#059669',
  publicacao:   '#D97706',
  distribuicao: '#7C3AED',
  outros:       '#6B7280',
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('pt-BR')
}

interface ProcessTimelineProps {
  movements: Movement[]
  currentId: string
  onSelect: (movement: Movement) => void
}

export default function ProcessTimeline({ movements, currentId, onSelect }: ProcessTimelineProps) {
  const sorted = [...movements].sort(
    (a, b) => new Date(a.published_at ?? a.created_at).getTime() - new Date(b.published_at ?? b.created_at).getTime()
  )

  return (
    <div className="relative">
      <div className="absolute left-3 top-0 bottom-0 w-0.5" style={{ background: '#E5E3DC' }} />
      <ul className="space-y-3">
        {sorted.map((m) => (
          <li key={m.id} className="relative pl-8">
            <div className="absolute left-1.5 top-2 w-3 h-3 rounded-full border-2 border-white"
              style={{
                background: TYPE_COLORS[m.type] ?? TYPE_COLORS.outros,
                boxShadow: currentId === m.id ? `0 0 0 2px ${TYPE_COLORS[m.type]}44` : undefined,
              }}
            />
            <button className="text-left w-full rounded-lg px-2 py-1 transition-colors"
              style={{ background: currentId === m.id ? '#F5F3EE' : 'transparent' }}
              onClick={() => onSelect(m)}>
              <p className="text-xs font-semibold" style={{ color: '#1C1C2E' }}>{TYPE_LABELS[m.type]}</p>
              <p className="text-xs" style={{ color: '#9CA3AF' }}>
                {formatDate(m.published_at ?? m.metadata_?.data_disponibilizacao as string ?? null)}
              </p>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
