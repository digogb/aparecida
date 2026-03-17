export type TaskPriority = 'high' | 'medium' | 'low'
export type TaskCategory = 'judicial' | 'administrativa' | 'parecer' | 'publicacao_dje' | 'prazo'

export interface Task {
  id: string
  column_id: string
  title: string
  description?: string
  category?: TaskCategory
  priority: TaskPriority
  assigned_to?: string
  due_date?: string
  position: number
  source_ref?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface Column {
  id: string
  board_id: string
  name: string
  position: number
  wip_limit?: number
  tasks: Task[]
}

export interface Board {
  id: string
  name: string
  columns: Column[]
}

export interface TaskCreatePayload {
  column_id: string
  title: string
  description?: string
  category?: TaskCategory
  priority?: TaskPriority
  assigned_to?: string
  due_date?: string
}

export interface TaskMovePayload {
  column_id: string
  position: number
}

export interface TaskHistoryEntry {
  id: string
  task_id: string
  from_column_id?: string
  to_column_id?: string
  changed_by?: string
  notes?: string
  created_at: string
}
