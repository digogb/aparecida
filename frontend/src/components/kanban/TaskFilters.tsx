import type { TaskCategory } from '../../types/task'

const CATEGORIES: { value: TaskCategory; label: string }[] = [
  { value: 'judicial', label: 'Judicial' },
  { value: 'administrativa', label: 'Administrativa' },
  { value: 'parecer', label: 'Parecer' },
  { value: 'publicacao_dje', label: 'DJE' },
  { value: 'prazo', label: 'Prazo' },
]

interface TaskFiltersProps {
  selectedCategory: TaskCategory | null
  onCategoryChange: (cat: TaskCategory | null) => void
}

export default function TaskFilters({ selectedCategory, onCategoryChange }: TaskFiltersProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <button
        onClick={() => onCategoryChange(null)}
        className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
          selectedCategory === null
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }`}
      >
        Todas
      </button>
      {CATEGORIES.map((cat) => (
        <button
          key={cat.value}
          onClick={() => onCategoryChange(selectedCategory === cat.value ? null : cat.value)}
          className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
            selectedCategory === cat.value
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          {cat.label}
        </button>
      ))}
    </div>
  )
}
