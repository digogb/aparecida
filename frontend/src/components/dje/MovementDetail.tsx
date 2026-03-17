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

const TYPE_COLORS: Record<MovementType, { color: string; bg: string }> = {
  intimacao:    { color: '#991B1B', bg: '#FEE2E2' },
  sentenca:     { color: '#3730A3', bg: '#E0E7FF' },
  despacho:     { color: '#0C4A6E', bg: '#E0F2FE' },
  acordao:      { color: '#065F46', bg: '#D1FAE5' },
  publicacao:   { color: '#92400E', bg: '#FEF3C7' },
  distribuicao: { color: '#5B21B6', bg: '#EDE9FE' },
  outros:       { color: '#374151', bg: '#F3F4F6' },
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })
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
  const colors = TYPE_COLORS[movement.type] ?? TYPE_COLORS.outros

  useEffect(() => {
    if (!movement.is_read) {
      markRead.mutate(movement.id)
    }
  }, [movement.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const meta = movement.metadata_ ?? {}
  const pubDate = formatDate(movement.published_at ?? (meta.data_disponibilizacao as string) ?? null)
  const processNumber = movement.process?.number ?? '—'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(28,28,46,0.5)' }}>
      <div className="rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col" style={{ background: '#fff', border: '1px solid #E5E3DC' }}>
        {/* Header */}
        <div className="flex items-start justify-between p-5" style={{ borderBottom: '1px solid #E5E3DC' }}>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full"
                style={{ background: colors.bg, color: colors.color }}>
                {TYPE_LABELS[movement.type]}
              </span>
              {movement.process?.court && (
                <span className="text-xs" style={{ color: '#9CA3AF' }}>{movement.process.court}</span>
              )}
            </div>
            <h2 className="font-display" style={{ fontSize: 20, fontWeight: 500, color: '#1C1C2E' }}>
              {processNumber}
            </h2>
          </div>
          <button onClick={onClose} className="ml-4 p-1.5 rounded-lg hover:bg-gray-100" style={{ color: '#9CA3AF' }}>
            <X size={18} />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Main content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-xs font-semibold uppercase tracking-widest block mb-1" style={{ color: '#9CA3AF' }}>Publicação</span>
                <p style={{ color: '#1C1C2E' }}>{pubDate}</p>
              </div>
              {meta.link && (
                <div>
                  <span className="text-xs font-semibold uppercase tracking-widest block mb-1" style={{ color: '#9CA3AF' }}>Link</span>
                  <a href={meta.link as string} target="_blank" rel="noopener noreferrer"
                    className="text-xs underline" style={{ color: '#4F46E5' }}>
                    Abrir no DJE
                  </a>
                </div>
              )}
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: '#9CA3AF' }}>Conteúdo</p>
              <div className="rounded-xl p-4 text-sm whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto"
                style={{ background: '#F5F3EE', color: '#374151', border: '1px solid #E5E3DC' }}>
                {movement.content || 'Texto não disponível.'}
              </div>
            </div>
          </div>

          {/* Sidebar: Timeline */}
          {relatedMovements.length > 1 && (
            <div className="w-52 overflow-y-auto flex-shrink-0 p-4" style={{ borderLeft: '1px solid #E5E3DC' }}>
              <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Histórico</p>
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
