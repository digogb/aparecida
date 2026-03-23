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
  // Normalize \xa0 (non-breaking space) to regular space
  t = t.replace(/\xa0/g, ' ')

  // Break before "ADVOGADO do(a)" entries
  t = t.replace(/\s+(ADVOGADO\s+do\(a\))/gi, '\n$1')

  // Break before party labels: APELANTE:, APELADO:, AUTOR:, RÉU:, IMPETRANTE:, etc.
  t = t.replace(/\s+((?:APELANTE|APELADO|AUTOR|RÉU|RÉ|REU|IMPETRANTE|IMPETRADO|REQUERENTE|REQUERIDO|RECORRENTE|RECORRIDO|AGRAVANTE|AGRAVADO|EMBARGANTE|EMBARGADO|LITISCONSORTE|INTERESSADO)(?:\(A\))?:)/gi, '\n$1')

  // Break before "ATO ORDINATÓRIO", "INTIMAÇÃO", "DESPACHO", "Despacho" (mid-text headers)
  t = t.replace(/\s+(ATO ORDINAT[ÓO]RIO|INTIMA[ÇC][ÃA]O PARA|Despacho\b|DESPACHO\b|Fundamento e decido)/g, '\n\n$1')

  // Break before numbered items: "1.", "2.", "3.1.", "3.2.", etc.
  // Only match 1-2 digit numbers (not years like 2010. or law refs like 8.429.)
  t = t.replace(/\s+(\d{1,2}\.\d{1,2}\.\s)/g, '\n\n$1')  // sub-items: 3.1. 3.2.
  t = t.replace(/([^0-9][.!?;\s])\s*(\d{1,2}\.\s+[A-ZÁÉÍÓÚÀÂÃÊÔÕÇA-z])/g, '$1\n\n$2')  // items: 1. 2. 3. (excludes sub-items like 3.1. and times like 09:00)

  // Break before "Intimem-se", "Cite-se", etc. — but NOT right after a number like "6."
  t = t.replace(
    /([^0-9][.!?])\s+(Intimem-se|Cite-se|Publique-se|Cumpra-se|Registre-se|Notifique-se|Diante do exposto|Ante o exposto|Considerando|Isso posto|Do exposto|Fica resguardada)/gi,
    '$1\n\n$2'
  )

  // Break before city+date: "Fortaleza, 13 de março de 2026" or "Salgueiro, data da assinatura"
  t = t.replace(
    /([.!?])\s+([A-ZÁÉÍÓÚÀÂÃÊÔÕÇ][a-záéíóúàâãêôõç]{2,}(?:\s+[a-záéíóúàâãêôõç]+)*,\s+(?:\d{1,2}\s+de\s+\w+\s+de\s+\d{4}|data\s+da\s+assinatura))/g,
    '$1\n\n$2'
  )

  // Break before " - Advs:" separator
  t = t.replace(/\s+-\s*Advs:/g, '\n\nAdvs:')

  // Break before ALL-CAPS signature block (3+ ALL-CAPS words after sentence end)
  t = t.replace(
    /([.!?])\s+([A-ZÁÉÍÓÚÀÂÃÊÔÕÇ]{3,}(?:\s+(?:DE|DA|DO|DOS|DAS|[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ]{2,})){2,})\s/g,
    '$1\n\n$2 '
  )

  // Break before "Nº" process number
  t = t.replace(/\s+(Nº\s+\d{7})/g, '\n$1')

  // Break before date pattern dd/mm/yyyy followed by "às"
  t = t.replace(/(\d{2}\/\d{2}\/\d{4}\s+às\s+\d{2}:\d{2})\.\s+/g, '$1.\n\n')

  // Break before judge name + title patterns (e.g. "Juiz Federal Titular")
  t = t.replace(/\s+([A-ZÁÉÍÓÚÀÂÃÊÔÕÇ][a-záéíóúàâãêôõç]+(?:\s+[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ][a-záéíóúàâãêôõç]+)+\s+(?:Juiz|Juíza|Desembargador|Desembargadora))/g, '\n\n$1')
  // Or title first: "Juiz Federal Titular da 20ª VF/SJPE"
  t = t.replace(/\s+((?:Juiz|Juíza|Desembargador|Desembargadora)\s+\w+)/g, '\n$1')

  return t
}

/**
 * Converts DJE formatting codes (B1/B0) to React elements.
 * B1 = bold start, B0 = bold end.
 */
