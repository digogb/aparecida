import type { ParecerFiltersState, ParecerStatus, ParecerTema } from '../../types/parecer'

const STATUS_OPTIONS: { value: ParecerStatus; label: string; color: string; active: string }[] = [
  { value: 'pendente',     label: 'Pendente',     color: '#92400E', active: '#FFFBF0' },
  { value: 'classificado', label: 'Classificado', color: '#1E40AF', active: '#DBEAFE' },
  { value: 'gerado',       label: 'Gerado',       color: '#3730A3', active: '#E0E7FF' },
  { value: 'em_revisao',   label: 'Em Revisão',   color: '#5B21B6', active: '#EDE9FE' },
  { value: 'devolvido',    label: 'Devolvido',    color: '#991B1B', active: '#FEE2E2' },
  { value: 'aprovado',     label: 'Aprovado',     color: '#065F46', active: '#D1FAE5' },
  { value: 'enviado',      label: 'Enviado',      color: '#374151', active: '#F3F4F6' },
]

const TEMA_OPTIONS: { value: ParecerTema; label: string; color: string; active: string }[] = [
  { value: 'administrativo', label: 'Administrativo', color: '#3730A3', active: '#E0E7FF' },
  { value: 'tributario',     label: 'Tributário',     color: '#92400E', active: '#FEF3C7' },
  { value: 'financeiro',     label: 'Financeiro',     color: '#0C4A6E', active: '#E0F2FE' },
  { value: 'previdenciario', label: 'Previdenciário', color: '#701A75', active: '#FAE8FF' },
  { value: 'licitacao',      label: 'Licitação',      color: '#3F6212', active: '#ECFCCB' },
]

export default function ParecerFilters({ filters, onChange }: {
  filters: ParecerFiltersState
  onChange: (f: ParecerFiltersState) => void
}) {
  const toggleStatus = (v: ParecerStatus) => onChange({ ...filters, status: filters.status === v ? '' : v })
  const toggleTema   = (v: ParecerTema)   => onChange({ ...filters, tema:   filters.tema   === v ? '' : v })

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1.5 items-center">
        <span className="text-xs font-semibold uppercase tracking-widest mr-1" style={{ color: '#9CA3AF', width: 52 }}>Status</span>
        {STATUS_OPTIONS.map(o => {
          const active = filters.status === o.value
          return (
            <button key={o.value} onClick={() => toggleStatus(o.value)}
              className="px-3 py-1 rounded-full text-xs font-semibold transition-all"
              style={active
                ? { background: o.active, color: o.color, border: `1.5px solid ${o.color}44` }
                : { background: '#fff', color: '#6B7280', border: '1.5px solid #E5E3DC' }}>
              {o.label}
            </button>
          )
        })}
      </div>
      <div className="flex flex-wrap gap-1.5 items-center">
        <span className="text-xs font-semibold uppercase tracking-widest mr-1" style={{ color: '#9CA3AF', width: 52 }}>Tema</span>
        {TEMA_OPTIONS.map(o => {
          const active = filters.tema === o.value
          return (
            <button key={o.value} onClick={() => toggleTema(o.value)}
              className="px-3 py-1 rounded-full text-xs font-semibold transition-all"
              style={active
                ? { background: o.active, color: o.color, border: `1.5px solid ${o.color}44` }
                : { background: '#fff', color: '#6B7280', border: '1.5px solid #E5E3DC' }}>
              {o.label}
            </button>
          )
        })}
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#9CA3AF', width: 52 }}>Busca</span>
        <input type="text" placeholder="Buscar por remetente..."
          value={filters.remetente}
          onChange={e => onChange({ ...filters, remetente: e.target.value })}
          className="rounded-xl px-3 py-1.5 text-sm focus:outline-none"
          style={{ background: '#fff', border: '1.5px solid #E5E3DC', width: 260, color: '#1C1C2E' }} />
      </div>
    </div>
  )
}
