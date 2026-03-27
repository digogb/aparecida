import { useState, useMemo, useCallback, useRef } from 'react'
import { createPortal } from 'react-dom'
import {
  DndContext, DragEndEvent, DragOverEvent, DragOverlay, DragStartEvent,
  MouseSensor, TouchSensor, closestCorners, useSensor, useSensors,
} from '@dnd-kit/core'
import { arrayMove } from '@dnd-kit/sortable'

import { useBoard, useMoveTask, useUsers } from '../../hooks/useTasks'
import { useTaskWebSocket } from '../../hooks/useTaskWebSocket'
import KanbanColumn from './KanbanColumn'
import TaskCard from './TaskCard'
import TaskFilters, { type TaskFiltersState } from './TaskFilters'
import CreateTaskModal from './CreateTaskModal'
import TaskDetailModal from './TaskDetailModal'
import type { Board, Column, Task } from '../../types/task'

const METRIC_DEFS = [
  { key: 'total',   label: 'Total',           tone: '#0A1120' },
  { key: 'high',    label: 'Alta prioridade',  tone: '#8B2332' },
  { key: 'overdue', label: 'Vencidas',         tone: '#C9A94E' },
  { key: 'done',    label: 'Concluídas',       tone: '#5B7553' },
]

/** Deep-clone columns so we can mutate locally during drag */
function cloneColumns(columns: Column[]): Column[] {
  return columns.map(c => ({ ...c, tasks: c.tasks.map(t => ({ ...t })) }))
}

/** Find which column contains a given id (task id or column id) */
function findColumnOfItem(columns: Column[], id: string): Column | undefined {
  // Is it a column id?
  const col = columns.find(c => c.id === id)
  if (col) return col
  // Is it a task id?
  return columns.find(c => c.tasks.some(t => t.id === id))
}

