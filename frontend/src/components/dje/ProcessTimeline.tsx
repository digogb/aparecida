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
  intimacao:    '#8B2332',
  sentenca:     '#142038',
  despacho:     '#6B6860',
  acordao:      '#5B7553',
  publicacao:   '#C9A94E',
  distribuicao: '#A69B8D',
  outros:       '#6B6860',
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
      <div className="absolute left-3 top-0 bottom-0 w-0.5" style={{ background: '#E0D9CE' }} />
      <ul className="space-y-3">
        {sorted.map((m) => {
          const color = TYPE_COLORS[m.type] ?? TYPE_COLORS.outros
          return (
            <li key={m.id} className="relative pl-8">
              <div className="absolute left-1.5 top-2 w-3 h-3 rounded-full"
                style={{
                  background: color,
                  border: '2px solid #F5F0E8',
                  boxShadow: currentId === m.id ? `0 0 0 2px ${color}44` : undefined,
                }}
              />
              <button className="text-left w-full rounded-lg px-2 py-1 transition-all duration-150 cursor-pointer"
                style={{ background: currentId === m.id ? '#EDE8DF' : 'transparent' }}
                onClick={() => onSelect(m)}>
                <p className="text-sm font-medium" style={{ color: '#0A1120' }}>{TYPE_LABELS[m.type]}</p>
                <p className="text-sm" style={{ color: '#A69B8D' }}>
                  {formatDate(m.published_at ?? m.metadata_?.data_disponibilizacao as string ?? null)}
                </p>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
