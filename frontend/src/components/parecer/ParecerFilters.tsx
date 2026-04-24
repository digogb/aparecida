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

  const hasActiveFilter = filters.status || filters.tema || filters.remetente

  // Busca sempre visível; tema+status colapsáveis em mobile
  return (
    <div className="space-y-2">
      {/* Busca — sempre visível */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EDE8DF' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Busca</span>
        <input type="text" placeholder="Buscar por remetente..."
          value={filters.remetente}
          onChange={e => onChange({ ...filters, remetente: e.target.value })}
          className="w-full rounded-xl px-3 py-1.5 text-base focus:outline-none"
          style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120' }} />
      </div>

      {/* Filtros adicionais — colapsáveis em mobile, sempre abertos em md+ */}
      <details className="md:open group" open={!!hasActiveFilter}>
        <summary className="md:hidden list-none cursor-pointer">
          <div
            className="rounded-xl px-4 py-2.5 flex items-center justify-between"
            style={{ background: '#EDE8DF' }}
          >
            <span className="text-xs font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
              Mais filtros
              {hasActiveFilter && <span className="ml-1.5 w-2 h-2 rounded-full inline-block align-middle" style={{ background: '#C9A94E' }} />}
            </span>
            <svg
              className="transition-transform group-open:rotate-180"
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A69B8D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </summary>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 md:mt-0">
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
                      : { background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
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
                      : { background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
                    {o.label}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </details>
    </div>
  )
}
