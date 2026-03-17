import type { MovementFiltersState } from '../../types/movement'

const TYPES = [
  { value: 'intimacao',    label: 'Intimação',    color: '#991B1B', bg: '#FEE2E2' },
  { value: 'sentenca',     label: 'Sentença',     color: '#3730A3', bg: '#E0E7FF' },
  { value: 'despacho',     label: 'Despacho',     color: '#0C4A6E', bg: '#E0F2FE' },
  { value: 'acordao',      label: 'Acórdão',      color: '#065F46', bg: '#D1FAE5' },
  { value: 'publicacao',   label: 'Publicação',   color: '#92400E', bg: '#FEF3C7' },
  { value: 'distribuicao', label: 'Distribuição', color: '#5B21B6', bg: '#EDE9FE' },
  { value: 'outros',       label: 'Outros',       color: '#374151', bg: '#F3F4F6' },
]

export default function MovementFilters({ filters, onChange }: {
  filters: MovementFiltersState
  onChange: (f: MovementFiltersState) => void
}) {
  const toggle = (v: string) => onChange({ ...filters, type: filters.type === v ? '' : v as MovementFiltersState['type'] })

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1.5 items-center">
        <span className="text-xs font-semibold uppercase tracking-widest mr-1" style={{ color: '#9CA3AF', width: 52 }}>Tipo</span>
        {TYPES.map(t => {
          const active = filters.type === t.value
          return (
            <button key={t.value} onClick={() => toggle(t.value)}
              className="text-xs px-3 py-1 rounded-full font-semibold transition-all"
              style={active
                ? { background: t.bg, color: t.color, border: `1.5px solid ${t.color}44` }
                : { background: '#fff', color: '#6B7280', border: '1.5px solid #E5E3DC' }}>
              {t.label}
            </button>
          )
        })}
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#9CA3AF', width: 52 }}>Leitura</span>
        <select value={filters.is_read} onChange={e => onChange({ ...filters, is_read: e.target.value })}
          className="rounded-xl px-3 py-1.5 text-xs font-medium focus:outline-none appearance-none"
          style={{ background: '#fff', border: '1.5px solid #E5E3DC', color: '#1C1C2E' }}>
          <option value="">Todas</option>
          <option value="false">Não lidas</option>
          <option value="true">Lidas</option>
        </select>
        <input type="text" placeholder="Buscar processo..." value={filters.search}
          onChange={e => onChange({ ...filters, search: e.target.value })}
          className="rounded-xl px-3 py-1.5 text-sm focus:outline-none"
          style={{ background: '#fff', border: '1.5px solid #E5E3DC', width: 220, color: '#1C1C2E' }} />
      </div>
    </div>
  )
}
