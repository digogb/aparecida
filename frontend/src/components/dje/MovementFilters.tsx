import { Search } from 'lucide-react'
import type { MovementType } from '../../types/movement'
import type { MovementFiltersState } from '../../types/movement'

const TYPES: { value: MovementType; label: string }[] = [
  { value: 'intimacao', label: 'Intimação' },
  { value: 'sentenca', label: 'Sentença' },
  { value: 'despacho', label: 'Despacho' },
  { value: 'acordao', label: 'Acórdão' },
  { value: 'publicacao', label: 'Publicação' },
  { value: 'distribuicao', label: 'Distribuição' },
  { value: 'outros', label: 'Outros' },
]

interface MovementFiltersProps {
  filters: MovementFiltersState
  onChange: (filters: MovementFiltersState) => void
}

export default function MovementFilters({ filters, onChange }: MovementFiltersProps) {
  function setType(value: MovementType | '') {
    onChange({ ...filters, movement_type: value })
  }

  function setRead(value: 'true' | 'false' | '') {
    onChange({ ...filters, is_read: value })
  }

  function setSearch(value: string) {
    onChange({ ...filters, search: value })
  }

  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="relative">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar processo, resumo..."
          value={filters.search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Type pills */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setType('')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            filters.movement_type === ''
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Todos
        </button>
        {TYPES.map((t) => (
          <button
            key={t.value}
            onClick={() => setType(filters.movement_type === t.value ? '' : t.value)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filters.movement_type === t.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Read status */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">Leitura:</span>
        {(
          [
            { value: '' as const, label: 'Todas' },
            { value: 'false' as const, label: 'Não lidas' },
            { value: 'true' as const, label: 'Lidas' },
          ] as { value: 'true' | 'false' | ''; label: string }[]
        ).map((opt) => (
          <button
            key={opt.value}
            onClick={() => setRead(opt.value)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filters.is_read === opt.value
                ? 'bg-gray-800 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}
