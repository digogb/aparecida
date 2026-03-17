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

const TYPE_COLORS: Record<MovementType, { color: string; bg: string }> = {
  intimacao:    { color: '#991B1B', bg: '#FEE2E2' },
  sentenca:     { color: '#3730A3', bg: '#E0E7FF' },
  despacho:     { color: '#0C4A6E', bg: '#E0F2FE' },
  acordao:      { color: '#065F46', bg: '#D1FAE5' },
  publicacao:   { color: '#92400E', bg: '#FEF3C7' },
  distribuicao: { color: '#5B21B6', bg: '#EDE9FE' },
  outros:       { color: '#374151', bg: '#F3F4F6' },
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('pt-BR')
}

function excerpt(text: string | null): string {
  if (!text) return ''
  return text.length > 120 ? text.slice(0, 120) + '…' : text
}

interface MovementCardProps {
  movement: Movement
  onClick: (movement: Movement) => void
}

export default function MovementCard({ movement, onClick }: MovementCardProps) {
  const colors = TYPE_COLORS[movement.type] ?? TYPE_COLORS.outros
  const processNumber = movement.process?.number ?? '—'
  const pubDate = formatDate(movement.published_at ?? movement.metadata_?.data_disponibilizacao as string ?? null)

  return (
    <button
      className="w-full text-left rounded-2xl overflow-hidden transition-shadow hover:shadow-md"
      style={{
        background: '#fff',
        border: `1px solid ${movement.is_read ? '#E5E3DC' : colors.color + '44'}`,
        borderLeft: `4px solid ${movement.is_read ? '#E5E3DC' : colors.color}`,
      }}
      onClick={() => onClick(movement)}
    >
      <div className="px-4 py-3 flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full"
              style={{ background: colors.bg, color: colors.color }}>
              {TYPE_LABELS[movement.type]}
            </span>
            {!movement.is_read && (
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: colors.color }} />
            )}
          </div>
          <p className="text-sm font-semibold truncate" style={{ color: '#1C1C2E' }}>{processNumber}</p>
          {movement.content && (
            <p className="text-xs mt-1 line-clamp-2" style={{ color: '#6B7280' }}>{excerpt(movement.content)}</p>
          )}
        </div>
        <div className="text-right flex-shrink-0 text-xs space-y-0.5">
          <p style={{ color: '#9CA3AF' }}>Pub: {pubDate}</p>
          {movement.process?.court && (
            <p className="font-medium" style={{ color: '#6B7280' }}>{movement.process.court}</p>
          )}
        </div>
      </div>
    </button>
  )
}
