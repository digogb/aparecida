import React, { useEffect } from 'react'
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

const TYPE_COLORS: Record<MovementType, string> = {
  intimacao:    '#8B2332',
  sentenca:     '#1B2838',
  despacho:     '#6B6860',
  acordao:      '#5B7553',
  publicacao:   '#C4953A',
  distribuicao: '#A69B8D',
  outros:       '#6B6860',
}

/**
 * Inserts paragraph breaks at natural DJE structural boundaries when the
 * text arrives as a single flat block (which is the common case from the API).
 */
function preprocessDjeText(raw: string): string {
  let t = raw.trim()

  // Break before city+date line: "Fortaleza, 13 de março de 2026."
  t = t.replace(
    /([.;])\s+([A-ZÁÉÍÓÚÀÂÃÊÔÕÇ][a-záéíóúàâãêôõç]{2,}(?:\s+[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ][a-záéíóúàâãêôõç]+)*,\s+\d{1,2}\s+de\s+\w+\s+de\s+\d{4})/g,
    '$1\n\n$2'
  )

  // Break before " - Advs:" separator
  t = t.replace(/\s+-\s*Advs:/g, '\n\nAdvs:')

  // Break before ALL-CAPS judge/rapporteur signature block
  // (3+ consecutive ALL-CAPS words after a sentence end)
  t = t.replace(
    /([.!?])\s+([A-ZÁÉÍÓÚÀÂÃÊÔÕÇ]{3,}(?:\s+(?:DE|DA|DO|DOS|DAS|[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ]{2,})){2,})\s/g,
    '$1\n\n$2 '
  )

  // Break before common decision openers when stuck to prior sentence
  t = t.replace(
    /([.!?])\s+-\s+(Diante\b|Ante\b|Considerando\b|Isso\s+posto\b|Do\s+exposto\b|Ante\s+o\s+exposto\b)/gi,
    '$1\n\n$2'
  )

  return t
}

// Renders DJE plain text with structured paragraphs and indentation for numbered items
function FormattedContent({ text }: { text: string }) {
  const processed = preprocessDjeText(text)
  const paragraphs = processed.split('\n\n').map(p => p.trim()).filter(Boolean)
  // Matches: "1.", "2)", "I.", "II.", "a)", "b." etc. at start of line
  const numberedRe = /^(\s*(?:[0-9]+|[IVXivx]+|[a-zA-Z])[.)]\s)/

  return (
    <div className="space-y-3">
      {paragraphs.map((para, pi) => {
        const lines = para.split('\n').map(l => l.trim()).filter(Boolean)
        return (
          <p key={pi} className="leading-relaxed">
            {lines.map((line, li) => {
              const isNumbered = numberedRe.test(line)
              return (
                <span
                  key={li}
                  className={isNumbered ? 'block' : undefined}
                  style={isNumbered ? { paddingLeft: '1.25rem', textIndent: '-1.25rem' } : undefined}
                >
                  {li > 0 && !isNumbered && <br />}
                  {line}
                </span>
              )
            })}
          </p>
        )
      })}
    </div>
  )
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
  const color = TYPE_COLORS[movement.type] ?? TYPE_COLORS.outros

  useEffect(() => {
    if (!movement.is_read) {
      markRead.mutate(movement.id)
    }
  }, [movement.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const meta = movement.metadata_ ?? {}
  const pubDate = formatDate(movement.published_at ?? (meta.data_disponibilizacao as string) ?? null)
  const processNumber = movement.process?.number ?? '—'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col" style={{ background: '#FAF8F5', border: '1.5px solid #DDD9D2', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        {/* Header */}
        <div className="flex items-start justify-between p-5" style={{ borderBottom: '1px solid #EBE8E2' }}>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-lg"
                style={{ background: `${color}18`, color }}>
                {TYPE_LABELS[movement.type]}
              </span>
              {movement.process?.court && (
                <span className="text-sm" style={{ color: '#A69B8D' }}>{movement.process.court}</span>
              )}
            </div>
            <h2 className="font-display" style={{ fontSize: 20, fontWeight: 500, color: '#1B2838' }}>
              {processNumber}
            </h2>
          </div>
          <button onClick={onClose} className="ml-4 p-1.5 rounded-lg transition-all duration-150 hover:brightness-[0.97] cursor-pointer" style={{ color: '#A69B8D' }}>
            <X size={18} />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Main content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Publicação</span>
                <p style={{ color: '#2D2D3A' }}>{pubDate}</p>
              </div>
              {typeof meta.link === 'string' && meta.link && (
                <div>
                  <span className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Link</span>
                  <a href={meta.link} target="_blank" rel="noopener noreferrer"
                    className="text-sm underline" style={{ color: '#C4953A' }}>
                    Abrir no DJE
                  </a>
                </div>
              )}
            </div>

            <div>
              <p className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>Conteúdo</p>
              <div className="rounded-xl p-4 text-base leading-relaxed max-h-96 overflow-y-auto"
                style={{ background: '#EBE8E2', color: '#2D2D3A', border: '1px solid #DDD9D2' }}>
                {movement.content ? <FormattedContent text={movement.content} /> : <span style={{ color: '#A69B8D' }}>Texto não disponível.</span>}
              </div>
            </div>
          </div>

          {/* Sidebar: Timeline */}
          {relatedMovements.length > 1 && (
            <div className="w-52 overflow-y-auto flex-shrink-0 p-4" style={{ borderLeft: '1px solid #EBE8E2' }}>
              <p className="text-sm font-medium uppercase tracking-widest mb-3" style={{ color: '#A69B8D' }}>Histórico</p>
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
