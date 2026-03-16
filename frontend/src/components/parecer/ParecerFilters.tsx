import type { ParecerFiltersState, ParecerStatus, ParecerTema } from '../../types/parecer'

const STATUS_OPTIONS: { value: ParecerStatus; label: string }[] = [
  { value: 'pendente', label: 'Pendente' },
  { value: 'classificado', label: 'Classificado' },
  { value: 'gerado', label: 'Gerado' },
  { value: 'em_revisao', label: 'Em Revisão' },
  { value: 'devolvido', label: 'Devolvido' },
  { value: 'aprovado', label: 'Aprovado' },
  { value: 'enviado', label: 'Enviado' },
]

const TEMA_OPTIONS: { value: ParecerTema; label: string }[] = [
  { value: 'administrativo', label: 'Administrativo' },
  { value: 'tributario', label: 'Tributário' },
  { value: 'financeiro', label: 'Financeiro' },
  { value: 'previdenciario', label: 'Previdenciário' },
  { value: 'licitacao', label: 'Licitação' },
]

interface ParecerFiltersProps {
  filters: ParecerFiltersState
  onChange: (filters: ParecerFiltersState) => void
}

export default function ParecerFilters({ filters, onChange }: ParecerFiltersProps) {
  function toggleStatus(value: ParecerStatus) {
    onChange({ ...filters, status: filters.status === value ? '' : value })
  }

  function toggleTema(value: ParecerTema) {
    onChange({ ...filters, tema: filters.tema === value ? '' : value })
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide w-16">Status</span>
        {STATUS_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => toggleStatus(opt.value)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              filters.status === opt.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide w-16">Tema</span>
        {TEMA_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => toggleTema(opt.value)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              filters.tema === opt.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide w-16">Busca</span>
        <input
          type="text"
          placeholder="Buscar por remetente..."
          value={filters.remetente}
          onChange={(e) => onChange({ ...filters, remetente: e.target.value })}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
    </div>
  )
}
