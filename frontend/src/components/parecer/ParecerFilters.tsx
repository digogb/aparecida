import type { ParecerFiltersState, ParecerStatus, ParecerTema } from '../../types/parecer'

const STATUS_OPTIONS: { value: ParecerStatus; label: string; color: string }[] = [
  { value: 'gerado',      label: 'Aguardando revisão', color: '#A69B8D' },
  { value: 'em_correcao', label: 'Em correção',        color: '#D97706' },
  { value: 'devolvido',   label: 'Devolvido',          color: '#8B2332' },
  { value: 'aprovado',    label: 'Aprovado',           color: '#5B7553' },
  { value: 'enviado',     label: 'Enviado',            color: '#8C8A82' },
]

const TEMA_OPTIONS: { value: ParecerTema; label: string; color: string }[] = [
  { value: 'licitacao',      label: 'Licitação',            color: '#C4953A' },
  { value: 'administrativo', label: 'Administrativo geral', color: '#6B6860' },
]

export default function ParecerFilters({ filters, onChange }: {
  filters: ParecerFiltersState
  onChange: (f: ParecerFiltersState) => void
}) {
  const toggleStatus = (v: ParecerStatus) => onChange({ ...filters, status: filters.status === v ? '' : v })
  const toggleTema   = (v: ParecerTema)   => onChange({ ...filters, tema:   filters.tema   === v ? '' : v })

  return (
    <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-3 items-stretch">
      {/* Status */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EBE8E2' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Status</span>
        <div className="flex flex-wrap gap-1.5">
          {STATUS_OPTIONS.map(o => {
            const active = filters.status === o.value
            return (
              <button key={o.value} onClick={() => toggleStatus(o.value)}
                className="px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
                style={active
                  ? { background: `${o.color}18`, color: o.color, border: `1.5px solid ${o.color}44` }
                  : { background: '#FAF8F5', color: '#6B6860', border: '1.5px solid #DDD9D2' }}>
                {o.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tema */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EBE8E2' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Tema</span>
        <div className="flex flex-wrap gap-1.5">
          {TEMA_OPTIONS.map(o => {
            const active = filters.tema === o.value
            return (
              <button key={o.value} onClick={() => toggleTema(o.value)}
                className="px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
                style={active
                  ? { background: `${o.color}18`, color: o.color, border: `1.5px solid ${o.color}44` }
                  : { background: '#FAF8F5', color: '#6B6860', border: '1.5px solid #DDD9D2' }}>
                {o.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Busca */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EBE8E2' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Busca</span>
        <input type="text" placeholder="Buscar por remetente..."
          value={filters.remetente}
          onChange={e => onChange({ ...filters, remetente: e.target.value })}
          className="w-full rounded-xl px-3 py-1.5 text-base focus:outline-none"
          style={{ background: '#FAF8F5', border: '1.5px solid #DDD9D2', color: '#2D2D3A' }} />
      </div>
    </div>
  )
}