function renderDjeText(text: string): React.ReactNode[] {
  const parts = text.split(/(B1[\s\S]*?B0)/g)
  return parts.map((part, i) => {
    if (part.startsWith('B1') && part.endsWith('B0')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>
    }
    return <React.Fragment key={i}>{part}</React.Fragment>
  })
}

/**
 * Parses DJE content into structured sections:
 * - heading: first line if ALL CAPS (DESPACHO, ACÓRDÃO, etc.)
 * - header: process number, parties, action type
 * - body: the decision text
 * - signature: judge/desembargador name
 * - lawyers: list of lawyers with OAB
 */
function parseDjeStructure(raw: string) {
  const text = preprocessDjeText(raw)
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)

  let heading = ''
  const headerLines: string[] = []
  const bodyLines: string[] = []
  let signature = ''
  const lawyerLines: string[] = []

  // Detect heading: first line if ALL CAPS and short (DESPACHO, ACÓRDÃO, etc.)
  let startIdx = 0
  const firstLine = lines[0] ?? ''
  if (/^[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ\s\d.,ª°º()]+$/.test(firstLine) && firstLine.length < 120) {
    heading = firstLine
    startIdx = 1
  }

  // Classify each line into a bucket
  const headerPattern = /^(Nº\s|Processo:|APELA[ÇC]|APELANTE|APELADO|AUTOR:|RÉU:|RÉ:|IMPETRANTE|IMPETRADO|REQUERENTE|REQUERIDO|RECORRENTE|RECORRIDO|AGRAVANTE|AGRAVADO|EMBARGANTE|EMBARGADO|LITISCONSORTE|INTERESSADO|Custos\s+legis|Ação|AÇÃO|\d{7}-|TRF|TJCE|ESTADO DO|PODER JUDIC|GABINETE)/i
  const lawyerPattern = /^ADVOGADO\s+do\(a\)/i
  const sigPattern = /^(DESEMBARGADOR|JUIZ|Relator)/i
  const advsSeparator = /^-?\s*Advs?:/i

  let reachedBody = false

  for (let i = startIdx; i < lines.length; i++) {
    const line = lines[i]

    // ADVOGADO do(a) lines → lawyers
    if (lawyerPattern.test(line)) {
      lawyerLines.push(line)
      continue
    }

    // "Advs:" separator → lawyers (rest of line)
    if (advsSeparator.test(line)) {
      lawyerLines.push(line)
      continue
    }

    // Header lines (only before body starts)
    if (!reachedBody && headerPattern.test(line)) {
      headerLines.push(line)
      continue
    }

    // Everything else is body
    reachedBody = true
    bodyLines.push(line)
  }

  // Extract signature from end of body (ALL CAPS name or DESEMBARGADOR...)
  while (bodyLines.length > 0) {
    const last = bodyLines[bodyLines.length - 1]
    if (sigPattern.test(last) || (/^[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ\s]+$/.test(last) && last.length > 5 && last.length < 100)) {
      signature = signature ? `${last} ${signature}` : last
      bodyLines.pop()
    } else {
      break
    }
  }

  return { heading, headerLines, bodyLines, signature, lawyerLines }
}

