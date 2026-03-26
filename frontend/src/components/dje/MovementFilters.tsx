import type { MovementFiltersState } from '../../types/movement'

const TYPES: { value: string; label: string; color: string }[] = [
  { value: 'intimacao',    label: 'Intimação',    color: '#8B2332' },
  { value: 'sentenca',     label: 'Sentença',     color: '#142038' },
  { value: 'despacho',     label: 'Despacho',     color: '#6B6860' },
  { value: 'acordao',      label: 'Acórdão',      color: '#5B7553' },
  { value: 'publicacao',   label: 'Publicação',   color: '#C9A94E' },
  { value: 'distribuicao', label: 'Distribuição',  color: '#A69B8D' },
  { value: 'outros',       label: 'Outros',       color: '#6B6860' },
]

export default function MovementFilters({ filters, onChange }: {
  filters: MovementFiltersState
  onChange: (f: MovementFiltersState) => void
}) {
  const toggle = (v: string) => onChange({ ...filters, type: filters.type === v ? '' : v as MovementFiltersState['type'] })

  return (
    <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-3 items-start">
      {/* Tipo */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EDE8DF' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Tipo</span>
        <div className="flex flex-wrap gap-1.5">
          {TYPES.map(t => {
            const active = filters.type === t.value
            return (
              <button key={t.value} onClick={() => toggle(t.value)}
                className="px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
                style={active
                  ? { background: `${t.color}18`, color: t.color, border: `1.5px solid ${t.color}44` }
                  : { background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
                {t.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Leitura */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EDE8DF' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Leitura</span>
        <select value={filters.is_read} onChange={e => onChange({ ...filters, is_read: e.target.value as '' | 'true' | 'false' })}
          className="rounded-xl px-3 py-1.5 text-base font-medium focus:outline-none"
          style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120' }}>
          <option value="">Todas</option>
          <option value="false">Não lidas</option>
          <option value="true">Lidas</option>
        </select>
      </div>

      {/* Busca */}
      <div className="rounded-xl px-4 py-3" style={{ background: '#EDE8DF' }}>
        <span className="text-xs font-medium uppercase tracking-widest block mb-2" style={{ color: '#A69B8D' }}>Busca</span>
        <input type="text" placeholder="Buscar processo..." value={filters.search}
          onChange={e => onChange({ ...filters, search: e.target.value })}
          className="w-full rounded-xl px-3 py-1.5 text-base focus:outline-none"
          style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120' }} />
      </div>
    </div>
  )
}
