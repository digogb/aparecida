import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Calendar, User } from 'lucide-react'
import type { Task } from '../../types/task'

const PRIORITY_COLORS: Record<string, string> = {
  high: '#8B2332',
  medium: '#C4953A',
  low: '#5B7553',
}

const CATEGORY_LABELS: Record<string, string> = {
  judicial: 'Judicial',
  administrativa: 'Administrativa',
  parecer: 'Parecer',
  publicacao_dje: 'DJE',
  prazo: 'Prazo',
}

const CATEGORY_COLORS: Record<string, { color: string }> = {
  judicial: { color: '#1B2838' },
  administrativa: { color: '#6B6860' },
  parecer: { color: '#C4953A' },
  publicacao_dje: { color: '#A69B8D' },
  prazo: { color: '#8B2332' },
}

interface TaskCardProps {
  task: Task
}

export default function TaskCard({ task }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  const isOverdue = task.due_date && new Date(task.due_date) < new Date()
  const dueDateStr = task.due_date
    ? new Date(task.due_date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    : null

  const processId = null

  const priorityColor = PRIORITY_COLORS[task.priority] ?? '#A69B8D'

  return (
    <div
      ref={setNodeRef}
      style={{ ...style, background: '#FAF8F5', border: '1.5px solid #DDD9D2' }}
      {...attributes}
      {...listeners}
      className="rounded-xl cursor-grab active:cursor-grabbing select-none overflow-hidden"
    >
      {/* Priority bar */}
      <div className="h-1 w-full" style={{ background: priorityColor }} />

      <div className="p-3 space-y-2">
        {/* Title */}
        <p className="text-sm font-medium leading-tight line-clamp-2" style={{ color: '#2D2D3A' }}>
          {task.title}
        </p>

        {/* Process ref */}
        {processId && (
          <p className="text-xs font-mono" style={{ color: '#A69B8D' }}>#{processId}</p>
        )}

        <div className="flex items-center justify-between gap-2 flex-wrap">
          {/* Category badge */}
          {task.category && (() => {
            const cat = CATEGORY_COLORS[task.category]
            const color = cat?.color ?? '#6B6860'
            return (
              <span className="text-xs px-2 py-0.5 rounded-lg font-medium"
                style={{ background: `${color}18`, color }}>
                {CATEGORY_LABELS[task.category] ?? task.category}
              </span>
            )
          })()}

          <div className="flex items-center gap-2 ml-auto">
            {/* Assignee avatar */}
            {task.assigned_to && (
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center"
                style={{ background: '#C4953A18' }}
                title={task.assigned_to}
              >
                <User className="w-3 h-3" style={{ color: '#C4953A' }} />
              </div>
            )}

            {/* Due date */}
            {dueDateStr && (
              <div className="flex items-center gap-1 text-xs" style={{ color: isOverdue ? '#8B2332' : '#A69B8D' }}>
                <Calendar className="w-3 h-3" />
                <span>{dueDateStr}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
