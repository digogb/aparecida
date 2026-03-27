import { Search } from 'lucide-react'
import type { TaskCategory, TaskPriority, UserMinimal } from '../../types/task'

const CATS: { value: TaskCategory; label: string; color: string }[] = [
  { value: 'judicial',       label: 'Judicial',       color: '#142038' },
  { value: 'administrativa', label: 'Administrativa', color: '#6B6860' },
  { value: 'parecer',        label: 'Parecer',        color: '#C9A94E' },
  { value: 'publicacao_dje', label: 'DJE',            color: '#A69B8D' },
  { value: 'prazo',          label: 'Prazo',          color: '#8B2332' },
]

const PRIORITIES: { value: TaskPriority; label: string; color: string }[] = [
  { value: 'high',   label: 'Alta',  color: '#8B2332' },
  { value: 'medium', label: 'Média', color: '#C9A94E' },
  { value: 'low',    label: 'Baixa', color: '#5B7553' },
]

export interface TaskFiltersState {
  category: TaskCategory | null
  priority: TaskPriority | null
  assignee: string | null
  search: string
}

interface TaskFiltersProps {
  filters: TaskFiltersState
  onFiltersChange: (filters: TaskFiltersState) => void
  users?: UserMinimal[]
}

const pillBase = "px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"

export default function TaskFilters({ filters, onFiltersChange, users }: TaskFiltersProps) {
  const setFilter = (patch: Partial<TaskFiltersState>) => {
    onFiltersChange({ ...filters, ...patch })
  }

  return (
    <div className="space-y-3">
      {/* Search bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: '#A69B8D' }} />
        <input
          type="text"
          value={filters.search}
          onChange={(e) => setFilter({ search: e.target.value })}
          className="w-full rounded-xl pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2"
          style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
          placeholder="Buscar tarefas..."
        />
      </div>

      {/* Filter pills */}
      <div className="flex items-center gap-4 flex-wrap">
        {/* Category */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs font-medium uppercase tracking-widest mr-0.5" style={{ color: '#A69B8D' }}>Categoria</span>
          <button onClick={() => setFilter({ category: null })} className={pillBase}
            style={filters.category === null
              ? { background: '#142038', color: '#F5F0E8', border: '1.5px solid transparent' }
              : { background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
            Todas
          </button>
          {CATS.map(c => (
            <button key={c.value}
              onClick={() => setFilter({ category: filters.category === c.value ? null : c.value })}
              className={pillBase}
              style={filters.category === c.value
                ? { background: `${c.color}18`, color: c.color, border: `1.5px solid ${c.color}44` }
                : { background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
              {c.label}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="w-px h-5" style={{ background: '#E0D9CE' }} />

        {/* Priority */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs font-medium uppercase tracking-widest mr-0.5" style={{ color: '#A69B8D' }}>Prioridade</span>
          {PRIORITIES.map(p => (
            <button key={p.value}
              onClick={() => setFilter({ priority: filters.priority === p.value ? null : p.value })}
              className={pillBase}
              style={filters.priority === p.value
                ? { background: `${p.color}18`, color: p.color, border: `1.5px solid ${p.color}44` }
                : { background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
              {p.label}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="w-px h-5" style={{ background: '#E0D9CE' }} />

        {/* Assignee */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-medium uppercase tracking-widest mr-0.5" style={{ color: '#A69B8D' }}>Responsável</span>
          <select
            value={filters.assignee ?? ''}
            onChange={(e) => setFilter({ assignee: e.target.value || null })}
            className="rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2"
            style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
          >
            <option value="">Todos</option>
            {users?.map(u => (
              <option key={u.id} value={u.id}>{u.name}</option>
            ))}
          </select>
        </div>

        {/* Clear all */}
        {(filters.category || filters.priority || filters.assignee || filters.search) && (
          <>
            <div className="w-px h-5" style={{ background: '#E0D9CE' }} />
            <button
              onClick={() => onFiltersChange({ category: null, priority: null, assignee: null, search: '' })}
              className="text-xs font-medium cursor-pointer hover:underline"
              style={{ color: '#8B2332' }}>
              Limpar filtros
            </button>
          </>
        )}
      </div>
    </div>
  )
}
