import { useSortable, defaultAnimateLayoutChanges, type AnimateLayoutChanges } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Calendar, User, Clock, CheckSquare, Tag, MessageSquare } from 'lucide-react'
import type { Task, UserMinimal } from '../../types/task'

const PRIORITY_COLORS: Record<string, string> = {
  high: '#8B2332',
  medium: '#C9A94E',
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
  judicial: { color: '#142038' },
  administrativa: { color: '#6B6860' },
  parecer: { color: '#C9A94E' },
  publicacao_dje: { color: '#A69B8D' },
  prazo: { color: '#8B2332' },
}

interface TaskCardProps {
  task: Task
  users?: UserMinimal[]
  onClick?: () => void
}

function getDueDateInfo(dueDateStr: string): { label: string; isOverdue: boolean; isUrgent: boolean } {
  const due = new Date(dueDateStr)
  const now = new Date()
  const diffMs = due.getTime() - now.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return { label: `${Math.abs(diffDays)}d atrasada`, isOverdue: true, isUrgent: false }
  }
  if (diffDays === 0) {
    return { label: 'Vence hoje', isOverdue: false, isUrgent: true }
  }
  if (diffDays <= 2) {
    return { label: `Vence em ${diffDays}d`, isOverdue: false, isUrgent: true }
  }
  const formatted = due.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  return { label: formatted, isOverdue: false, isUrgent: false }
}

const noLayoutAnimation: AnimateLayoutChanges = (args) =>
  defaultAnimateLayoutChanges({ ...args, wasDragging: true })

export default function TaskCard({ task, users, onClick }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
    animateLayoutChanges: noLayoutAnimation,
  })

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  const dueDateInfo = task.due_date ? getDueDateInfo(task.due_date) : null
  const priorityColor = PRIORITY_COLORS[task.priority] ?? '#A69B8D'

  const assigneeName = task.assigned_to && users
    ? users.find(u => u.id === task.assigned_to)?.name
    : null

  const checklistProgress = task.checklist?.length
    ? { done: task.checklist.filter(i => i.done).length, total: task.checklist.length }
    : null

  return (
    <div
      ref={setNodeRef}
      style={{ ...style, background: '#F5F0E8', border: '1.5px solid #E0D9CE' }}
      {...attributes}
      {...listeners}
      onClick={onClick}
      className="rounded-xl cursor-grab active:cursor-grabbing select-none overflow-hidden group hover:border-[#C9A94E88] transition-all duration-150"
    >
      {/* Priority bar */}
      <div className="h-1 w-full" style={{ background: priorityColor }} />

      <div className="p-3 space-y-2">
        {/* Title */}
        <p className="text-sm font-medium leading-tight line-clamp-2" style={{ color: '#0A1120' }}>
          {task.title}
        </p>

        {/* Tags */}
        {task.tags && task.tags.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {task.tags.slice(0, 3).map((tag, i) => (
              <span key={i} className="text-[10px] px-1.5 py-0.5 rounded font-medium"
                style={{ background: '#C9A94E18', color: '#8B7A3A' }}>
                {tag}
              </span>
            ))}
            {task.tags.length > 3 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ color: '#A69B8D' }}>
                +{task.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Checklist progress bar */}
        {checklistProgress && (
          <div className="flex items-center gap-1.5">
            <CheckSquare className="w-3 h-3" style={{ color: checklistProgress.done === checklistProgress.total ? '#5B7553' : '#A69B8D' }} />
            <div className="flex-1 h-1 rounded-full" style={{ background: '#E0D9CE' }}>
              <div className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${(checklistProgress.done / checklistProgress.total) * 100}%`,
                  background: checklistProgress.done === checklistProgress.total ? '#5B7553' : '#C9A94E',
                }} />
            </div>
            <span className="text-[10px] font-medium" style={{ color: '#A69B8D' }}>
              {checklistProgress.done}/{checklistProgress.total}
            </span>
          </div>
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
            {/* Estimated hours */}
            {task.estimated_hours && (
              <div className="flex items-center gap-0.5 text-[10px]" style={{ color: '#A69B8D' }}>
                <Clock className="w-3 h-3" />
                <span>{task.estimated_hours}h</span>
              </div>
            )}

            {/* Assignee */}
            {task.assigned_to && (
              <div
                className="flex items-center gap-1 shrink-0"
                title={assigneeName ?? task.assigned_to}
              >
                <div className="w-5 h-5 rounded-full flex items-center justify-center"
                  style={{ background: '#C9A94E18' }}>
                  <User className="w-2.5 h-2.5" style={{ color: '#C9A94E' }} />
                </div>
                {assigneeName && (
                  <span className="text-[10px] font-medium max-w-[60px] truncate" style={{ color: '#6B6860' }}>
                    {assigneeName.split(' ')[0]}
                  </span>
                )}
              </div>
            )}

            {/* Due date */}
            {dueDateInfo && (
              <div className="flex items-center gap-1 text-xs"
                style={{ color: dueDateInfo.isOverdue ? '#8B2332' : dueDateInfo.isUrgent ? '#C9A94E' : '#A69B8D' }}>
                <Calendar className="w-3 h-3" />
                <span className={dueDateInfo.isOverdue ? 'font-medium' : ''}>{dueDateInfo.label}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
