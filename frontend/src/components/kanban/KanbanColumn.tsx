import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import TaskCard from './TaskCard'
import type { Column, Task } from '../../types/task'

interface KanbanColumnProps {
  column: Column
  tasks: Task[]
}

export default function KanbanColumn({ column, tasks }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: column.id })

  const wipExceeded = column.wip_limit != null && tasks.length >= column.wip_limit
  const wipNear = column.wip_limit != null && tasks.length === column.wip_limit - 1

  return (
    <div className="flex flex-col min-w-0 w-full">
      {/* Column header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="text-sm font-semibold text-gray-700 truncate">{column.name}</h3>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full ${
            wipExceeded
              ? 'bg-red-100 text-red-700'
              : wipNear
              ? 'bg-yellow-100 text-yellow-700'
              : 'bg-gray-100 text-gray-500'
          }`}>
            {tasks.length}
            {column.wip_limit != null ? `/${column.wip_limit}` : ''}
          </span>
          {wipExceeded && (
            <span className="text-xs text-red-600 font-medium" title="WIP limit atingido">⚠</span>
          )}
        </div>
      </div>

      {/* Drop zone */}
      <div
        ref={setNodeRef}
        className={`flex-1 flex flex-col gap-2 p-2 rounded-lg min-h-32 transition-colors ${
          isOver ? 'bg-indigo-50 ring-2 ring-indigo-300' : 'bg-gray-100'
        } ${wipExceeded ? 'ring-1 ring-red-200' : ''}`}
      >
        <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </SortableContext>
        {tasks.length === 0 && (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-xs text-gray-400">Arraste tarefas aqui</p>
          </div>
        )}
      </div>
    </div>
  )
}