export default function KanbanBoard() {
  useTaskWebSocket()

  const { data: board, isLoading, isError } = useBoard()
  const { data: users } = useUsers()
  const moveTask = useMoveTask()

  const [activeTask, setActiveTask] = useState<Task | null>(null)
  const [localColumns, setLocalColumns] = useState<Column[] | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [filters, setFilters] = useState<TaskFiltersState>({
    category: null,
    priority: null,
    assignee: null,
    search: '',
  })

  // Track original position at drag start for the API call
  const dragOrigin = useRef<{ columnId: string; position: number } | null>(null)

  const sensors = useSensors(
    useSensor(MouseSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 5 } }),
  )

  // Use local columns during drag, otherwise use server data
  const columns = localColumns ?? board?.columns ?? []

  const metrics = useMemo(() => {
    if (!board) return { total: 0, high: 0, overdue: 0, done: 0 }
    const all = board.columns.flatMap(c => c.tasks)
    const now = new Date()
    return {
      total: all.length,
      high: all.filter(t => t.priority === 'high').length,
      overdue: all.filter(t => t.due_date && new Date(t.due_date) < now).length,
      done: board.columns.find(c => c.name === 'Concluída')?.tasks.length ?? 0,
    }
  }, [board])

  const handleDragStart = ({ active }: DragStartEvent) => {
    if (!board) return
    const cols = cloneColumns(board.columns)
    const col = cols.find(c => c.tasks.some(t => t.id === active.id))
    const task = col?.tasks.find(t => t.id === active.id)
    if (task && col) {
      setActiveTask(task)
      dragOrigin.current = { columnId: col.id, position: task.position }
      setLocalColumns(cols)
    }
  }

  const handleDragOver = ({ active, over }: DragOverEvent) => {
    if (!over || !localColumns) return
    const activeId = String(active.id)
    const overId = String(over.id)
    if (activeId === overId) return

    const fromCol = findColumnOfItem(localColumns, activeId)
    const toCol = findColumnOfItem(localColumns, overId)
    if (!fromCol || !toCol) return

    if (fromCol.id === toCol.id) {
      // Reorder within same column
      const oldIdx = fromCol.tasks.findIndex(t => t.id === activeId)
      const overTask = fromCol.tasks.findIndex(t => t.id === overId)
      if (oldIdx === -1 || overTask === -1 || oldIdx === overTask) return
      setLocalColumns(prev => {
        if (!prev) return prev
        return prev.map(c => {
          if (c.id !== fromCol.id) return c
          const reordered = arrayMove([...c.tasks], oldIdx, overTask)
          reordered.forEach((t, i) => { t.position = i })
          return { ...c, tasks: reordered }
        })
      })
    } else {
      // Move across columns
      const taskIdx = fromCol.tasks.findIndex(t => t.id === activeId)
      if (taskIdx === -1) return
      const task = { ...fromCol.tasks[taskIdx] }
      const overIdx = toCol.tasks.findIndex(t => t.id === overId)
      const insertAt = overIdx === -1 ? toCol.tasks.length : overIdx

      setLocalColumns(prev => {
        if (!prev) return prev
        return prev.map(c => {
          if (c.id === fromCol.id) {
            const tasks = c.tasks.filter(t => t.id !== activeId)
            tasks.forEach((t, i) => { t.position = i })
            return { ...c, tasks }
          }
          if (c.id === toCol.id) {
            const tasks = [...c.tasks]
            task.column_id = c.id
            tasks.splice(insertAt, 0, task)
            tasks.forEach((t, i) => { t.position = i })
            return { ...c, tasks }
          }
          return c
        })
      })
    }
  }

  const handleDragEnd = ({ active }: DragEndEvent) => {
    setActiveTask(null)

    if (!localColumns || !dragOrigin.current) {
      setLocalColumns(null)
      return
    }

    // Find final position of the dragged task
    const taskId = String(active.id)
    const destCol = localColumns.find(c => c.tasks.some(t => t.id === taskId))
    const task = destCol?.tasks.find(t => t.id === taskId)

    if (destCol && task) {
      const orig = dragOrigin.current
      const changed = orig.columnId !== destCol.id || orig.position !== task.position
      if (changed) {
        moveTask.mutate({
          taskId,
          payload: { column_id: destCol.id, position: task.position },
        })
      }
    }

    dragOrigin.current = null
    setLocalColumns(null)
  }

  const handleDragCancel = () => {
    setActiveTask(null)
    setLocalColumns(null)
    dragOrigin.current = null
  }

  const handleTaskClick = useCallback((task: Task) => {
    setSelectedTask(task)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-full flex items-center justify-center" style={{ background: '#F5F0E8' }}>
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin" style={{ borderColor: '#E0D9CE44', borderTopColor: '#A69B8D' }} />
          <p className="text-sm" style={{ color: '#A69B8D' }}>Carregando quadro…</p>
        </div>
      </div>
    )
  }

  if (isError || !board) {
    return (
      <div className="min-h-full flex items-center justify-center" style={{ background: '#F5F0E8' }}>
        <div className="rounded-xl px-6 py-5 text-base" style={{ background: '#8B233218', color: '#8B2332', border: '1.5px solid #8B233222' }}>
          Erro ao carregar o quadro Kanban.
        </div>
      </div>
    )
  }

  const metricValues = [metrics.total, metrics.high, metrics.overdue, metrics.done]

  // Apply filters
  const filteredColumns = columns.map(col => ({
    ...col,
    tasks: col.tasks.filter(t => {
      if (filters.category && t.category !== filters.category) return false
      if (filters.priority && t.priority !== filters.priority) return false
      if (filters.assignee && t.assigned_to !== filters.assignee) return false
      if (filters.search) {
        const q = filters.search.toLowerCase()
        const matchTitle = t.title.toLowerCase().includes(q)
        const matchDesc = t.description?.toLowerCase().includes(q)
        const matchTags = t.tags?.some(tag => tag.toLowerCase().includes(q))
        if (!matchTitle && !matchDesc && !matchTags) return false
      }
      return true
    }),
  }))

  const totalFiltered = filteredColumns.reduce((sum, col) => sum + col.tasks.length, 0)
  const totalAll = columns.reduce((sum, col) => sum + col.tasks.length, 0)
  const isFiltered = filters.category || filters.priority || filters.assignee || filters.search

  return (
    <div className="min-h-full flex flex-col" style={{ background: '#F5F0E8' }}>
      <div className="px-6 py-8 space-y-6">

        {/* Header */}
        <div className="animate-fade-up flex items-end justify-between">
          <h1 className="font-display" style={{ fontSize: 32, fontWeight: 400, color: '#142038', letterSpacing: '-0.02em' }}>
            Tarefas
          </h1>
          <button onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
            style={{ background: '#142038', color: '#F5F0E8' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Nova Tarefa
          </button>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {METRIC_DEFS.map((m, i) => (
            <div key={m.key} className="animate-count rounded-xl overflow-hidden"
              style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', animationDelay: `${i * 50}ms` }}>
              <div className="h-1" style={{ background: m.tone }} />
              <div className="px-5 py-4">
                <span className="font-display leading-none block"
                  style={{ fontSize: 38, fontWeight: 500, color: m.tone, letterSpacing: '-0.03em', fontVariantNumeric: 'tabular-nums' }}>
                  {metricValues[i]}
                </span>
                <span className="text-sm font-medium" style={{ color: '#6B6860' }}>{m.label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="animate-fade-up" style={{ animationDelay: '180ms' }}>
          <TaskFilters filters={filters} onFiltersChange={setFilters} users={users} />
          {isFiltered && (
            <p className="text-xs mt-2" style={{ color: '#A69B8D' }}>
              Mostrando {totalFiltered} de {totalAll} tarefas
            </p>
          )}
        </div>
      </div>

      {/* Kanban board */}
      <div className="px-6 pb-8 flex-1 animate-fade-up" style={{ animationDelay: '260ms' }}>
        <DndContext sensors={sensors} collisionDetection={closestCorners}
          onDragStart={handleDragStart} onDragOver={handleDragOver}
          onDragEnd={handleDragEnd} onDragCancel={handleDragCancel}>
          <div className="grid gap-4 overflow-x-auto pb-2"
            style={{ gridTemplateColumns: `repeat(${board.columns.length}, minmax(220px, 1fr))` }}>
            {filteredColumns.map(col => (
              <KanbanColumn key={col.id} column={col} tasks={col.tasks} users={users} onTaskClick={handleTaskClick} />
            ))}
          </div>
          {createPortal(
            <DragOverlay>{activeTask ? <TaskCard task={activeTask} users={users} /> : null}</DragOverlay>,
            document.body,
          )}
        </DndContext>
      </div>

      {showCreateModal && (
        <CreateTaskModal columns={board.columns} onClose={() => setShowCreateModal(false)} />
      )}

      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          columns={board.columns}
          onClose={() => setSelectedTask(null)}
        />
      )}
    </div>
  )
}
