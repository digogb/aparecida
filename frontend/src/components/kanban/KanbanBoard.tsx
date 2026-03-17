import { useState, useMemo } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  MouseSensor,
  TouchSensor,
  closestCorners,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import { Plus, LayoutDashboard, Clock, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'

import { useBoard, useMoveTask } from '../../hooks/useTasks'
import { useTaskWebSocket } from '../../hooks/useTaskWebSocket'
import KanbanColumn from './KanbanColumn'
import TaskCard from './TaskCard'
import TaskFilters from './TaskFilters'
import CreateTaskModal from './CreateTaskModal'
import type { Task, TaskCategory } from '../../types/task'

export default function KanbanBoard() {
  useTaskWebSocket()

  const { data: board, isLoading, isError } = useBoard()
  const moveTask = useMoveTask()

  const [activeTask, setActiveTask] = useState<Task | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<TaskCategory | null>(null)

  const sensors = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 5 } }),
  )

  // Derived metrics
  const metrics = useMemo(() => {
    if (!board) return { total: 0, high: 0, overdue: 0, done: 0 }
    const allTasks = board.columns.flatMap((c) => c.tasks)
    const now = new Date()
    const doneColumn = board.columns.find((c) => c.name === 'Concluída')
    return {
      total: allTasks.length,
      high: allTasks.filter((t) => t.priority === 'high').length,
      overdue: allTasks.filter((t) => t.due_date && new Date(t.due_date) < now).length,
      done: doneColumn?.tasks.length ?? 0,
    }
  }, [board])

  // Build task lookup map for DnD
  const taskMap = useMemo(() => {
    const map = new Map<string, Task>()
    board?.columns.flatMap((c) => c.tasks).forEach((t) => map.set(t.id, t))
    return map
  }, [board])

  const handleDragStart = ({ active }: DragStartEvent) => {
    const task = taskMap.get(String(active.id))
    if (task) setActiveTask(task)
  }

  const handleDragEnd = ({ active, over }: DragEndEvent) => {
    setActiveTask(null)
    if (!over || !board) return

    const taskId = String(active.id)
    const task = taskMap.get(taskId)
    if (!task) return

    // Determine target column and position
    let targetColumnId = String(over.id)
    let targetPosition = 0

    // If dropped on a task, find that task's column
    if (taskMap.has(targetColumnId)) {
      const targetTask = taskMap.get(targetColumnId)!
      targetColumnId = targetTask.column_id
      targetPosition = targetTask.position
    } else {
      // Dropped on column droppable — append to end
      const targetColumn = board.columns.find((c) => c.id === targetColumnId)
      targetPosition = targetColumn?.tasks.length ?? 0
    }

    if (task.column_id === targetColumnId && task.position === targetPosition) return

    moveTask.mutate({ taskId, payload: { column_id: targetColumnId, position: targetPosition } })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
      </div>
    )
  }

  if (isError || !board) {
    return (
      <div className="p-6">
        <p className="text-red-600 text-sm">Erro ao carregar o quadro Kanban.</p>
      </div>
    )
  }

  // Apply category filter
  const filteredColumns = board.columns.map((col) => ({
    ...col,
    tasks: selectedCategory
      ? col.tasks.filter((t) => t.category === selectedCategory)
      : col.tasks,
  }))

  return (
    <div className="p-6 flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Tarefas</h1>
          <p className="text-sm text-gray-500">{board.name}</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nova Tarefa
        </button>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricCard icon={<LayoutDashboard className="w-4 h-4" />} label="Total" value={metrics.total} color="indigo" />
        <MetricCard icon={<AlertCircle className="w-4 h-4" />} label="Alta prioridade" value={metrics.high} color="red" />
        <MetricCard icon={<Clock className="w-4 h-4" />} label="Vencidas" value={metrics.overdue} color="yellow" />
        <MetricCard icon={<CheckCircle2 className="w-4 h-4" />} label="Concluídas" value={metrics.done} color="green" />
      </div>

      {/* Filters */}
      <TaskFilters selectedCategory={selectedCategory} onCategoryChange={setSelectedCategory} />

      {/* Kanban grid with DnD */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div
          className="grid gap-4 overflow-x-auto pb-2"
          style={{ gridTemplateColumns: `repeat(${board.columns.length}, minmax(220px, 1fr))` }}
        >
          {filteredColumns.map((col) => (
            <KanbanColumn key={col.id} column={col} tasks={col.tasks} />
          ))}
        </div>

        <DragOverlay>
          {activeTask ? <TaskCard task={activeTask} /> : null}
        </DragOverlay>
      </DndContext>

      {/* Create task modal */}
      {showCreateModal && (
        <CreateTaskModal
          columns={board.columns}
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </div>
  )
}

interface MetricCardProps {
  icon: React.ReactNode
  label: string
  value: number
  color: 'indigo' | 'red' | 'yellow' | 'green'
}

const COLOR_CLASSES: Record<string, string> = {
  indigo: 'bg-indigo-50 text-indigo-600',
  red: 'bg-red-50 text-red-600',
  yellow: 'bg-yellow-50 text-yellow-600',
  green: 'bg-green-50 text-green-600',
}

function MetricCard({ icon, label, value, color }: MetricCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-3">
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${COLOR_CLASSES[color]}`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xl font-bold text-gray-900">{value}</p>
        <p className="text-xs text-gray-500 truncate">{label}</p>
      </div>
    </div>
  )
}
