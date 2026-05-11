import { useState } from 'react'
import type { ParecerFiltersState, ParecerStatus, ParecerTema } from '../../types/parecer'

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

export default function ParecerFilters({ filters, onChange }: {
  filters: ParecerFiltersState
  onChange: (f: ParecerFiltersState) => void
}) {
  const toggleStatus = (v: ParecerStatus) => onChange({ ...filters, status: filters.status === v ? '' : v })
  const toggleTema   = (v: ParecerTema)   => onChange({ ...filters, tema:   filters.tema   === v ? '' : v })

  const hasActiveFilter = !!(filters.status || filters.tema || filters.remetente)
  // No mobile o grid começa fechado e abre se o usuário clicar ou já houver filtro ativo.
  // No desktop (md+) o grid é sempre visível via `md:grid`.
  const [showMoreMobile, setShowMoreMobile] = useState(false)
  const mobileOpen = showMoreMobile || hasActiveFilter

  return (
    <div className="space-y-2">
      {/* Busca — sempre visível */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EDE8DF' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Busca</span>
        <input type="text" placeholder="Buscar por remetente..."
          value={filters.remetente}
          onChange={e => onChange({ ...filters, remetente: e.target.value })}
          className="w-full rounded-xl px-3 py-1.5 text-base focus:outline-none"
          style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE', color: '#0A1120' }} />
      </div>

      {/* Mobile-only toggle */}
      <button
        type="button"
        onClick={() => setShowMoreMobile(s => !s)}
        className="md:hidden w-full rounded-xl px-4 py-2.5 flex items-center justify-between cursor-pointer"
        style={{ background: '#EDE8DF' }}
      >
        <span className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
          Mais filtros
          {hasActiveFilter && <span className="ml-1.5 w-2 h-2 rounded-full inline-block align-middle" style={{ background: '#C9A94E' }} />}
        </span>
        <svg
          className={`transition-transform ${mobileOpen ? 'rotate-180' : ''}`}
          width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {/* Filtros: visível no mobile só quando aberto; no md+ sempre visível. */}
      <div className={`${mobileOpen ? 'grid' : 'hidden'} md:grid grid-cols-1 md:grid-cols-2 gap-2`}>
        {/* Status */}
        <div className="rounded-xl px-4 py-3" style={{ background: '#EDE8DF' }}>
          <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Status</span>
          <div className="flex flex-wrap gap-1.5">
            {STATUS_OPTIONS.map(o => {
              const active = filters.status === o.value
              return (
                <button key={o.value} onClick={() => toggleStatus(o.value)}
                  className="px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
                  style={active
                    ? { background: `${o.color}18`, color: o.color, border: `1.5px solid ${o.color}44` }
                    : { background: '#FAF8F5', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
                  {o.label}
                </button>
              )
            })}
          </div>
        </div>

        {/* Tema */}
        <div className="rounded-xl px-4 py-3" style={{ background: '#EDE8DF' }}>
          <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Tema</span>
          <div className="flex flex-wrap gap-1.5">
            {TEMA_OPTIONS.map(o => {
              const active = filters.tema === o.value
              return (
                <button key={o.value} onClick={() => toggleTema(o.value)}
                  className="px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
                  style={active
                    ? { background: `${o.color}18`, color: o.color, border: `1.5px solid ${o.color}44` }
                    : { background: '#FAF8F5', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
                  {o.label}
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
