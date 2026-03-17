import type { MovementType } from './index'

export type { MovementType }

export interface ProcessOut {
  id: string
  number: string
  subject: string | null
  court: string | null
  is_active: boolean
  created_at: string
}

export interface Movement {
  id: string
  process_id: string
  dje_id: string | null
  type: MovementType
  content: string | null
  published_at: string | null
  is_read: boolean
  metadata_: Record<string, unknown> | null
  created_at: string
  process: ProcessOut | null
}

export interface MovementListResponse {
  items: Movement[]
  total: number
}

export interface MovementMetrics {
  total: number
  unread: number
  by_type: Record<string, number>
  last_sync: string | null
}

export interface MovementFiltersState {
  type: MovementType | ''
  is_read: 'true' | 'false' | ''
  search: string
}