// Renders DJE content with structured formatting
function FormattedContent({ text }: { text: string }) {
  const { heading, headerLines, bodyLines, signature, lawyerLines } = parseDjeStructure(text)
  const numberedRe = /^(\s*(?:[0-9]+|[IVXivx]+|[a-zA-Z])[.)]\s)/

  // Parse lawyers: extract "NAME - OAB" from various formats
  const lawyers: string[] = []
  for (const line of lawyerLines) {
    // Format: "ADVOGADO do(a) ROLE: NAME   OAB"  or  "Advs: Name (OAB: 123/CE) - Name2..."
    let cleaned = line
      .replace(/^ADVOGADO\s+do\(a\)\s*/i, '')
      .replace(/^-?\s*Advs?:\s*/i, '')
      // Remove role prefix like "APELANTE:"
      .replace(/^[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ]+:\s*/i, '')
      .trim()
    if (cleaned) {
      // Split by " - " between names, or by OAB pattern boundaries
      const entries = cleaned.split(/\s+-\s+(?=[A-ZÁÉÍÓÚÀÂÃÊÔÕÇ])/).map(s => s.trim()).filter(Boolean)
      lawyers.push(...entries)
    }
  }
  // Deduplicate
  const uniqueLawyers = [...new Set(lawyers)]

  return (
    <div className="space-y-4">
      {/* Heading */}
      {heading && (
        <p className="text-sm font-semibold uppercase tracking-widest text-center" style={{ color: '#6B6860' }}>
          {heading}
        </p>
      )}

      {/* Header: process info */}
      {headerLines.length > 0 && (
        <div className="rounded-lg px-4 py-3 text-sm" style={{ background: '#EBE8E2', color: '#6B6860' }}>
          {headerLines.map((line, i) => (
            <p key={i}>{renderDjeText(line)}</p>
          ))}
        </div>
      )}

      {/* Body */}
      {bodyLines.length > 0 && (
        <div className="space-y-3">
          {bodyLines.map((line, i) => {
            const isNumbered = numberedRe.test(line)
            return (
              <p
                key={i}
                className="text-base leading-relaxed"
                style={{
                  color: '#2D2D3A',
                  ...(isNumbered ? { paddingLeft: '1.25rem', textIndent: '-1.25rem' } : {}),
                }}
              >
                {renderDjeText(line)}
              </p>
            )
          })}
        </div>
      )}

      {/* Signature */}
      {signature && (
        <p className="text-sm font-semibold text-center pt-2" style={{ color: '#6B6860', borderTop: '1px solid #DDD9D2' }}>
          {signature}
        </p>
      )}

      {/* Lawyers */}
      {uniqueLawyers.length > 0 && (
        <div className="pt-2" style={{ borderTop: '1px solid #DDD9D2' }}>
          <p className="text-xs font-medium uppercase tracking-widest mb-1.5" style={{ color: '#A69B8D' }}>Advogados</p>
          <div className="flex flex-wrap gap-1.5">
            {uniqueLawyers.map((lawyer, i) => (
              <span key={i} className="text-xs px-2 py-0.5 rounded-lg" style={{ background: '#EBE8E2', color: '#6B6860' }}>
                {lawyer}
              </span>
            ))}
          </div>
        </div>
      )}
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
              {typeof meta.link === 'string' && meta.link && (
                <a href={meta.link} target="_blank" rel="noopener noreferrer"
                  className="text-xs font-medium underline ml-auto" style={{ color: '#C4953A' }}>
                  Abrir no DJE &rarr;
                </a>
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
              {typeof meta.orgao === 'string' && meta.orgao && (
                <div>
                  <span className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Órgão</span>
                  <p style={{ color: '#2D2D3A' }}>{meta.orgao as string}</p>
                </div>
              )}
              {movement.process?.subject && (
                <div className="col-span-2">
                  <span className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Assunto</span>
                  <p style={{ color: '#2D2D3A' }}>{movement.process.subject}</p>
                </div>
              )}
            </div>

            {/* Partes */}
            {meta.polos && typeof meta.polos === 'object' && (() => {
              const polos = meta.polos as Record<string, string[]>
              const ativo = polos.ativo?.filter(Boolean) ?? []
              const passivo = polos.passivo?.filter(Boolean) ?? []
              if (ativo.length === 0 && passivo.length === 0) return null
              return (
                <div>
                  <p className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>Partes</p>
                  <div className="grid grid-cols-2 gap-3">
                    {ativo.length > 0 && (
                      <div className="rounded-xl p-3" style={{ background: '#EBE8E2', border: '1px solid #DDD9D2' }}>
                        <p className="text-xs font-semibold uppercase tracking-widest mb-1.5" style={{ color: '#5B7553' }}>Polo ativo</p>
                        {ativo.map((name, i) => (
                          <p key={i} className="text-sm" style={{ color: '#2D2D3A' }}>{name}</p>
                        ))}
                      </div>
                    )}
                    {passivo.length > 0 && (
                      <div className="rounded-xl p-3" style={{ background: '#EBE8E2', border: '1px solid #DDD9D2' }}>
                        <p className="text-xs font-semibold uppercase tracking-widest mb-1.5" style={{ color: '#8B2332' }}>Polo passivo</p>
                        {passivo.map((name, i) => (
                          <p key={i} className="text-sm" style={{ color: '#2D2D3A' }}>{name}</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )
            })()}

            <div>
              <p className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>Conteúdo</p>
              <div className="rounded-xl p-4 text-base leading-relaxed"
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
