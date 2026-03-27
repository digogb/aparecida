export type TaskPriority = 'high' | 'medium' | 'low'
export type TaskCategory = 'judicial' | 'administrativa' | 'parecer' | 'publicacao_dje' | 'prazo'

export interface ChecklistItem {
  text: string
  done: boolean
}

export interface Task {
  id: string
  column_id: string
  title: string
  description?: string
  category?: TaskCategory
  priority: TaskPriority
  assigned_to?: string
  due_date?: string
  start_date?: string
  estimated_hours?: number
  tags?: string[]
  checklist?: ChecklistItem[]
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
  start_date?: string
  estimated_hours?: number
  tags?: string[]
  checklist?: ChecklistItem[]
}

export interface TaskUpdatePayload {
  title?: string
  description?: string
  category?: TaskCategory
  priority?: TaskPriority
  assigned_to?: string | null
  due_date?: string | null
  start_date?: string | null
  estimated_hours?: number | null
  tags?: string[]
  checklist?: ChecklistItem[]
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

export interface TaskComment {
  id: string
  task_id: string
  user_id: string
  content: string
  created_at: string
  updated_at: string
}

export interface UserMinimal {
  id: string
  name: string
  email: string
}
