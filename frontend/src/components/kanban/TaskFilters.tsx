import type { TaskCategory } from '../../types/task'

const CATS: { value: TaskCategory; label: string; color: string; bg: string }[] = [
  { value: 'judicial',      label: 'Judicial',      color: '#3730A3', bg: '#E0E7FF' },
  { value: 'administrativa',label: 'Administrativa', color: '#0C4A6E', bg: '#E0F2FE' },
  { value: 'parecer',       label: 'Parecer',        color: '#065F46', bg: '#D1FAE5' },
  { value: 'publicacao_dje',label: 'DJE',            color: '#92400E', bg: '#FEF3C7' },
  { value: 'prazo',         label: 'Prazo',          color: '#991B1B', bg: '#FEE2E2' },
]

export default function TaskFilters({ selectedCategory, onCategoryChange }: {
  selectedCategory: TaskCategory | null
  onCategoryChange: (cat: TaskCategory | null) => void
}) {
  return (
    <div className="flex items-center gap-1.5 flex-wrap">
      <span className="text-xs font-semibold uppercase tracking-widest mr-1" style={{ color: '#9CA3AF' }}>Categoria</span>
      <button onClick={() => onCategoryChange(null)}
        className="text-xs px-3 py-1 rounded-full font-semibold transition-all"
        style={selectedCategory === null
          ? { background: '#1C1C2E', color: '#fff', border: '1.5px solid transparent' }
          : { background: '#fff', color: '#6B7280', border: '1.5px solid #E5E3DC' }}>
        Todas
      </button>
      {CATS.map(c => (
        <button key={c.value} onClick={() => onCategoryChange(selectedCategory === c.value ? null : c.value)}
          className="text-xs px-3 py-1 rounded-full font-semibold transition-all"
          style={selectedCategory === c.value
            ? { background: c.bg, color: c.color, border: `1.5px solid ${c.color}44` }
            : { background: '#fff', color: '#6B7280', border: '1.5px solid #E5E3DC' }}>
          {c.label}
        </button>
      ))}
    </div>
  )
}
