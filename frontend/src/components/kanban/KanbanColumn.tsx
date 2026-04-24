import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import TaskCard from './TaskCard'
import type { Column, Task, UserMinimal } from '../../types/task'

interface KanbanColumnProps {
  column: Column
  tasks: Task[]
  users?: UserMinimal[]
  onTaskClick?: (task: Task) => void
}

export default function KanbanColumn({ column, tasks, users, onTaskClick }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: column.id })

  const wipExceeded = column.wip_limit != null && tasks.length >= column.wip_limit
  const wipNear = column.wip_limit != null && tasks.length === column.wip_limit - 1

  return (
    <div className="flex flex-col min-w-0 w-full">
      {/* Column header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="text-sm font-medium truncate" style={{ color: '#0A1120' }}>{column.name}</h3>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="text-xs font-medium px-2 py-0.5 rounded-lg"
            style={
              wipExceeded
                ? { background: '#8B233218', color: '#8B2332' }
                : wipNear
                ? { background: '#C9A94E18', color: '#C9A94E' }
                : { background: '#FAF8F5', color: '#A69B8D', border: '1px solid #E0D9CE' }
            }>
            {tasks.length}
            {column.wip_limit != null ? `/${column.wip_limit}` : ''}
          </span>
          {wipExceeded && (
            <span className="text-xs font-medium" style={{ color: '#8B2332' }} title="WIP limit atingido">⚠</span>
          )}
        </div>
      </div>

      {/* Drop zone */}
      <div
        ref={setNodeRef}
        className="flex-1 flex flex-col gap-2 p-2 rounded-xl min-h-32 transition-all duration-150"
        style={{
          background: isOver ? '#C9A94E0A' : 'transparent',
          border: isOver ? '1.5px solid #C9A94E44' : '1.5px solid #E0D9CE',
          ...(wipExceeded ? { outline: '1px solid #8B233244' } : {}),
        }}
      >
        <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} users={users} onClick={() => onTaskClick?.(task)} />
          ))}
        </SortableContext>
        {tasks.length === 0 && (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-sm" style={{ color: '#A69B8D' }}>Arraste tarefas aqui</p>
          </div>
        )}
      </div>
    </div>
  )
}
