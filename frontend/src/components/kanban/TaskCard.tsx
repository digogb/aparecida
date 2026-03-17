import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Calendar, User } from 'lucide-react'
import type { Task } from '../../types/task'

const PRIORITY_COLORS: Record<string, string> = {
  high: 'bg-red-500',
  medium: 'bg-yellow-400',
  low: 'bg-green-400',
}

const CATEGORY_LABELS: Record<string, string> = {
  judicial: 'Judicial',
  administrativa: 'Administrativa',
  parecer: 'Parecer',
  publicacao_dje: 'DJE',
  prazo: 'Prazo',
}

const CATEGORY_COLORS: Record<string, string> = {
  judicial: 'bg-blue-100 text-blue-700',
  administrativa: 'bg-gray-100 text-gray-700',
  parecer: 'bg-purple-100 text-purple-700',
  publicacao_dje: 'bg-orange-100 text-orange-700',
  prazo: 'bg-red-100 text-red-700',
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

  const processId = (task.source_ref?.process_id as string | undefined)
    ? String(task.source_ref!.process_id).slice(0, 8)
    : null

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-white rounded-lg shadow-sm border border-gray-200 cursor-grab active:cursor-grabbing select-none overflow-hidden"
    >
      {/* Priority bar */}
      <div className={`h-1 w-full ${PRIORITY_COLORS[task.priority] ?? 'bg-gray-300'}`} />

      <div className="p-3 space-y-2">
        {/* Title */}
        <p className="text-sm font-medium text-gray-900 leading-tight line-clamp-2">
          {task.title}
        </p>

        {/* Process ref */}
        {processId && (
          <p className="text-xs text-gray-400 font-mono">#{processId}</p>
        )}

        <div className="flex items-center justify-between gap-2 flex-wrap">
          {/* Category badge */}
          {task.category && (
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${CATEGORY_COLORS[task.category] ?? 'bg-gray-100 text-gray-600'}`}>
              {CATEGORY_LABELS[task.category] ?? task.category}
            </span>
          )}

          <div className="flex items-center gap-2 ml-auto">
            {/* Assignee avatar */}
            {task.assigned_to && (
              <div
                className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center"
                title={task.assigned_to}
              >
                <User className="w-3 h-3 text-indigo-600" />
              </div>
            )}

            {/* Due date */}
            {dueDateStr && (
              <div className={`flex items-center gap-1 text-xs ${isOverdue ? 'text-red-600' : 'text-gray-400'}`}>
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
