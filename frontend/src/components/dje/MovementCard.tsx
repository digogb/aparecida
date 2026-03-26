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

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('pt-BR')
}

function titleCase(s: string): string {
  const MINOR = new Set(['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'no', 'na', 'nos', 'nas', 'à', 'ao', 'às', 'aos', 'por', 'para', 'com'])
  return s.toLowerCase().split(' ').map((w, i) =>
    i > 0 && MINOR.has(w) ? w : w.charAt(0).toUpperCase() + w.slice(1)
  ).join(' ')
}

function buildSummary(movement: Movement): string | null {
  const meta = movement.metadata_ as Record<string, unknown> | null
  if (!meta) return null

  const parts: string[] = []

  const nomeClasse = meta.nome_classe as string | undefined
  if (nomeClasse) parts.push(titleCase(nomeClasse))

  const orgao = meta.orgao as string | undefined
  if (orgao) parts.push(titleCase(orgao))

  const dest = meta.destinatarios as string[] | undefined
  if (dest?.length) parts.push(dest.map(d => titleCase(d)).join(', '))

  return parts.length > 0 ? parts.join(' · ') : null
}

interface MovementCardProps {
  movement: Movement
  onClick: (movement: Movement) => void
}

export default function MovementCard({ movement, onClick }: MovementCardProps) {
  const color = TYPE_COLORS[movement.type] ?? TYPE_COLORS.outros
  const processNumber = movement.process?.number ?? '—'
  const pubDate = formatDate(movement.published_at ?? movement.metadata_?.data_disponibilizacao as string ?? null)
  const summary = buildSummary(movement)

  return (
    <button
      className="w-full text-left rounded-xl overflow-hidden transition-all duration-150 hover:brightness-[0.97]"
      style={{
        background: '#F5F0E8',
        border: `1.5px solid ${movement.is_read ? '#E0D9CE' : color + '44'}`,
        borderLeft: `4px solid ${movement.is_read ? '#E0D9CE' : color}`,
      }}
      onClick={() => onClick(movement)}
    >
      <div className="px-4 py-3 flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-lg"
              style={{ background: `${color}18`, color }}>
              {TYPE_LABELS[movement.type]}
            </span>
            {!movement.is_read && (
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
            )}
          </div>
          <p className="text-base font-medium truncate" style={{ color: '#0A1120' }}>{processNumber}</p>
          {summary && (
            <p className="text-sm mt-1 line-clamp-2" style={{ color: '#A69B8D' }}>{summary}</p>
          )}
        </div>
        <div className="text-right flex-shrink-0 space-y-0.5">
          <p className="text-sm" style={{ color: '#A69B8D' }}>Pub: {pubDate}</p>
          {movement.process?.court && (
            <p className="text-sm font-medium" style={{ color: '#6B6860' }}>{movement.process.court}</p>
          )}
        </div>
      </div>
    </button>
  )
}
