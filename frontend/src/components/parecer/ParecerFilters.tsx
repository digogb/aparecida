import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import type { ParecerFiltersState, ParecerStatus, ParecerTema } from '../../types/parecer'
import { fetchMunicipios } from '../../services/parecerApi'
import { fetchLawyers } from '../../services/editorApi'

const STATUS_OPTIONS: { value: ParecerStatus; label: string; color: string }[] = [
  { value: 'gerado',      label: 'Aguardando revisão', color: '#A69B8D' },
  { value: 'em_correcao', label: 'Em correção',        color: '#D97706' },
  { value: 'devolvido',   label: 'Devolvido',          color: '#8B2332' },
  { value: 'aprovado',    label: 'Aprovado',           color: '#5B7553' },
  { value: 'enviado',     label: 'Enviado',            color: '#8C8A82' },
]

const TEMA_OPTIONS: { value: ParecerTema; label: string; color: string }[] = [
  { value: 'licitacao',      label: 'Licitação',            color: '#C9A94E' },
  { value: 'administrativo', label: 'Administrativo geral', color: '#6B6860' },
]

const selectStyle: React.CSSProperties = {
  background: '#FAF8F5', border: '1.5px solid #E0D9CE', color: '#0A1120',
}

export default function ParecerFilters({ filters, onChange, total, onClear }: {
  filters: ParecerFiltersState
  onChange: (f: ParecerFiltersState) => void
  /** Total do recorte atual (reflete os filtros) — exibido logo abaixo dos dropdowns. */
  total?: number
  onClear?: () => void
}) {
  const toggleStatus = (v: ParecerStatus) => onChange({ ...filters, status: filters.status === v ? '' : v })
  const toggleTema   = (v: ParecerTema)   => onChange({ ...filters, tema:   filters.tema   === v ? '' : v })

  const { data: municipios = [] } = useQuery({
    queryKey: ['parecer-municipios'],
    queryFn: fetchMunicipios,
    staleTime: 5 * 60_000,
  })
  const { data: lawyers = [] } = useQuery({
    queryKey: ['lawyers', 'all'],
    queryFn: () => fetchLawyers(true),
    staleTime: 5 * 60_000,
  })

  const hasActiveFilter = !!(filters.status || filters.tema || filters.municipio || filters.enviado_por || filters.remetente)
  // No mobile a área de filtros começa fechada e abre ao clicar (ou se já houver filtro ativo).
  const [showMoreMobile, setShowMoreMobile] = useState(false)
  const mobileOpen = showMoreMobile || hasActiveFilter

  const chip = (active: boolean, color: string): React.CSSProperties =>
    active
      ? { background: `${color}18`, color, border: `1.5px solid ${color}44` }
      : { background: '#FAF8F5', color: '#6B6860', border: '1.5px solid #E0D9CE' }

  return (
    <div className="rounded-xl px-3 py-2.5 space-y-2" style={{ background: '#EDE8DF' }}>
      {/* Linha 1: busca (cresce) + selects de município e enviado-por */}
      <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_auto] gap-2">
        <div className="relative">
          <svg className="absolute left-2.5 top-1/2 -translate-y-1/2" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
          </svg>
          <input type="text" placeholder="Buscar por remetente..."
            value={filters.remetente}
            onChange={e => onChange({ ...filters, remetente: e.target.value })}
            className="w-full rounded-lg pl-8 pr-3 py-1.5 text-sm focus:outline-none"
            style={selectStyle} />
        </div>

        {municipios.length > 0 && (
          <select
            value={filters.municipio}
            onChange={e => onChange({ ...filters, municipio: e.target.value })}
            className="rounded-lg px-2.5 py-1.5 text-sm focus:outline-none cursor-pointer"
            style={selectStyle}
          >
            <option value="">Município: todos</option>
            {municipios.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        )}

        {lawyers.length > 0 && (
          <select
            value={filters.enviado_por}
            onChange={e => onChange({ ...filters, enviado_por: e.target.value })}
            className="rounded-lg px-2.5 py-1.5 text-sm focus:outline-none cursor-pointer"
            style={selectStyle}
          >
            <option value="">Enviado por: todos</option>
            {lawyers.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        )}
      </div>

      {/* Total do recorte atual — compacto, logo abaixo dos dropdowns */}
      {/* Mobile-only toggle para os chips de status/tema */}
      <button
        type="button"
        onClick={() => setShowMoreMobile(s => !s)}
        className="md:hidden w-full flex items-center justify-between text-xs font-medium uppercase tracking-widest cursor-pointer pt-1"
        style={{ color: '#A69B8D' }}
      >
        <span>
          Status e tema
          {(filters.status || filters.tema) && <span className="ml-1.5 w-2 h-2 rounded-full inline-block align-middle" style={{ background: '#C9A94E' }} />}
        </span>
        <svg className={`transition-transform ${mobileOpen ? 'rotate-180' : ''}`} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {/* Linha 2: chips de status + tema, com rótulos inline */}
      <div className={`${mobileOpen ? 'flex' : 'hidden'} md:flex flex-wrap items-center gap-x-2 gap-y-1.5`}>
        <span className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>Status</span>
        {STATUS_OPTIONS.map(o => (
          <button key={o.value} onClick={() => toggleStatus(o.value)}
            className="px-2.5 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
            style={chip(filters.status === o.value, o.color)}>
            {o.label}
          </button>
        ))}
        <span className="w-px h-4 mx-1" style={{ background: '#D0C9BE' }} />
        <span className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>Tema</span>
        {TEMA_OPTIONS.map(o => (
          <button key={o.value} onClick={() => toggleTema(o.value)}
            className="px-2.5 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
            style={chip(filters.tema === o.value, o.color)}>
            {o.label}
          </button>
        ))}

        {/* Total do recorte — no final da linha, à direita */}
        {typeof total === 'number' && (
          <span className="ml-auto flex items-center gap-2 text-sm" style={{ color: '#6B6860' }}>
            {hasActiveFilter && onClear && (
              <button onClick={onClear} className="font-medium cursor-pointer hover:underline" style={{ color: '#C9A94E' }}>
                Limpar
              </button>
            )}
            <span>
              <span className="font-semibold tabular-nums">{total}</span>{' '}
              {total === 1 ? 'parecer' : 'pareceres'}{hasActiveFilter ? ' no filtro' : ''}
            </span>
          </span>
        )}
      </div>
    </div>
  )
}
