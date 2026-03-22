import type { TaskCategory } from '../../types/task'

const CATS: { value: TaskCategory; label: string; color: string }[] = [
  { value: 'judicial',       label: 'Judicial',       color: '#1B2838' },
  { value: 'administrativa', label: 'Administrativa', color: '#6B6860' },
  { value: 'parecer',        label: 'Parecer',        color: '#C4953A' },
  { value: 'publicacao_dje', label: 'DJE',            color: '#A69B8D' },
  { value: 'prazo',          label: 'Prazo',          color: '#8B2332' },
]

export default function TaskFilters({ selectedCategory, onCategoryChange }: {
  selectedCategory: TaskCategory | null
  onCategoryChange: (cat: TaskCategory | null) => void
}) {
  return (
    <div className="flex items-center gap-1.5 flex-wrap">
      <span className="text-sm font-medium uppercase tracking-widest mr-1" style={{ color: '#A69B8D' }}>Categoria</span>
      <button onClick={() => onCategoryChange(null)}
        className="px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
        style={selectedCategory === null
          ? { background: '#1B2838', color: '#FAF8F5', border: '1.5px solid transparent' }
          : { background: '#FAF8F5', color: '#6B6860', border: '1.5px solid #DDD9D2' }}>
        Todas
      </button>
      {CATS.map(c => (
        <button key={c.value} onClick={() => onCategoryChange(selectedCategory === c.value ? null : c.value)}
          className="px-3 py-1 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer"
          style={selectedCategory === c.value
            ? { background: `${c.color}18`, color: c.color, border: `1.5px solid ${c.color}44` }
            : { background: '#FAF8F5', color: '#6B6860', border: '1.5px solid #DDD9D2' }}>
          {c.label}
        </button>
      ))}
    </div>
  )
}
